from Owls.LogFileParser import LogFile, LogKey
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt


def call(jobs):

    col_iter = ["init", "final", "iter"]
    col_time = ["time"]
    p_steps = ["_p", "_pFinal"]
    U_components = ["_x", "_y", "_z"]

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

    d_tmp = {}

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

        # skip first row / first time step
        d_tmp.update({j.sp["modifyBlock"]: df.iloc[1:].mean()["time_solve"]})

    # random plot for now
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot([0, 1, 2], [10, 20, 3])
    fig.savefig("assets/image.png")
    plt.close(fig)
