import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

from jobgeneration import buildrocket, buildjob, config, create_benchmark_ci

config.ensure_dirs()
buildjob.build_slurm_job_files()
buildrocket.build_rocket_files()
create_benchmark_ci.build_benchmark_ci_file()
