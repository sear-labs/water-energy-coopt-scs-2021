"""The published reference values, in one place.

Every threshold and every published number in this repository is imported from
here - by `scripts/run_all.py`, by `tests/`, and by both notebooks. That is
deliberate: a tolerance or a reference value written out in two files is a value
with copies, and the copy is where a correction fails to reach. See the standard,
"the agreement assertion protects the models, not the checks".

Nothing in this module is computed. These are transcribed measurements, and the
source of each one is named beside it.
"""

# --- the base household model -------------------------------------------------
# archive/gams-base-model/Project_Modelv4.gms, re-solved under GAMS 42.5 / CPLEX
# with optcr = 0 AND optca = 0, so the optimum is proven rather than accepted
# inside a band. A gap-tolerant run is not a valid target for a different solver.
GAMS_OBJECTIVE = 30336.4771
GAMS_Y1 = {"RWI": 1, "RWO": 1, "HGW": 1, "CGW": 1, "CSW": 0}
GAMS_Y = {"RWI": 6.4935, "RWO": 24.4683, "HGW": 0.0, "CGW": 100.0, "CSW": 0.0}

# NOT every entry of GAMS_Y1 is determined by the optimum, and asserting the ones
# that are not is how a correct answer turns a suite red on someone else's machine.
#
# y1["HGW"] is free. Household technologies are costed on y (adopters), not on y1,
# and HGW adopts nobody: x["HGW"] is fixed to zero and v["HGW"] is capped by
# y["HGW"] = 0, so both big-M rows have a left-hand side of zero and the binary
# appears in no cost term. Measured 2026-09-11 by forcing it both ways:
#
#     forced to 0 -> 30336.477068
#     forced to 1 -> 30336.477068
#
# Identical to every digit. GAMS returned 1 and gurobipy returns 1, which is
# agreement by coincidence of vertex choice, not by the model determining it.
Y1_DETERMINED = ("RWI", "RWO", "CGW", "CSW")
Y1_UNDETERMINED = ("HGW",)

# The GAMS report writer emitted four decimal places, so 1e-3 is what the
# RECORDED VALUE supports - it is not a statement about the solve, which is
# exact (MIPGap = 0). Tightening this asserts precision the reference does not
# carry; loosening it would admit a real disagreement.
TOL_OBJECTIVE = 1e-3
TOL_SOLUTION = 1e-3

# --- the full co-optimisation model (model-gams/) -----------------------------
# Not reimplemented in Python: 799,394 x 900,467, commercial solver only.
# These are the published-side numbers, recorded so the README and the
# verification notebook cannot drift from each other.
FULL_MODEL_PROVEN_OPTIMUM = 1005948.1924      # optcr = 0, optca = 0
FULL_MODEL_AT_OPTCR_05 = 1009606.8517         # as the original shipped, optcr = 0.05
FULL_MODEL_SYNTHETIC = 1002084.10             # synthetic instance, seed as shipped

# Agreed before the synthetic instance was built; docs/synthetic-data-findings.md
# records why 1% is unreachable and 5% is the honest figure.
TOL_SYNTHETIC_RELATIVE = 0.05

# --- what a reader's environment must provide ---------------------------------
# Verified by SOLVING under the pip-bundled restricted licence on 2026-09-11,
# not by counting declared variables - the standard requires the former because
# some licences are enforced at optimize().
GUROBI_LIMITED_LICENCE_CAP = 2000


def full_model_synthetic_error() -> float:
    """Signed relative error of the synthetic instance against the real optimum."""
    return (FULL_MODEL_SYNTHETIC - FULL_MODEL_PROVEN_OPTIMUM) / FULL_MODEL_PROVEN_OPTIMUM


def full_model_gap_cost() -> float:
    """Relative penalty the original's optcr = 0.05 accepted."""
    return (FULL_MODEL_AT_OPTCR_05 - FULL_MODEL_PROVEN_OPTIMUM) / FULL_MODEL_PROVEN_OPTIMUM
