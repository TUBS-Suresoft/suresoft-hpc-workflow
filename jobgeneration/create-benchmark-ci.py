import config
from pathlib import Path

hpc_rocket_jobs = config.ROCKET_CONFIG_DIR.glob("rocket-*.yml")


benchmark_ci_file = """
stages: 
  - benchmark
.benchmark:
  stage: benchmark
  image: python:3.10
  before_script:
    - pip install hpc-rocket==0.3.1
"""

for hpc_rocket_job in hpc_rocket_jobs:
    benchmark_ci_file += f"""
benchmark:{hpc_rocket_job.stem}:
  extends: .benchmark

  script:
    - hpc-rocket launch --watch {hpc_rocket_job}
    - cat results/laplace.out

  artifacts:
    expire_in: 1 hrs
    paths:
      - results/

  needs:
    - pipeline: $PARENT_PIPELINE_ID
      job: build_singularity_container_mpich
    - pipeline: $PARENT_PIPELINE_ID
      job: build_singularity_container_openmpi
    - pipeline: $PARENT_PIPELINE_ID
      job: create_benchmark_ci
"""

config.BENCHMARK_CI_FILE.write_text(benchmark_ci_file)
