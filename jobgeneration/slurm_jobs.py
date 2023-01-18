import logging
from jobgeneration import config
from dataclasses import asdict, dataclass
from jinja2 import Template

JOB_TEMPLATE: Template = Template(config.SLURM_JOB_TEMPLATE_PATH.read_text())

MPICH_RUN_MODULES = ["singularity/3.9.9", "mpi/mpich/mpich_3.2"]
OPENMPI_RUN_MODULES = ["singularity/3.9.9", "mpi/openmpi/4.10/4.10"]
NATIVE_RUN_MODULES = ["mpi/mpich/mpich_3.2", "comp/gcc/9.3.0", "comp/cmake/3.25.0"]

SRUN = "srun --mpi=pmi2"
MPIRUN = "mpirun -np {nodes}"

SINGULARITY_CMD = "singularity exec {bind} {image} /build/bin/laplace {nx} {ny}"
SINGULARITY_BIND_OPT = "--bind {bind}"

NATIVE_CMD = "build/bin/laplace {nx} {ny}"

MPICH_IMG = "rockylinux9-mpich.sif"
MPICH_BIND_IMG = "rockylinux9-mpich-bind.sif"
OPENMPI_IMG = "rockylinux9-openmpi.sif"

MPI_DIR = "/cluster/mpi/mpich"

NATIVE_BUILD_CMD = "mkdir -p build && cd build && cmake .. && make -j4 && cd .."


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


MODULES_BY_VARIANT = {
    "mpich": MPICH_RUN_MODULES,
    "mpich-bind": MPICH_RUN_MODULES,
    "openmpi": OPENMPI_RUN_MODULES,
    "native": NATIVE_RUN_MODULES,
}

IMAGES_BY_VARIANT = {
    "mpich": MPICH_IMG,
    "mpich-bind": MPICH_BIND_IMG,
    "openmpi": OPENMPI_IMG,
    "native": "",
}

MPICMD_BY_VARIANT = {
    "mpich": SRUN,
    "mpich-bind": SRUN,
    "openmpi": MPIRUN,
    "native": SRUN,
}

APPCMD_BY_VARIANT = {
    "mpich": SINGULARITY_CMD,
    "mpich-bind": SINGULARITY_CMD,
    "openmpi": SINGULARITY_CMD,
    "native": NATIVE_CMD,
}

def get_bind_opt(variant: str) -> str:
    if "bind" in variant:
        return SINGULARITY_BIND_OPT.format(bind=MPI_DIR)

    return ""

def get_build_cmd(variant: str) -> str:
    if variant == "native":
        return NATIVE_BUILD_CMD

    return ""

def make_job(nodes: int, variant: str) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=config.TASKS_PER_NODE,
        workdir=f"{variant}-{nodes}",
        output=f"{variant}-{nodes}.out",
        modules=" ".join(MODULES_BY_VARIANT[variant]),
        mpicmd=MPICMD_BY_VARIANT[variant],
        buildcmd=get_build_cmd(variant),
        app=APPCMD_BY_VARIANT[variant].format(
            image=IMAGES_BY_VARIANT[variant],
            bind=get_bind_opt(variant),
            **config.NODE_SCALING[nodes],
        ),
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
    for variant in config.MPI_TYPES:
        for nodes in config.NODE_SCALING:
            job = make_job(nodes, variant)
            jobfile = f"{variant}-{nodes}.job"
            write_job_file(jobfile, job)
