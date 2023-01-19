import logging
import os
import re
from typing import Iterable
from jobgeneration import config
from pathlib import Path
from dataclasses import asdict, dataclass
from jinja2 import Template

from jobgeneration.variants import RuntimeVariant


ROCKET_TEMPLATE = Template(config.ROCKET_TEMPLATE_PATH.read_text())


@dataclass
class Rocket:
    copy_instructions: list[tuple[str, str]]
    collect_instructions: list[tuple[str, str]]
    jobfile: str


def save_rocket_file(variant: RuntimeVariant, nodes: int) -> None:
    rocket_filename = f"rocket-{variant.runtime_approach}-{nodes}.yml"
    rocket_file = config.ROCKET_CONFIG_DIR / rocket_filename
    rocket = get_rocket_config(variant, nodes)

    rendered = ROCKET_TEMPLATE.render(**asdict(rocket))
    logging.info(f"Writing hpc-rocket file [green]{rocket_file}[/]")
    rocket_file.write_text(rendered)


def get_rocket_config(variant: RuntimeVariant, nodes: int) -> Rocket:
    jobfile = get_jobfile(variant, nodes)
    remote_dir = f"{variant.runtime_approach}-{nodes}"
    logfilename = f"{remote_dir}.out"
    variant_files = variant_copy_instructions(variant, remote_dir)

    return Rocket(
        copy_instructions=[
            copy(jobfile, remote_dir, "laplace.job"),
            *variant_files,
        ],
        collect_instructions=[
            (
                f"{remote_dir}/{logfilename}",
                f"results/{logfilename}",
            ),
        ],
        jobfile=f"{remote_dir}/{jobfile.name}",
    )


def variant_copy_instructions(
    variant: RuntimeVariant, remote_dir: str
) -> list[tuple[str, str]]:
    return [copy(file, remote_dir) for file in variant.files()]


def copy(file: Path, remote_dir: str, remote_filename: str = "") -> tuple[str, str]:
    if not file.exists():
        logging.warning(f"File {file} does not exist")

    filename = file.name
    if remote_filename:
        filename = remote_filename

    return (str(file), os.path.join(remote_dir, filename))


def get_jobfile(variant: RuntimeVariant, nodes: int) -> Path:
    jobfile = config.SLURM_JOB_DIR / f"{variant.runtime_approach}-{nodes}.job"
    if not jobfile.exists():
        logging.warning(f"Jobfile {jobfile} does not exist")

    return jobfile


def create() -> None:
    for variant in config.VARIANTS:
        for nodes in config.NODE_SCALING:
            save_rocket_file(variant, nodes)
