from Owls.LogFileParser import LogFile, LogKey
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from obr import signac_operations


def plot_simple_break_down(jobs):
    """ the basic break down the solver annotations without OGL data """

    query = " and ".join([
        "solver",
        "executor",
        "SolveP_rel",
        "MomentumPredictor_rel",
        "MatrixAssemblyU_rel",
        "MatrixAssemblyPI:_rel",
        "MatrixAssemblyPII:_rel",
        "nCells"
        ])

    res = signac_operations.query_to_dict(list(jobs), query) 
    res = [list(d.values())[0] for d in res]
    df = pd.DataFrame.from_records(res, index=["solver"])

    grouped = df.groupby("nCells");
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(nrows=1, ncols=len(group_keys), figsize=(12,4), sharey=True)

    axes[0].set_ylabel("Time [%]")

    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h,l = ax.get_legend_handles_labels()
    l = [_.replace("_rel","").replace(":","") for _ in l]

    ax.legend(h, l, loc='center left', bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/of_breakdown.png", bbox_inches='tight')

def plot_gko_break_down(jobs):
    """ the basic break down the solver annotations without OGL data """

    query = " and ".join([
        "solver",
        "Ux: update_local_matrix_data:",
        "Ux: update_non_local_matrix_data:",
        "Ux_matrix: call_update:",
        "Ux_rhs: call_update:",
        "Ux: init_precond:",
        "Ux: generate_solver:",
        "Ux: solve:",
        "Ux: copy_x_back:",
        "nCells"
        ])

    res = signac_operations.query_to_dict(list(jobs), query) 
    res = [list(d.values())[0] for d in res]
    df = pd.DataFrame.from_records(res, index=["solver"])

    grouped = df.groupby("nCells");
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(nrows=1, ncols=len(group_keys), figsize=(12,4), sharey=True)

    axes[0].set_ylabel("Time [ms]")

    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h,l = ax.get_legend_handles_labels()
    l = [_.replace("_rel","").replace(":","") for _ in l]

    ax.legend(h, l, loc='center left', bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/gko_breakdown.png", bbox_inches='tight')

def plot_gko_break_down_over_runs(jobs):
    """ the basic break down the solver annotations without OGL data """

    query = " and ".join([
        "solver",
        "p: update_local_matrix_data:",
        "p: update_non_local_matrix_data:",
        "p_matrix: call_update:",
        "p_rhs: call_update:",
        "p: init_precond:",
        "p: generate_solver:",
        "p: solve:",
        "p: copy_x_back:",
        "nCells"
        ])
    print(query)

    res = signac_operations.query_to_dict(list(jobs), query, False, False) 

    # unpack results to records
    def pop_if_list(d):
        d_tmp = {}
        all_scalars = True
        for k, v in d.items():
            if not isinstance(v, list):
                d_tmp.update({k:v})
                continue
            if len(v) > 0:
                all_scalars = False
                d_tmp["run"] = len(v)
                d_tmp.update({k:v.pop()})
                
        return d, all_scalars, d_tmp

    records = []
    for d_ in res:
        all_scalars = False
        d = list(d_.values())[0]
        while(not all_scalars):
            d, all_scalars, d_tmp = pop_if_list(d)
            records.append(d_tmp)


    print(records)
    df = pd.DataFrame.from_records(records, index=["run"]).dropna()
    print(df)

    grouped = df.groupby("nCells");
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(nrows=1, ncols=len(group_keys), figsize=(12,4), sharey=True)

    axes[0].set_ylabel("Time [ms]")

    # iterate over nCells
    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h,l = ax.get_legend_handles_labels()
    l = [_.replace("_rel","").replace(":","") for _ in l]

    ax.legend(h, l, loc='center left', bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/gko_breakdown_over_runs.png", bbox_inches='tight')


def plot_time_over_cells(jobs):
    query = " and ".join([
        "solver",
        "executor",
        # "SolveP",
        "MomentumPredictor",
        # "TimeStep",
        "nCells"
        ])

    res = signac_operations.query_to_dict(list(jobs), query) 
    res = [list(d.values())[0] for d in res]
    df = pd.DataFrame.from_records(res, index=["nCells"])

    grouped = df.groupby("solver");
    linestyles = ["-", "-.", ":" ]
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12,4), sharey=True)
    axes.set_ylabel("Time [ms]")

    for key, lt in zip(group_keys, linestyles):
        group = grouped.get_group(key)
        group = group.sort_index()
        ax = group.plot(ax=axes, legend=False, linestyle=lt, marker="x")

    h,ls = ax.get_legend_handles_labels()
    l = []
    for k in group_keys:
        for _ in ["MomentumPredictor"]:
            l.append(f"{_} {k}")

    print(l)

    ax.legend(h, l, loc='center left', bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/time_solve.png", bbox_inches='tight')

def call(jobs):
    """ entry point for plotting """
    # storage format
    # assets/images/plots/hash.png
    # assets/images/plots/hash.json

    plot_gko_break_down_over_runs(jobs)
    #plot_simple_break_down(jobs)
    #plot_gko_break_down(jobs)
    #plot_time_over_cells(jobs)
