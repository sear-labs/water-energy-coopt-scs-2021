# Synthetic inputs: what they reproduce, and the tolerance

Acceptance criteria set by Jones: **objective within 5%**, **same technologies selected**.
Reference is the real-data proven optimum **1,005,948.1924** (`optcr = 0`).

## Result

    cd model-gams && gams Water_Energy_Run.gms      # uses data/raw/indata-synthetic.xlsx

The shipped instance is seed **11**. Across four seeds, solved to `optcr = 0`:

| Seed | Objective | Deviation | Technologies vs real |
|---|---|---|---|
| 20260905 | 1,000,636.12 | -0.528% | missing `U_ELC3`, extra `C_BAT` |
| **11 (shipped)** | **1,002,084.10** | **-0.384%** | **all real technologies, extra `C_BAT`** |
| 42 | 1,007,104.82 | +0.115% | missing `U_ELC3`, extra `C_BAT` |
| 777 | 1,001,270.74 | -0.465% | all real technologies, extra `C_BAT` |

**Objective: every seed inside 0.53%**, comfortably within the agreed 5% and in fact within 1%.

**Technologies: not an exact match, and the difference is systematic.** *Every* seed buys a community
battery `C_BAT` that the real instance does not. That is not sampling noise — synthesis slightly
smooths the household profile, which raises the arbitrage value of storage just past its threshold.
Two of four seeds also drop `U_ELC3` (20 units). Seed 11 was chosen because it selects every
technology the real instance does; the extra `C_BAT` remains.

So the second criterion is met **in part**: no real technology is missing, but one extra appears.
Stated plainly rather than rounded off, and it is a property of synthesis here, not of the seed.

Per input, regenerated in isolation:

| Regenerated | Objective | Deviation |
|---|---|---|
| `Rainfall` | 1,005,948.1924 | 0.000% - it never binds |
| `CapacityFactor` | 1,001,398.0494 | +0.452% |

### Reproducing a comparable number

`Water_Energy_Run.gms` ships with the original `optcr = 0.05`, so a default run returns
`MODEL STATUS 8 Integer Solution` - an incumbent inside a 5% band, which is not solver-independent.
**Set `optcr = 0` to compare against the figures above.** The default is left as the paper had it.

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
