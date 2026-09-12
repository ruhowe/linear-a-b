#!/usr/bin/env python3
"""Calibration table for Kober 0.4, the context-restricted statistics (TODO item 8,
"Build and run"; CHANGELOG "0.4"; design docs/ai_context/kober-method.md "Version 0.4").

Reads ``results/kober-context/`` (full Linear B seeds 0 and 1; twenty type-model and
twenty tablet-model 988-word-type subsamples, `--context`, null seed 0, 200 draws) and,
per model, reports:

    (1) the count of twenty where the real strict top three are all on the reference
        list (the 0.4 criterion itself, CHANGELOG "0.4");
    (2) the median and range, across the twenty subsamples, of that event's own chance
        rate under the stratified N2 (``context.top_three_all_matched_chance_rate``);
    (3) the count of twenty where at least four of the real top five are on the list;
    (4) the count of twenty where the strict top-10 matched count exceeds its own
        stratified-N2 99th percentile;
    (5) the median class-agreement fraction (A-091) among the real top ten, pooled
        over all twenty subsamples' top-ten entries.

No criterion is chosen here; that reading belongs to the session. The 0.3 baseline
numbers (results/kober-precision-table.json) are quoted alongside for comparison, not
recomputed: (1) against criterion (b)'s (3,3) raw count, (3) against (5,4), (4) against
criterion (a) strict's real-above-null-p99 count at n=10. 0.3 has no per-subsample
chance rate or class-agreement fraction (context restriction did not exist under 0.3),
so those two 0.3 cells are reported as null.

    .venv/bin/python scripts/kober_context_table.py

Writes results/kober-context-table.json and results/kober-context-table.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "results" / "kober-context"
PRECISION_TABLE_PATH = ROOT / "results" / "kober-precision-table.json"
JSON_OUT = ROOT / "results" / "kober-context-table.json"
MD_OUT = ROOT / "results" / "kober-context-table.md"


def _full_files() -> list[Path]:
    return sorted(CONTEXT_DIR / f"kober-damos-seed{s}.json" for s in (0, 1))


def _type_988_files() -> list[Path]:
    return sorted(CONTEXT_DIR.glob("kober-damos-seed0-sub988-s*.json"))


def _tablet_988_files() -> list[Path]:
    return sorted(CONTEXT_DIR.glob("kober-damos-seed0-docs*-s*.json"))


MODELS = {
    "full": _full_files,
    "type-988": _type_988_files,
    "tablet-988": _tablet_988_files,
}


def _load(files: list[Path]) -> list[dict]:
    missing = [f for f in files if not f.exists()]
    if missing:
        print(f"missing {len(missing)} expected file(s), e.g. {missing[0]}", file=sys.stderr)
        raise SystemExit(1)
    return [json.loads(f.read_text()) for f in files]


def _median_range(values: list[float]) -> dict:
    return {
        "median": statistics.median(values) if values else None,
        "range": [min(values), max(values)] if values else None,
    }


def _top_three_all_matched(top_3: list[dict]) -> bool:
    return len(top_3) == 3 and all(e["rule"] is not None for e in top_3)


def _four_of_top_five(top_10: list[dict]) -> bool:
    top_5 = top_10[:5]
    return sum(1 for e in top_5 if e["rule"] is not None) >= 4


def score_model(files: list[Path]) -> dict:
    reports = _load(files)
    n_runs = len(reports)

    top_three_all_matched_count = 0
    four_of_top_five_count = 0
    top10_exceeds_null_p99_count = 0
    chance_rates: list[float] = []
    class_agreement_fractions: list[float] = []

    for d in reports:
        c = d["context"]
        if _top_three_all_matched(c["top_3"]):
            top_three_all_matched_count += 1
        if _four_of_top_five(c["top_10"]):
            four_of_top_five_count += 1
        n10 = c["grammar_match_null_strict_stratified"]["10"]
        if n10["real_value"] > n10["p99"]:
            top10_exceeds_null_p99_count += 1
        chance_rates.append(c["top_three_all_matched_chance_rate"])
        class_agreement_fractions.extend(e["class_agreement_fraction"] for e in c["top_10"])

    return {
        "n_runs": n_runs,
        "files": [f.name for f in files],
        "top_three_all_matched_count": {"pass": top_three_all_matched_count, "of": n_runs},
        "chance_rate_median_range": _median_range(chance_rates),
        "four_of_top_five_count": {"pass": four_of_top_five_count, "of": n_runs},
        "top10_exceeds_null_p99_count": {"pass": top10_exceeds_null_p99_count, "of": n_runs},
        "median_class_agreement_fraction": (
            statistics.median(class_agreement_fractions) if class_agreement_fractions else None
        ),
        "class_agreement_fraction_n": len(class_agreement_fractions),
    }


def _baseline_03(precision_table: dict) -> dict:
    """The 0.3 baseline numbers, quoted (not recomputed) from
    results/kober-precision-table.json, per model."""
    out: dict[str, dict] = {}
    for name, m in precision_table["models"].items():
        b = m["criterion_b_raw_k_of_top_n"]
        a_strict = m["criterion_a_strict_real_above_null_p99"]
        out[name] = {
            "top_three_all_matched_count": {"pass": b["3_3"]["pass"], "of": b["3_3"]["of"]},
            "chance_rate_median_range": None,  # 0.3 has no per-subsample chance rate
            "four_of_top_five_count": {"pass": b["5_4"]["pass"], "of": b["5_4"]["of"]},
            "top10_exceeds_null_p99_count": {"pass": a_strict["10"]["pass"], "of": a_strict["10"]["of"]},
            "median_class_agreement_fraction": None,  # context restriction did not exist under 0.3
        }
    return out


def build_table() -> dict:
    if not PRECISION_TABLE_PATH.exists():
        print(f"missing {PRECISION_TABLE_PATH}; run scripts/kober_precision_table.py first", file=sys.stderr)
        raise SystemExit(1)
    precision_table = json.loads(PRECISION_TABLE_PATH.read_text())
    return {
        "protocol": (
            "Kober 0.4, context-restricted statistics under stratified (length, class) "
            "nulls (CHANGELOG '0.4'); TODO item 8, 'Build and run'"
        ),
        "source_dir": str(CONTEXT_DIR.relative_to(ROOT)),
        "baseline_source": str(PRECISION_TABLE_PATH.relative_to(ROOT)),
        "models": {name: score_model(get_files()) for name, get_files in MODELS.items()},
        "baseline_0_3": _baseline_03(precision_table),
    }


def _fmt_mr(mr: dict | None) -> str:
    if mr is None or mr["median"] is None:
        return "n/a"
    lo, hi = mr["range"]
    return f"{mr['median']:.3f} ({lo:.3f} to {hi:.3f})"


def _fmt_frac(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def render_markdown(table: dict) -> str:
    lines = [
        "# Kober 0.4 context calibration table",
        "",
        table["protocol"] + ".",
        "",
        f"Source: `{table['source_dir']}/`. 0.3 baseline quoted from `{table['baseline_source']}`.",
        "",
        "## 0.4 (context-restricted, stratified nulls)",
        "",
        "| model | N | strict top 3 all matched | chance rate median (range) | "
        "4 of top 5 | top-10 > null p99 | median class agreement fraction |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        lines.append(
            f"| {name} | {m['n_runs']} | "
            f"{m['top_three_all_matched_count']['pass']}/{m['top_three_all_matched_count']['of']} | "
            f"{_fmt_mr(m['chance_rate_median_range'])} | "
            f"{m['four_of_top_five_count']['pass']}/{m['four_of_top_five_count']['of']} | "
            f"{m['top10_exceeds_null_p99_count']['pass']}/{m['top10_exceeds_null_p99_count']['of']} | "
            f"{_fmt_frac(m['median_class_agreement_fraction'])} |"
        )
    lines += [
        "",
        "## 0.3 baseline (quoted from kober-precision-table.json, not recomputed)",
        "",
        "| model | strict top 3 all matched | chance rate median (range) | "
        "4 of top 5 | top-10 > null p99 | median class agreement fraction |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for name, b in table["baseline_0_3"].items():
        lines.append(
            f"| {name} | {b['top_three_all_matched_count']['pass']}/{b['top_three_all_matched_count']['of']} | "
            f"{_fmt_mr(b['chance_rate_median_range'])} | "
            f"{b['four_of_top_five_count']['pass']}/{b['four_of_top_five_count']['of']} | "
            f"{b['top10_exceeds_null_p99_count']['pass']}/{b['top10_exceeds_null_p99_count']['of']} | "
            f"{_fmt_frac(b['median_class_agreement_fraction'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    table = build_table()
    JSON_OUT.write_text(json.dumps(table, indent=2, ensure_ascii=False) + "\n")
    md = render_markdown(table)
    MD_OUT.write_text(md)
    print(md)
    print(f"\nWrote {JSON_OUT}")
    print(f"Wrote {MD_OUT}")


if __name__ == "__main__":
    main()
