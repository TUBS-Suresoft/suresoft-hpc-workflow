from dataclasses import asdict, dataclass


job_content: str
with open("slurmjobs/laplace.job.template") as job_template:
    job_content = job_template.read()

mpich_run_modules = [
    "singularity/3.9.9",
    "mpi/mpich/mpich_3.2"
]

openmpi_run_modules = [
    "singularity/3.9.9",
    "mpi/openmpi/4.10/4.10"
]

node_scale = {
    16: {"nx": 4, "ny": 4},
    32: {"nx": 8, "ny": 4},
    64: {"nx": 8, "ny": 8},
}

srun = "srun --mpi=pmi2"
mpirun = "mpirun -np {nodes}"

singularity_cmd = "singularity exec {image} /build/bin/laplace {nx} {ny}"

@dataclass
class Job:
    nodes: int
    ntasks_per_node: int
    output: str
    workdir: str
    modules: str
    mpicmd: str
    app: str

MPICH_IMG = "rockylinux9-mpich.sif"
OPENMPI_IMG = "rockylinux9-openmpi.sif"

def mpich_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"mpich_{nodes}",
        output=f"mpich_{nodes}.out",
        modules= " ".join(mpich_run_modules),
        mpicmd=srun,
        app=singularity_cmd.format(image=MPICH_IMG, **node_scale[nodes]),
    )


def openmpi_job(nodes: int) -> Job:
    return Job(
        nodes=nodes,
        ntasks_per_node=1,
        workdir=f"openmpi_{nodes}",
        output=f"openmpi_{nodes}.out",
        modules=" ".join(openmpi_run_modules),
        mpicmd=mpirun.format(nodes=nodes),
        app=singularity_cmd.format(image=OPENMPI_IMG, **node_scale[nodes]),
    )

def format_job_content(job: Job) -> str:
    return job_content.format(**asdict(job))


def write_job_file(name: str, job: Job) -> None:
    with open(name, "w") as job_file:
        job_file.write(format_job_content(job))


if __name__ == "__main__":
    for nodes, partioning in node_scale.items():
        job = mpich_job(nodes)
        write_job_file(f"mpich_{nodes}.job", job)

        job = openmpi_job(nodes)
        write_job_file(f"openmpi_{nodes}.job", job)