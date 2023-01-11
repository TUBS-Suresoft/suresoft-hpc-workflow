hpcRocketjobs = ["rocket-mpich", "rocket-native", "rocket-openmpi", "rocket-mpich-bind"]


benchmark_ci_file = """
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
"""



with open("benchmark-gitlab-ci.yml", "w") as file:
    file.write(benchmark_ci_file)