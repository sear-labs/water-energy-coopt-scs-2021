#!/usr/bin/env python
"""Regenerate MANIFEST.sha256 - the frozen fingerprint of the published originals.

    python scripts/freeze_archive.py --check      # what the test does; changes nothing
    python scripts/freeze_archive.py --rewrite    # only when ADDING an original

**--rewrite is destructive to the guard, not to the files.** The manifest exists so
that an edit to an archived original turns a test red. Rewriting it makes that red
go green without anything having been fixed, which is the one way this protection
fails. Run it only when a genuinely new original is being added to the archive, and
say so in the commit message.
"""
import argparse, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"

# Both of these produced published numbers and neither is maintained. model-gams/
# sits outside archive/ because a reader with GAMS can still run it against the
# synthetic instance - being runnable is not the same as being maintained.
FROZEN = ("archive", "model-gams")
SKIP_SUFFIXES = {".pyc"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


def content_hash(path: Path) -> str:
    """sha256 of the file with line endings normalised to LF.

    Hashing the bytes on disk is NOT portable, and the failure is invisible until
    someone clones. git stores these blobs with LF and `core.autocrlf` rewrites
    them to CRLF on checkout, so the same commit produces different bytes on
    Windows and Linux - and a freeze test that fails on a clean clone gets
    deleted rather than believed. Measured 2026-09-11: a fresh clone reported two
    archived files CHANGED that nobody had touched.

    A file containing a NUL byte is treated as binary and hashed as-is, since
    normalising those would corrupt the fingerprint rather than stabilise it.
    """
    raw = path.read_bytes()
    if b"\x00" in raw:
        return hashlib.sha256(raw).hexdigest()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def entries():
    for top in FROZEN:
        for p in sorted((ROOT / top).rglob("*")):
            if not p.is_file() or p.suffix in SKIP_SUFFIXES or p.name in SKIP_NAMES:
                continue
            yield p.relative_to(ROOT).as_posix(), content_hash(p)


def render() -> str:
    return "".join(f"{h}  {rel}\n" for rel, h in entries())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rewrite", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    current = render()
    if args.rewrite:
        MANIFEST.write_text(current, encoding="utf-8", newline="\n")
        print(f"rewrote {MANIFEST.name}: {len(current.splitlines())} files")
        return 0

    if not MANIFEST.exists():
        print("MANIFEST.sha256 is missing", file=sys.stderr)
        return 1
    recorded = MANIFEST.read_text(encoding="utf-8")
    if recorded == current:
        print(f"archive intact: {len(current.splitlines())} files")
        return 0

    rec = dict(l.split("  ", 1)[::-1] for l in recorded.splitlines() if l)
    cur = dict(l.split("  ", 1)[::-1] for l in current.splitlines() if l)
    for rel in sorted(set(rec) | set(cur)):
        if rel not in cur:
            print(f"REMOVED  {rel}")
        elif rel not in rec:
            print(f"ADDED    {rel}")
        elif rec[rel] != cur[rel]:
            print(f"CHANGED  {rel}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
