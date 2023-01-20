import math


def is_power_of_two(n: int) -> bool:
    return n != 0 and ((n & (n - 1)) == 0)


def find_next_higher_power_of_two(n: float) -> int:
    return int(2 ** math.ceil(math.log2(n)))


def node_scale_for(nodes: int) -> tuple[int, int]:
    if nodes == 1:
        return 1, 1

    if not is_power_of_two(nodes):
        raise ValueError("nodes must be a power of two")

    sqrt = math.sqrt(nodes)
    if math.isclose(sqrt % 2, 0):
        return int(sqrt), int(sqrt)

    higher = find_next_higher_power_of_two(sqrt)
    lower = higher // 2

    return lower, higher
