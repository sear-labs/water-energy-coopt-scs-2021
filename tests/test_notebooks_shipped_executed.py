"""The notebooks ship with their outputs, and their outputs are clean.

A notebook stripped of outputs cannot be checked by a reader without a licence and
twenty minutes, which defeats the point of shipping a verification notebook at all.
So the committed outputs are the artifact, and these assertions guard them.

This does NOT re-execute anything. Re-running the notebooks is a deliberate act -
`python scripts/run_all.py --all` then executing them - because executing on every
test run would quietly re-stamp the committed outputs with whatever licence and
platform happened to be present.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))


def test_there_are_notebooks():
    names = [p.name for p in NOTEBOOKS]
    assert "00_verification.ipynb" in names, "the licence-free verification notebook is missing"
    assert "01_example.ipynb" in names, "the runnable example notebook is missing"


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_is_shipped_executed_and_error_free(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert code_cells, "no code cells"

    errors = [o for c in code_cells for o in c.get("outputs", [])
              if o.get("output_type") == "error"]
    assert not errors, (
        f"{path.name} shipped with {len(errors)} error output(s): "
        f"{[e.get('ename') for e in errors]}"
    )

    # The install cell legitimately produces nothing when the package is present.
    with_output = [c for c in code_cells if c.get("outputs")]
    assert len(with_output) >= len(code_cells) - 2, (
        f"{path.name} looks stripped: only {len(with_output)} of {len(code_cells)} "
        "code cells carry output. Ship it executed."
    )

    assert all(c.get("execution_count") is not None for c in with_output), (
        f"{path.name} has outputs with no execution count - it was edited after running"
    )


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_every_code_cell_has_markdown_above_it(path):
    """No orphan cells: a code cell with nothing explaining it - Part 3."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    kinds = [c["cell_type"] for c in nb["cells"]]
    orphans = [i for i, k in enumerate(kinds)
               if k == "code" and (i == 0 or kinds[i - 1] != "markdown")]
    assert not orphans, f"{path.name}: code cells with no markdown above them at {orphans}"


def test_the_verification_notebook_never_imports_a_solver():
    """Its whole claim is that it does not need one."""
    nb = json.loads((ROOT / "notebooks" / "00_verification.ipynb").read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        assert "import gurobipy" not in src, (
            "00_verification.ipynb imports a solver - its licence-free claim is void"
        )


def test_the_teaching_notebook_ends_with_an_agreement_assertion():
    """Part 4: deliberate duplication with nothing comparing the copies is just duplication."""
    nb = json.loads((ROOT / "notebooks" / "01_example.ipynb").read_text(encoding="utf-8"))
    sources = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    joined = "\n".join(sources)
    assert "from water_energy import build" in joined, "the notebook never imports the package"
    assert "notebook and package disagree" in joined, "no agreement assertion found"


def test_notebook_install_cells_name_a_tag_not_a_branch():
    """A notebook that follows `main` silently changes its answer."""
    for path in NOTEBOOKS:
        src = path.read_text(encoding="utf-8")
        if "pip install" not in src:
            continue
        assert "@v" in src, f"{path.name}: the install line does not pin a release tag"
        assert "@main" not in src, f"{path.name}: the install line follows a branch"
