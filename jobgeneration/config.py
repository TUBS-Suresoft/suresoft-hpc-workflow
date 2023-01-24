from pathlib import Path
from jobgeneration.mpi import OpenMPI, Srun
from jobgeneration.nodescaling import node_scale_for


from jobgeneration.variants import (
    NativeVariant,
    RuntimeVariant,
    SingularityVariant,
)


TEMPLATES_DIR = Path(__file__).parent / "templates"
ROCKET_TEMPLATE_PATH = TEMPLATES_DIR / "rocket.yml.j2"
SLURM_JOB_TEMPLATE_PATH = TEMPLATES_DIR / "laplace.job.j2"
BENCHMARK_CI_TEMPLATE = TEMPLATES_DIR / "benchmark-ci.yml.j2"

GENERATED_DIR = Path("generated")
SLURM_JOB_DIR = GENERATED_DIR / "slurmjobs"
ROCKET_CONFIG_DIR = GENERATED_DIR / "hpc-rocket"
BENCHMARK_CI_FILE = GENERATED_DIR / "benchmark-gitlab-ci.yml"

RESULT_DIR = Path("results")
BENCHMARK_GRAPH_IMAGE = RESULT_DIR / "benchmark.png"
BENCHMARK_GRAPH_FILE = RESULT_DIR / "graph_data.out"


VARIANTS: list[RuntimeVariant] = [
    NativeVariant(mpi=Srun(name="mpich")),
    SingularityVariant(mpi=OpenMPI(), mpi_approach="hybrid"),
    SingularityVariant(mpi=Srun("mpich"), mpi_approach="hybrid"),
    SingularityVariant(mpi=Srun("mpich"), mpi_approach="bind"),
]

TASKS_PER_NODE = 2
NODES = [8, 16, 32]

PROCESSES = [TASKS_PER_NODE * n for n in NODES]

NODE_SCALING = {}
for n in PROCESSES:
    nx, ny = node_scale_for(n)
    NODE_SCALING[n] = {"nx": nx, "ny": ny}

def ensure_dirs() -> None:
    SLURM_JOB_DIR.mkdir(parents=True, exist_ok=True)
    ROCKET_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
