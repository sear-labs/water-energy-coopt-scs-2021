"""Where the notebooks get their numbers from - tested by name, not by reasoning.

Part 4 lists five candidate locations and two properties that are easy to state
and easy to get wrong:

    a NAMED location is honoured or refused, never silently replaced
    LOCAL must win, or a reader's edit is ignored in silence

The second is the one that matters for teaching: the notebook invites a reader to
re-solve and watch the numbers move. If the published copy won, their run would be
discarded with nothing reporting it - nothing fails, the reader is simply misled.

No test here touches the network. The URL branch is asserted by construction, not
by fetching: a test that reaches GitHub fails on a train.
"""
import os
from pathlib import Path

import pytest

from water_energy import tables

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "results" / "tables"


def test_local_tables_are_found_from_the_repository():
    assert tables.table_dir() == REAL or tables.table_dir().samefile(REAL)
    assert "local:" in tables.source()


def test_local_wins_over_the_published_copy(tmp_path, monkeypatch):
    """A reader's edited copy must be what the notebook reports."""
    (tmp_path / "summary_base.csv").write_text(
        "quantity,value\nobjective,12345.6789\n", encoding="utf-8")
    got = tables.load_summary("base", path=tmp_path, verbose=False)
    assert got["objective"] == 12345.6789, (
        "an explicitly named copy was ignored - the reader's edit would vanish silently"
    )


def test_a_named_path_that_is_wrong_is_refused_not_replaced(tmp_path):
    with pytest.raises(FileNotFoundError) as e:
        tables.load_summary("base", path=tmp_path / "nowhere", verbose=False)
    assert "honoured or refused" in str(e.value)


def test_the_environment_variable_is_also_named(tmp_path, monkeypatch):
    monkeypatch.setenv(tables.ENV_VAR, str(tmp_path / "nowhere"))
    with pytest.raises(FileNotFoundError):
        tables.load_summary("base", verbose=False)

    (tmp_path / "summary_base.csv").write_text(
        "quantity,value\nobjective,777.0\n", encoding="utf-8")
    monkeypatch.setenv(tables.ENV_VAR, str(tmp_path))
    assert tables.load_summary("base", verbose=False)["objective"] == 777.0


def test_the_argument_beats_the_environment_variable(tmp_path, monkeypatch):
    env, arg = tmp_path / "env", tmp_path / "arg"
    for d, v in ((env, 1.0), (arg, 2.0)):
        d.mkdir()
        (d / "summary_base.csv").write_text(f"quantity,value\nobjective,{v}\n", encoding="utf-8")
    monkeypatch.setenv(tables.ENV_VAR, str(env))
    assert tables.load_summary("base", path=arg, verbose=False)["objective"] == 2.0


def test_the_published_url_names_a_tag_and_not_a_branch():
    """main moves; a notebook fetching it silently changes its answer."""
    assert "/main/" not in tables.PUBLISHED_URL
    assert tables.PUBLISHED_REF.startswith("v")
    assert tables.PUBLISHED_REF in tables.PUBLISHED_URL


def test_the_committed_tables_parse_and_agree_with_the_reference():
    from water_energy.reference import GAMS_OBJECTIVE, GAMS_Y, TOL_OBJECTIVE, TOL_SOLUTION

    s = tables.load_summary("base", verbose=False)
    assert abs(s["objective"] - GAMS_OBJECTIVE) < TOL_OBJECTIVE
    assert abs(s["capital_cost"] + s["water_cost"] + s["energy_cost"] - s["objective"]) < 1e-3

    a = tables.load_adoption("base", verbose=False)
    for tech, expected in GAMS_Y.items():
        assert abs(a[tech] - expected) < TOL_SOLUTION, tech
