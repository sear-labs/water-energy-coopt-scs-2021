#!/usr/bin/env python
"""One command reproduces everything - Part 1, invariant 1.

    python scripts/run_all.py            # base case
    python scripts/run_all.py --scenario discount-10pct-payback-5yr
"""
import argparse, csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from water_energy import build, load_config, TECHS, MONTHS, available_scenarios          # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / "results"
REFERENCE_OBJECTIVE = 30336.4771        # GAMS/CPLEX, optcr=0, proven optimal


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.scenario)
    m = build(cfg)
    m.Params.OutputFlag = 0 if args.quiet else 1
    m.Params.MIPGap = 0.0                # never accept a gap: see README
    m.optimize()

    if m.Status != 2:
        print(f"NOT OPTIMAL - Gurobi status {m.Status}", file=sys.stderr)
        return 1

    # Domain invariants. These must hold of any correct answer - Part 6.
    V = m._vars
    assert m.ObjVal > 0, "total cost must be positive"
    assert all(V["s"][t].X >= -1e-6 for t in MONTHS), "storage cannot go negative"
    for i in TECHS:
        assert V["y"][i].X <= cfg["households"] + 1e-6, f"{i}: adopters exceed households"
        if V["y"][i].X > 1e-6:
            assert V["y1"][i].X > 0.5, f"{i}: capacity bought without paying the fixed cost"

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "tables").mkdir(exist_ok=True)
    tag = args.scenario or "base"
    with open(RESULTS / "tables" / f"adoption_{tag}.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["technology", "invest_binary", "households_adopting"])
        for i in TECHS:
            wr.writerow([i, round(V["y1"][i].X), round(V["y"][i].X, 4)])

    print(f"\nscenario   : {tag}")
    print(f"size       : {m.NumConstrs} rows x {m.NumVars} cols, {m.NumBinVars} binary")
    print(f"objective  : {m.ObjVal:.4f}")
    if args.scenario is None:
        delta = abs(m.ObjVal - REFERENCE_OBJECTIVE)
        print(f"reference  : {REFERENCE_OBJECTIVE:.4f}  (GAMS/CPLEX)   delta = {delta:.6f}")
    print(f"wrote      : results/tables/adoption_{tag}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
