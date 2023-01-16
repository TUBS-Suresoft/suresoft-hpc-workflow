from jobgeneration import config
import textwrap


def build_benchmark_job_string() -> str:
    hpc_rocket_jobs = config.ROCKET_CONFIG_DIR.glob("rocket-*.yml")

    benchmark_ci_file = """
    stages: 
      - benchmark
    .benchmark:
      stage: benchmark
      image: python:3.10
      before_script:
        - pip install hpc-rocket==0.3.2
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

    return textwrap.dedent(benchmark_ci_file)


def build_benchmark_ci_file() -> None:
    benchmark_ci_file = build_benchmark_job_string()
    config.BENCHMARK_CI_FILE.write_text(benchmark_ci_file)
