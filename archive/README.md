# `archive/` — what produced the published result, preserved verbatim

Everything in this directory is **frozen**. It is the record of what the paper actually did, and
its job is to say what happened — not to be right, and not to keep working.

`tests/test_archive_frozen.py` recomputes `MANIFEST.sha256` and fails if any byte here changes.
That test is the reason the rest of the repository can be maintained freely: a correction goes
into `src/water_energy/`, and the divergence gets written down, rather than being applied here
where it would quietly rewrite the history of the result.

| | What it is | Language | Who ran it |
|---|---|---|---|
| `gams-base-model/` | the base household model, unmodified | GAMS | produced the target the Python port reproduces |
| `figures-r/` | the aggregation and plotting behind `figures/` | R | ran once, on data that is not distributable |

## Why the R is archived rather than ported

The repository's rule is one maintained implementation, in Python. That rule is about the
stages a reader has to **re-run**. Nobody re-runs this one:

- It reads `indata1/2/3.xlsx`, sheet `Results` — raw GAMS output from the full co-optimisation
  model, built on restricted Pecan Street–derived inputs that are not distributed here.
- The intermediate it passes between its two halves is `graph_data.RData`, a saved R
  global-environment image, also not distributed.
- Its outputs are in the repository already: the thirteen PDFs in `figures/`.

So porting it would produce a Python program with no inputs, reproducing figures that are
already committed, for a reader who cannot run either version. What a reader can run is
`scripts/make_figures.py`, which draws the reproducible base model from committed cleaned
output.

**This does not excuse the layer's real defects, and they are worth naming** so nobody reads
the archive as an endorsement:

1. It parses the solver's raw report directly rather than a cleaned tier — the pattern that
   silently drops columns when a report's index width varies.
2. It commits no cleaned output of its own; everything lives in the `.RData` image.
3. It is a notebook (`.Rmd`) where a figure stage should be a script.

Those are why the *published* figures are not reproducible from this repository. They are
recorded here and in the root README rather than repaired, because repairing them would mean
editing an archived original.

## Not maintained means not maintained

Do not fix bugs in this directory. If something here is wrong, fix it in `src/water_energy/`
and record the divergence in the root README.
