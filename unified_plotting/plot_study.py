#!/usr/bin/env python3
"""
Unified plotting for multi-study comparisons with per-study variation/cost, figure-specific
overrides, global/per-study color scope, optional skipping of variants, and comparison
metrics (DER, CTSF, TTSF) based on FVOPS max.

Now uses --input as a JSON array of study objects.
Example:

--input '[{
  "path": "postpro_c8gn.json",
  "times_key": "clockTimeDelta",
  "unit": "s",
  "cpu_hr_ondemand": 0.05925,
  "cpu_hr_reserved": 0.01872448,
  "variation_key": "preconditioner",
  "variation_map": {
    "FDIC": "c8gn.48xl<br>(PCG solver)",
    "none": "c8gn.48xl<br>(GAMG solver)"
  },
  "cpu_cores_per_node": 192
},
{
  "path": "postpro_hpc7a_opt_ompi5.json",
  "times_key": "clockTimeDelta",
  "unit": "s",
  "cpu_hr_ondemand": 0.0375,
  "cpu_hr_reserved": 0.017625,
  "variation_key": "preconditioner",
  "variation_map": {
    "FDIC": "hpc7a.96xl<br>(PCG solver)",
    "none": "hpc7a.96xl<br>(GAMG solver)"
  },
  "cpu_cores_per_node": 192
}]'
"""

import os, json, argparse, csv
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

# -------------------- STYLE --------------------
ucfdGrey, ucfdLightGrey = '#626366', '#EFEFF0'
ucfdBlue, ucfdLightBlue = '#1C81AC', '#5BBCE4'
ucfdGreen, ucfdLightGreen = '#206869', '#61BF80'
ucfdPurple, ucfdOrange = '#954F72', '#EAB30E'

plt.rcParams.update({
    'font.size': 16,
    'text.color': ucfdGrey,
    'axes.labelsize': 16,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'lines.markersize': 4,
    'lines.markeredgewidth': 1,
    'lines.linewidth': 2.5,
    'legend.edgecolor': ucfdBlue,
    'axes.edgecolor': ucfdGrey,
    'axes.labelcolor': ucfdGrey,
    'xtick.color': ucfdGrey,
    'ytick.color': ucfdGrey,
    'axes.prop_cycle': cycler('color', [
        ucfdGrey, ucfdBlue, ucfdLightGreen, ucfdPurple, ucfdOrange,
        ucfdLightBlue, ucfdGreen, '#1f77b4', '#ff7f0e', '#2ca02c',
        '#d62728', '#9467bd', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]),
    'grid.color': ucfdLightGrey,
    'grid.alpha': 0.6,
})

_PALETTE = plt.rcParams['axes.prop_cycle'].by_key()['color']
_STYLES = [
    {'linestyle': '-',  'marker': 'o'},
    {'linestyle': ':',  'marker': 's'},
    {'linestyle': '-.', 'marker': 'x'},
    {'linestyle': '--', 'marker': '^'},
    {'linestyle': (0, (1, 1)), 'marker': 'd'},
]

# -------------------- HELPERS --------------------
def _ensure_dirs(base, *subs):
    os.makedirs(base, exist_ok=True)
    paths = []
    for sub in subs:
        p = os.path.join(base, sub)
        os.makedirs(p, exist_ok=True)
        paths.append(p)
    return paths

def _apply_nDevices_twin(ax, nCells,main_label):
    sec = ax.twiny()
    sec.set_xscale('log')
    c_lo, c_hi = ax.get_xlim()
    sec.set_xlim(nCells / c_lo, nCells / c_hi)
    sec.set_xlabel(main_label, color=ucfdGrey)
    sec.tick_params(axis='x', colors=ucfdGrey)
    return sec

def _normalize_key_for_map(key, var_map):
    """Ensure keys like 'none', None, or 'None' normalize and match map keys."""
    if key is None:
        s = 'none'
    else:
        s = str(key).strip()
        if s.lower() == 'none':
            s = 'none'
    if s in var_map:
        return s
    sl = s.lower()
    for mk in var_map.keys():
        if str(mk).strip().lower() == sl:
            return mk
    return s

# -------------------- DATA PREP --------------------
def prepare_dataset(entries, ndt, nPISOCorr, variation_key, var_map,
                    cpu_on, cpu_rsv, gpu_on, gpu_rsv,
                    gpus_per_node, cpu_cores_per_node, default_ranks_per_gpu,
                    study_mode):
    if not entries:
        return 0, {}, None

    entries = sorted(entries, key=lambda e: int(e.get('numberOfSubdomains', 0)))
    nCells = entries[0].get('nCells', 0)
    pKey = (
        'p_NoIterations' if 'p_NoIterations' in entries[0] else
        'p_rgh_NoIterations' if 'p_rgh_NoIterations' in entries[0] else
        'pItersPerDtMean' if 'pItersPerDtMean' in entries[0] else None
    )

    out = {}
    for el in entries:
        var_val_raw = el.get(variation_key, None)
        var_key = _normalize_key_for_map(var_val_raw, var_map)
        if var_key not in out:
            out[var_key] = {
                'cells_per_device': [], 'times': [], 'fvops': [], 'throughput': [],
                'cost_on': [], 'cost_rs': [], 'pIter': [], 'procs': []
            }

        times = float(el['_times_sec'])
        procs = int(el.get('numberOfSubdomains', 0))
        ranks_per_gpu = int(el.get('ranksPerGPU', default_ranks_per_gpu))
        nCells_el = float(el.get('nCells', nCells))

        nodes = procs / (gpus_per_node if study_mode == 'gpu' else cpu_cores_per_node)
        pimple = el.get('PIMPLE_count', 0.5 * (ndt - 1))
        iter_per_dt = (nPISOCorr * ((pimple * 2) / (ndt - 1))) if (ndt - 1) else 0.0

        fvops = (nCells_el * iter_per_dt) / (times * (procs / ranks_per_gpu)) if times > 0 and procs > 0 else 0.0
        throughput = (nCells_el * iter_per_dt) / times if times > 0 else 0.0

        on, rsv = (cpu_on, cpu_rsv) if study_mode == 'cpu' else (gpu_on, gpu_rsv)
        if iter_per_dt > 0:
            denom_n = (cpu_cores_per_node * nodes) if study_mode == 'cpu' else (gpus_per_node * nodes)
            cost_on = ((on / 3600.0) * (times / iter_per_dt) * denom_n) / nCells_el
            cost_rs = ((rsv / 3600.0) * (times / iter_per_dt) * denom_n) / nCells_el
        else:
            cost_on = cost_rs = 0.0

        d = out[var_key]
        d['cells_per_device'].append(nCells_el / procs if procs > 0 else 0.0)
        d['times'].append(times)
        d['fvops'].append(fvops)
        d['throughput'].append(throughput)
        d['cost_on'].append(cost_on)
        d['cost_rs'].append(cost_rs)
        d['pIter'].append(el.get(pKey, 0) if pKey else 0)
        d['procs'].append(procs)

    return nCells, out, pKey

def label_for(var_key, var_map, study_label):
    k = _normalize_key_for_map(var_key, var_map)
    base = var_map.get(k, k)
    return base + (f"\n[{study_label}]" if study_label else "")

# -------------------- MAIN --------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True,
                    help='JSON array of study dicts (each contains path, variation_map, etc.)')
    ap.add_argument('--outdir', default='plots')
    ap.add_argument('--outname', default='study')
    ap.add_argument('--color-scope', choices=['global','per-study'], default='per-study')
    ap.add_argument('--skip', default=None)
    ap.add_argument('--compare-base', default='OF: CPU')
    ap.add_argument('--compare-match', default='c8gn,hpc7a,c7i,H100,H200')
    ap.add_argument('--xlabel-top', default='nDevices')

    for name in ['fvops','throughput','cost_on','cost_rs','times','pIter']:
        ap.add_argument(f'--ylim-{name}', nargs=2, type=float)
        ap.add_argument(f'--ylabel-{name}', default=None)
        ap.add_argument(f'--xlabel-{name}', default=None)

    args = ap.parse_args()
    studies_raw = json.loads(args.input)
    if not isinstance(studies_raw, list):
        raise ValueError("--input must be a JSON list of study objects")

    skip_list = [s.strip() for s in args.skip.split(',')] if args.skip else []
    compare_targets = [s.strip() for s in args.compare_match.split(',')] if args.compare_match else []

    out_fvops, out_thr, out_cost_on, out_cost_rs, out_tstep, out_piter = _ensure_dirs(
        args.outdir, 'fvops_per_device', 'throughput_raw',
        'cost_ondemand', 'cost_reserved', 'time_per_timestep', 'pressure_iterations'
    )

    # ---------- Load datasets ----------
    studies = []
    for spec in studies_raw:
        path = spec['path']
        label = spec.get('label')
        tkey = spec.get('times_key', 'clockTimeDelta')
        unit = spec.get('unit', 's')
        ndt = int(spec.get('ndt', 100))
        nPISOCorr = float(spec.get('nPISOCorr', 1.0))
        cpu_cores_per_node = int(spec.get('cpu_cores_per_node', 76))
        gpus_per_node = int(spec.get('gpus_per_node', 4))
        default_ranks_per_gpu = int(spec.get('default_ranks_per_gpu', 1))
        # auto-detect study mode
        gpu_on = float(spec.get('gpu_hr_ondemand', 0.0) or 0.0)
        gpu_rsv = float(spec.get('gpu_hr_reserved', 0.0) or 0.0)
        cpu_on = float(spec.get('cpu_hr_ondemand', 0.086953125))
        cpu_rsv = float(spec.get('cpu_hr_reserved', 0.03742))
        study_mode = spec.get('study_mode')
        if not study_mode:
            study_mode = 'gpu' if (gpu_on > 0 or gpu_rsv > 0) else 'cpu'
        var_key = spec.get('variation_key', 'preconditioner')
        var_map = spec.get('variation_map', {}) or {}

        with open(path) as f:
            arr = json.load(f)
        for el in arr:
            val = el.get(tkey, 0)
            el['_times_sec'] = (0.001 * float(val)) if unit == 'ms' else float(val)

        nCells, data, pKey = prepare_dataset(
            arr, ndt, nPISOCorr, var_key, var_map,
            cpu_on, cpu_rsv, gpu_on, gpu_rsv,
            gpus_per_node, cpu_cores_per_node, default_ranks_per_gpu,
            study_mode
        )
        studies.append({'nCells': nCells, 'data': data, 'var_map': var_map, 'label': label, 'pKey': pKey})

    if not studies:
        print("No valid datasets loaded.")
        return

    same_case = len({s['nCells'] for s in studies}) == 1
    nCells_ref = studies[0]['nCells']

    def should_skip(lbl):
        return any(x.lower() in lbl.lower() for x in skip_list)

    # ---------- Plot function ----------
    def _plot_combined(y_field, default_ylabel, out_dir, ylog=False, scale_1e12=False):
        ylabel = getattr(args, f'ylabel_{y_field}') or default_ylabel
        xlabel = getattr(args, f'xlabel_{y_field}') or "cells/device"
        xlabel_top = getattr(args, f'xlabel_top') or "nDevices"
        ylim = getattr(args, f'ylim_{y_field}')
        fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=300)
        ax.set_xscale('log'); ax.invert_xaxis()
        if ylog: ax.set_yscale('log')
        if ylim: ax.set_ylim(ylim)
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)

        color_idx = 0
        for s_idx, s in enumerate(studies):
            style = _STYLES[s_idx % len(_STYLES)]
            local_idx = 0
            present = set(s['data'].keys())
            ordered_keys = [k for k in s['var_map'] if k in present] + [k for k in present if k not in s['var_map']]
            for k in ordered_keys:
                v = s['data'][k]
                lbl = label_for(k, s['var_map'], s['label'])
                if should_skip(lbl): continue
                color = (_PALETTE[color_idx % len(_PALETTE)]
                         if args.color_scope == 'global'
                         else _PALETTE[local_idx % len(_PALETTE)])
                x = np.array(v['cells_per_device']); y = np.array(v[y_field]) * (1e12 if scale_1e12 else 1)
                ax.plot(x, y, linestyle=style['linestyle'], marker=style['marker'],
                        color=color, label=lbl)
                color_idx += 1; local_idx += 1

        if same_case: _apply_nDevices_twin(ax, nCells_ref,xlabel_top)
        ax.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.legend(fontsize=10, loc=(1.05, -0.1))
        plt.tight_layout()
        out_png = os.path.join(out_dir, f"{args.outname}_{y_field}.png")
        plt.savefig(out_png, dpi=300)
        print(f"Saved image: {out_png}")

        # CSV output
        csv_path = os.path.join(out_dir, f"{args.outname}_{y_field}.csv")
        with open(csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['label', 'cells_per_device', 'nSubdomains', y_field])
            for s in studies:
                for k, v in s['data'].items():
                    lbl = label_for(k, s['var_map'], s['label'])
                    if should_skip(lbl): continue
                    mult = 1e12 if scale_1e12 else 1.0
                    for xv, pv, yv in zip(v['cells_per_device'], v['procs'], v[y_field]):
                        w.writerow([lbl, xv, pv, yv * mult])
        print(f"Saved table: {csv_path}")

    # ---------- Plots ----------
    _plot_combined('cost_on', 'Cost/TFVO [$] (on-demand)', out_cost_on, scale_1e12=True)
    _plot_combined('cost_rs', 'Cost/TFVO [$] (3yr reserved)', out_cost_rs, scale_1e12=True)
    _plot_combined('fvops', 'FVOPS/device [1/s]', out_fvops, ylog=True)
    _plot_combined('throughput', 'Throughput [FVOPS]', out_thr, ylog=True)
    _plot_combined('times', 'Time/timestep [s]', out_tstep, ylog=True)
    _plot_combined('pIter', 'Pressure iterations', out_piter, ylog=True)

    # ---------- Console output: summary ----------
    all_variants = []
    for s_idx, s in enumerate(studies):
        for k, v in s['data'].items():
            lbl = label_for(k, s['var_map'], s['label'])
            if should_skip(lbl): continue
            p = np.array(v['procs'], dtype=float)
            deff = np.array(v['fvops'], dtype=float)
            ceff = np.array(v['cost_on'], dtype=float)
            thr = np.array(v['throughput'], dtype=float)
            if deff.size == 0: continue
            i_best = int(np.argmax(deff))
            rec = {'lbl': lbl, 'deff': float(np.max(deff)),
                   'ceff': float(1e12 * np.min(ceff)),
                   'teff': float(thr[i_best]),
                   'tmax': float(max(thr)),
                   'best_nSubdomains': int(p[i_best]) if p.size else None}
            all_variants.append(rec)
            print(f"[study {s_idx}] {lbl}\n  Max device eff.: {rec['deff']:.6g}\n"
                  f"  Min cost:        {rec['ceff']:.6g}\n  FVOPS@Eff.:      {rec['teff']:.6g}\n" 
                  f"  nSubdomains:     {rec['best_nSubdomains']}\n"
                  f"  FVOPS max:       {rec['tmax']:.6g}")

    def pick_best(variants, substr):
        cand = [v for v in variants if substr.lower() in v['lbl'].lower()]
        return max(cand, key=lambda v: v['deff']) if cand else None

    base = pick_best(all_variants, args.compare_base)
    if not base:
        print(f"\nNo baseline found matching '{args.compare_base}'\n"); return

    print(f"\nBaseline: {base['lbl']} (deff={base['deff']:.6g}, "
          f"ceff={base['ceff']:.6g}, teff={base['teff']:.6g})\n")
    for m in compare_targets:
        tgt = pick_best(all_variants, m)
        if tgt is None:
            print(f"No target found for '{m}'")
            continue

        DER  = tgt['deff'] / base['deff']
        CTSF = base['ceff'] / tgt['ceff']
        TTSF = tgt['teff'] / base['teff']

        print(f"{m} vs BASE:")
        print(f"  DER   = {DER:.6g}")
        print(f"  CTSF  = {CTSF:.6g}")
        print(f"  TTSF  = {TTSF:.6g}")
        print(f"  Target chosen: {tgt['lbl']} "
              f"(deff={tgt['deff']:.6g}, ceff={tgt['ceff']:.6g}, teff={tgt['teff']:.6g})\n")

if __name__ == "__main__":
    main()