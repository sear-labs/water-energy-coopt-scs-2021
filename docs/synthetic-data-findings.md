# Can a synthetic instance reproduce the published objective?

Measured 2026-09-05, against the real-data proven optimum **1,005,948.1924**.
Acceptance criteria set by Jones: **objective within 1%**, **same technologies selected**.

## Result per input

Each range regenerated in isolation, everything else real:

| Regenerated | Model status | Objective | Deviation | Meets 1%? |
|---|---|---|---|---|
| `Rainfall` | Optimal | 1,005,948.1924 | **0.000%** | yes — it never binds |
| `CapacityFactor` | Optimal | 1,001,398.0494 | **0.452%** | **yes** |
| `HDemand` + `Demand` | **Infeasible** | — | — | **no** |

## Why household demand is different, and it is not a defect in the generator

Take the **real** household values and merely **permute them among houses** within each
(fuel, month). That changes no aggregate, no support, and no marginal distribution — it is the
same multiset of numbers. It solves, and it gives:

    1,051,813.1419      +4.56%

**and it gives exactly that for every random seed tried (7, 11, 23, 42).**

Identical across seeds means the objective is invariant to *which* household holds which value, but
shifts by 4.56% the moment each household's own month-to-month profile is broken. That 4.56% is the
value the model extracts from **within-household temporal structure** — a household that is reliably
heavy justifies an investment that an average household does not.

That structure is exactly the licensed content. So:

> **A synthetic household instance cannot both protect the Pecan Street data and reproduce the
> published objective within 1%.** Destroying the household-level correlation costs 4.56% before any
> synthesis error is added at all. The 1% target is unreachable in principle, not by a wider search.

## Where that leaves it

- `CapacityFactor` and `Rainfall` **can** ship synthetic — verified at 0.45% and 0.00%.
- `HDemand` cannot. Three honest options, in order of preference:
  1. **Ask Pecan Street about this specific matrix.** It is 32 households x 12 **monthly** totals,
     already de-identified to integers — far coarser than their interval product. A narrow request.
  2. **Accept a stated wider tolerance** for the household split — around 5% — and say so in the
     README rather than implying reproduction.
  3. **Ship a synthetic instance labelled as not reproducing the published run**, the arrangement
     `covid-optsc-ffutr-2021` already documents: the schema anticipates real data, the shipped
     instance is synthetic.

## Reproducing this

    python scripts/make_synthetic_inputs.py --real <indata2.xlsx> --out <out.xlsx>

Writes `fitted_parameters.json` beside the output — the fitted aggregates, which are safe to publish,
and the seed. The generator is deterministic given the seed.

### Three failures worth keeping, all silent

1. **Formulas, not values.** `HDemand!E10` is `=HWDemand_input!A2`. Loading without `data_only=True`
   fits nothing and leaves references pointing at sheets the script deletes.
2. **The header is numeric.** Row 10 holds month indices 1..12, so an "all cells numeric" test
   accepts it as data and overwrites it. GDXXRW then reports duplicate month indices three steps
   later. Data starts at row 11.
3. **Support is part of the fit.** An unclamped lognormal put capacity factors above 1.0 and
   household peaks ~30% over the observed maximum. The model went integer infeasible with no
   indication of the cause.

Each of these produced a script that reported success and a workbook that was wrong.
