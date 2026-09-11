#!/usr/bin/env python
"""Draw the reproducible figures from committed cleaned output. No solver needed.

    python scripts/make_figures.py

Reads results/tables/*.csv - which are committed - and writes results/figures/*.png.
It never re-solves and never touches the raw solver report: a figure that parses a
solver's own output is re-implementing the clean-up stage, and the second copy is
the one that drifts.

These are NOT the paper's figures. figures/*.pdf are the published co-optimisation
results, drawn by archive/figures-r/ from restricted inputs that are not
distributed. These show the base household model, which is the part of this
repository a reader can actually run. Every image says so on its face, because a
chart gets screenshotted into a slide and a caption does not follow it.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                        # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from water_energy import TECHS, TECH_NAMES                             # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"

STAMP = ("base household model (233 x 214) - NOT the published "
         "co-optimisation result; see figures/ for those")
LABELS = {"base": "base", "discount-10pct-payback-5yr": "10% discount\n5yr payback",
          "discount-5pct-payback-10yr": "5% discount\n10yr payback"}


def read_summary(tag):
    with open(TABLES / f"summary_{tag}.csv", newline="") as fh:
        return {r["quantity"]: float(r["value"]) for r in csv.DictReader(fh)}


def read_adoption(tag):
    with open(TABLES / f"adoption_{tag}.csv", newline="") as fh:
        return {r["technology"]: float(r["households_adopting"]) for r in csv.DictReader(fh)}


def stamp(fig):
    fig.text(0.5, 0.005, STAMP, ha="center", va="bottom", fontsize=7.5, color="#555")


def tags():
    found = sorted(p.stem[len("summary_"):] for p in TABLES.glob("summary_*.csv"))
    if not found:
        raise SystemExit(
            "no cleaned output in results/tables/. These files are committed, so an "
            "empty directory means the clone is broken, not that you need to solve. "
            "If you have a licence: python scripts/run_all.py --all"
        )
    return ["base"] + [t for t in found if t != "base"]


def cost_figure(order):
    parts = [("capital_cost", "capital"), ("water_cost", "water"), ("energy_cost", "energy")]
    summaries = [read_summary(t) for t in order]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bottom = [0.0] * len(order)
    for key, label in parts:
        vals = [s[key] for s in summaries]
        ax.bar([LABELS.get(t, t) for t in order], vals, bottom=bottom, label=label)
        bottom = [b + v for b, v in zip(bottom, vals)]

    for x, total in enumerate(bottom):
        ax.text(x, total, f"{total:,.0f}", ha="center", va="bottom", fontsize=9)

    ax.set_ylabel("annualised cost")
    ax.set_title("Cost by component, base household model")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(y=0.15)
    stamp(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def adoption_figure(order):
    adoptions = [read_adoption(t) for t in order]
    width = 0.8 / len(order)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for k, (tag, a) in enumerate(zip(order, adoptions)):
        xs = [i + k * width for i in range(len(TECHS))]
        ax.bar(xs, [a[t] for t in TECHS], width=width,
               label=LABELS.get(tag, tag).replace("\n", " "))

    ax.set_xticks([i + 0.4 - width / 2 for i in range(len(TECHS))])
    ax.set_xticklabels([f"{t}\n{TECH_NAMES[t]}" for t in TECHS], fontsize=8)
    ax.set_ylabel("households adopting (of 100)")
    ax.set_title("Adoption by technology")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    stamp(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def main() -> int:
    order = tags()
    FIGURES.mkdir(parents=True, exist_ok=True)
    for name, fig in [("cost_by_component", cost_figure(order)),
                      ("adoption_by_technology", adoption_figure(order))]:
        out = FIGURES / f"{name}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"wrote results/figures/{name}.png")
    print(f"scenarios drawn: {', '.join(order)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
