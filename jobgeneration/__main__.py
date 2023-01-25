from jobgeneration import (
    config,
    clusterconfig,
    slurm_jobs,
    hpc_rocket_files,
    benchmark_ci,
    benchmark_plot,
    variants,
)
from jobgeneration.logging import configure_logging
import sys

configure_logging()
config.ensure_dirs()
if sys.argv[1] == "build":
    slurm_jobs.create(clusterconfig.CLUSTER_CONFIGS["phoenix"])
    hpc_rocket_files.create()
    benchmark_ci.create()
elif sys.argv[1] == "plot":
    benchmark_plot.create()
