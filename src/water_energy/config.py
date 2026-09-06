"""Config loading. Scenarios are data, never edits to the model - Part 1, invariant 2.

Paths resolve relative to THIS MODULE, not to a repository root. A root-relative
path (`parents[2]`) is correct only in a source checkout; installed into
site-packages it lands on `Lib/` and the failure reads like a corrupt download.
The config therefore lives inside the package and ships in the wheel - see the
standard, "The published path is not the path you develop on".
"""
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.yaml"
SCENARIOS = HERE / "scenarios"


def available_scenarios() -> list[str]:
    return sorted(p.stem for p in SCENARIOS.glob("*.yaml"))


def load_config(scenario: str | None = None) -> dict:
    """Base config, optionally overlaid with scenarios/<scenario>.yaml."""
    if not CONFIG.exists():                      # packaging regression, not user error
        raise FileNotFoundError(
            f"{CONFIG} is missing. The package was built without its data files; "
            "check [tool.setuptools.package-data] in pyproject.toml."
        )
    cfg = yaml.safe_load(CONFIG.read_text())
    if scenario:
        path = SCENARIOS / f"{scenario}.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"no scenario {scenario!r}; available: {available_scenarios()}"
            )
        for k, v in (yaml.safe_load(path.read_text()) or {}).items():
            cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) else v
    cfg["rainfall_mm"] = {int(k): v for k, v in cfg["rainfall_mm"].items()}
    return cfg
