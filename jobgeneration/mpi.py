from dataclasses import dataclass
from typing import Literal, Protocol


class MPIImplementation(Protocol):
    @property
    def name(self) -> Literal["mpich", "openmpi"]:
        ...

    def command(self, num_processes: int) -> str:
        ...


@dataclass(frozen=True)
class Srun:
    name: Literal["mpich", "openmpi"]

    def command(self, num_processes: int) -> str:
        return f"srun --mpi=pmi2"


@dataclass
class OpenMPI:
    @property
    def name(self) -> Literal["mpich", "openmpi"]:
        return "openmpi"

    def command(self, num_processes: int) -> str:
        return f"mpirun -np {num_processes}"
