# `archive/` — what produced the published result, preserved verbatim

Everything in this directory is **frozen**. It is the record of what the paper actually did, and
its job is to say what happened — not to be right, and not to keep working.

`tests/test_archive_frozen.py` recomputes `MANIFEST.sha256` and fails if any byte here changes.
That test is the reason the rest of the repository can be maintained freely: a correction goes
into `src/water_energy/`, and the divergence gets written down, rather than being applied here
where it would quietly rewrite the history of the result.

| | What it is | Language | Status |
|---|---|---|---|
| `gams-base-model/` | the base household model, unmodified | GAMS | produced the target the Python port reproduces |
| `figures-r/` | the aggregation and plotting behind `figures/` | R | ran in 2021; re-run 2026-09-11, reproduces the figures |
| `extraction/` | exported the R workspace to committed CSVs | R | ran once, 2026-09-11 |

## Why the R is archived rather than ported

The repository's rule is one maintained implementation, in Python. That rule is about the stages
a **reader** has to re-run, and no reader can re-run this one:

- It reads `indata1/2/3.xlsx`, sheet `Results` — raw GAMS output from the full co-optimisation
  model, built on restricted Pecan Street–derived inputs that are not distributed here.
- The intermediate it passes between its two halves is a saved R workspace image, also not
  distributed.
- Its outputs are in the repository already: the thirteen PDFs in `figures/`, and now the
  aggregate tables in `results/tables/published/`.

So porting it would produce a Python program with no inputs a reader could give it, regenerating
figures that are already committed. What a reader can run is `scripts/make_figures.py`, which
draws the base model from committed cleaned output.

**Be precise about who cannot run it.** A *reader* cannot. The author can, and did — see below.
An earlier draft of this file said it "cannot run for anyone", which was wrong, and wrong in the
direction that flatters the decision.

## It was re-run, and it reproduces the published figures

On 2026-09-11, with R 4.6.1, a scratch copy of `Water_Energy_graphs2.Rmd` was pointed at the
archived workspace image and executed. It exited cleanly and regenerated six of the published
figures — `costs`, `elc_cap`, `emissions`, `prod_elc`, `prod_water`, `water_cap` — matching the
committed PDFs bar for bar and point for point. The only visible difference is legend text
metrics, from ggplot2 4.0.3 rendering differently than the 2021 version did.

**The committed `figures/*.pdf` were left alone.** They are the artifacts of record. Replacing
them with cosmetically different renderings would trade the published images for newer ones and
gain nothing.

**The archived `.Rmd` was not edited to do this**, which is why the freeze test still passes: the
run used a scratch copy with its `load()` path repointed. Anyone repeating it should do the same.

## What this layer does, which is more than plotting

It computes reported quantities — costs, capacity, production, fractions — and in the nine-stage
vocabulary that is stages 6–7, not stage 9. Those quantities are now extracted and committed to
`results/tables/published/`, so the paper's aggregates are checkable without R, GAMS, or the
restricted inputs. `extraction/extract_published_tables.R` is the record of how.

**The layer's real defects are worth naming**, so the archive does not read as an endorsement:

1. It parses the solver's raw report directly rather than a cleaned tier — the pattern that
   silently drops columns when a report's index width varies.
2. It commits no cleaned output of its own; everything lived in the workspace image until it was
   extracted.
3. It is a notebook (`.Rmd`) where a figure stage should be a script.

Those are recorded rather than repaired, because repairing them would mean editing an archived
original.

## Not maintained means not maintained

Do not fix bugs in this directory. If something here is wrong, fix it in `src/water_energy/` and
record the divergence in the root README.
