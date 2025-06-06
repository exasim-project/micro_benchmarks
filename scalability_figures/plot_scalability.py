#!/usr/bin/env python3
"""
plot_case.py

Usage:
    python plot_case.py --json /path/to/postpro.json [--tick-step N]

This script expects that `postpro.json` is a JSON array (a list of dicts), each dict having at least these keys:
    "numberOfSubdomains"   (string or int)
    "preconditioner"       (one of: "none", "BJ", "FDIC", or some GPU Multigrid string)
    "TimeStep"             (in milliseconds)
    "ranksPerGPU"          (only for GPU runs; CPU runs omit it)
    "nCells"               (same integer on every entry)
    plus optional keys “p_NoIterations” or “p_rgh_NoIterations” (we detect whichever exists).

It calls `prepareData_final(...)` to produce:
    nCells, dict_RPG
where dict_RPG has up to four keys: "GAMG", "PCG", "BJCG", "GKOMG".

It then plots FVOPs vs. nodes for each solver‐type (log‐scale on the y‐axis), with twin x‐axes showing “cells per GPU” and “cells per Core.” To reduce overlapping tick labels, you can specify `--tick-step N` so that only every Nth tick is labeled (default is 1, i.e. label every tick).

The figure is saved to disk as `<case_name>.png`, where `case_name` is the directory name containing `postpro.json`.

Example:
    python plot_case.py --json /home/alex/experiments/WindsorBody/postpro.json --tick-step 2
    → saves `WindsorBody.png` in the current working directory, labeling every 2nd tick.
"""

import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib.ticker as ticker

# ----------------------------------------------------------------------------------------
# (1)   GLOBAL PLOTTING PARAMETERS (as in your notebook)
# ----------------------------------------------------------------------------------------
ucfdGrey        = '#626366'
ucfdLightGrey   = '#EFEFF0'
ucfdBlue        = '#1C81AC'
ucfdLightBlue   = '#5BBCE4'
ucfdGreen       = '#206869'
ucfdLightGreen  = '#61BF80'
ucfdPurple      = '#954F72'
ucfdOrange      = '#EAB30E'

plt.rcParams['font.size']             = '16'
plt.rcParams['text.color']            = ucfdGrey
plt.rcParams['axes.labelsize']        = '16'
plt.rcParams['xtick.labelsize']       = '16'
plt.rcParams['ytick.labelsize']       = '16'
#plt.rcParams['font.family']           = 'sans-serif'
#plt.rcParams['font.sans-serif']       = 'Barlow Semi Condensed'
plt.rcParams['lines.markersize']      = 4
plt.rcParams['lines.markeredgewidth'] = 1
plt.rcParams['lines.linewidth']       = 2.5
plt.rcParams['lines.color']           = ucfdGrey
plt.rcParams['legend.edgecolor']      = ucfdBlue
plt.rcParams['axes.edgecolor']        = ucfdGrey
plt.rcParams['axes.labelcolor']       = ucfdGrey
plt.rcParams['axes.prop_cycle']       = cycler(
    'color',
    [
        ucfdGrey, ucfdBlue, ucfdLightGreen, ucfdPurple, ucfdOrange,
        ucfdLightBlue, ucfdGreen, '#1f77b4', '#ff7f0e', '#2ca02c',
        '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf'
    ]
)
plt.rcParams['xtick.color']           = ucfdGrey
plt.rcParams['ytick.color']           = ucfdGrey
plt.rcParams['grid.color']            = ucfdLightGrey

# ----------------------------------------------------------------------------------------
# (2)   prepareData_final(...) exactly as in the notebook
# ----------------------------------------------------------------------------------------
def prepareData_final(data_list):
    """
    Input:  data_list = [ { ... }, { ... }, ... ]   (each dict has keys like
             "numberOfSubdomains", "preconditioner", "TimeStep", "ranksPerGPU", etc.)
    Output: (nCells, dict_RPG) where
            nCells   = data_list[0]['nCells']
            dict_RPG = {
                "GAMG":  {"times":[...], "procs":[...], "nodes":[...], "pIter":[...], "cost":[...], "fvops":[...]},
                "PCG":   { ... },
                "BJCG":  { ... },
                "GKOMG": { ... }
            }
    (Sorted by increasing numberOfSubdomains before processing.)
    """
    data_list.sort(key=lambda element: int(element['numberOfSubdomains']))
    GPUHr = 1.819   # Euro per GPU‐hour
    CoreHr = 0.02116   # Euro per CPU‐core‐hour

    nCells = data_list[0]['nCells']

    if "p_NoIterations" in data_list[0]:
        pKey = "p_NoIterations"
    else:
        pKey = "p_rgh_NoIterations"

    dict_RPG = {}
    for element in data_list:
        pc = element['preconditioner']
        if pc == 'none':
            keystr = "GAMG"
        elif pc == 'BJ':
            keystr = "BJCG"
        elif pc == 'FDIC':
            keystr = "PCG"
        else:
            keystr = "GKOMG"

        try:
            times = 0.001 * element["TimeStep"]
        except KeyError:
            times = 0.0

        procs = int(element["numberOfSubdomains"])

        try:
            nodes = np.divide(procs, 4 * element["ranksPerGPU"])
        except (KeyError, ZeroDivisionError):
            nodes = np.divide(procs, 76)

        try:
            pIter = element[pKey]
        except KeyError:
            pIter = 0

        cost = np.multiply(GPUHr * times / 3600, 4 * nodes)

        try:
            fvops = np.divide(np.divide(nCells, times), nodes)
        except (ZeroDivisionError, FloatingPointError):
            fvops = 0.0

        if keystr in dict_RPG:
            dict_RPG[keystr]["times"].append(times)
            dict_RPG[keystr]["procs"].append(procs)
            dict_RPG[keystr]["nodes"].append(nodes)
            dict_RPG[keystr]["pIter"].append(pIter)
            dict_RPG[keystr]["cost"].append(cost)
            dict_RPG[keystr]["fvops"].append(fvops)
        else:
            dict_RPG[keystr] = {
                "times": [times],
                "procs": [procs],
                "nodes": [nodes],
                "pIter": [pIter],
                "cost": [cost],
                "fvops": [fvops]
            }

    return nCells, dict_RPG

# ----------------------------------------------------------------------------------------
# (3)   MAIN: parse arguments, load JSON, run prepareData_final, and save figure
# ----------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Read a folder's postpro.json, run prepareData_final, and save the FVOPs‐vs‐nodes plot."
    )
    parser.add_argument(
        "--json",
        type=str,
        default="postpro.json",
        help="Path to postpro.json (must be a JSON array of dicts)."
    )
    parser.add_argument(
        "--tick-step",
        type=int,
        default=1,
        help="Only label every Nth tick on the x‐axes (default=1 means label every tick)."
    )
    args = parser.parse_args()

    json_path = args.json
    tick_step = max(1, args.tick_step)  # ensure at least 1

    try:
        with open(json_path, "r") as f:
            raw_list = json.load(f)
    except FileNotFoundError:
        print(f"Error: Cannot open '{json_path}'. Please check that it exists.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: JSON decode error in '{json_path}': {e}")
        return

    if not isinstance(raw_list, list):
        print(f"Error: Expected {json_path} to be a JSON array (list of dicts).")
        return
    if len(raw_list) == 0:
        print(f"Error: {json_path} is an empty list. Nothing to plot.")
        return

    dir_of_json = os.path.dirname(os.path.abspath(json_path))
    case_name   = os.path.basename(dir_of_json)

    nCells, data_dict = prepareData_final(raw_list)

    fig, ax = plt.subplots(dpi=300)
    solver_order = ["PCG", "GAMG", "BJCG", "GKOMG"]
    for solver in solver_order:
        if solver not in data_dict:
            print(f"Warning: Solver '{solver}' not found in JSON. Skipping it.")
            continue

        nodes_arr = np.array(data_dict[solver]["nodes"])
        fvops_arr = np.array(data_dict[solver]["fvops"])

        ax.plot(
            nodes_arr,
            fvops_arr,
            marker='o',
            linestyle='-',
            label=solver
        )

    ax.set_yscale('log')
    ax.set_xlabel("nodes")
    ax.set_ylim((5e5,1e6))
    ax.set_ylabel(r"FVOPS per node [$s^{-1}$]")
    ax.set_title(f"{case_name}")
    ax.grid(which='major', axis='both', linestyle='--', linewidth=0.5, alpha=0.6)
    ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=12, loc='best')

    # Determine x‐range
    all_nodes = np.concatenate(
        [np.array(data_dict[s]["nodes"]) for s in solver_order if s in data_dict]
    )
    x_max = int(np.max(all_nodes)) if len(all_nodes) > 0 else 1

    # Build tick positions from 0 to x_max (integers)
    tick_positions = np.arange(0, x_max + 1, 1)

    # Primary x‐axis: label every tick_step (but still show tick marks at every integer)
    ax.set_xticks(tick_positions)
    primary_labels = [
        str(n) if (n % tick_step == 0) else ""
        for n in tick_positions
    ]
    ax.set_xticklabels(primary_labels)

    # ===  twin axis #1: cells/GPU  ===
    ax3 = ax.twiny()
    ax3.set_facecolor('none')
    ax3.set_xlim(ax.get_xlim())

    # Only place ticks every tick_step on the GPU axis
    gpu_ticks = tick_positions[::tick_step]
    ax3.set_xticks(gpu_ticks)
    cpugpu_labels = []
    for n in gpu_ticks:
        if n == 0:
            cpugpu_labels.append("cells/GPU")
        else:
            cpugpu_labels.append(f"{(nCells / (n * 4)):.1e}")
    ax3.set_xticklabels(cpugpu_labels, fontsize=9)

    # Move the "cells/GPU" label slightly left to avoid overlap:
    gpu_ticklabels = ax3.get_xticklabels()
    if gpu_ticklabels:
        gpu_ticklabels[0].set_horizontalalignment("center")

    # ===  twin axis #2: cells/Core  ===
    ax4 = ax.twiny()
    ax4.set_facecolor('none')
    ax4.set_xlim(ax.get_xlim())
    ax4.spines['top'].set_position(('outward', 30))

    # Only place ticks every tick_step on the Core axis
    core_ticks = tick_positions[::tick_step]
    ax4.set_xticks(core_ticks)
    cpucore_labels = []
    for n in core_ticks:
        if n == 0:
            cpucore_labels.append("cells/Core")
        else:
            cpucore_labels.append(f"{(nCells / (n * 76)):.1e}")
    ax4.set_xticklabels(cpucore_labels, fontsize=9)

    core_ticklabels = ax4.get_xticklabels()
    if core_ticklabels:
        core_ticklabels[0].set_horizontalalignment("center")

    plt.tight_layout()
    output_filename = f"{case_name}.png"
    plt.savefig(output_filename, dpi=300)
    print(f"Saved figure to '{output_filename}'.")

if __name__ == "__main__":
    main()

