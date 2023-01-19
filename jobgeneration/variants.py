from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from jobgeneration.mpi import MPIImplementation


class RuntimeVariant(Protocol):
    @property
    def mpi(self) -> MPIImplementation:
        ...

    @property
    def runtime_approach(self) -> str:
        ...

    def files(self) -> list[Path]:
        ...


@dataclass
class NativeVariant:
    mpi: MPIImplementation

    @property
    def runtime_approach(self) -> str:
        return f"native-{self.mpi.name}"

    def files(self) -> list[Path]:
        return list(Path("laplace2d").glob("*"))


CONTAINER_DIR = Path("Containers")
CONTAINER_PREFIX = "rockylinux9"


@dataclass
class SingularityVariant:
    mpi: MPIImplementation
    mpi_approach: Literal["bind", "hybrid"]

    @property
    def runtime_approach(self) -> str:
        return f"singularity-{self.mpi.name}-{self.mpi_approach}"

    def files(self) -> list[Path]:
        return [self.image]

    @property
    def image(self) -> Path:
        return (
            CONTAINER_DIR
            / f"{CONTAINER_PREFIX}-{self.mpi.name}-{self.mpi_approach}.sif"
        )
