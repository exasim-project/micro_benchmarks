from Owls.LogFileParser import LogFile, LogKey
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from obr import signac_operations
import os

import exasim_plot_helpers as eph
import numpy as np


def normalized_plots(jobs: list, case: str, append_to_fn: str = ""):
    """plot figures that need some kind of normalisation"""

    annotated_query = eph.signac_conversion.build_annotated_query()
    df = eph.signac_conversion.from_query_to_df(
        jobs,
        query=annotated_query,
        index=["nCells", "solver", "executor", "nSubDomains"],
    )
    base_query = [eph.helpers.query(idx="executor", val="CPU", op=eph.helpers.equal())]

    speed_up_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        "Number Cells [#]", "Speedup linear solver [-]"
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.facets_relative_to_base_over_x,
        case,
        speed_up_over_nCells,
        append_to_fn,
        df,
        "MPI ranks: {}",
        base_query=base_query,
        x="nCells",
        y="SolveP",
        facet="nSubDomains",
    )

    speed_up_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        "Number Cells [#]", "Speedup time step [-]"
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.facets_relative_to_base_over_x,
        case,
        speed_up_over_nCells,
        append_to_fn,
        df,
        "MPI ranks: {}",
        base_query=base_query,
        x="nCells",
        y="TimeStep",
        facet="nSubDomains",
    )

    speed_up_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        "Number Cells [#]", "Relative number of iterations [-]"
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.facets_relative_to_base_over_x,
        case,
        speed_up_over_nCells,
        append_to_fn,
        df,
        "MPI ranks: {}",
        base_query=base_query,
        x="nCells",
        y="iter_p",
        facet="nSubDomains",
    )


def unnormalized_plots(jobs: list, case: str, append_to_fn: str = ""):
    """plot figures that need some kind of normalisation"""

    annotated_query = eph.signac_conversion.build_annotated_query()
    df = eph.signac_conversion.from_query_to_df(
        jobs,
        query=annotated_query,
        index=["nCells", "solver", "executor", "nSubDomains"],
    )

    queries = {"PCG": [eph.helpers.query("solver", "PCG", eph.helpers.equal())]}

    gko_executor = os.environ.get("GINKGO_EXECUTOR")
    gko_mask = eph.helpers.idx_query_mask(
        df,
        [eph.helpers.query(idx="executor", val=gko_executor, op=eph.helpers.equal())],
    )

    gko_ranks = set(df[gko_mask].index.get_level_values("nSubDomains"))

    queries_subDomains = {
        "GKOCG - {} ranks".format(ranks): [
            eph.helpers.query("solver", "GKOCG", eph.helpers.equal()),
            eph.helpers.query("nSubDomains", ranks, eph.helpers.equal()),
        ]
        for ranks in gko_ranks
    }

    queries_subDomains.update(queries)

    speed_up_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        "Number Cells [#]", "Time [ms]"
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.facets_over_x,
        case,
        speed_up_over_nCells,
        append_to_fn,
        df,
        "{}",
        queries_subDomains,
        x="nCells",
        y="SolveP",
    )

    speed_up_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        "Number Cells [#]", "Iterations [#]"
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.facets_over_x,
        case,
        speed_up_over_nCells,
        append_to_fn,
        df,
        "{}",
        queries_subDomains,
        x="nCells",
        y="iter_p",
    )


def simple_break_down(jobs, case, append_to_fn: str = ""):
    """the basic break down the solver annotations without OGL data"""

    query = eph.signac_conversion.build_annotated_query()
    df = eph.signac_conversion.from_query_to_df(
        jobs, query, index=["nCells", "solver", "executor", "nSubDomains"]
    )

    # same ranks different resolution
    # NOTE this is valid for repartitoned cases
    # for other cases number of nodes should be considered
    cpu_mask = eph.helpers.idx_query_mask(
        df, [eph.helpers.query(idx="executor", val="CPU", op=eph.helpers.equal())]
    )

    cpu_ranks = list(set(df[cpu_mask].index.get_level_values("nSubDomains")))

    filtered_df = df[
        eph.helpers.idx_query_mask(
            df,
            [
                eph.helpers.query(
                    idx="nSubDomains", val=cpu_ranks[0], op=eph.helpers.equal()
                )
            ],
        )
    ]
    filtered_df.index = filtered_df.index.droplevel("nSubDomains")

    # drop columns that are irelevant
    filtered_df = filtered_df.drop(
        columns=["TimeStep", "iter_p", "iter_Ux", "final_p", "final_Ux"]
    )

    break_down_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        y_label="Time [ms]", getter=lambda x: x[0]
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.bar_facet,
        case,
        break_down_over_nCells,
        f"_ranks{cpu_ranks[0]}" + append_to_fn,
        filtered_df,
        facet="nCells",
    )


def simple_break_down_rel(jobs: list, case: str, append_to_fn: str = ""):
    """the basic break down the solver annotations without OGL data

    NOTE Computes ratio based on single execution, thus if p is computed
    several  times per time step, the total ratio is underestimated
    """

    query = eph.signac_conversion.build_annotated_query()
    # NOTE if pressure is com
    df = eph.signac_conversion.from_query_to_df(
        jobs, query, index=["nCells", "solver", "executor", "nSubDomains"]
    )

    # same ranks different resolution
    # NOTE this is valid for repartitoned cases
    # for other cases number of nodes should be considered
    cpu_mask = eph.helpers.idx_query_mask(
        df, [eph.helpers.query(idx="executor", val="CPU", op=eph.helpers.equal())]
    )

    cpu_ranks = list(set(df[cpu_mask].index.get_level_values("nSubDomains")))

    filtered_df = df[
        eph.helpers.idx_query_mask(
            df,
            [
                eph.helpers.query(
                    idx="nSubDomains", val=cpu_ranks[0], op=eph.helpers.equal()
                )
            ],
        )
    ]
    filtered_df.index = filtered_df.index.droplevel("nSubDomains")

    # drop columns that are irelevant
    filtered_df = filtered_df.div(filtered_df["TimeStep"], axis=0)
    filtered_df = filtered_df.drop(
        columns=["TimeStep", "iter_p", "iter_Ux", "final_p", "final_Ux"]
    )

    break_down_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        y_label="Time [ms]", getter=lambda x: x[0]
    )
    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.bar_facet,
        case,
        break_down_over_nCells,
        f"_ranks{cpu_ranks[0]}_rel" + append_to_fn,
        filtered_df,
        facet="nCells",
    )


def gko_break_down(jobs: list, field: str, case: str, append_to_fn: str = ""):
    """the basic break down the solver annotations without OGL data"""

    query = eph.signac_conversion.build_gko_query(field)
    df = eph.signac_conversion.from_query_to_df(
        jobs, query, index=["nCells", "solver", "executor", "nSubDomains"]
    )

    break_down_over_nCells = eph.plot_funcs.ax_handler_wrapper(
        y_label="Time [ms]", getter=lambda x: x[0]
    )

    # since we look at gko cases on a single machine all
    # executor should be the same
    df.index = df.index.droplevel("executor")

    eph.plot_funcs.dispatch_plot(
        eph.plot_funcs.bar_facet,
        case,
        break_down_over_nCells,
        f"_gko" + append_to_fn,
        df,
        facet="nCells",
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
    return fig
