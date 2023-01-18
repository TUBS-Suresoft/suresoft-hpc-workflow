from pathlib import Path
import re
import matplotlib.pyplot as plt
from jobgeneration import config


def create_graph() -> None:
    output = ""

    configs = ['native', 'mpich', 'openmpi', 'mpich-bind']
    processes = [8, 16, 32]

    for cfg in configs:
        y = []
        for process in processes:
            path = f"results/{cfg}-{process}.out"
            p = Path(path)
            if not p.exists():
                print(f"skip {path} - does not exist")
                continue
            output += str(path)
            output += "; "

            content = p.read_text()
            content = content.split("\n")
            for line in content:
                if line.startswith("Average MNUPS"):
                    nups = re.findall(r'\d+', line)
                    output += nups[0]
                    output += "\n"
                    y.append(int(nups[0]))

        if y != 3:
            continue
        line, = plt.plot(processes, y)
        line.set_label(cfg)
        plt.legend()
        plt.xticks(processes)
        plt.xlabel('Processes')
        plt.ylabel('MNUPS')
        plt.savefig("results/benchmark.png")

    config.BENCHMARK_GRAPH_FILE.write_text(output)

