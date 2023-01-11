hpcRocketjobs = ["rocket-mpich", "rocket-mpich-bind", "rocket-openmpi", "rocket-native"]

benchmark_ci_file = """
stages: 
  - benchmark
.benchmark:
  stage: benchmark
  image: python:3.10
  before_script:
    - pip install hpc-rocket==0.3.1
"""

for hpcRocketjob in hpcRocketjobs:
    benchmark_ci_file += f"""
benchmark:{hpcRocketjob}:
  extends: .benchmark

  script:
    - hpc-rocket launch --watch {hpcRocketjob}.yml
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
"""



with open("benchmark-gitlab-ci.yml", "w") as file:
    file.write(benchmark_ci_file)