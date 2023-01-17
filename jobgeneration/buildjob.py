import logging
from jobgeneration import config
from dataclasses import asdict, dataclass
from jinja2 import Template

JOB_TEMPLATE: Template = Template(config.SLURM_JOB_TEMPLATE_PATH.read_text())

MPICH_RUN_MODULES = ["singularity/3.9.9", "mpi/mpich/mpich_3.2"]
OPENMPI_RUN_MODULES = ["singularity/3.9.9", "mpi/openmpi/4.10/4.10"]
NATIVE_RUN_MODULES = ["mpi/mpich/mpich_3.2", "comp/gcc/9.3.0", "comp/cmake/3.25.0"]

NODE_SCALE = {
    8: {"nx": 4, "ny": 2},
    16: {"nx": 4, "ny": 4},
    32: {"nx": 8, "ny": 4},
    # 64: {"nx": 8, "ny": 8},
}

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


def mpich_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"mpich-{nodes}",
        output=f"mpich-{nodes}.out",
        modules=" ".join(MPICH_RUN_MODULES),
        mpicmd=SRUN,
        app=SINGULARITY_CMD.format(image=MPICH_IMG, bind="", **NODE_SCALE[nodes]),
    )


def mpich_bind_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"mpich-bind-{nodes}",
        output=f"mpich-bind-{nodes}.out",
        modules=" ".join(MPICH_RUN_MODULES),
        mpicmd=SRUN,
        app=SINGULARITY_CMD.format(
            image=MPICH_BIND_IMG,
            bind=SINGULARITY_BIND_OPT.format(bind=MPI_DIR),
            **NODE_SCALE[nodes],
        ),
    )


def openmpi_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"openmpi-{nodes}",
        output=f"openmpi-{nodes}.out",
        modules=" ".join(OPENMPI_RUN_MODULES),
        mpicmd=MPIRUN.format(nodes=nodes),
        app=SINGULARITY_CMD.format(image=OPENMPI_IMG, bind="", **NODE_SCALE[nodes]),
    )


def native_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"native-{nodes}",
        output=f"native-{nodes}.out",
        modules=" ".join(NATIVE_RUN_MODULES),
        mpicmd=SRUN,
        app=NATIVE_CMD.format(**NODE_SCALE[nodes]),
        buildcmd=NATIVE_BUILD_CMD,
    )


def format_job_content(job: Job) -> str:
    partition = "shortrun_small" if job.nodes <= 50 else "shortrun_large"
    return JOB_TEMPLATE.render(**asdict(job), partition=partition)


def write_job_file(jobfilename: str, job: Job) -> None:
    path = config.SLURM_JOB_DIR / jobfilename
    logging.info(f"Writing job file [green]{path}[/]")
    path.touch(exist_ok=True)
    path.write_text(format_job_content(job))


def build_slurm_job_files() -> None:
    for nodes in NODE_SCALE:
        job = mpich_job(nodes)
        jobfile = f"mpich-{nodes}.job"
        write_job_file(jobfile, job)

        job = mpich_bind_job(nodes)
        jobfile = f"mpich-bind-{nodes}.job"
        write_job_file(jobfile, job)

        job = openmpi_job(nodes)
        jobfile = f"openmpi-{nodes}.job"
        write_job_file(jobfile, job)

        job = native_job(nodes)
        jobfile = f"native-{nodes}.job"
        write_job_file(jobfile, job)
