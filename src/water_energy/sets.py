"""The model's index sets. Deliberately free of any solver import.

notebooks/00_verification.ipynb must run with no solver and no licence, so
everything it touches - the sets, the reference values, the config loader - has
to be importable without gurobipy. A licence-free claim made in a file that
fails at import for someone without a solver is not licence-free.
"""

TECHS = ["RWI", "RWO", "HGW", "CGW", "CSW"]
MONTHS = list(range(1, 13))

TECH_NAMES = {
    "RWI": "rainwater, indoor",
    "RWO": "rainwater, outdoor",
    "HGW": "household greywater",
    "CGW": "community greywater",
    "CSW": "community stormwater",
}
