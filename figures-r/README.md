# Figure generation (R)

The scripts that draw the paper's figures. Moved here from `yamierick/gradschool-research-code`,
where they were the only part of the published pipeline still living outside a named repository.

**They do not run from a clean clone.** They read `graph_data.RData` and the `indata*.xlsx`
scenario workbooks, neither of which is distributed — the workbooks carry the Pecan Street–derived
sheets, and the `.RData` is derived from them. The scripts are here as the record of how
`figures/` was produced, and to be read alongside it.

| Script | Draws |
|---|---|
| `Water_Energy_graphs.Rmd` | the main cost, capacity, production and emissions figures |
| `Water_Energy_graphs2.Rmd` | the revised set used in the published version |
| `old graph data.Rmd` | superseded; kept so nobody rediscovers it and takes it for the current one |

Making these runnable would mean pointing them at `data/raw/indata-synthetic.xlsx` and regenerating
`graph_data.RData` from it — the same treatment the model got. Not done yet.
