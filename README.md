# water-energy-coopt

Household water-supply technology optimisation, behind Jones (2021), *Sustainable Cities and
Society* — [10.1016/j.scs.2020.102515](https://doi.org/10.1016/j.scs.2020.102515).

The repository holds **two models at two scales**, and it matters which one you want.

| | Rows × cols | Solver needed | Status |
|---|---|---|---|
| **`src/water_energy/`** — Python port of the base model | 233 × 214 | **the free licence bundled with `pip install gurobipy`** | reproduces the original exactly |
| **`model-gams/`** — the full co-optimisation model behind the paper | 799,394 × 900,467 | commercial (CPLEX / full Gurobi) | archived; runs, but see *What is not reproducible here* |

## Start here — two notebooks, and neither needs a clone

| | Opens in Colab | Needs | Answers |
|---|---|---|---|
| [`notebooks/00_verification.ipynb`](notebooks/00_verification.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sear-labs/water-energy-coopt-scs-2021/blob/v1.0.0/notebooks/00_verification.ipynb) | **nothing** — no solver, no licence | is the published result correct? |
| [`notebooks/01_example.ipynb`](notebooks/01_example.ipynb) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sear-labs/water-energy-coopt-scs-2021/blob/v1.0.0/notebooks/01_example.ipynb) | a free solver | does the implementation run, and what does it do? |

Both ship **executed**, so you can read every number without running anything.

The two claims are kept apart on purpose. A verification notebook that imports a solver is not
licence-free, however little it uses it, so `00_verification.ipynb` imports none — a test
asserts that. `01_example.ipynb` carries the **whole** base model, not a reduced instance: at
233 × 214 it fits inside the restricted licence that `pip install gurobipy` provides, verified
by solving under that licence rather than by counting variables.

## Quick start, locally

```bash
pip install -e ".[dev]"
pytest                             # 30 tests: reproduction, invariants, the frozen archive
python scripts/run_all.py --all    # solve every scenario, write results/tables/
python scripts/make_figures.py     # draw results/figures/ from those tables - no solver
```

`requirements-lock.txt` records the environment that produced everything committed here;
`pyproject.toml` states the ranges the code tolerates. You need both — a range re-resolved next
month installs something else.

**The config lives inside the package, not at the repository root.** That is deliberate: a
root-relative path passes every source-checkout test and then fails the moment someone
`pip install`s, because `parents[2]` from `site-packages` lands on `Lib/`. Verified by installing
into a clean virtualenv and solving from outside the source tree — the only check that walks a
reader's path.

## What "reproduces exactly" means here

The Python model is a port of `archive/gams-base-model/Project_Modelv4.gms`. The GAMS original
was re-solved with `optcr = 0` **and** `optca = 0` so its optimum is *proven*, not merely within
a tolerance — which is what makes it a valid target for a *different* solver. Both agree:

| | objective | `y1` (invest) | `y` (households adopting) |
|---|---|---|---|
| GAMS 42.5 / CPLEX | 30336.4771 | RWI 1, RWO 1, HGW 1, CGW 1, CSW 0 | 6.4935, 24.4683, 0, 100, 0 |
| Python / gurobipy | **30336.4771** | **identical** | **identical** |

`tests/test_reproduces_gams.py` asserts the objective, the adoption levels, and the investment
decisions **the optimum actually determines** — see *One binary is not determined*, below.

### Why the port has fewer rows than the original

270 × 221 in GAMS against 233 × 214 here, and every row is accounted for:

- **30 duplicate constraints.** `water1(t)` and `iwater1(t)` are declared over `t` but reference
  month `'1'` only, so GAMS generates twelve identical rows of each; likewise `comrestrict1/2(i)`
  over `i`. The port writes one of each.
- **7 accounting equations** (`cost`, `cost1`–`cost3`, `totale`, `fraction1`, `fraction2`) folded
  into the objective expression rather than carried as free variables.

Neither changes the feasible region, which is why the objective and the full solution vector
match.

## Configuration, and the scenarios that used to be comments

The original switched scenarios by commenting and uncommenting parameter blocks, with
`*Have to change manually` beside them. Those are now data:

```bash
python scripts/run_all.py --scenario discount-10pct-payback-5yr
python scripts/run_all.py --scenario discount-5pct-payback-10yr
```

Every parameter lives in `config.yaml`; `scenarios/*.yaml` overlay it. No scenario requires a
code edit.

## Three things a reader should know before trusting a number

**The solver is never given a gap.** `MIPGap = 0.0` throughout. The original shipped with
`optcr = 0.01`, and the large model in `model-gams/` shipped with `optcr = 0.05` — at which
setting it returns 1,009,606.8517, while its proven optimum is **1,005,948.1924**, 0.364% lower.
A tolerance that loose makes the answer solver-dependent and not reproducible. Note that
`optca` must be zeroed too: `optcr` is the relative gap and `optca` the absolute one, and leaving
either at its default lets the solve stop early.

**The big-M is badly scaled.** `investi`/`investo` use `M = 9,999,999,999,999` against Gurobi's
and CPLEX's default integrality tolerance of 1e-5, which in principle admits ~1e8 of flow through
a technology that is switched "off" — four orders of magnitude more than the whole objective. It
does not bite in the base case: the binaries come back at exactly 1 and 0, and
`01_example.ipynb` checks that rather than assuming it. It is inherited from the original and has
not been tightened here, because tightening it would change the model the tests pin. Treat it as
known debt.

**One binary is not determined by the optimum.** `y1["HGW"]` can be 0 or 1 with no effect on the
answer: household technologies are costed on `y` (adopters), not on `y1`, and HGW adopts nobody,
so the variable appears in no cost term and both of its big-M rows have a left-hand side of zero.
Forcing it each way gives 30336.477068 both times, identical to every digit. GAMS returned 1 and
gurobipy returns 1 — agreement by coincidence of vertex choice, not because the model says so. It
is therefore **excluded from the assertions**, with the measurement recorded in
`src/water_energy/reference.py`. Asserting it would be testing which vertex this solver walked to,
and would go red on a correct answer somewhere else.

## Layout

```
notebooks/               00_verification (no solver) - 01_example (free solver)
src/water_energy/        model.py - config.py - tables.py - reference.py
  config.yaml            every parameter; nothing numeric lives in the model code
  scenarios/             overlays - the formerly commented-out discount-rate cases
scripts/run_all.py       solve, assert invariants, write cleaned output
  make_figures.py        draw results/figures/ from that output - no solver
  make_synthetic_inputs.py   regenerate the synthetic instance from a seed
  freeze_archive.py      recompute MANIFEST.sha256
  freeze_environment.py  regenerate requirements-lock.txt
tests/                   reproduction, invariants, the frozen archive, table resolution
results/tables/          COMMITTED cleaned output - what the notebooks read
results/figures/         COMMITTED reproducible figures, from those tables
figures/                 the PUBLISHED figures - not reproducible, see below
archive/                 FROZEN originals: the GAMS base model, and the R that drew figures/
model-gams/              FROZEN: the full co-optimisation model, GAMS source
MANIFEST.sha256          the fingerprint of everything frozen
```

**Two generated things are committed on purpose**, which is rule 5's documented exception:
`results/tables/` because without it nothing in the repository works from a clean clone — the
verification notebook would have no numbers to check — and `results/figures/` plus `figures/` so
a reader without a licence still sees what the prose refers to.

### Exactly one implementation is maintained, and it is Python

`archive/` and `model-gams/` hold the originals, frozen: `tests/test_archive_frozen.py`
recomputes `MANIFEST.sha256` and fails if any byte changes. Corrections go into
`src/water_energy/` and the divergence gets written down, because the original's job is to say
what the paper did, not to be right.

**The R that drew the published figures is archived rather than ported**, and
[`archive/README.md`](archive/README.md) argues why: it reads restricted workbooks that are not
distributed, its intermediate is an R workspace image that is not distributed either, and its
outputs are already committed. Porting it would produce a Python program with no inputs,
regenerating figures that are already here, for a reader who can run neither version. The test
that keeps this honest is `test_only_python_is_maintained`, which fails if non-Python source
appears outside the frozen directories.

## What is not reproducible here, and why

Stated plainly, because a repository that is quiet about this invites a reader to assume more
than it delivers.

**The published figures cannot be regenerated by anyone, including the author.** `figures/*.pdf`
were drawn from the raw output of the full co-optimisation model, run on Pecan Street–derived
inputs. Those inputs are not distributed — the data shipped here is **synthetic**, precisely to
protect that dataset — and the intermediate `graph_data.RData` is derived from them and is not
distributed either. The figures are committed as the published artifacts and the code that drew
them is archived as the record. Neither is a reproducible path, and neither is presented as one.

**The full model's headline numbers are transcribed, not verified here.** 1,005,948.1924 came
from a commercial solver on the real inputs. There is no Python implementation of that model;
the port covers the base model only. `00_verification.ipynb` section 4 records those numbers and
labels them as transcribed.

**The per-scenario aggregates behind the figures are not committed.** The archived R computed
costs, capacity, production, curtailment and the PI shares and persisted them only into its R
workspace. Extracting them once, from the real run, and committing them as CSVs is the one thing
still owed — it needs both R and the restricted workbooks. Until then the paper's aggregates are
not independently checkable from this repository.

**What you can reproduce**: the base model, exactly, from a clean clone, with a free licence —
and the full model's *structure*, by running `model-gams/` against the synthetic instance if you
have GAMS and a commercial solver.

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

Worth reading that error against the gap setting above: replacing every input with synthetic data
cost 0.384%, and the tolerance the original shipped with cost 0.364%. The same order of magnitude.

`scripts/make_synthetic_inputs.py` regenerates it deterministically from a seed;
`data/raw/fitted_parameters.json` holds the fitted aggregates.

### On the underlying data

The original inputs derive from **Pecan Street** household data. Per the author, that data was
already de-identified, and at the time of this work was available to academics on request; the
paywall came later. The shipped instance is in any case **sampled from fitted aggregate
parameters**, not perturbed from the originals, so it does not reproduce any household series.

The original workbooks are **not distributed here** — `.gitignore` blocks every `.xlsx` except the
synthetic one, verified with `git add --dry-run` rather than assumed.

### A warning before editing any input

This model is numerically fragile. Each of these is enough to make it **integer infeasible** with
no indication of the cause:

- rounding input values to 4 decimal places
- setting the monthly aggregate to the *exact* household sum

The workbook states each monthly aggregate as the household sum **plus exactly 1.0e-5** — measured
at 1.000e-05 across all twelve months and both fuels. That slack is deliberate: the balance is an
equality against fixed utility capacity, and removing it removes the only feasible margin.
`AGGREGATE_SLACK` in the generator preserves it.

## Licences

Two, because one is not enough for a repository that ships data.

- **[`LICENSE`](LICENSE)** — MIT. Covers all source: `src/`, `scripts/`, `tests/`, `notebooks/`,
  and the archived originals under `archive/` and `model-gams/`.
- **[`LICENSE-DATA`](LICENSE-DATA)** — CC BY 4.0. Covers the data and the images: `data/raw/`,
  `results/tables/`, `results/figures/`, `figures/`, `docs/`.

MIT speaks about *the Software* and says nothing about a database right, so without the second
file the tables a reader is invited to edit would be the one part of the repository whose terms
were unstated. Neither licence grants any right to the Pecan Street data, which is not here.

## How to cite

Cite the paper. `CITATION.cff` carries both the software and the article.

> Jones, Erick C., Jr. "Co-optimization and community: Maximizing the benefits of distributed
> electricity and water technologies." *Sustainable Cities and Society*, 2021.
> doi:10.1016/j.scs.2020.102515

Note for BibTeX: the suffix is the **middle** field — `author = {Jones, Jr., Erick C.}`.
