from pathlib import Path
import re
import logging
import matplotlib.pyplot as plt
from jobgeneration import config


def create() -> None:
    output = ""

    for cfg in config.MPI_TYPES:
        y = []
        for process in config.PROCESSES:
            path = f"results/{cfg}-{process}.out"
            p = Path(path)
            if not p.exists():
                logging.warning(f"skip {path} - does not exist")
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

        if len(y) != 3:
            continue
        logging.info("Plot " + cfg)
        line, = plt.plot(config.PROCESSES, y)
        line.set_label(cfg)
        plt.legend()

    plt.xticks(config.PROCESSES)
    plt.xlabel('Processes')
    plt.ylabel('MNUPS')

    logging.info("Save image to: " + str(config.BENCHMARK_GRAPH_IMAGE))
    plt.savefig(config.BENCHMARK_GRAPH_IMAGE)

    config.BENCHMARK_GRAPH_FILE.write_text(output)

