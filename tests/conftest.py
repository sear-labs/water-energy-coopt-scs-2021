"""Make `src/` importable for the whole suite, once.

Without this the suite passes only by accident of collection order: the first
test module to run `sys.path.insert` leaves it there for every module imported
after it, so a file that does not insert its own passes in the full run and
errors when run alone. Measured 2026-09-11 - tests/test_table_resolution.py did
exactly that.

`pip install -e ".[dev]"` is still the documented path and makes this a no-op.
This exists so a bare clone can run the suite before installing anything.
"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
