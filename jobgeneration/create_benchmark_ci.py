from pathlib import Path
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
        - pip install hpc-rocket==0.4.0
    """

    for hpc_rocket_job in hpc_rocket_jobs:
        variant_name = get_variant_name_from_rocket_file(hpc_rocket_job)
        benchmark_ci_file += f"""
    benchmark:{hpc_rocket_job.stem}:
      extends: .benchmark

      script:
        - hpc-rocket launch {hpc_rocket_job} |& tee hpcrocket.log
        - hpc-rocket watch {hpc_rocket_job} $(python parsejobid.py hpcrocket.log)
        - hpc-rocket finalize {hpc_rocket_job}
        - cat results/laplace.out

      after_script:
        - hpc-rocket cancel {hpc_rocket_job} $(python parsejobid.py hpcrocket.log)

      artifacts:
        expire_in: 1 hrs
        paths:
          - results/

      needs:
        - pipeline: $PARENT_PIPELINE_ID
          job: build_singularity_container_{variant_name}
    """

    return textwrap.dedent(benchmark_ci_file)


def get_variant_name_from_rocket_file(hpc_rocket_job: Path) -> str:
    variant_name = hpc_rocket_job.stem.removeprefix("rocket-").replace("-", "_")
    last_underscore = variant_name.rfind("_")
    variant_name = variant_name[:last_underscore]
    return variant_name


def build_benchmark_ci_file() -> None:
    benchmark_ci_file = build_benchmark_job_string()
    config.BENCHMARK_CI_FILE.write_text(benchmark_ci_file)
