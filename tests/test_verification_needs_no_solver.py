"""The verification path must not import a solver.

Archetype P separates two claims: the verification notebook says *the published
result is correct* and needs no solver and no licence; the example notebook says
*the implementation runs* and needs a free one. A verification claim made in a
file that fails at import for someone without a solver is not licence-free, so
this is the assertion that keeps the two apart.

It runs in a subprocess because import side effects cannot be undone in-process:
once pytest has imported gurobipy for another test, checking sys.modules here
would pass for the wrong reason.
"""
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(body: str):
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(body)],
        cwd=ROOT, capture_output=True, text=True,
    )


def test_importing_the_package_does_not_import_gurobipy():
    r = _run("""
        import sys
        sys.path.insert(0, "src")
        import water_energy
        from water_energy import reference, load_config, TECHS, MONTHS
        load_config()
        assert "gurobipy" not in sys.modules, "importing water_energy pulled in a solver"
        print("OK")
    """)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout + r.stderr


def test_the_cleaned_output_the_notebook_reads_is_committed():
    """A solver-free notebook needs committed numbers to check.

    Without this the verification notebook would pass on a machine that had run
    the model and fail on a clean clone - which is the case the whole committed
    cleaned-output exception exists for.
    """
    tables = ROOT / "results" / "tables"
    required = ["summary_base.csv", "adoption_base.csv"]
    missing = [f for f in required if not (tables / f).exists()]
    assert not missing, f"cleaned output missing: {missing} - run scripts/run_all.py --all"

    tracked = subprocess.run(["git", "ls-files", "results/tables"],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    untracked = [f for f in required if f"results/tables/{f}" not in tracked]
    assert not untracked, (
        f"cleaned output exists but is not committed: {untracked}. "
        "A clean clone would have nothing for the verification notebook to read."
    )


def test_build_is_still_reachable():
    """Laziness must not break the ordinary path."""
    r = _run("""
        import sys
        sys.path.insert(0, "src")
        import water_energy
        assert callable(water_energy.build)
        assert "gurobipy" in sys.modules, "build should have pulled the solver in"
        print("OK")
    """)
    assert r.returncode == 0 and "OK" in r.stdout, r.stdout + r.stderr
