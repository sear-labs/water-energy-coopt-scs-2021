# Synthetic inputs: what they reproduce, and the tolerance

Acceptance criteria set by Jones: **objective within 5%**, **same technologies selected**.
Reference is the real-data proven optimum **1,005,948.1924** (`optcr = 0`).

## Result

    python scripts/make_synthetic_inputs.py --real <indata2.xlsx> --out data/raw/indata-synthetic.xlsx

| | |
|---|---|
| Status | **Optimal** |
| Objective | **1,000,636.1195** |
| Deviation | **-0.528%** — inside the 5% tolerance, and inside 1% |
| Technology set | **9 of 10 match** — see below |

Per input, regenerated in isolation:

| Regenerated | Objective | Deviation |
|---|---|---|
| `Rainfall` | 1,005,948.1924 | 0.000% — it never binds |
| `CapacityFactor` | 1,001,398.0494 | +0.452% |
| all four together | 1,000,636.1195 | **-0.528%** |

### The technology difference

| | Real | Synthetic |
|---|---|---|
| shared | `C_PV`, `C_WND`, `U_ELC1`, `U_ELC2`, `U_H2O1`–`U_H2O5` | same |
| only real | `U_ELC3` (20 units) | — |
| only synthetic | — | `C_BAT` (1 unit) |

The synthetic instance buys a community battery instead of the third utility electricity tier. Both
are marginal purchases and the cost difference is half a percent, but **the sets are not identical**,
so the second criterion is met only in part. Stated here rather than rounded off.

## Why the tolerance is 5% and not tighter

Take the **real** household values and merely **permute them among houses** within each fuel-month —
same multiset, same aggregate, same support, same marginals, nothing synthetic. It solves at
**+4.56%**, and gives exactly that for every seed tried (7, 11, 23, 42).

That invariance across seeds is the point: the objective does not care *which* household holds which
value, but moves 4.56% when each household's own month-to-month profile is broken. That 4.56% is what
the model extracts from within-household temporal structure — and that structure is the licensed
content. A tolerance below roughly 5% would therefore be asking the synthetic instance to preserve
the very thing it exists to remove.

## The model is numerically fragile — read this before editing inputs

Three separate perturbations, each mathematically negligible, each making the model **integer
infeasible** with no indication of the cause:

| Change | Result |
|---|---|
| Real values written back unchanged | Optimal, 1,005,948.1924 |
| **The same values rounded to 4 decimal places** | **Integer infeasible** |
| **Aggregate set to the exact household sum** | **Integer infeasible** |

The last one is the trap. The workbook states each monthly aggregate as the household sum **plus
exactly 1.0e-5** — measured at 1.000e-05 across all twelve months and both fuels, so a deliberate
slack, not rounding. The balance is an equality against *fixed* utility capacity
(`Purchase.fx('U_H2O1') = h*b`, with every household water technology fixed to zero), so removing
that slack removes the only feasible margin. `AGGREGATE_SLACK` in the generator preserves it.

Together with the `M = 9,999,999,999,999` big-M documented in the README, this model has real
conditioning problems. Treat any input edit as capable of making it unsolvable.

## Three silent failures found on the way

Each produced a script that reported success and a workbook that was wrong:

1. **Formulas, not values.** `HDemand!E10` is `=HWDemand_input!A2`. Loading without
   `data_only=True` fits nothing and leaves references pointing at sheets the script deletes.
2. **The header is numeric.** Row 10 holds month indices 1..12, so an "all cells numeric" test
   accepts it as data and overwrites it. GDXXRW then reports duplicate month indices three steps
   later. Data starts at row 11.
3. **Support is part of the fit.** An unclamped lognormal put capacity factors above 1.0 and
   household peaks ~30% over the observed maximum.

## What is shipped

`fitted_parameters.json` holds the fitted aggregates and the seed — safe to publish, and what makes
the instance reproducible. The generator is deterministic given the seed. The restricted workbook
itself stays outside version control, at
`University of Texas at Austin\Research\Restricted Data (Pecan Street)\`.
