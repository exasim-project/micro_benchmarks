from Owls.LogFileParser import LogFile, LogKey
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from obr import signac_operations

import exasim_plot_helpers as eph



def dispatch_plot(func, args):
    try:
        func(*args)
    except Exception as e:
        print("failed to plot", func.__name__, e)


def plot_impl_():
    pass


def simple_break_down_rel(jobs, field):
    """the basic break down the solver annotations without OGL data"""

    query = build_annotated_query_rel()
    df, grouped, group_keys = from_query_to_grouped_df(jobs, query, "solver", "nCells")

    fig, axes = plt.subplots(
        nrows=1, ncols=len(group_keys), figsize=(12, 4), sharey=True
    )

    axes[0].set_ylabel("Time [%]")

    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h, l = ax.get_legend_handles_labels()
    l = [_.replace("_rel", "").replace(":", "") for _ in l]

    ax.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/of_breakdown_rel.png", bbox_inches="tight")


def speed_up_over_resolution_impl(jobs, x):
    annotated_query = eph.signac_conversion.build_annotated_query()
    df = eph.signac_conversion.from_query_to_df(
            jobs,
            query = annotated_query, 
            index=["nCells", "solver", "executor", "nSubDomains"])

    partitionings = set(
        df[df.index.get_level_values("executor") != "CPU"].index.get_level_values("nSubDomains"))

    fig, axes = plt.subplots( 
                nrows=1, ncols=1, figsize=(8, 5), sharey=True
                )

    labels = []

    # generate over different partitionings
    # get base_ranks TODO find a generic way to do this 
    base_ranks = 32 

    # get available partitionings for non CPU case 
    partitionings = set(
            df[df.index.get_level_values("executor") != "CPU"].index.get_level_values("nSubDomains")
            )

    for part in partitionings:
        # compute individual speed up
        filtered_df = df[
            (df.index.get_level_values("nSubDomains") == part) | (df.index.get_level_values("executor") == "CPU")]
                    
        speedup = eph.helpers.compute_speedup(
            filtered_df, 
            [("executor", "CPU")], 
            ignore_indices=["nSubDomains"],
            drop_indices=["solver"])
                        
        speedup = eph.helpers.idx_query(speedup, [("executor","hip")])     
        speedup = eph.helpers.idx_keep_only(speedup, "nCells")     
        speedup[x].plot(label=f"mpi ranks {part}")
        labels.append(f"MPI ranks: {part}")
                                        
    axes.legend(labels)
    axes.grid(True, which="both")
    axes.set_xscale("log")
    axes.set_ylabel(f"Speedup {x} [-]")

    return fig 
    


def simple_break_down(jobs, field):
    """the basic break down the solver annotations without OGL data"""

    query = build_annotated_query()
    group_key = "nCells"
    sub_group = "solver"
    df, grouped, group_keys = from_query_to_grouped_df(
        jobs, query, sub_group, group_key
    )

    df = df[df["nSubDomains"] == 32]

    fig, axes = plt.subplots(
        nrows=1, ncols=len(group_keys), figsize=(12, 4), sharey=True
    )

    axes[0].set_ylabel("Time [ms]")

    #
    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=[group_key]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"{group_key} = {key}")

    h, l = ax.get_legend_handles_labels()
    l = [_.replace("_rel", "").replace(":", "") for _ in l]
    ax.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/of_breakdown.png", bbox_inches="tight")


def gko_break_down_over_x(jobs, field, x):
    """the basic break down the solver annotations without OGL data"""

    query = build_gko_query(field)
    df, grouped, group_keys = from_query_to_grouped_df(jobs, query, x, "nCells")

    fig, axes = plt.subplots(
        nrows=1, ncols=len(group_keys), figsize=(12, 4), sharey=True
    )

    axes[0].set_ylabel("Time [ms]")

    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h, l = ax.get_legend_handles_labels()
    l = [_.replace("_rel", "").replace(":", "") for _ in l]

    ax.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig(
        f"assets/images/gko_breakdown_{field}_over_{x}.png", bbox_inches="tight"
    )


def gko_break_down_over_runs(jobs, field):
    """the basic break down the solver annotations without OGL data"""

    query = build_gko_query(field)
    res = signac_operations.query_to_dict(list(jobs), query, False, False)

    # unpack results to records
    def pop_if_list(d):
        d_tmp = {}
        all_scalars = True
        for k, v in d.items():
            if not isinstance(v, list):
                d_tmp.update({k: v})
                continue
            if len(v) > 0:
                all_scalars = False
                d_tmp["run"] = len(v)
                d_tmp.update({k: v.pop()})

        return d, all_scalars, d_tmp

    records = []
    for d_ in res:
        all_scalars = False
        d = list(d_.values())[0]
        while not all_scalars:
            d, all_scalars, d_tmp = pop_if_list(d)
            records.append(d_tmp)

    # no records created stop here
    if not records:
        return

    df = pd.DataFrame.from_records(records, index=["run"]).dropna()

    grouped = df.groupby("nCells")
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(
        nrows=1, ncols=len(group_keys), figsize=(12, 4), sharey=True
    )

    axes[0].set_ylabel("Time [ms]")

    # iterate over nCells
    for key, ax in zip(group_keys, axes.flatten()):
        group = grouped.get_group(key)
        group = group.sort_index()

        ax = group.drop(columns=["nCells"]).plot.bar(ax=ax, stacked=True, legend=False)
        ax.set_title(f"nCells = {key}")

    h, l = ax.get_legend_handles_labels()
    l = [_.replace("_rel", "").replace(":", "") for _ in l]

    ax.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig(
        f"assets/images/gko_breakdown_over_runs_{field}.png", bbox_inches="tight"
    )


def time_over_cells(jobs, field):
    query = build_annotated_query()
    df, grouped, group_keys = from_query_to_grouped_df(jobs, query, x, "nCells")

    df = df[df["nSubDomains"] == 32]

    grouped = df.groupby("solver")
    linestyles = ["-", "-.", ":"]
    group_keys = grouped.groups.keys()

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 4), sharey=True)
    axes.set_ylabel("Time [ms]")

    for key, lt in zip(group_keys, linestyles):
        group = grouped.get_group(key)
        group = group.sort_index()
        ax = group.plot(ax=axes, legend=False, linestyle=lt, marker="x")

    h, ls = ax.get_legend_handles_labels()
    l = []
    for k in group_keys:
        for _ in ["MomentumPredictor"]:
            l.append(f"{_} {k}")

    ax.legend(h, l, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig("assets/images/time_solve.png", bbox_inches="tight")


def call(jobs):
    """entry point for plotting"""
    # storage format
    # assets/images/plots/hash.png
    # assets/images/plots/hash.json

    dispatch_plot(gko_break_down_over_runs, (jobs, "p"))
    dispatch_plot(simple_break_down, (jobs, "p"))
    dispatch_plot(gko_break_down_over_x, (jobs, "p", "solver"))
    dispatch_plot(gko_break_down_over_x, (jobs, "p", "nSubDomains"))
    dispatch_plot(time_over_cells, (jobs, "p"))
