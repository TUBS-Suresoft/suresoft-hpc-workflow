from jobgeneration import buildrocket, buildjob, config, create_benchmark_ci

config.ensure_dirs()
buildjob.build_slurm_job_files()
buildrocket.build_rocket_files()
create_benchmark_ci.build_benchmark_ci_file()
