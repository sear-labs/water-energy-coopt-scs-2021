# Extract the published aggregate tables from the archived R workspace.
#
# ARCHIVED, not maintained, and frozen with everything else under archive/.
# It is here as the record of how results/tables/published/*.csv were produced,
# not as a step anyone re-runs: its input is an R workspace image derived from
# restricted Pecan Street workbooks, and that image is not distributed.
#
# Which is the same test the rest of this directory is archived under - a stage a
# reader must re-run is ported; a stage that ran once and committed its output is
# archived, whatever language it is in.
#
# Run once on 2026-09-11 with R 4.6.1, from the repository root:
#
#     Rscript archive/extraction/extract_published_tables.R
#
# It writes CSVs and nothing else. It does not touch the source workspace, and it
# exports ONLY data frames - the workspace also holds ggplot objects, which carry
# their own copy of the data and would be a second, undiffable copy of it.

SOURCE <- file.path("G:", "My Drive", "School Documents", "Coding", "R",
                    "Research", "Co-Opt Paper", "Water_Energy_graphs2.Rmd.RData")
OUTDIR <- file.path("results", "tables", "published")

if (!file.exists(SOURCE)) {
  stop(paste0("The archived workspace is not on this machine:\n  ", SOURCE,
              "\nIt is not distributed - it derives from the restricted Pecan Street ",
              "workbooks.\nThe tables it produced are already committed under ", OUTDIR,
              ";\nthis script exists to say where they came from, not to be re-run."))
}

e <- new.env()
load(SOURCE, envir = e)
dir.create(OUTDIR, recursive = TRUE, showWarnings = FALSE)

objs <- sort(ls(e))
frames <- objs[sapply(objs, function(n) is.data.frame(get(n, e)))]

written <- 0
for (name in frames) {
  d <- get(name, e)
  if (nrow(d) == 0) {
    cat(sprintf("%-24s skipped, empty\n", name))
    next
  }
  # The production frames carry a column literally named "1" - the single
  # timeslice the annual figures aggregate to. Name it, or a reader has to guess.
  names(d)[names(d) == "1"] <- "Value"
  path <- file.path(OUTDIR, paste0(name, ".csv"))
  write.csv(d, path, row.names = FALSE)
  cat(sprintf("%-24s %5d x %2d -> %s\n", name, nrow(d), ncol(d), path))
  written <- written + 1
}

cat(sprintf("\n%d tables written, %d empty frames skipped, %d non-frame objects ignored\n",
            written, length(frames) - written, length(objs) - length(frames)))
