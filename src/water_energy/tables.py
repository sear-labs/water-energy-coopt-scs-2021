"""Finding the committed cleaned output, from wherever the notebook is running.

`results/tables/` is a path, and a path is true of the development machine. A
notebook opened in Colab has no clone, and `pip install git+...` ships the
package but NOT the repository's `results/` directory - it is not package data
and never enters the wheel.

So the location is resolved once, here, local copy first:

    an explicit argument        a test, or a reader's own copy
    WATER_ENERGY_TABLES         an override that needs no code change
    results/tables beside the   a clone, or an editable install
      package
    results/tables under cwd    a notebook that has chdir'd into place
    the published raw URL       everything else

**The first two are NAMED, and a named location is honoured or refused - never
silently replaced by the next candidate.** Falling through would hand a reader
who pointed at their own edited copy the numbers from the published branch, with
nothing reporting it.

**Local must win**, and that is not a preference. A reader is invited to re-solve
and check the numbers move; if the URL won, their run would be ignored silently
and the notebook would go on reporting the published branch.

No solver is imported here, and none is needed: this module is the whole reason
the verification notebook can make a licence-free claim.
"""
import csv
import os
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
ENV_VAR = "WATER_ENERGY_TABLES"

# A release tag, never `main`. main moves, and a notebook fetching it silently
# changes its answer when somebody edits a table - see the standard, Part 1 rule 8.
PUBLISHED_REF = "v1.0.2"
PUBLISHED_URL = (
    "https://raw.githubusercontent.com/sear-labs/"
    f"water-energy-coopt-scs-2021/{PUBLISHED_REF}/results/tables"
)


def _candidates():
    """The GUESSES only - the two named locations are handled before this."""
    yield HERE.parents[1] / "results" / "tables"      # editable install: src/<pkg>/../..
    yield HERE.parents[2] / "results" / "tables"      # a plain clone
    yield Path.cwd() / "results" / "tables"
    yield Path.cwd().parent / "results" / "tables"    # a notebook run from notebooks/


def table_dir(path=None) -> Path | None:
    """Where the tables are, or None if they must be fetched.

    A named location that does not hold the tables raises rather than falling
    through to the next candidate.
    """
    for named, source in ((path, "the path argument"), (os.environ.get(ENV_VAR), ENV_VAR)):
        if named:
            p = Path(named)
            if not (p / "summary_base.csv").exists():
                raise FileNotFoundError(
                    f"{source} points at {p}, which holds no summary_base.csv. "
                    "A named location is honoured or refused, never silently "
                    "replaced by the published copy - fix the path or unset it."
                )
            return p

    for p in _candidates():
        if (p / "summary_base.csv").exists():
            return p
    return None


def _parse(text, value_column):
    rows = list(csv.DictReader(text.splitlines()))
    key = list(rows[0])[0]
    return {r[key]: r[value_column] for r in rows}


def _read(name, path=None, verbose=True):
    local = table_dir(path)
    if local is not None:
        return (local / name).read_text(encoding="utf-8"), str(local / name)
    url = f"{PUBLISHED_URL}/{name}"
    if verbose:
        print(f"no local results/tables - reading the published copy at {PUBLISHED_REF}\n  {url}")
    with urlopen(url) as fh:                                   # noqa: S310 - fixed https host
        return fh.read().decode("utf-8"), url


def load_summary(tag="base", path=None, verbose=True) -> dict:
    """{quantity: float} for one scenario, from committed cleaned output."""
    text, _ = _read(f"summary_{tag}.csv", path, verbose)
    return {k: float(v) for k, v in _parse(text, "value").items()}


def load_adoption(tag="base", path=None, verbose=True) -> dict:
    """{technology: households adopting} for one scenario."""
    text, _ = _read(f"adoption_{tag}.csv", path, verbose)
    return {k: float(v) for k, v in _parse(text, "households_adopting").items()}


def load_investment(tag="base", path=None, verbose=True) -> dict:
    """{technology: 0 or 1} - whether the fixed cost was paid."""
    text, _ = _read(f"adoption_{tag}.csv", path, verbose)
    return {k: int(v) for k, v in _parse(text, "invest_binary").items()}


def source(path=None) -> str:
    """Human-readable statement of where the numbers came from. Print it."""
    local = table_dir(path)
    return f"local: {local}" if local else f"published: {PUBLISHED_URL}"
