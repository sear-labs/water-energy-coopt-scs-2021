"""The acceptance test: the Python port must reproduce the original GAMS answer.

The GAMS run is in archive/gams-base-model/, solved with optcr=0 so the optimum is
proven and therefore solver-independent. A gap-tolerant run would not be a valid
target - a different solver returns a different incumbent inside the band.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from water_energy import build, load_config, available_scenarios, TECHS, MONTHS  # noqa: E402
from water_energy.reference import (                                              # noqa: E402
    GAMS_OBJECTIVE, GAMS_Y1, GAMS_Y, TOL_OBJECTIVE, TOL_SOLUTION,
    GUROBI_LIMITED_LICENCE_CAP, Y1_DETERMINED, Y1_UNDETERMINED,
)

# The reference values and tolerances are imported, never restated here. A
# threshold written out in both a test and a script is a value with copies, and
# the copy is where a correction fails to reach.


@pytest.fixture(scope="module")
def solved():
    m = build(load_config())
    m.Params.OutputFlag = 0
    m.Params.MIPGap = 0.0
    m.optimize()
    assert m.Status == 2, f"expected OPTIMAL, got status {m.Status}"
    return m


def test_objective_matches_gams(solved):
    assert solved.ObjVal == pytest.approx(GAMS_OBJECTIVE, abs=TOL_OBJECTIVE)


def test_investment_decisions_match_gams(solved):
    """Only the binaries the optimum actually determines.

    y1["HGW"] is a free coordinate of the optimal face - see reference.py, where
    the measurement is recorded. Asserting it would be testing which vertex this
    solver happened to return, and would go red on a correct answer elsewhere.
    """
    got = {i: round(solved._vars["y1"][i].X) for i in TECHS}
    for i in Y1_DETERMINED:
        assert got[i] == GAMS_Y1[i], f"{i}: investment decision differs from the published run"


def test_the_undetermined_binary_is_still_undetermined(solved):
    """The degeneracy is asserted, not worked around.

    If a future edit makes HGW's binary load-bearing, this fails and the exclusion
    above stops being correct - which is the point. A documented degeneracy that
    nothing watches is a comment.
    """
    for i in Y1_UNDETERMINED:
        assert solved._vars["y"][i].X == pytest.approx(0.0, abs=TOL_SOLUTION), (
            f"{i} now has adopters, so its binary may be determined - recheck"
        )


def test_buying_capacity_implies_paying_the_fixed_cost(solved):
    """The invariant that holds for every technology, determined or not."""
    for i in TECHS:
        if solved._vars["y"][i].X > TOL_SOLUTION:
            assert solved._vars["y1"][i].X > 0.5, f"{i}: capacity bought without the fixed cost"


def test_adoption_levels_match_gams(solved):
    for i in TECHS:
        assert solved._vars["y"][i].X == pytest.approx(GAMS_Y[i], abs=TOL_SOLUTION), f"tech {i}"


def test_model_fits_gurobi_limited_licence(solved):
    """Small enough for the pip-bundled restricted licence, so a reader can run it.

    A size check is a proxy. The claim was verified by SOLVING under that licence
    on 2026-09-11 - "Restricted license - for non-production use only" in the
    solver log, returning the same optimum - because some licences are enforced
    at optimize() and a declaration-only probe reports success under one that
    then refuses the build.
    """
    cap = GUROBI_LIMITED_LICENCE_CAP
    assert solved.NumConstrs <= cap and solved.NumVars <= cap


def test_domain_invariants(solved):
    V, h = solved._vars, load_config()["households"]
    assert all(V["s"][t].X >= -1e-6 for t in MONTHS)
    assert all(V["e"][t].X >= -1e-6 for t in MONTHS)
    for i in TECHS:
        assert V["y"][i].X <= h + 1e-6
        if V["y"][i].X > 1e-6:
            assert V["y1"][i].X > 0.5


def test_scenarios_load_and_change_the_answer(solved):
    """A scenario must be a config edit, not a code edit - Part 1, invariant 2."""
    m = build(load_config("discount-10pct-payback-5yr"))
    m.Params.OutputFlag = 0
    m.Params.MIPGap = 0.0
    m.optimize()
    assert m.Status == 2
    assert m.ObjVal > solved.ObjVal, "a higher discount rate must not be cheaper"


def test_config_resolves_from_the_package_not_a_repo_root():
    """Guards the published path: config must sit inside the package.

    A root-relative path passes every source-checkout test and fails the moment
    someone pip-installs. This assertion fails in the source tree too if the
    layout regresses, which is the point - see the standard, 'The published path
    is not the path you develop on'.
    """
    from water_energy import config as C
    assert C.CONFIG.exists(), f"{C.CONFIG} missing"
    assert C.CONFIG.parent.name == "water_energy", (
        f"config.yaml must live inside the package, found at {C.CONFIG}"
    )
    assert C.SCENARIOS.parent.name == "water_energy"
    assert available_scenarios(), "no scenarios found - packaging regression"
