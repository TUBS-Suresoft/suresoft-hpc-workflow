from jobgeneration import buildjob, buildrocket, config, create_benchmark_ci, create_graph
from jobgeneration.logging import configure_logging
import sys

configure_logging()
config.ensure_dirs()
if sys.argv[1] == "build":
    buildjob.build_slurm_job_files()
    buildrocket.build_rocket_files()
    create_benchmark_ci.build_benchmark_ci_file()
elif sys.argv[1] == "plot":
    create_graph.create_graph()
