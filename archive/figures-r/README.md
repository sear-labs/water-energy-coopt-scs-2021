# Figure generation (R) — ARCHIVED, not maintained

**Frozen.** `tests/test_archive_frozen.py` fails if any file here changes. See
[`../README.md`](../README.md) for why this layer is archived rather than ported to Python.

The scripts that drew the paper's figures. Moved here from
`yamierick/gradschool-research-code`, where they were the only part of the published pipeline
still living outside a named repository; moved again from `figures-r/` at the repository root
on 2026-09-11, when the archive boundary was made explicit and testable.

**They do not run from a clean clone, and they never will.** They read a saved R workspace
image and the `indata*.xlsx` scenario workbooks, neither of which is distributed — the workbooks
carry the Pecan Street–derived sheets, and the image is derived from them.

**They do still run for the author**, from a private drive, and on 2026-09-11 they were run:
a scratch copy of `Water_Energy_graphs2.Rmd`, repointed at the workspace image, regenerated six
of the published figures and matched the committed PDFs. See [`../README.md`](../README.md) for
the detail. Nothing in this directory was edited to do it.

| Script | Lines | Draws |
|---|---|---|
| `Water_Energy_graphs.Rmd` | 2,776 | the main cost, capacity, production and emissions figures |
| `Water_Energy_graphs2.Rmd` | 614 | the revised set used in the published version |
| `old graph data.Rmd` | 780 | superseded; kept so nobody rediscovers it and takes it for the current one |

## What it actually does, which is more than plotting

Worth stating, because the folder name says "figures" and the contents are not only figures.
`Water_Energy_graphs.Rmd` reads the raw GAMS output workbook (`indata1/2/3.xlsx`, sheet
`Results`) and derives:

    costs        capacity        prod_elc      prod_water
    frac         curt_elc        curt_water    purchase      demand

plus the electricity and water PI shares — with the whole block copy-pasted once per scenario
(`_1b`, `_10b`, `_100b`, `_3200b`). Those are quantities the paper reports. In the nine-stage
vocabulary this is stages 6–7, clean-up output code and cleaned output, not stage 9.

It persists none of them to a file; `save.image("Co-Op_graphs.RData")` writes the whole R
global environment, and `Water_Energy_graphs2.Rmd` opens by loading that image from an absolute
path, `~/Coding/R/Research/Co-Opt Paper/graph_data.RData`. That path does not resolve on any
current machine, and the file at the other end has since been renamed — the surviving image is
`Water_Energy_graphs2.Rmd.RData`, in that same folder on the author's Drive. An absolute path
plus a rename is why this looked unrunnable for longer than it was.

## The aggregates it computed are now committed

The tables this layer derives — cost, capacity, production and demand fractions, by scenario and
by system configuration — were extracted from the workspace image on 2026-09-11 and committed to
[`results/tables/published/`](../../results/tables/published/). A reader can now check the
paper's aggregates without R, without GAMS, and without the restricted workbooks.

`../extraction/extract_published_tables.R` is the record of how, and is archived for the same
reason this directory is: its input is not distributable, so no reader re-runs it.
