#!/usr/bin/env python
"""Fit a compact generator to the restricted inputs, then sample a shippable instance.

    python scripts/make_synthetic_inputs.py --real <indata2.xlsx> --out data/raw/indata-synthetic.xlsx

**Why a generator and not a perturbation.** The real workbook carries Pecan Street
licensed data. Adding noise to it produces a derivative of that data. Fitting a small
number of parameters and *sampling* from them produces an instance derived from the
parameters, which are aggregate statistics — roughly 50 numbers per fuel rather than
754x18 of licensed series. Only the parameters are written to `fitted_parameters.json`;
that file is safe to publish and is what makes the synthetic instance reproducible.

The model reads six ranges (per the workbook's own `index` sheet). This script
regenerates the four that carry restricted lineage and leaves the two that are
literature-cited costs alone:

    regenerated   Demand!D5:P7 · Hdemand!C9:P74 · CapacityFactor!C10 · Rainfall!E10:Q754
    untouched     Technologies!B6 · Costs!B5:C32,F4:G32,J5:K32,N5:O32

Unused sheets carrying the same lineage (Demand_kWh, Demand_GAL, the *_input grids and
the 41,043-row Results dump) are deleted outright — nothing reads them.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
from pathlib import Path

import openpyxl

DROP_SHEETS = [
    "Demand_kWh", "Demand_GAL", "Demand_GAL_input", "Demand_kWh_input",
    "capfactor_input", "rainfall_input", "wind_capfactor_input",
    "HEDemand_input", "HWDemand_input", "Results", "indexold",
]


# ----------------------------------------------------------------------- fitting

def fit_hdemand(ws):
    """Per-fuel monthly means, per-house scale factors, and residual spread."""
    rows = []
    for r in range(9, 75):
        fuel, house = ws.cell(r, 3).value, ws.cell(r, 4).value
        if not fuel or house is None:
            continue
        months = [ws.cell(r, c).value for c in range(5, 17)]
        if all(isinstance(v, (int, float)) for v in months):
            rows.append((r, fuel, house, months))
    fuels = sorted({f for _, f, _, _ in rows})
    fit = {}
    for fuel in fuels:
        sub = [(r, h, m) for r, f, h, m in rows if f == fuel]
        monthly = [st.mean([m[i] for _, _, m in sub]) for i in range(12)]
        grand = st.mean(monthly)
        factors = {}
        resid = []
        for _, h, m in sub:
            fac = st.mean(m) / grand
            factors[h] = fac
            for i, v in enumerate(m):
                expected = monthly[i] * fac
                if expected:
                    resid.append(v / expected)
        flat = [v for _, _, m in sub for v in m]
        # Support again. Capacity is sized on the observed peak: measured, an
        # unclamped lognormal put per-house peaks ~30% above the real maximum and
        # the model went INTEGER INFEASIBLE with no indication why.
        fit[fuel] = {
            "monthly_mean": monthly,
            "house_factor": {str(k): round(v, 6) for k, v in factors.items()},
            "residual_cv": round(st.pstdev(resid), 6),
            "observed_min": round(min(flat), 6),
            "observed_max": round(max(flat), 6),
        }
    return fit, rows


def fit_profile(ws, rng, key_cols, n_months):
    """Timeslice x month table: keep the month-mean shape and the within-month spread."""
    cells = list(ws[rng])
    recs = []
    for row in cells:
        keys = [c.value for c in row[:key_cols]]
        vals = [c.value for c in row[key_cols:key_cols + n_months]]
        # A data row must be labelled. Refusing unlabelled rows is what stops a
        # header of numeric month indices being mistaken for data.
        if any(k is None or str(k).strip() == "" for k in keys):
            continue
        if all(isinstance(v, (int, float)) for v in vals):
            recs.append((row, keys, vals))
    if not recs:
        raise ValueError(f"no numeric rows parsed from {rng}")
    groups = {}
    for _, keys, vals in recs:
        groups.setdefault(str(keys[0]), []).append(vals)
    fit = {}
    for g, series in groups.items():
        monthly = [st.mean([s[i] for s in series]) for i in range(n_months)]
        flat = [v for s in series for v in s]
        nz = [v for v in flat if v > 0]
        # The SUPPORT is part of the fit, not a detail. Capacity factors are
        # physically bounded; a lognormal tail that ignores the observed maximum
        # puts a technology above its rating and the model goes integer infeasible.
        # Measured: dropping this produced 368 values >1.0 where the real data has 11.
        fit[g] = {
            "monthly_mean": [round(v, 6) for v in monthly],
            "zero_fraction": round(1 - len(nz) / len(flat), 6) if flat else 0.0,
            "nonzero_cv": round(st.pstdev(nz) / st.mean(nz), 6) if len(nz) > 1 and st.mean(nz) else 0.0,
            "observed_min": round(min(nz), 6) if nz else 0.0,
            "observed_max": round(max(nz), 6) if nz else 0.0,
        }
    return fit, recs


# --------------------------------------------------------------------- sampling

def draw(rng: random.Random, mean: float, cv: float, lo=0.0, hi=None):
    """Lognormal draw with the given mean and coefficient of variation."""
    if mean <= 0 or cv <= 0:
        return mean
    sigma2 = max(1e-12, __import__("math").log(1 + cv * cv))
    sigma = sigma2 ** 0.5
    mu = __import__("math").log(mean) - sigma2 / 2
    v = rng.lognormvariate(mu, sigma)
    v = max(lo, v)
    return min(v, hi) if hi is not None else v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", required=True, help="path to the restricted workbook")
    ap.add_argument("--out", required=True)
    ap.add_argument("--params", default=None, help="where to write fitted_parameters.json")
    ap.add_argument("--seed", type=int, default=20260905)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    # data_only=True yields the CACHED VALUES, not the formulas. The workbook is a
    # web of cross-sheet references - HDemand!E10 is "=HWDemand_input!A2" - so a
    # formula-preserving load would fit nothing (the cells are strings) and would
    # leave references pointing at the *_input sheets this script deletes. Reading
    # values and writing literals removes every dependency, which is also what makes
    # the output safe to ship.
    wb = openpyxl.load_workbook(args.real, data_only=True)
    params = {"seed": args.seed}

    # --- HDemand -------------------------------------------------------------
    ws = wb["HDemand"]
    hfit, hrows = fit_hdemand(ws)
    params["hdemand"] = hfit
    real_month_total = {}
    for _, fuel, _, months in hrows:
        acc = real_month_total.setdefault(fuel, [0.0] * 12)
        for i, v in enumerate(months):
            acc[i] += v
    for fuel, f in hfit.items():
        members = [(r, h) for r, fl, h, _ in hrows if fl == fuel]
        lo, hi = f["observed_min"], f["observed_max"]
        for i in range(12):
            drawn = [draw(rng, f["monthly_mean"][i] * f["house_factor"][str(h)],
                          f["residual_cv"], lo=lo, hi=hi) for _, h in members]
            # Match the REAL monthly aggregate exactly, not merely the mean.
            # The run file fixes every tank and water technology to zero
            # (Purchase.fx(TANK)=0, Purchase.fx(WTECH)=0), so demand is met solely by
            # utility purchases at FIXED capacity. A synthetic month even slightly
            # above the real one is then unservable and the model is INTEGER
            # INFEASIBLE. Measured: month 1 at 578,185 against a real 578,018.
            # Community monthly totals are aggregates, not the sensitive per-household
            # detail, so pinning them costs nothing and buys feasibility.
            target = f["monthly_mean"][i]
            for _ in range(25):
                realised = sum(drawn) / len(drawn)
                if abs(realised - target) <= 0.002 * target:
                    break
                headroom = [j for j, v in enumerate(drawn) if lo < v < hi - 1e-12]
                if not headroom:
                    break
                k = target / realised
                for j in headroom:
                    drawn[j] = min(hi, max(lo, drawn[j] * k))
            # Hit the real monthly aggregate EXACTLY while keeping every household
            # inside the observed [min, max]. Both bind: the aggregate because
            # utility capacity is fixed, the per-house cap because every household
            # technology is fixed to zero, so nothing local can absorb a spike.
            # Scaling alone breaches the cap; clamping alone misses the aggregate.
            # Water-fill instead - the real data satisfies both, so a solution exists.
            real_total = real_month_total[fuel][i]
            for _ in range(200):
                got = sum(drawn)
                gap = real_total - got
                if abs(gap) <= 1e-6 * max(1.0, real_total):
                    break
                movable = [j for j, v in enumerate(drawn)
                           if (gap > 0 and v < hi - 1e-9) or (gap < 0 and v > lo + 1e-9)]
                if not movable:
                    break
                room = sum((hi - drawn[j]) if gap > 0 else (drawn[j] - lo) for j in movable)
                if room <= 0:
                    break
                share = min(1.0, abs(gap) / room)
                for j in movable:
                    head = (hi - drawn[j]) if gap > 0 else (drawn[j] - lo)
                    drawn[j] += share * head * (1 if gap > 0 else -1)
            for (r, _), v in zip(members, drawn):
                ws.cell(r, 5 + i).value = round(min(hi, max(lo, v)), 4)

    # --- aggregate Demand: keep it consistent with the households ------------
    dws = wb["Demand"]
    agg = {}
    for r, fuel, house, _ in hrows:
        for i in range(12):
            agg.setdefault(fuel, [0.0] * 12)[i] += ws.cell(r, 5 + i).value
    # Demand IS the sum of HDemand in the real workbook - 384 x 17,344.5 = 6,660,288
    # against a stated 6,660,292 - and the model enforces that identity. Rescaling the
    # aggregate to preserve the old annual total breaks it by exactly the scale factor
    # and the model goes INTEGER INFEASIBLE, with nothing pointing at the cause.
    # So write the exact sum and let the annual total move.
    drift = {}
    for row in (6, 7):
        label = dws.cell(row, 4).value
        if label in agg:
            before = sum(v for v in (dws.cell(row, 5 + i).value for i in range(12))
                         if isinstance(v, (int, float)))
            for i in range(12):
                dws.cell(row, 5 + i).value = round(agg[label][i], 6)
            after = sum(agg[label])
            drift[label] = round(100 * (after - before) / before, 4) if before else 0.0
    params["aggregate_demand_drift_pct"] = drift

    # --- CapacityFactor and Rainfall ----------------------------------------
    # Ranges start at the first key column: CapacityFactor C=technology, D=timeslice,
    # months from E; Rainfall E=timeslice, months from F.
    for sheet, rngspec, keyc, nm, tag in [
        # Row 10 is the HEADER (month numbers 1..12). Those are numeric, so a naive
        # "all cells numeric" test accepts it as data and overwrites the header -
        # which GDXXRW then reports as duplicate month indices, three steps later.
        # Data starts at row 11.
        ("CapacityFactor", "C11:Q1499", 2, 12, "capacity_factor"),
        ("Rainfall", "E11:Q754", 1, 12, "rainfall"),
    ]:
        w = wb[sheet]
        fit, recs = fit_profile(w, rngspec, keyc, nm)
        params[tag] = fit
        # Draw, then RESCALE each (group, month) to its target mean before writing.
        # Clamping to the observed support truncates the upper tail, which for a
        # heavy-tailed series like rainfall loses real volume - measured: monthly
        # totals fell to roughly two thirds of the observed ones. Rescaling restores
        # the first moment; a second clamp keeps the support intact.
        for g_name, g in fit.items():
            members = [row for row, keys, _ in recs if str(keys[0]) == g_name]
            denom = max(1e-9, 1 - g["zero_fraction"])
            for i in range(nm):
                drawn = []
                for row in members:
                    if rng.random() < g["zero_fraction"]:
                        drawn.append(0.0)
                    else:
                        drawn.append(draw(rng, g["monthly_mean"][i] / denom,
                                          g["nonzero_cv"] or 0.3,
                                          lo=g["observed_min"], hi=g["observed_max"]))
                # Scaling then clamping loses the gain again, so iterate and put the
                # shortfall only on values that are not already at the cap.
                target, cap = g["monthly_mean"][i], g["observed_max"]
                for _ in range(25):
                    realised = sum(drawn) / len(drawn) if drawn else 0.0
                    if realised <= 0 or abs(realised - target) <= 1e-9 + 0.002 * target:
                        break
                    headroom = [j for j, v in enumerate(drawn) if 0 < v < cap - 1e-12]
                    if not headroom:
                        break
                    deficit = (target - realised) * len(drawn)
                    room = sum(cap - drawn[j] for j in headroom)
                    if deficit > 0 and room > 0:
                        share = min(1.0, deficit / room)
                        for j in headroom:
                            drawn[j] = min(cap, drawn[j] + share * (cap - drawn[j]))
                    else:
                        k = target / realised
                        for j in headroom:
                            drawn[j] = min(cap, drawn[j] * k)
                for row, v in zip(members, drawn):
                    row[keyc + i].value = round(v, 6)

    for name in DROP_SHEETS:
        if name in wb.sheetnames:
            del wb[name]

    # Nothing GAMS reads may be left empty. A cell whose cached value was never
    # written comes back None, which GDXXRW reads as a missing entry rather than an
    # error - the silent-empty failure Part 6 warns about.
    holes = []
    for sheet, rows, cols in [("HDemand", range(9, 75), range(5, 17)),
                              ("Demand", range(6, 8), range(5, 17)),
                              ("CapacityFactor", range(10, 1500), range(5, 17)),
                              ("Rainfall", range(10, 755), range(6, 18))]:
        w = wb[sheet]
        for r in rows:
            for c in cols:
                v = w.cell(r, c).value
                if v is not None and not isinstance(v, (int, float)):
                    holes.append(f"{sheet}!{w.cell(r, c).coordinate}={v!r}")
    if holes:
        print(f"  ERROR: {len(holes)} non-numeric cells remain in ranges GAMS reads:")
        for h in holes[:8]:
            print(f"     {h}")
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    pfile = Path(args.params) if args.params else out.with_name("fitted_parameters.json")
    pfile.write_text(json.dumps(params, indent=2))

    print(f"  wrote {out}  ({out.stat().st_size:,} B)")
    print(f"  wrote {pfile}")
    print(f"  sheets kept: {wb.sheetnames}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
