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

GAMS_OBJECTIVE = 30336.4771
GAMS_Y1 = {"RWI": 1, "RWO": 1, "HGW": 1, "CGW": 1, "CSW": 0}
GAMS_Y = {"RWI": 6.4935, "RWO": 24.4683, "HGW": 0.0, "CGW": 100.0, "CSW": 0.0}


@pytest.fixture(scope="module")
def solved():
    m = build(load_config())
    m.Params.OutputFlag = 0
    m.Params.MIPGap = 0.0
    m.optimize()
    assert m.Status == 2, f"expected OPTIMAL, got status {m.Status}"
    return m


def test_objective_matches_gams(solved):
    assert solved.ObjVal == pytest.approx(GAMS_OBJECTIVE, abs=1e-3)


def test_investment_decisions_match_gams(solved):
    got = {i: round(solved._vars["y1"][i].X) for i in TECHS}
    assert got == GAMS_Y1


def test_adoption_levels_match_gams(solved):
    for i in TECHS:
        assert solved._vars["y"][i].X == pytest.approx(GAMS_Y[i], abs=1e-3), f"tech {i}"


def test_model_fits_gurobi_limited_licence(solved):
    """<=2000 rows and cols, so a reader without a full licence can still run it."""
    assert solved.NumConstrs <= 2000 and solved.NumVars <= 2000


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
