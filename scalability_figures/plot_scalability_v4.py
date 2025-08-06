#!/usr/bin/env python3
"""
plot_case.py

Usage:
    python plot_case.py --json /path/to/postpro.json [--spuma-json /path/to/clocktimes.json]
                         [--tick-step N] [--y-limits YMIN YMAX]
                         [--plot-times] [--plot-piter]
                         [--ndt N] [--nPISOCorr M]

Options:
    --tick-step N         Only label every Nth tick on the x‑axes (default=1).
    --y-limits YMIN YMAX  Set y‑axis limits for the FVOPS plot.
    --plot-times          Plot raw time per timestep in a separate figure.
    --plot-piter          Plot number of pressure iterations in a separate figure.
    --spuma-json PATH     Path to clocktimes.json (SPuMA data).
    --ndt N               Number of time steps in the study (default=100).
    --nPISOCorr M         Number of PISO correction loops used (default=1.0).
"""

import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

# ----------------------------------------------------------------------------------------
# (1)   GLOBAL PLOTTING PARAMETERS
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
# (2)   prepareData_final(...) with per-entry PIMPLE_count
# ----------------------------------------------------------------------------------------
def prepareData_final(data_list, ndt, nPISOCorr):
    data_list.sort(key=lambda el: int(el['numberOfSubdomains']))
    GPUHr = 1.701247   # Euro per GPU-hour
    CoreHr = 0.03747   # Euro per CPU-core-hour

    nCells = data_list[0].get('nCells', 0)
    pKey = 'p_NoIterations' if 'p_NoIterations' in data_list[0] else 'p_rgh_NoIterations'

    dict_RPG = {}
    for element in data_list:
        pc = element.get('preconditioner', '')
        if pc == 'none': keystr = 'GAMG'
        elif pc == 'BJ': keystr = 'BJCG'
        elif pc == 'FDIC': keystr = 'PCG'
        else: keystr = 'GKOMG'

        times = 0.001 * element.get('TimeStep', 0)
        procs = int(element['numberOfSubdomains'])
        nodes = procs / (4 * element.get('ranksPerGPU', 19))
        pIter = element.get(pKey, 0)
        costGPU = GPUHr * times / 3600 * (4 * nodes)
        costCPU = CoreHr * times / 3600 * (76 * nodes)

        pimple_count = element.get('PIMPLE_count', 0.5*(ndt-1))
        iter_per_dt = (nPISOCorr * ((pimple_count * 2) / (ndt - 1)))

        fvops = (nCells * iter_per_dt) / (times * (procs / element.get('ranksPerGPU', 1))) if times > 0 and procs > 0 else 0.0

        dict_RPG.setdefault(keystr, {'times': [], 'procs': [], 'nodes': [], 'pIter': [], 'cost': [], 'fvops': []})
        d = dict_RPG[keystr]
        d['times'].append(times)
        d['procs'].append(procs)
        d['nodes'].append(nodes)
        d['pIter'].append(pIter)
        d['cost'].append(costCPU if keystr in ('GAMG', 'PCG') else costGPU)
        d['fvops'].append(fvops)

    return nCells, dict_RPG

# ----------------------------------------------------------------------------------------
# (3)   MAIN: parse args, load JSON, run prepareData_final, and save figures
# ----------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Read postpro.json, run prepareData_final, and save the FVOPS vs. devices plot.'
    )
    parser.add_argument('--json', type=str, default='postpro.json')
    parser.add_argument('--spuma-json', type=str)
    parser.add_argument('--tick-step', type=int, default=1)
    parser.add_argument('--y-limits', nargs=2, type=float, metavar=('YMIN','YMAX'))
    parser.add_argument('--plot-times', action='store_true')
    parser.add_argument('--plot-piter', action='store_true')
    parser.add_argument('--ndt', type=int, default=100)
    parser.add_argument('--nPISOCorr', type=float, default=1.0)
    args = parser.parse_args()

    with open(args.json, 'r') as f:
        raw_list = json.load(f)
    if not raw_list:
        print(f"Error: '{args.json}' empty or invalid")
        return

    case_name = os.path.basename(os.path.dirname(os.path.abspath(args.json)))
    nCells, data_dict = prepareData_final(raw_list, args.ndt, args.nPISOCorr)

    spuma_dict = {}
    spuma_suffix=""
    if args.spuma_json:
        spuma_suffix="_spuma"
        try:
            with open(args.spuma_json, 'r') as f:
                spuma_raw = json.load(f)
        except Exception as e:
            print(f"Error reading SPuMA JSON '{args.spuma_json}': {e}")
            return
        for lst in spuma_raw.values():
            for ent in lst:
                solver = ent.get('solver'); dt = ent.get('deltaClock',0); ng = ent.get('np',0); iPdt = ent.get('avgPIMPLE',1)
                ns = ng/4; fv = (nCells*args.nPISOCorr*iPdt)/(dt*ng) if dt>0 and ng>0 else 0
                spuma_dict.setdefault(solver, {'nodes':[], 'procs': [],'fvops':[],'times':[]})
                spuma_dict[solver]['nodes'].append(ns)
                spuma_dict[solver]['procs'].append(ng)
                spuma_dict[solver]['fvops'].append(fv)
                spuma_dict[solver]['times'].append(dt)
        for sol,dat in spuma_dict.items():
            idx = np.argsort(dat['nodes'])
            spuma_dict[sol]['nodes'] = np.array(dat['nodes'])[idx]
            spuma_dict[sol]['procs'] = np.array(dat['procs'])[idx]
            spuma_dict[sol]['fvops'] = np.array(dat['fvops'])[idx]
            spuma_dict[sol]['times'] = np.array(dat['times'])[idx]

    solver_order = ['PCG','GAMG','BJCG','GKOMG']
    setfig = (8.8,4.8)

    all_procs = np.concatenate([np.array(data_dict[s]['procs']) for s in solver_order if s in data_dict])
    x_min, x_max = (max(1,int(np.min(all_procs))), int(np.max(all_procs))) if all_procs.size else (1,1)

    # Labels with full descriptions
    label_map = {
        'PCG': "OF: CPU\n(PCG solver)",
        'GAMG': "OF: CPU\n(GAMG solver)",
        'BJCG': "OGL: CPU+GPU\n(Ginkgo CG solver\n+ Block Jacobi precond.)",
        'GKOMG': "OGL: CPU+GPU\n(Ginkgo CG solver\n+ Multigrid precond.)"
    }

    # --- FVOPS ---
    fig,ax = plt.subplots(figsize=setfig,dpi=300)
    ax.set_xscale('log')
    ax.set_xlabel('nSubdomains')
    peak_ref=0
    for sol in solver_order:
        if sol not in data_dict: continue
        p = np.array(data_dict[sol]['procs']); f = np.array(data_dict[sol]['fvops'])
        if sol == 'GAMG' or sol == 'PCG':
            if peak_ref < max(data_dict[sol]['fvops']):
                peak_ref = max(data_dict[sol]['fvops'])
        ax.plot(p, f, marker='o', linestyle='-', label=label_map[sol], zorder=2)
    # SPuMA overlay
    for sol in ('PCG','GAMG'):
        if sol in spuma_dict:
            procs_sp = spuma_dict[sol]['procs']; fv_sp = spuma_dict[sol]['fvops']
            clr = ucfdGrey if sol=='PCG' else ucfdBlue
            ax.plot(procs_sp, fv_sp, marker='s', linestyle=':', linewidth=2, color=clr,
                    label=f"SPUMA: GPU ({sol} solver)")
    if args.spuma_json:
        ax.plot(12, 35170250.9, marker='s',color='r', linestyle='none', label="Comm. ref.")
    ax.set_yscale('log')
    if args.y_limits: ax.set_ylim(args.y_limits)
    ax.set_ylabel('FVOPS/device [$s^{-1}$]')
    # secondary axis: cells/device = nCells / devices
    sec = ax.twiny()
    sec.set_xscale('log')
    p_lo, p_hi = ax.get_xlim()          # e.g. [1, 16]
    y_min, y_max = ax.get_ylim()
    feasibility_distance=45.7    # AWS c6i vs p4d
    y0 = peak_ref
    y1 = peak_ref*feasibility_distance
    # Draw the vertical line in figure coordinates
    x_fig=p_hi*0.95
    '''ax.plot([x_fig, x_fig], [y0, y1],linewidth=1.5, color='black')
    # Caps
    cap_half = p_hi*0.01  # 1% of figure width
    cap_half2 = p_hi*0.005  # 1% of figure width
    ax.plot([x_fig - cap_half, x_fig + cap_half], [y0, y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [2*y0, 2*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [3*y0, 3*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [4*y0, 4*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [5*y0, 5*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [6*y0, 6*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [7*y0, 7*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [8*y0, 8*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [9*y0, 9*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half, x_fig + cap_half], [10*y0, 10*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [20*y0, 20*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [30*y0, 30*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half2, x_fig + cap_half2], [40*y0, 40*y0],linewidth=1.5,color='black')
    ax.plot([x_fig - cap_half, x_fig + cap_half], [y1, y1],linewidth=1.5, color='black')
    # Optional label
    #fig.text(x_fig + 0.01, y_center_fig, f"{feasibility_distance:.0f}", va='center', ha='left', rotation=90)
'''
    sec.set_xlim(nCells/p_hi, nCells/p_lo)
    sec.xaxis.set_inverted(True)
    sec.set_xlabel('cells/device')
    ax.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
    ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=10, loc=(1.05,0.4))
    plt.tight_layout()
    plt.savefig(f"{case_name}{spuma_suffix}.png", dpi=300)
    print(f"Saved FVOPS to {case_name}.png")

    # --- Time per timestep ---
    if args.plot_times:
        fig2,ax2 = plt.subplots(figsize=setfig,dpi=300)
        ax2.set_xscale('log'); ax2.set_xlabel('nDevices')
        for sol in solver_order:
            if sol not in data_dict: continue
            ax2.plot(data_dict[sol]['procs'], data_dict[sol]['times'], marker='x', linestyle='-', label=label_map[sol])
        # SPuMA overlay for time
        for sol in ('PCG','GAMG'):
            if sol in spuma_dict:
                procs_sp = spuma_dict[sol]['procs']; t_sp = spuma_dict[sol]['times']
                clr = ucfdGrey if sol=='PCG' else ucfdBlue
                ax2.plot(procs_sp, t_sp, marker='s', linestyle=':', linewidth=2, color=clr,
                         label=f"SPUMA: GPU ({sol} solver)")
        if args.spuma_json:
            ax2.plot(12, 0.896657806, marker='s',color='r', linestyle='none', label="Comm. ref.")
        ax2.set_yscale('log'); ax2.set_ylabel('Time/timestep [s]')
        sec2 = ax2.twiny()
        sec2.set_xscale('log')
        p_lo, p_hi = ax.get_xlim()          # e.g. [1, 16]
        sec2.set_xlim(nCells/p_hi, nCells/p_lo)
        sec2.xaxis.set_inverted(True)
        sec2.set_xlabel('cells/device')
        ax2.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        ax2.legend(fontsize=10,loc=(1.05,0.5))
        plt.tight_layout()
        plt.savefig(f"{case_name}{spuma_suffix}_times.png", dpi=300)
        print(f"Saved time to {case_name}_times.png")

    # --- Pressure iterations ---
    if args.plot_piter:
        fig3,ax3 = plt.subplots(figsize=setfig,dpi=300)
        ax3.set_xscale('log'); ax3.set_xlabel('nDevices')
        for sol in solver_order:
            if sol not in data_dict: continue
            ax3.plot(data_dict[sol]['procs'], data_dict[sol]['pIter'], marker='^', linestyle='-', label=label_map[sol])
        ax3.set_yscale('log'); ax3.set_ylim((1,5000)); ax3.set_ylabel('Pressure iterations')
        sec3 = ax3.twiny()
        sec3.set_xscale('log')
        p_lo, p_hi = ax.get_xlim()          # e.g. [1, 16]
        sec3.set_xlim(nCells/p_hi, nCells/p_lo)
        sec3.xaxis.set_inverted(True)
        sec3.set_xlabel('cells/device')
        ax3.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        ax3.legend(fontsize=10,loc=(1.05,0.5))
        plt.tight_layout()
        plt.savefig(f"{case_name}_piter.png", dpi=300)
        print(f"Saved pIter to {case_name}_piter.png")

if __name__=='__main__': main()

