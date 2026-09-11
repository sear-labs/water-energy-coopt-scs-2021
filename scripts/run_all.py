#!/usr/bin/env python
"""One command reproduces everything - Part 1, invariant 1.

    python scripts/run_all.py            # base case
    python scripts/run_all.py --scenario discount-10pct-payback-5yr
    python scripts/run_all.py --all      # base case and every scenario

Writes the CLEANED OUTPUT that the rest of the repository reads: one adoption
table and one summary row per scenario, under results/tables/. Those files are
committed, so notebooks/00_verification.ipynb reproduces every published number
with no solver and no licence.
"""
import argparse, csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from water_energy import build, load_config, TECHS, MONTHS, available_scenarios  # noqa: E402
from water_energy import reference as R                                          # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / "results"


def solve(scenario, quiet):
    cfg = load_config(scenario)
    m = build(cfg)
    m.Params.OutputFlag = 0 if quiet else 1
    m.Params.MIPGap = 0.0                # never accept a gap: see README
    m.optimize()
    if m.Status != 2:
        raise SystemExit(f"NOT OPTIMAL - Gurobi status {m.Status}")

    # Domain invariants. These must hold of any correct answer - Part 6.
    V = m._vars
    assert m.ObjVal > 0, "total cost must be positive"
    assert all(V["s"][t].X >= -1e-6 for t in MONTHS), "storage cannot go negative"
    for i in TECHS:
        assert V["y"][i].X <= cfg["households"] + 1e-6, f"{i}: adopters exceed households"
        if V["y"][i].X > 1e-6:
            assert V["y1"][i].X > 0.5, f"{i}: capacity bought without paying the fixed cost"
    return m


def write_tables(m, tag):
    (RESULTS / "tables").mkdir(parents=True, exist_ok=True)
    V = m._vars

    with open(RESULTS / "tables" / f"adoption_{tag}.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["technology", "invest_binary", "households_adopting"])
        for i in TECHS:
            wr.writerow([i, round(V["y1"][i].X), round(V["y"][i].X, 4)])

    with open(RESULTS / "tables" / f"summary_{tag}.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["quantity", "value"])
        for k, v in [
            ("objective", round(m.ObjVal, 4)),
            ("capital_cost", round(m._costs["z1"].getValue(), 4)),
            ("water_cost", round(m._costs["z2"].getValue(), 4)),
            ("energy_cost", round(m._costs["z3"].getValue(), 4)),
            ("rows", m.NumConstrs),
            ("columns", m.NumVars),
            ("binaries", m.NumBinVars),
            ("mip_gap_requested", 0.0),
        ]:
            wr.writerow([k, v])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--all", action="store_true", help="base case and every scenario")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    tags = [None, *available_scenarios()] if args.all else [args.scenario]
    for scenario in tags:
        m = solve(scenario, args.quiet)
        tag = scenario or "base"
        write_tables(m, tag)

        print(f"\nscenario   : {tag}")
        print(f"size       : {m.NumConstrs} rows x {m.NumVars} cols, {m.NumBinVars} binary")
        print(f"objective  : {m.ObjVal:.4f}")
        if scenario is None:
            delta = abs(m.ObjVal - R.GAMS_OBJECTIVE)
            print(f"reference  : {R.GAMS_OBJECTIVE:.4f}  (GAMS/CPLEX)   delta = {delta:.6f}")
            assert delta < R.TOL_OBJECTIVE, f"base case no longer reproduces GAMS: {delta}"
        print(f"wrote      : results/tables/{{adoption,summary}}_{tag}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
