from jobgeneration import buildjob, buildrocket, config, create_benchmark_ci
from jobgeneration.logging import configure_logging

configure_logging()

config.ensure_dirs()
buildjob.build_slurm_job_files()
buildrocket.build_rocket_files()
create_benchmark_ci.build_benchmark_ci_file()
