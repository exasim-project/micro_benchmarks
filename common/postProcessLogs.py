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
    OGLAnnotationKeys = [
            key.format(field)
            for key in [ 
                "{}: update_local_matrix_data:",
                "{}: update_non_local_matrix_data:",
                "{}_matrix: call_update:",
                "{}_rhs: call_update:",
                "{}: init_precond:",
                "{}: generate_solver:",
                "{}: solve:",
                "{}: copy_x_back:",
                "{}: solve_multi_gpu",
                ]
            for field in ["Ux", "Uy", "Uz", "p"]
        ]

    OGLAnnotations = [
        LogKey(search, ["proc", "time"], append_search_to_col=True)
        for search in OGLAnnotationKeys
    ]

    # Solver annotations
    SolverAnnotationKeys = [
            "MatrixAssemblyU",
            "MomentumPredictor",
            "SolveP",
            "MatrixAssemblyPI:",
            "MatrixAssemblyPII:",
            "TimeStep",
        ]

    CombinedKeys = SolverAnnotationKeys + OGLAnnotationKeys

    SolverAnnotations = [
        LogKey(search, col_time, append_search_to_col=True)
        for search in  SolverAnnotationKeys
    ]

    logKeys = [pIter, UIter]
    logKeys += SolverAnnotations
    logKeys += OGLAnnotations

    cache = signac_operations.JobCache(jobs)

    for job in jobs:
        solver = job.doc["obr"].get("solver")

        # skip jobs without a solver
        if not solver:
            continue

        case_path = Path(job.path) / "case"

        # get latest log
        runs = job.doc["obr"][solver]
        solver = job.sp["solver"]
        # pop old results
        for k in CombinedKeys:
            try:
                 job.doc["obr"].pop(k)
                 job.doc["obr"].pop(k + "_rel")
            except Exception as e:
                print(e)

        for i, run in enumerate(runs):
            log_path = case_path / run["log"]

            # parse logs for given keys
            df = LogFile(logKeys).parse_to_df(log_path)

            # write average times to job.doc
            for k in CombinedKeys:
                try:
                     prev_res = job.doc["obr"].get(k, [])
                     val = df.iloc[1:].mean()["time_" + k]
                     prev_res.append(val)
                     job.doc["obr"][k] = prev_res
                except Exception as e:
                    print(e)

            # write average times step ratio to job.doc
            for k, rel in zip(CombinedKeys, ["time_TimeStep", "Ux: solve_multi_gpu"]):
                try:
                     prev_res = job.doc["obr"].get(k + "_rel", [])
                     prev_res.append(df.iloc[1:].mean()[rel])
                     job.doc["obr"][k + "_rel"] =  prev_res
                except Exception as e:
                    print(e)

            job.doc["obr"]["nCells"] = cache.search_parent(job, "nCells")
