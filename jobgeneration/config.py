from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
ROCKET_TEMPLATE_PATH = TEMPLATES_DIR / "rocket.yml.j2"
SLURM_JOB_TEMPLATE_PATH = TEMPLATES_DIR / "laplace.job.j2"

GENERATED_DIR = Path("generated")
SLURM_JOB_DIR = GENERATED_DIR / "slurmjobs"
ROCKET_CONFIG_DIR = GENERATED_DIR / "hpc-rocket"
BENCHMARK_CI_FILE = GENERATED_DIR / "benchmark-gitlab-ci.yml"


def ensure_dirs() -> None:
    SLURM_JOB_DIR.mkdir(parents=True, exist_ok=True)
    ROCKET_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
