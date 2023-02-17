from Owls.LogFileParser import LogFile, LogKey
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from obr import signac_operations


def call(jobs):

    col_iter = ["init", "final", "iter"]
    col_time = ["time"]
    p_steps = ["_p", "_pFinal"]
    U_components = ["_Ux", "_Uy", "_Uz"]

    pIter = LogKey("Solving for p", col_iter, p_steps)
    UIter = LogKey("Solving for U", col_iter, U_components)
    pTiming = LogKey("Linear solve p", col_time, p_steps)
    pTiming = LogKey("Linear solve U", col_time, ["_U"])

    logKeys = [
        LogKey(search, col_time, append_search_to_col=True)
        for search in [
            "global_index_init",
            "update_local_matrix_data",
            "update_non_local_matrix_data",
            "p_matrix: call_update",
            "p_rhs: call_update",
            "init_precond",
            "generate_solver",
            "solve",
            "copy_x_back",
        ]
    ]

    logKeys += [pIter, UIter, pTiming]

    cache = signac_operations.JobCache(jobs)
    records = []
    d_tmp = defaultdict(list)

    for j in jobs:
        solver = j.doc["obr"].get("solver")

        # skip jobs without a solver
        if not solver:
            continue

        case_path = Path(j.path) / "case"

        # get latest log
        log_path = case_path / j.doc["obr"][solver][-1]["log"]

        # parse logs for given keys
        df = LogFile(logKeys).parse_to_df(log_path)
        print(df)

        # skip first row / first time step
        solver = j.sp["solver"]
        d_tmp[solver].append((cache.search_parent(j, "nCells"), [df.iloc[1:].mean()["time_solve"]]))

    fig, ax = plt.subplots(nrows=1, ncols=1)
    for solver, data in d_tmp.items():
         nCells, time = zip(*data)
         line, = ax.plot(nCells, time)
         line.set_label(solver)

    ax.legend()
    ax.set_xlabel("Number of cells [-]")
    ax.set_ylabel("Time [ms]")
    fig.savefig("assets/image.png")
    plt.close(fig)
