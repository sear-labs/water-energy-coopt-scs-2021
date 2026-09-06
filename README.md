# water-energy-coopt

Household water-supply technology optimisation, behind Jones (2021), *Sustainable Cities and
Society* — [10.1016/j.scs.2020.102515](https://doi.org/10.1016/j.scs.2020.102515).

The repository holds **two models at two scales**, and it matters which one you want.

| | Rows × cols | Solver needed | Status |
|---|---|---|---|
| **`src/water_energy/`** — Python port of the base model | 233 × 214 | **Gurobi limited licence is enough** | reproduces the original exactly |
| **`model-gams/`** — the full co-optimisation model behind the paper | 799,394 × 900,467 | commercial (CPLEX / full Gurobi) | runs; **input workbooks not distributable**, see below |

## Quick start

```bash
pip install -e ".[dev]"
python scripts/run_all.py          # solves, checks invariants, writes results/tables/
pytest                             # the acceptance test against the original GAMS answer
```

**The config lives inside the package, not at the repository root.** That is deliberate: a
root-relative path passes every source-checkout test and then fails the moment someone
`pip install`s, because `parents[2]` from `site-packages` lands on `Lib/`. Verified by installing
into a clean virtualenv and solving from outside the source tree — the only check that walks a
reader's path.

## What "reproduces exactly" means here

The Python model is a port of `archive/gams-base-model/Project_Modelv4.gms`. The GAMS original was
re-solved with `optcr = 0` so its optimum is **proven**, not merely within a tolerance — which is
what makes it a valid target for a *different* solver. Both agree:

| | objective | `y1` (invest) | `y` (households adopting) |
|---|---|---|---|
| GAMS 42.5 / CPLEX | 30336.4771 | RWI 1, RWO 1, HGW 1, CGW 1, CSW 0 | 6.4935, 24.4683, 0, 100, 0 |
| Python / gurobipy | **30336.4771** | **identical** | **identical** |

`tests/test_reproduces_gams.py` asserts all three. It fails if a future edit changes the answer.

### Why the port has fewer rows than the original

270 × 221 in GAMS against 233 × 214 here, and every row is accounted for:

- **30 duplicate constraints.** `water1(t)` and `iwater1(t)` are declared over `t` but reference
  month `'1'` only, so GAMS generates twelve identical rows of each; likewise `comrestrict1/2(i)`
  over `i`. The port writes one of each.
- **7 accounting equations** (`cost`, `cost1`–`cost3`, `totale`, `fraction1`, `fraction2`) folded
  into the objective expression rather than carried as free variables.

Neither changes the feasible region, which is why the objective and the full solution vector match.

## Configuration, and the scenarios that used to be comments

The original switched scenarios by commenting and uncommenting parameter blocks, with
`*Have to change manually` beside them. Those are now data:

```bash
python scripts/run_all.py --scenario discount-10pct-payback-5yr
python scripts/run_all.py --scenario discount-5pct-payback-10yr
```

Every parameter lives in `config.yaml`; `scenarios/*.yaml` overlay it. No scenario requires a code edit.

## Two things a reader should know before trusting a number

**The solver is never given a gap.** `MIPGap = 0.0` throughout. The original shipped with
`optcr = 0.01`, and the large model in `model-gams/` shipped with `optcr = 0.05` — at which setting it
returns 1,009,606.8517, while its proven optimum is **1,005,948.1924**, 0.364% lower. A tolerance that
loose makes the answer solver-dependent and not reproducible.

**The big-M is badly scaled.** `investi`/`investo` use `M = 9,999,999,999,999` against Gurobi's and
CPLEX's default integrality tolerance of 1e-5, which in principle admits ~1e8 of flow through a
technology that is switched "off". It does not bite in the base case — the binaries come back clean
at 1/0, verified — but it is inherited from the original and has not been tightened here, because
tightening it would change the model the tests pin. Treat it as known debt.

## Layout

```
src/water_energy/        model.py (the model) - config.py (loading)
  config.yaml            every parameter; nothing numeric lives in the model code
  scenarios/             overlays - the formerly commented-out discount-rate cases
scripts/run_all.py       one command: solve, assert invariants, write results
tests/                   the acceptance test against GAMS, plus domain invariants
model-gams/              the full co-optimisation model, GAMS source (see below)
archive/gams-base-model/ the original .gms, unmodified, as the port's reference
results/                 generated - gitignored
```

## The input data is not in this repository

`model-gams/` needs `indata1.xlsx`–`indata3.xlsx`. **They are not distributed here.** They carry
`Demand_kWh`, `CapacityFactor` and `Rainfall` sheets derived from **Pecan Street** data, which is
licensed and not ours to redistribute — and unlike elsewhere in this project these sheets are
load-bearing: the model's own index sheet reads `Rainfall!E10:Q754`, `CapacityFactor!C10` and
`Hdemand!C9:P74`.

So `model-gams/` is **source you can read and audit, not a runnable artefact**, until that licence
question is settled. The originals sit outside version control at
`Documents\gamsdir\projdir\Water Energy CoOp\`.

The Python model in `src/` has no such dependency — every input is in `config.yaml`, and it runs
from a clean clone.

## How to cite

Cite the paper. `CITATION.cff` carries both the software and the article.

> Jones, Erick C., Jr. "Co-optimization and community: Maximizing the benefits of distributed
> electricity and water technologies." *Sustainable Cities and Society*, 2021.
> doi:10.1016/j.scs.2020.102515

Note for BibTeX: the suffix is the **middle** field — `author = {Jones, Jr., Erick C.}`.
