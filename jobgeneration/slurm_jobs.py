import logging
from typing import Dict, Type, TypedDict
from jobgeneration import config
from dataclasses import asdict, dataclass
from jinja2 import Template

from jobgeneration.variants import NativeVariant, RuntimeVariant, SingularityVariant

JOB_TEMPLATE: Template = Template(config.SLURM_JOB_TEMPLATE_PATH.read_text())

MPICH_RUN_MODULES = ["singularity/3.9.9", "mpi/mpich/mpich_3.2"]
OPENMPI_RUN_MODULES = ["singularity/3.9.9", "mpi/openmpi/4.10/4.10"]
NATIVE_RUN_MODULES = ["mpi/mpich/mpich_3.2", "comp/gcc/9.3.0", "comp/cmake/3.25.0"]


MPI_DIR = "/cluster/mpi/mpich"
SINGULARITY_CMD = "singularity exec {bind} {image} /build/bin/laplace {nx} {ny}"
SINGULARITY_BIND_OPT = "--bind {bind}"

NATIVE_CMD = "build/bin/laplace {nx} {ny}"
NATIVE_BUILD_CMD = "mkdir -p build && cd build && cmake .. && make -j4 && cd .."


VARIANT_BASED_MODULES = {
    SingularityVariant: ["singularity/3.9.9"],
    NativeVariant: ["comp/gcc/9.3.0", "comp/cmake/3.25.0"],
}

MPI_BASED_MODULES = {
    "mpich": ["mpi/mpich/mpich_3.2"],
    "openmpi": ["mpi/openmpi/4.10/4.10"],
}

APPCMD_BY_VARIANT = {
    SingularityVariant: SINGULARITY_CMD,
    NativeVariant: NATIVE_CMD,
}


def get_modules(variant: RuntimeVariant) -> list[str]:
    return [
        # NOTE: We have to load MPI before the variant based modules,
        # because CMake causes a build error if the necessary modules are not available when it's loaded.
        *MPI_BASED_MODULES[variant.mpi.name],
        *VARIANT_BASED_MODULES[type(variant)],
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


def get_bind_opt(variant: RuntimeVariant) -> str:
    if isinstance(variant, SingularityVariant) and variant.mpi_approach == "bind":
        return SINGULARITY_BIND_OPT.format(bind=MPI_DIR)

    return ""


def get_app_cmd(variant: RuntimeVariant, nodes: int) -> str:
    app_cmd = APPCMD_BY_VARIANT[type(variant)]

    if isinstance(variant, SingularityVariant):
        return app_cmd.format(
            image=variant.image.name,
            bind=get_bind_opt(variant),
            **config.NODE_SCALING[nodes],
        )

    return app_cmd.format(**config.NODE_SCALING[nodes])


def get_build_cmd(variant: RuntimeVariant) -> str:
    if isinstance(variant, NativeVariant):
        return NATIVE_BUILD_CMD

    return ""


def make_job(nodes: int, variant: RuntimeVariant) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=config.TASKS_PER_NODE,
        workdir=f"{variant.runtime_approach}-{nodes}",
        output=f"{variant.runtime_approach}-{nodes}.out",
        modules=" ".join(get_modules(variant)),
        mpicmd=variant.mpi.command(nodes),
        buildcmd=get_build_cmd(variant),
        app=get_app_cmd(variant, nodes),
    )


def format_job_content(job: Job) -> str:
    partition = "shortrun_small" if job.nodes <= 50 else "shortrun_large"
    return JOB_TEMPLATE.render(**asdict(job), partition=partition)


def write_job_file(jobfilename: str, job: Job) -> None:
    path = config.SLURM_JOB_DIR / jobfilename
    logging.info(f"Writing job file [green]{path}[/]")
    path.touch(exist_ok=True)
    path.write_text(format_job_content(job))


def create() -> None:
    for variant in config.VARIANTS:
        for nodes in config.NODE_SCALING:
            job = make_job(nodes, variant)
            jobfile = f"{variant.runtime_approach}-{nodes}.job"
            write_job_file(jobfile, job)
