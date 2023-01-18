from dataclasses import dataclass
from pathlib import Path
from jobgeneration import config

from jinja2 import Template


@dataclass
class RocketVariant:
    filepath: Path

    @property
    def extended_name(self) -> str:
        return self.filepath.stem.removeprefix("rocket-")

    @property
    def name(self) -> str:
      variant_name = self.extended_name
      last_underscore = variant_name.rfind("-")
      variant_name = variant_name[:last_underscore]
      return variant_name


def build_benchmark_job_string() -> str:
    hpc_rocket_jobs = [RocketVariant(job) for job in config.ROCKET_CONFIG_DIR.glob("rocket-*.yml")]
    template = Template(config.BENCHMARK_CI_TEMPLATE.read_text())
    return template.render(hpc_rocket_jobs=hpc_rocket_jobs)


def create() -> None:
    benchmark_ci_file = build_benchmark_job_string()
    config.BENCHMARK_CI_FILE.write_text(benchmark_ci_file)
