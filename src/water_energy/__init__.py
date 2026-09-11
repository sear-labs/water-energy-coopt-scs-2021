"""Household water-supply technology MILP - Jones (2021), Sust. Cities and Society.

`build` is imported LAZILY. Everything else here - the sets, the config loader,
the published reference values - is importable with no solver installed, which
is what lets notebooks/00_verification.ipynb make a licence-free claim.
"""
from . import reference, tables
from .config import load_config, available_scenarios
from .sets import TECHS, MONTHS, TECH_NAMES

__all__ = ["build", "load_config", "available_scenarios", "reference", "tables",
           "TECHS", "MONTHS", "TECH_NAMES"]


def __getattr__(name):                     # PEP 562: defer the gurobipy import
    if name == "build":
        from .model import build
        return build
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
