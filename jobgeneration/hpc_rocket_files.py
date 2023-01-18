import logging
import re
from typing import Iterable
from jobgeneration import config
from pathlib import Path
from dataclasses import asdict, dataclass
from jinja2 import Template


CONTAINER_DIR = Path("Containers")
CONTAINER_BASENAME = "rockylinux9"

ROCKET_TEMPLATE = Template(config.ROCKET_TEMPLATE_PATH.read_text())


@dataclass
class Rocket:
    copy_instructions: list[tuple[str, str]]
    collect_instructions: list[tuple[str, str]]
    jobfile: str


def collect_images() -> list[Path]:
    return list(CONTAINER_DIR.glob("*.sif"))


def get_variant(image: Path) -> str:
    return image.stem.removeprefix(CONTAINER_BASENAME + "-")


def collect_variant_job_files(job_dir: Path, variant: str) -> list[Path]:
    job_files = job_dir.glob("*.job")
    pattern = re.compile(f"^{variant}-[1-9][0-9]*.job$")
    return [file for file in job_files if pattern.match(file.name)]


def collect_jobs_by_variant(variant_names: Iterable[str]) -> dict[str, list[Path]]:
    jobs_by_variant: dict[str, list[Path]] = {}
    for variant in variant_names:
        jobs_by_variant[variant] = collect_variant_job_files(
            config.SLURM_JOB_DIR, variant
        )

    jobs_by_variant["native"] = collect_variant_job_files(
        config.SLURM_JOB_DIR, "native"
    )
    return jobs_by_variant


def collect_images_by_variant() -> dict[str, Path]:
    images = collect_images()
    images_by_variant = {}
    for image in images:
        variant_name = get_variant(image)
        images_by_variant[variant_name] = image
        logging.info(f"Using image {image} for variant {variant_name}")

    return images_by_variant


def rocket_from_variant(
    variant: str, images_by_variant: dict[str, Path], jobfile: Path
) -> Rocket:
    remote_jobfile = jobfile.stem + "/laplace.job"
    remote_output = jobfile.stem + "/" + jobfile.stem + ".out"
    remote_results = jobfile.stem + "/results"

    copy_instructions = build_copy_instructions(
        variant, images_by_variant, jobfile, remote_jobfile
    )

    return Rocket(
        copy_instructions=copy_instructions,
        collect_instructions=[
            (remote_output, f"results/{jobfile.stem}.out"),
            (remote_results, "results/"),
        ],
        jobfile=remote_jobfile,
    )


def build_copy_instructions(
    variant: str, images_by_variant: dict[str, Path], jobfile: Path, remote_jobfile: str
) -> list[tuple[str, str]]:
    copy_instructions = [(str(jobfile), remote_jobfile)]
    copy_instructions.extend(
        image_copy_instructions(variant, images_by_variant, jobfile)
    )
    copy_instructions.extend(native_copy_instructions(variant, jobfile.stem))
    return copy_instructions


def native_copy_instructions(variant: str, remote_dir: str) -> list[tuple[str, str]]:
    if variant == "native":
        return [("laplace2d/*", remote_dir)]

    return []


def image_copy_instructions(
    variant: str, images_by_variant: dict[str, Path], jobfile: Path
) -> list[tuple[str, str]]:
    if variant in images_by_variant:
        image = images_by_variant[variant]
        remote_image = jobfile.stem + "/" + image.name
        local_image = str(image)
        copy_instruction = [(local_image, remote_image)]
        logging.info("Variant: " + variant)
        logging.info(f"Copying {local_image} to {remote_image}")

        return copy_instruction

    return []


def save_rocket_file(
    variant: str, images_by_variant: dict[str, Path], jobfile: Path
) -> None:
    rendered = ROCKET_TEMPLATE.render(
        **asdict(rocket_from_variant(variant, images_by_variant, jobfile))
    )
    rocket_filename = "rocket-" + jobfile.stem + ".yml"
    rocket_file = config.ROCKET_CONFIG_DIR / rocket_filename
    rocket_file.write_text(rendered)


def create() -> None:
    images_by_variant = collect_images_by_variant()
    jobs_by_variant = collect_jobs_by_variant(images_by_variant.keys())
    for variant, jobfiles in jobs_by_variant.items():
        for jobfile in jobfiles:
            save_rocket_file(variant, images_by_variant, jobfile)
