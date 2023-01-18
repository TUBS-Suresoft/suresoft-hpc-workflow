from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
ROCKET_TEMPLATE_PATH = TEMPLATES_DIR / "rocket.yml.j2"
SLURM_JOB_TEMPLATE_PATH = TEMPLATES_DIR / "laplace.job.j2"

GENERATED_DIR = Path("generated")
SLURM_JOB_DIR = GENERATED_DIR / "slurmjobs"
ROCKET_CONFIG_DIR = GENERATED_DIR / "hpc-rocket"
BENCHMARK_CI_FILE = GENERATED_DIR / "benchmark-gitlab-ci.yml"
BENCHMARK_GRAPH_FILE =  GENERATED_DIR / "graph.txt"

RESULT_DIR = Path("results")
BENCHMARK_GRAPH_IMAGE =  RESULT_DIR / "benchmark.png"

MPI_TYPES = ['native', 'mpich', 'openmpi', 'mpich-bind']

NODE_SCALING = {
    8: {"nx": 4, "ny": 2},
    16: {"nx": 4, "ny": 4},
    32: {"nx": 8, "ny": 4},
    # 64: {"nx": 8, "ny": 8},
}

TASKS_PER_NODE = 1

PROCESSES = list(NODE_SCALING.keys())

def ensure_dirs() -> None:
    SLURM_JOB_DIR.mkdir(parents=True, exist_ok=True)
    ROCKET_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
