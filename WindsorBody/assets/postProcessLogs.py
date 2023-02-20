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

    # OGL keys
    OGLAnnotations = [
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

    # Solver annotations
    SolverAnnotations = [
        LogKey(search, col_time, append_search_to_col=True)
        for search in [
            "MatrixAssemblyU:",
            "MomemtumPredictor:",
            "SolveP:",
            "MatrixAssemblyPI:",
            "MatrixAssemblyPII:",
            "TimeStep:",
        ]
    ]

    logKeys = [pIter, UIter, pTiming]
    logKeys += SolverAnnotations
    logKeys += OGLAnnotations

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
        solver = j.sp["solver"]

        # write to job.doc
        job.doc["time_SolveP"] = df.iloc[1:].mean()["time_solve"]
        job.doc["time_MomentumPredictor"] = df.iloc[1:].mean()["time_solve"]
        job.doc["time_TimeStep"] = df.iloc[1:].mean()["time_solve"]
