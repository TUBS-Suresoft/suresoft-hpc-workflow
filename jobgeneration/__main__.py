from jobgeneration import buildrocket, buildjob, config, create_benchmark_ci

config.ensure_dirs()
buildrocket.build_rocket_files()
buildjob.build_slurm_job_files()
create_benchmark_ci.build_benchmark_ci_file()
