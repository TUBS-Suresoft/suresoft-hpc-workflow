import logging
from dataclasses import dataclass
from pathlib import Path
from jobgeneration import config

from jinja2 import Template

from jobgeneration.variants import RuntimeVariant


@dataclass
class RocketVariant:
    runtime_variant: RuntimeVariant
    configpath: Path

    @property
    def extended_name(self) -> str:
        return self.configpath.stem.removeprefix("rocket-")

    @property
    def name(self) -> str:
        return self.runtime_variant.runtime_approach


def build_benchmark_job_string(hpc_rocket_jobs: list[RocketVariant]) -> str:
    template = Template(config.BENCHMARK_CI_TEMPLATE.read_text())
    return template.render(hpc_rocket_jobs=hpc_rocket_jobs)


def rocket_variant(variant: RuntimeVariant, nodes: int) -> RocketVariant:
    rocket_config_name = "rocket-" + variant.runtime_approach + "-" + str(nodes) + ".yml"
    rocket_config = config.ROCKET_CONFIG_DIR / rocket_config_name
    if not rocket_config.exists():
        logging.warning(f"Rocket config {rocket_config} does not exist")

    return RocketVariant(variant, rocket_config)


def create() -> None:
    hpc_rocket_jobs = [
        rocket_variant(variant, nodes)
        for nodes in config.NODE_SCALING
        for variant in config.VARIANTS
    ]
    benchmark_ci_file = build_benchmark_job_string(hpc_rocket_jobs)
    config.BENCHMARK_CI_FILE.write_text(benchmark_ci_file)
