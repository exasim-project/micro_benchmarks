#!/usr/bin/env python3
"""
Unified plotting script with multi-dataset input, flexible time keys/units,
per-study variation grouping, per-study CPU/GPU override, flexible cost mapping
(instance or arbitrary key=value), and per-study hardware layout (GPUs/CPUs
per node, default ranksPerGPU).

All studies passed via --input are plotted together on the same axes:
- Study 1: solid + circle ('-', 'o')
- Study 2: dotted + square (':', 's')
- Study 3: dashdot + x ('-.', 'x')
- Study 4+: fallbacks

Outputs (under --outdir), one combined image per metric:
  - fvops_per_device/       (FVOPS/device)              [y-log]
  - throughput_raw/         (nCells * iter_per_dt / t)
  - cost_ondemand/          ($/TFVO on-demand)          [scaled by 1e12]
  - cost_reserved/          ($/TFVO reserved)           [scaled by 1e12]
  - time_per_timestep/      (seconds per timestep)      [y-log]
  - pressure_iterations/    (p_NoIterations or p_rgh_NoIterations) [y-log]

Usage (example):
  python plot_study.py \
    --input path=/path/A.json,times_key=TimeStep,unit=ms,ndt=120,nPISOCorr=1.5,label="Study A",gpus_per_node=8,cpu_cores_per_node=128,default_ranks_per_gpu=8,variation_key=preconditioner,variation_map="FDIC=OF: CPU\\n(PCG solver),none=OF: CPU\\n(GAMG solver)",cpu_on=0.09,cpu_rsv=0.06,gpu_on=2.8,gpu_rsv=2.1 \
    --input path=/path/B.json,label="Study B",gpus_per_node=4,cpu_cores_per_node=64,study_mode=gpu,variation_key=solverType,variation_map="BJ=OGL: CPU+GPU\\n(Ginkgo CG solver\\n+ Block Jacobi precond.),GKOMG=OGL: CPU+GPU\\n(Ginkgo CG solver\\n+ Multigrid precond.)",gpu_hr_ondemand=3.6,gpu_hr_reserved=2.6 \
    --default-gpu-hr-ondemand 2.74470525 --default-cpu-core-hr-ondemand 0.086953125 \
    --default-gpu-hr-reserved 1.17175    --default-cpu-core-hr-reserved 0.03742 \
    --instance-cost "c8g.48xlarge:cpu:0.087:0.060,H100:gpu:3.60:2.60" \
    --cost-group "preconditioner=FDIC:cpu:0.087:0.060,preconditioner=none:cpu:0.087:0.060" \
    --outdir plots
"""

import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

# ----------------------------------------------------------------------------------------
# (1)   GLOBAL PLOTTING PARAMETERS  (UNCHANGED STYLE)
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
# (2)   Helpers
# ----------------------------------------------------------------------------------------
def _smart_split_commas(s: str):
    """Split on commas, honoring backslash-escaping (\,) to keep commas inside fields."""
    parts, cur, esc = [], [], False
    for ch in s:
        if esc:
            cur.append(ch); esc = False
        elif ch == '\\':
            esc = True
        elif ch == ',':
            parts.append(''.join(cur).strip()); cur = []
        else:
            cur.append(ch)
    parts.append(''.join(cur).strip())
    return [p for p in parts if p]

def _normalize_nl(txt: str) -> str:
    """Accept '\n' and '<br>' as line breaks in CLI strings."""
    return txt.replace("\\n", "\n").replace("<br>", "\n")

def _parse_variation_map(s: str):
    """Plain string map like 'FDIC=Label\\n,none=Label2'. Commas in labels must be escaped as '\\,'."""
    if not s: return {}
    out = {}
    for item in _smart_split_commas(s):
        if '=' not in item:
            continue
        k, v = item.split('=', 1)
        out[k.strip()] = _normalize_nl(v.strip())
    return out

def _parse_variation_map_json_string(s: str):
    """JSON string for {value: label, ...}."""
    data = json.loads(s)
    return {k: _normalize_nl(str(v)) for k, v in data.items()}

def _parse_variation_map_file(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return {k: _normalize_nl(str(v)) for k, v in data.items()}

def _parse_input_spec(s: str):
    """
    Parse one --input spec:
      'path=...[,times_key=clockTimeDelta][,unit=s][,ndt=100][,nPISOCorr=1.0]
               [,label=...][,gpus_per_node=4][,cpu_cores_per_node=76][,default_ranks_per_gpu=19]
               [,variation_key=...]
               [,variation_map=val=Label\\n,val2=Label2\\n,...]    # escape commas in labels as \\\\,
               [,variation_map_json={...}] or [,variation_map_file=/path/to/map.json]
               [,study_mode=cpu|gpu]
               [,cpu_on=...][,cpu_rsv=...][,gpu_on=...][,gpu_rsv=...]
               [,cpu_hr_ondemand=...][,cpu_hr_reserved=...][,gpu_hr_ondemand=...][,gpu_hr_reserved=...]'
    """
    # Known keys for the first-level k=v pairs in --input
    KNOWN = {
        'path','times_key','unit','ndt','nPISOCorr','label',
        'gpus_per_node','cpu_cores_per_node','default_ranks_per_gpu',
        'variation_key','variation_map','variation_map_json','variation_map_file',
        'study_mode',
        # per-study price overrides (short + aliases)
        'cpu_on','cpu_rsv','gpu_on','gpu_rsv',
        'cpu_hr_ondemand','cpu_hr_reserved','gpu_hr_ondemand','gpu_hr_reserved'
    }
    out = {
        'times_key': 'clockTimeDelta',
        'unit': 's',
        'ndt': 100,
        'nPISOCorr': 1.0,
        'gpus_per_node': 4,
        'cpu_cores_per_node': 76,
        'default_ranks_per_gpu': 1,   # kept as in your file
        'study_mode': None,
    }
    vm_extras = []  # collect stray 'key=value' items likely belonging to variation_map

    for part in _smart_split_commas(s):
        if not part or '=' not in part:
            continue
        k, v = part.split('=', 1)
        k = k.strip(); v = v.strip()
        if k in ('ndt','gpus_per_node','cpu_cores_per_node','default_ranks_per_gpu'):
            out[k] = int(v)
        elif k == 'nPISOCorr':
            out[k] = float(v)
        elif k == 'study_mode':
            vv = v.lower()
            if vv not in ('cpu','gpu'):
                raise ValueError("study_mode must be 'cpu' or 'gpu'")
            out[k] = vv
        elif k in ('cpu_on','cpu_rsv','gpu_on','gpu_rsv',
                   'cpu_hr_ondemand','cpu_hr_reserved','gpu_hr_ondemand','gpu_hr_reserved'):
            # store as float; aliases normalized later
            try:
                out[k] = float(v)
            except Exception:
                raise ValueError(f"{k} must be a float, got {v!r}")
        elif k in KNOWN:
            out[k] = v
        else:
            # Unknown top-level key inside --input: treat as a variation_map entry like 'FDIC=...'
            vm_extras.append((k, v))

    if 'path' not in out:
        raise ValueError("Each --input needs at least path=...")
    if out['unit'] not in ('ms','s'):
        raise ValueError("unit must be 'ms' or 's'")

    # Normalize price alias keys to short names if provided
    if 'cpu_hr_ondemand' in out: out['cpu_on'] = out.get('cpu_on', out['cpu_hr_ondemand'])
    if 'cpu_hr_reserved'  in out: out['cpu_rsv'] = out.get('cpu_rsv', out['cpu_hr_reserved'])
    if 'gpu_hr_ondemand' in out: out['gpu_on'] = out.get('gpu_on', out['gpu_hr_ondemand'])
    if 'gpu_hr_reserved'  in out: out['gpu_rsv'] = out.get('gpu_rsv', out['gpu_hr_reserved'])
    out.pop('cpu_hr_ondemand', None)
    out.pop('cpu_hr_reserved', None)
    out.pop('gpu_hr_ondemand', None)
    out.pop('gpu_hr_reserved', None)

    # If user supplied variation_map as plain string, parse it
    var_map_dict = {}
    if 'variation_map' in out:
        var_map_dict = _parse_variation_map(out['variation_map'])
        out.pop('variation_map', None)

    # Merge any stray 'key=value' entries into the variation map dict
    for kk, vv in vm_extras:
        var_map_dict[kk.strip()] = _normalize_nl(vv.strip())

    # If JSON or file is provided, that takes precedence
    if 'variation_map_file' in out:
        var_map_dict = _parse_variation_map_file(out['variation_map_file'])
        out.pop('variation_map_file', None)
    elif 'variation_map_json' in out:
        var_map_dict = _parse_variation_map_json_string(out['variation_map_json'])
        out.pop('variation_map_json', None)

    if var_map_dict:
        out['variation_map_dict'] = var_map_dict

    return out

def _parse_instance_cost(s: str):
    """Parse INST:MODE:ON:RSV entries; MODE in {cpu,gpu}; ON/RSV are per core-hr or per GPU-hr."""
    if not s: return {}
    out = {}
    for item in _smart_split_commas(s):
        inst, mode, on, rsv = item.split(':', 3)
        out[inst.strip()] = (mode.strip().lower(), float(on), float(rsv))
    return out

def _parse_cost_groups(s: str):
    """Parse KEY=VALUE:MODE:ON:RSV entries; MODE in {cpu,gpu}."""
    if not s: return []
    out = []
    for item in _smart_split_commas(s):
        kv, mode, on, rsv = item.split(':', 3)
        key, val = kv.split('=', 1)
        out.append((key.strip(), val.strip(), mode.strip().lower(), float(on), float(rsv)))
    return out

def _ensure_dirs(base, *subs):
    paths = []
    os.makedirs(base, exist_ok=True)
    for sub in subs:
        p = os.path.join(base, sub)
        os.makedirs(p, exist_ok=True)
        paths.append(p)
    return paths

def _apply_cells_per_device_twin(ax, nCells):
    sec = ax.twiny()
    sec.set_xscale('log')
    p_lo, p_hi = ax.get_xlim()
    sec.set_xlim(nCells/p_hi, nCells/p_lo)
    sec.xaxis.set_inverted(True)
    sec.set_xlabel('cells/device')
    return sec

# Color palette identical to rc cycle order (so we can “reset” per study)
_PALETTE = [
    ucfdGrey, ucfdBlue, ucfdLightGreen, ucfdPurple, ucfdOrange,
    ucfdLightBlue, ucfdGreen, '#1f77b4', '#ff7f0e', '#2ca02c',
    '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf'
]

# Per-study linestyle/marker
_STUDY_STYLES = [
    {'linestyle': '-',  'marker': 'o'},  # 1st study
    {'linestyle': ':',  'marker': 's'},  # 2nd study
    {'linestyle': '-.', 'marker': 'x'},  # 3rd study
    {'linestyle': '--', 'marker': '^'},  # 4th
    {'linestyle': (0, (1, 1)), 'marker': 'd'},  # 5th
]

# ----------------------------------------------------------------------------------------
# (3)   Core calculations
# ----------------------------------------------------------------------------------------
def prepare_dataset(
    entries, ndt, nPISOCorr, variation_key,
    default_cpu_on, default_cpu_rs, default_gpu_on, default_gpu_rs,
    instance_cost_map, cost_groups,
    gpus_per_node, cpu_cores_per_node, default_ranks_per_gpu,
    study_mode=None
):
    if not entries:
        return 0, {}, None

    entries = sorted(entries, key=lambda el: int(el['numberOfSubdomains']))
    nCells = entries[0].get('nCells', 0)
    pKey = 'p_NoIterations' if 'p_NoIterations' in entries[0] else 'p_rgh_NoIterations'

    out = {}
    for el in entries:
        var_val = str(el.get(variation_key, ''))
        if var_val not in out:
            out[var_val] = {
                'times':[], 'procs':[], 'nodes':[], 'pIter':[],
                'fvops':[], 'throughput':[],
                'cost_on':[], 'cost_rs':[]
            }

        times = float(el['_times_sec'])  # normalized to seconds at load
        procs = int(el['numberOfSubdomains'])
        ranks_per_gpu = el.get('ranksPerGPU', default_ranks_per_gpu)  # still used for fvops denom

        # Determine nodes: OGL if ranks_per_gpu > 1 or forced study_mode == 'ogl'
        if ranks_per_gpu > 1 or study_mode == 'ogl':
            is_ogl=True
            nodes = procs / (gpus_per_node * ranks_per_gpu)
        else:
            is_ogl=False
            if procs % cpu_cores_per_node == 0 or study_mode == 'cpu':
                # pure CPU run
                nodes = procs / float(cpu_cores_per_node)
            else:
                # pure GPU run
                nodes = procs / float(gpus_per_node)

        pIter = el.get(pKey, 0)
        pimple_count = el.get('PIMPLE_count', 0.5*(ndt-1))
        iter_per_dt = (nPISOCorr * ((pimple_count * 2) / (ndt - 1)))

        fvops = (nCells * iter_per_dt) / (times * (procs / ranks_per_gpu)) if times > 0 and procs > 0 else 0.0
        throughput_raw = (nCells * iter_per_dt) / times if times > 0 else 0.0

        # -------- Pricing resolution (with optional study-wide override) --------
        mode = None; on = rsv = None
        if study_mode in ('cpu','gpu','ogl'):
            mode = 'gpu' if study_mode == 'ogl' else study_mode
            if mode == 'cpu':
                on, rsv = default_cpu_on, default_cpu_rs
            else:
                on, rsv = default_gpu_on, default_gpu_rs
        else:
            instance = el.get('instance')
            if instance and instance in instance_cost_map:
                mode, on, rsv = instance_cost_map[instance]
            else:
                for key, val, m, onf, rsvf in cost_groups:
                    if str(el.get(key)) == val:
                        mode, on, rsv = m, onf, rsvf
                        break
            if mode is None:
                if procs % cpu_cores_per_node == 0 and not is_ogl :
                    mode = 'cpu'; on, rsv = default_cpu_on, default_cpu_rs
                else:
                    mode = 'gpu'; on, rsv = default_gpu_on, default_gpu_rs
        # -----------------------------------------------------------------------
        if iter_per_dt > 0:
            if mode == 'cpu':
                cost_on = ((on/3600) * (times/iter_per_dt) * (cpu_cores_per_node * nodes))/nCells
                cost_rs  = ((rsv/3600) * (times/iter_per_dt) * (cpu_cores_per_node * nodes))/nCells
            else:
                cost_on = ((on/3600) * (times/iter_per_dt) * (gpus_per_node * nodes))/nCells
                cost_rs  = ((rsv/3600) * (times/iter_per_dt) * (gpus_per_node * nodes))/nCells
        else:
            cost_on = cost_rs = 0.0
        # TODO: edge cases where procs divisible by both cores_per_node and gpus_per_node
        d = out[var_val]
        d['times'].append(times)
        d['procs'].append(procs)
        d['nodes'].append(nodes)
        d['pIter'].append(pIter)
        d['fvops'].append(fvops)
        d['throughput'].append(throughput_raw)
        d['cost_on'].append(cost_on)
        d['cost_rs'].append(cost_rs)

    return nCells, out, pKey

# ----------------------------------------------------------------------------------------
# (4)   MAIN
# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='Unified plotting with per-study overrides; combined images; style preserved.')
    ap.add_argument('--input', action='append', required=True,
                    help='path=...[,times_key=clockTimeDelta][,unit=s][,ndt=100][,nPISOCorr=1.0]'
                         '[,label=...][,gpus_per_node=4][,cpu_cores_per_node=76][,default_ranks_per_gpu=19]'
                         '[,variation_key=...][,variation_map=val=Label\\n,...]'
                         '[,variation_map_json={"k":"v"}][,variation_map_file=/path/map.json]'
                         '[,study_mode=cpu|gpu]'
                         '[,cpu_on=...][,cpu_rsv=...][,gpu_on=...][,gpu_rsv=...]'
                         '[,cpu_hr_ondemand=...][,cpu_hr_reserved=...][,gpu_hr_ondemand=...][,gpu_hr_reserved=...]  (repeatable)')
    # Optional global defaults (used if a study does not override)
    ap.add_argument('--variation-key', required=False, default=None)
    ap.add_argument('--variation-map', required=False, default=None,
                    help=r'Comma-separated: val=Label (use \n or <br> for line breaks, escape commas as \,)')

    # Default cost baselines
    ap.add_argument('--default-gpu-hr-ondemand', type=float, default=2.74470525)
    ap.add_argument('--default-cpu-core-hr-ondemand', type=float, default=0.086953125)
    ap.add_argument('--default-gpu-hr-reserved', type=float, default=1.17175)
    ap.add_argument('--default-cpu-core-hr-reserved', type=float, default=0.03742)

    # Overrides
    ap.add_argument('--instance-cost', default=None,
                    help='INST:MODE:ON:RSV[,INST:MODE:ON:RSV...]  MODE in {cpu,gpu}')
    ap.add_argument('--cost-group', default=None,
                    help='KEY=VALUE:MODE:ON:RSV[,KEY=VALUE:MODE:ON:RSV...]')

    ap.add_argument('--y-limits', nargs=2, type=float, metavar=('YMIN','YMAX'))
    ap.add_argument('--outdir', default='plots')
    ap.add_argument('--outname', default='study')

    args = ap.parse_args()

    # Global variation defaults (optional)
    global_var_map = _parse_variation_map(args.variation_map) if args.variation_map else None
    global_var_key = args.variation_key

    instance_cost_map = _parse_instance_cost(args.instance_cost)
    cost_groups = _parse_cost_groups(args.cost_group)
    outname = args.outname

    out_fvops, out_thr, out_cost_on, out_cost_rs, out_tstep, out_piter = _ensure_dirs(
        args.outdir,
        'fvops_per_device', 'throughput_raw', 'cost_ondemand', 'cost_reserved', 'time_per_timestep', 'pressure_iterations'
    )

    # Load all datasets -> list of studies (dicts)
    studies = []
    for spec in args.input:
        cfg = _parse_input_spec(spec)
        path = cfg['path']
        tkey = cfg.get('times_key', 'clockTimeDelta')
        unit = cfg.get('unit', 's')
        ndt = int(cfg.get('ndt', 100))
        nPISOCorr = float(cfg.get('nPISOCorr', 1.0))
        study_label = cfg.get('label')
        gpus_per_node = int(cfg.get('gpus_per_node', 4))
        cpu_cores_per_node = int(cfg.get('cpu_cores_per_node', 76))
        default_ranks_per_gpu = int(cfg.get('default_ranks_per_gpu', 1))
        study_mode = cfg.get('study_mode')

        # Per-study price overrides (fallback to globals)
        cpu_on = float(cfg.get('cpu_on', args.default_cpu_core_hr_ondemand))
        cpu_rsv = float(cfg.get('cpu_rsv', args.default_cpu_core_hr_reserved))
        gpu_on = float(cfg.get('gpu_on', args.default_gpu_hr_ondemand))
        gpu_rsv = float(cfg.get('gpu_rsv', args.default_gpu_hr_reserved))

        # Per-study variation overrides (fallback to globals)
        var_key = cfg.get('variation_key', global_var_key)
        if 'variation_map_dict' in cfg:
            var_map = cfg['variation_map_dict']
        else:
            var_map = global_var_map or {}
        if not var_key:
            raise ValueError("variation_key must be provided globally (--variation-key) or per study (variation_key=...)")
        if not var_map:
            raise ValueError("variation_map must be provided globally (--variation-map) or per study (variation_map=..., variation_map_json=..., or variation_map_file=...)")

        with open(path, 'r') as f:
            arr = json.load(f)
        if not isinstance(arr, list) or not arr:
            print(f"Warning: '{path}' empty or not a list; skipping.")
            continue

        # Normalize times to seconds
        for el in arr:
            val = el.get(tkey, 0.0)
            el['_times_sec'] = (0.001 * float(val)) if unit == 'ms' else float(val)

        case_name = os.path.basename(os.path.dirname(os.path.abspath(path))) or "case"

        nCells, data_dict, pKey = prepare_dataset(
            arr, ndt, nPISOCorr, var_key,
            cpu_on, cpu_rsv, gpu_on, gpu_rsv,                      # <--- per-study prices applied here
            instance_cost_map, cost_groups,
            gpus_per_node, cpu_cores_per_node, default_ranks_per_gpu,
            study_mode=study_mode
        )
        if not data_dict:
            continue

        studies.append({
            'case_name': case_name,
            'nCells': nCells,
            'data': data_dict,
            'pKey': pKey,
            'label': study_label,
            'var_map': var_map
        })

    if not studies:
        print("No valid datasets loaded; nothing to do.")
        return

    # Use nCells of the first study for the twin axis (warn if they differ)
    nCells_ref = studies[0]['nCells']
    if any(s['nCells'] != nCells_ref for s in studies):
        print(f"Note: nCells differ across studies; using nCells={nCells_ref} for the cells/device twin axis.")

    def label_for(var_val, var_map, study_label=None):
        base = var_map.get(var_val, var_val)
        return base + (f"\n[{study_label}]" if study_label else "")

    setfig = (8.8, 4.8)

    # ---- COMBINED plots (one image per metric) ----
    def _plot_combined(y_field, ylabel, x_label, out_dir, scale_1e12=False, ylog=False, ylim=None):
        fig, ax = plt.subplots(figsize=setfig, dpi=300)
        ax.set_xscale('log')
        ax.set_xlabel(x_label)
        ax.set_ylabel(ylabel)
        if ylog: ax.set_yscale('log')
        if ylim: ax.set_ylim(ylim)

        # Plot each study with its own style; reset palette per study
        for s_idx, s in enumerate(studies):
            st = _STUDY_STYLES[s_idx % len(_STUDY_STYLES)]
            palette = _PALETTE  # reset color order per study

            present = set(s['data'].keys())
            ordered_keys = [k for k in s['var_map'].keys() if k in present] + [k for k in present if k not in s['var_map']]

            for i, k in enumerate(ordered_keys):
                series = np.array(s['data'][k][y_field])
                p = np.array(s['data'][k]['procs'])
                color = palette[i % len(palette)]
                y = (1e12 * series) if scale_1e12 else series
                ax.plot(
                    p, y,
                    linestyle=st['linestyle'],
                    marker=st['marker'],
                    linewidth=2.5,
                    color=color,
                    label=label_for(k, s['var_map'], s['label'])
                )

        ax.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        if y_field in ('cost_on','cost_rs','fvops','throughput'):
            ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.legend(fontsize=10, loc=(1.05, 0.3))
        _apply_cells_per_device_twin(ax, nCells_ref)
        plt.tight_layout()
        out_path = os.path.join(out_dir, f"{outname}.png")
        plt.savefig(out_path, dpi=300)
        print(f"Saved to {out_path}")

    # 1) Cost on-demand ($/TFVO) — scaled by 1e12
    _plot_combined('cost_on', 'Cost/TFVO [$] (on-demand)', 'nSubdomains',
                   out_cost_on, scale_1e12=True, ylim=tuple(args.y_limits) if args.y_limits else None)

    # 2) Cost reserved ($/TFVO) — scaled by 1e12
    _plot_combined('cost_rs', 'Cost/TFVO [$] (3yr reserved)', 'nSubdomains',
                   out_cost_rs, scale_1e12=True, ylim=tuple(args.y_limits) if args.y_limits else None)

    # 3) FVOPS per device — log y
    _plot_combined('fvops', 'FVOPS/device [1/s]', 'nSubdomains',
                   out_fvops, ylog=True)

    # 4) Throughput raw
    _plot_combined('throughput', 'Throughput [FVOPS]', 'nSubdomains',
                   out_thr, ylog=True)

    # 5) Time per timestep — log y, x label is nDevices
    _plot_combined('times', 'Time/timestep [s]', 'nDevices',
                   out_tstep, ylog=True)

    # 6) Pressure iterations — log y with fixed ylim, x label is nDevices
    fig_pi, ax_pi = plt.subplots(figsize=setfig, dpi=300)
    ax_pi.set_xscale('log'); ax_pi.set_xlabel('nDevices'); ax_pi.set_ylabel('Pressure iterations')
    ax_pi.set_yscale('log'); ax_pi.set_ylim((1, 5000))
    for s_idx, s in enumerate(studies):
        st = _STUDY_STYLES[s_idx % len(_STUDY_STYLES)]
        palette = _PALETTE
        present = set(s['data'].keys())
        ordered_keys = [k for k in s['var_map'].keys() if k in present] + [k for k in present if k not in s['var_map']]
        for i, k in enumerate(ordered_keys):
            p = np.array(s['data'][k]['procs'])
            y = np.array(s['data'][k]['pIter'])
            color = palette[i % len(palette)]
            ax_pi.plot(p, y, linestyle=st['linestyle'], marker=st['marker'], linewidth=2.5,
                       color=color, label=label_for(k, s['var_map'], s['label']))
    ax_pi.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
    ax_pi.legend(fontsize=10, loc=(1.05, 0.5))
    _apply_cells_per_device_twin(ax_pi, nCells_ref)
    plt.tight_layout()
    out_path = os.path.join(out_piter, f"{outname}.png")
    plt.savefig(out_path, dpi=300)
    print(f"Saved to {out_path}")

if __name__ == '__main__':
    main()

