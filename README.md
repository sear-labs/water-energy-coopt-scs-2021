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

## The data situation

**A synthetic instance ships and the model runs from a clean clone.**

```bash
cd model-gams && gams Water_Energy_Run.gms      # uses data/raw/indata-synthetic.xlsx
```

It reproduces the real-data optimum to **-0.384%** (1,002,084.10 against 1,005,948.1924), well
inside the 5% tolerance agreed for it. Every seed tried lands inside 0.53%. It is **not** an exact
technology match: every seed buys one community battery `C_BAT` that the real instance does not,
because synthesis slightly smooths the household profile. Full measurements, including why the
tolerance is 5% and not 1%, are in [`docs/synthetic-data-findings.md`](docs/synthetic-data-findings.md).

`scripts/make_synthetic_inputs.py` regenerates it deterministically from a seed;
`data/raw/fitted_parameters.json` holds the fitted aggregates.

### On the underlying data

The original inputs derive from **Pecan Street** household data. Per the author, that data was
already de-identified, and at the time of this work was available to academics on request; the
paywall came later. The shipped instance is in any case **sampled from fitted aggregate parameters**,
not perturbed from the originals, so it does not reproduce any household series.

The original workbooks are still **not distributed here** — `.gitignore` blocks every `.xlsx` except
the synthetic one, verified with `git add --dry-run` rather than assumed. They live outside version
control at `University of Texas at Austin\Research\Restricted Data (Pecan Street)\`.

### A warning before editing any input

This model is numerically fragile. Each of these is enough to make it **integer infeasible** with no
indication of the cause:

- rounding input values to 4 decimal places
- setting the monthly aggregate to the *exact* household sum

The workbook states each monthly aggregate as the household sum **plus exactly 1.0e-5** - measured at
1.000e-05 across all twelve months and both fuels. That slack is deliberate: the balance is an
equality against fixed utility capacity, and removing it removes the only feasible margin.
`AGGREGATE_SLACK` in the generator preserves it.

## How to cite

Cite the paper. `CITATION.cff` carries both the software and the article.

> Jones, Erick C., Jr. "Co-optimization and community: Maximizing the benefits of distributed
> electricity and water technologies." *Sustainable Cities and Society*, 2021.
> doi:10.1016/j.scs.2020.102515

Note for BibTeX: the suffix is the **middle** field — `author = {Jones, Jr., Erick C.}`.
