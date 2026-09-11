# Figure generation (R) — ARCHIVED, not maintained

**Frozen.** `tests/test_archive_frozen.py` fails if any file here changes. See
[`../README.md`](../README.md) for why this layer is archived rather than ported to Python.

The scripts that drew the paper's figures. Moved here from
`yamierick/gradschool-research-code`, where they were the only part of the published pipeline
still living outside a named repository; moved again from `figures-r/` at the repository root
on 2026-09-11, when the archive boundary was made explicit and testable.

**They do not run from a clean clone, and they never will.** They read `graph_data.RData` and
the `indata*.xlsx` scenario workbooks, neither of which is distributed — the workbooks carry
the Pecan Street–derived sheets, and the `.RData` is derived from them.

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
path (`~/Coding/R/Research/Co-Opt Paper/graph_data.RData`) on a machine that no longer exists.

## The one thing still owed

The aggregate tables this produces — cost, capacity, production, PI shares by scenario — should
be extracted once from the real run and committed as CSVs, so a reader can check the published
numbers without R, without GAMS, and without the restricted workbooks. That has **not** been
done: it needs both R and the Pecan Street workbooks, and neither is on the machine this
repository was assembled on. Tracked in the root README under *What is not reproducible here*.
