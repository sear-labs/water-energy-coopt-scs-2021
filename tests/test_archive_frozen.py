"""The archived originals are frozen, and Python is the only maintained language.

Archetype P keeps a preserved original and a maintained implementation in one
repository. What makes that safe is a test that fails when the archived half
changes - without it, "archived" is a claim in a README rather than a property
of the tree.

The work here is finished (published 2021), so FROZEN is the right assertion.
For active research it would be wrong: the original would still be the working
copy, and a test that fires on correct behaviour gets deleted, taking the
boundary with it.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_DIRS = ("archive", "model-gams")

# Languages that are allowed to exist only inside a frozen directory. Anything
# maintained is Python - see archive/README.md for why the R is archived rather
# than ported, and the root README for the one Python figure path a reader runs.
ARCHIVED_ONLY_SUFFIXES = {".gms", ".r", ".rmd", ".rdata", ".sas", ".m", ".do"}

# Directories that hold no source at all.
IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache", ".ipynb_checkpoints",
                 "build", "dist", ".venv", "venv"}


def _tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, f"git ls-files failed: {out.stderr}"
    return [Path(line) for line in out.stdout.splitlines() if line]


def test_archive_matches_its_manifest():
    """Recompute every hash. Fails on an edit, an addition or a deletion."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "freeze_archive.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "the archived originals no longer match MANIFEST.sha256:\n"
        f"{result.stdout}{result.stderr}\n"
        "An archived original is never edited. Fix it in src/water_energy/ and "
        "record the divergence; rewrite the manifest only to ADD an original."
    )


def test_only_python_is_maintained():
    """No non-Python source outside the frozen directories.

    The test is the stage, not the file: a stage a reader must re-run is Python;
    a stage that ran once and committed its output is archived, whatever language
    it is in. This asserts the second half - that nothing in another language has
    crept back into the maintained tree.
    """
    strays = []
    for rel in _tracked_files():
        if set(rel.parts) & IGNORED_PARTS or rel.parts[0] in FROZEN_DIRS:
            continue
        if rel.suffix.lower() in ARCHIVED_ONLY_SUFFIXES:
            strays.append(rel.as_posix())
    assert not strays, (
        "non-Python source outside the frozen directories: "
        f"{strays}. Either it is maintained, in which case port it, or it is "
        "an original, in which case move it under archive/ and re-freeze."
    )


def test_the_archived_gams_original_is_still_there():
    """A frozen manifest of an empty directory passes. Name what must exist."""
    must_exist = [
        "archive/gams-base-model/Project_Modelv4.gms",
        "archive/figures-r/Water_Energy_graphs.Rmd",
        "model-gams/Water_Energy_Model_mod.gms",
    ]
    missing = [p for p in must_exist if not (ROOT / p).exists()]
    assert not missing, f"archived originals missing: {missing}"
