import logging
from typing import Dict, Type, TypedDict
from jobgeneration import config
from dataclasses import asdict, dataclass
from jinja2 import Template
from jobgeneration.clusterconfig import ClusterConfig

from jobgeneration.variants import NativeVariant, RuntimeVariant, SingularityVariant

JOB_TEMPLATE: Template = Template(config.SLURM_JOB_TEMPLATE_PATH.read_text())

SINGULARITY_CMD = "singularity exec {bind} {image} /build/bin/laplace {nx} {ny}"
SINGULARITY_BIND_OPT = "--bind {bind}"

NATIVE_CMD = "build/bin/laplace {nx} {ny}"
NATIVE_BUILD_CMD = "mkdir -p build && cd build && cmake .. && make -j4 && cd .."

SINGULARITY_BIND_OPT = "--bind {bind}"


APPCMD_BY_VARIANT = {
    SingularityVariant: SINGULARITY_CMD,
    NativeVariant: NATIVE_CMD,
}


def get_modules(cluster_config: ClusterConfig, variant: RuntimeVariant) -> list[str]:
    return [
        # NOTE: We have to load MPI before the variant based modules,
        # because CMake causes a build error if the necessary modules are not available when it's loaded.
        *cluster_config.mpi_configs[variant.mpi.name].modules,
        *cluster_config.variant_modules[type(variant)]
    ]


@dataclass
class Job:
    nodes: int
    ntasks_per_node: int
    output: str
    workdir: str
    modules: str
    mpicmd: str
    app: str
    buildcmd: str = ""


def get_bind_opt(cluster_config: ClusterConfig, variant: RuntimeVariant) -> str:
    if isinstance(variant, SingularityVariant) and variant.mpi_approach == "bind":
        return SINGULARITY_BIND_OPT.format(bind=cluster_config.mpi_configs[variant.mpi.name])

    return ""


def get_app_cmd(cluster_config: ClusterConfig, variant: RuntimeVariant, nodes: int) -> str:
    app_cmd = APPCMD_BY_VARIANT[type(variant)]

    if isinstance(variant, SingularityVariant):
        return app_cmd.format(
            image=variant.image.name,
            bind=get_bind_opt(cluster_config, variant),
            **config.NODE_SCALING[nodes],
        )

    return app_cmd.format(**config.NODE_SCALING[nodes])


def get_build_cmd(variant: RuntimeVariant) -> str:
    if isinstance(variant, NativeVariant):
        return NATIVE_BUILD_CMD

    return ""


def make_job(cluster_config: ClusterConfig, nodes: int, variant: RuntimeVariant) -> Job:
    processes = nodes * config.TASKS_PER_NODE
    logging.info(f"Using node scaling: {config.NODE_SCALING}")

    return Job(
        nodes=nodes,
        ntasks_per_node=config.TASKS_PER_NODE,
        workdir=f"{variant.runtime_approach}-{processes}",
        output=f"{variant.runtime_approach}-{processes}.out",
        modules=" ".join(get_modules(cluster_config, variant)),
        mpicmd=variant.mpi.command(processes),
        buildcmd=get_build_cmd(variant),
        app=get_app_cmd(cluster_config, variant, processes),
    )


def format_job_content(job: Job) -> str:
    partition = "shortrun_small" if job.nodes <= 50 else "shortrun_large"
    return JOB_TEMPLATE.render(**asdict(job), partition=partition)


def write_job_file(jobfilename: str, job: Job) -> None:
    path = config.SLURM_JOB_DIR / jobfilename
    logging.info(f"Writing job file [green]{path}[/]")
    path.touch(exist_ok=True)
    path.write_text(format_job_content(job))


def create(cluster_config: ClusterConfig) -> None:
    for variant in config.VARIANTS:
        for nodes in config.NODES:
            job = make_job(cluster_config, nodes, variant)
            jobfile = f"{variant.runtime_approach}-{nodes * config.TASKS_PER_NODE}.job"
            write_job_file(jobfile, job)
