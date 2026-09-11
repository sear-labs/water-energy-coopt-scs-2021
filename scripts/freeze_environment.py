#!/usr/bin/env python
"""Record the resolved environment into requirements-lock.txt.

    python scripts/freeze_environment.py

`pyproject.toml` states ranges - what the code tolerates. This states what actually
ran. Both are needed: a range re-resolved next month installs something else, and a
lock alone tells a reader nothing about what the code will accept.

It walks the dependency closure of this project's own requirements rather than
running `pip freeze`, because the interpreter here is a shared Anaconda install and
a full freeze would record several hundred packages that have nothing to do with
this repository - a record that wide is not a record.
"""
import platform
import sys
from datetime import date
from importlib.metadata import PackageNotFoundError, requires, version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "requirements-lock.txt"

ROOTS = ["gurobipy", "PyYAML", "matplotlib", "pytest", "nbformat", "nbclient"]
MAX_DEPTH = 2

HEADER = """\
# Resolved environment for the run that produced results/ and the executed notebooks.
#
# pyproject.toml states RANGES - what the code tolerates. This states what actually
# ran, which is the other half of Part 1 rule 3.
#
# python      {py} ({impl})
# platform    {plat}
# recorded    {when}
#
# Licences used, because they differ and the distinction matters:
#   results/tables/ and results/figures/   Gurobi academic licence
#   notebooks/*.ipynb, as shipped          Gurobi RESTRICTED licence (pip-bundled),
#                                          expires 2027-11-29
# Both return 30336.4771 for the base case. The notebooks were deliberately executed
# under the restricted licence so their committed output shows what a reader sees.
#
# Regenerate:  python scripts/freeze_environment.py
"""


def closure():
    found = {}

    def walk(name, depth=0):
        key = name.lower().replace("_", "-")
        if key in found:
            return
        try:
            found[key] = version(name)
        except PackageNotFoundError:
            return
        if depth >= MAX_DEPTH:
            return
        for req in requires(name) or []:
            if ";" in req and "extra" in req.split(";", 1)[1]:
                continue
            dep = req.split(";")[0].split("[")[0]
            for sep in (">", "<", "=", "!", "~", " "):
                dep = dep.split(sep)[0]
            if dep:
                walk(dep.strip(), depth + 1)

    for r in ROOTS:
        walk(r)
    return found


def main() -> int:
    pkgs = closure()
    missing = [r for r in ROOTS if r.lower().replace("_", "-") not in pkgs]
    if missing:
        print(f"not installed, so not recorded: {missing}", file=sys.stderr)

    body = HEADER.format(py=platform.python_version(),
                         impl=platform.python_implementation(),
                         plat=platform.platform(),
                         when=date.today().isoformat())
    body += "\n" + "\n".join(f"{n}=={v}" for n, v in sorted(pkgs.items())) + "\n"
    OUT.write_text(body, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(pkgs)} packages, python {platform.python_version()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
