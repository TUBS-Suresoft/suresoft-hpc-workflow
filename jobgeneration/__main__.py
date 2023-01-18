from jobgeneration import config, slurm_jobs, hpc_rocket_files, benchmark_ci, benchmark_plot
from jobgeneration.logging import configure_logging
import sys

configure_logging()
config.ensure_dirs()
if sys.argv[1] == "build":
    slurm_jobs.create()
    hpc_rocket_files.create()
    benchmark_ci.create()
elif sys.argv[1] == "plot":
    benchmark_plot.create()
