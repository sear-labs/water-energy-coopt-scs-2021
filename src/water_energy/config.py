"""Config loading. Scenarios are data, never edits to the model - Part 1, invariant 2."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(scenario: str | None = None) -> dict:
    """Base config, optionally overlaid with scenarios/<scenario>.yaml."""
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    if scenario:
        path = ROOT / "scenarios" / f"{scenario}.yaml"
        if not path.exists():
            avail = sorted(p.stem for p in (ROOT / "scenarios").glob("*.yaml"))
            raise FileNotFoundError(f"no scenario {scenario!r}; available: {avail}")
        for k, v in (yaml.safe_load(path.read_text()) or {}).items():
            cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) else v
    cfg["rainfall_mm"] = {int(k): v for k, v in cfg["rainfall_mm"].items()}
    return cfg
