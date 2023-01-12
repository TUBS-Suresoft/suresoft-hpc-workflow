import config
from pathlib import Path
from dataclasses import asdict, dataclass
from jinja2 import Template


CONTAINER_DIR = Path("Containers")
CONTAINER_BASENAME = "rockylinux9"

DEF_FILES = CONTAINER_DIR.glob("*.def")
IMAGES = [def_file.with_suffix(".sif") for def_file in DEF_FILES]

VARIANT_NAMES = [image.stem.removeprefix(CONTAINER_BASENAME + "-") for image in IMAGES]
IMAGE_BY_VARIANT = dict(zip(VARIANT_NAMES, IMAGES))

ROCKET_TEMPLATE = Template(config.ROCKET_TEMPLATE_PATH.read_text())


@dataclass
class Rocket:
    copy_instructions: list[tuple[str, str]]
    collect_instructions: list[tuple[str, str]]
    jobfile: str


def collect_variants(job_dir: Path, variant: str) -> list[Path]:
    variant_job_files = job_dir.glob(f"{variant}*.job")
    return list(variant_job_files)


def collect_jobs_by_variant() -> dict[str, list[Path]]:
    jobs_by_variant: dict[str, list[Path]] = {}
    for variant in VARIANT_NAMES:
        jobs_by_variant[variant] = collect_variants(config.SLURM_JOB_DIR, variant)

    jobs_by_variant["native"] = collect_variants(config.SLURM_JOB_DIR, "native")
    return jobs_by_variant


def native_copy_instructions(remote_dir: str) -> list[tuple[str, str]]:
    if variant == "native":
        return [("laplace2d", remote_dir + "/laplace")]

    return []


def rocket_from_variant(variant: str, jobfile: Path) -> Rocket:
    remote_jobfile = jobfile.stem + "/laplace.job"
    remote_output = jobfile.stem + "/" + jobfile.stem + ".out"
    remote_results = jobfile.stem + "/results"

    copy_instructions = build_copy_instructions(variant, jobfile, remote_jobfile)

    return Rocket(
        copy_instructions=copy_instructions,
        collect_instructions=[
            (remote_output, "results/"),
            (remote_results, "results/"),
        ],
        jobfile=remote_jobfile,
    )


def build_copy_instructions(
    variant: str, jobfile: Path, remote_jobfile: str
) -> list[tuple[str, str]]:
    copy_instructions = [(str(jobfile), remote_jobfile)]
    copy_instructions.extend(image_copy_instructions(variant, jobfile))
    copy_instructions.extend(native_copy_instructions(jobfile.stem))
    return copy_instructions


def image_copy_instructions(variant: str, jobfile: Path) -> list[tuple[str, str]]:
    if variant in IMAGE_BY_VARIANT:
        remote_image = jobfile.stem + "/" + IMAGE_BY_VARIANT[variant].name
        local_image = str(IMAGE_BY_VARIANT[variant])
        return [(local_image, remote_image)]

    return []


def save_rocket_file(variant: str, jobfile: Path) -> None:
    rendered = ROCKET_TEMPLATE.render(**asdict(rocket_from_variant(variant, jobfile)))
    rocket_filename = "rocket-" + jobfile.stem + ".yml"
    rocket_file = config.ROCKET_CONFIG_DIR / rocket_filename
    rocket_file.write_text(rendered)


if __name__ == "__main__":
    config.ensure_dirs()
    jobs_by_variant = collect_jobs_by_variant()
    for variant, jobfiles in jobs_by_variant.items():
        for jobfile in jobfiles:
            save_rocket_file(variant, jobfile)
