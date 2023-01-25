from dataclasses import dataclass
from .variants import RuntimeVariant, SingularityVariant, NativeVariant


@dataclass
class MPIConfig:
    modules: list[str]
    dir: str


@dataclass
class ClusterConfig:
    host: str
    variant_modules: dict[type[RuntimeVariant], list[str]]
    mpi_configs: dict[str, MPIConfig]


CLUSTER_CONFIGS = {
    "phoenix": ClusterConfig (
        host="phoenix.hlr.rz.tu-bs.de",
        variant_modules={
            SingularityVariant: ["singularity/3.9.9"],
            NativeVariant: ["comp/gcc/9.3.0", "comp/cmake/3.25.0"],
        },
        mpi_configs={
            "mpich": MPIConfig(modules=["mpi/mpich/mpich_3.2"], dir="/cluster/mpi/mpich"),
            "openmpi": MPIConfig(modules=["mpi/openmpi/4.10/4.10"], dir="/cluster/mpi/mpich"),
        }
    )
}
