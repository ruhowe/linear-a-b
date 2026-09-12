#!/usr/bin/env python3
"""Calibration table for Kober 0.5, the entry-role tie-break (CHANGELOG "0.5";
design docs/ai_context/kober-method.md).

Reads ``results/kober-role-tiebreak/`` (full Linear B seeds 0 and 1; twenty
type-model and twenty tablet-model 988-word-type subsamples, ``--role-tiebreak``,
null seed 0, 200 draws) and, per model, reports:

    (1) the count of twenty where the real strict top three (role-tiebreak
        ordering) are all on the reference list;
    (2) the median and range, across the twenty subsamples, of that ordering's
        own chance rate under the role-tiebreak N2 (``role_tiebreak.
        top_three_all_matched_chance_rate``);
    (3) the count of twenty where at least two of the real top three are on
        the list;
    (4) the count of twenty where the strict top-ten matched count (under the
        role-tiebreak ordering) exceeds its own null 99th percentile.

No criterion is chosen here; that reading belongs to the session. The 0.3
baseline (results/kober-precision-table.json) and the 0.4 result
(results/kober-context-table.json) are quoted alongside for comparison, not
recomputed: (1) against 0.3's criterion (b) (3,3) raw count and 0.4's own
top_three_all_matched_count; (2) against 0.4's chance_rate_median_range (0.3 has
none); (3) against 0.3's criterion (b) (3,2) raw count (0.4's context table has
no "at least two of top three" cell, so that cell is null); (4) against 0.3's
criterion (a) strict real-above-null-p99 count at n=10, and 0.4's
top10_exceeds_null_p99_count.

    .venv/bin/python scripts/kober_tiebreak_table.py

Writes results/kober-tiebreak-table.json and results/kober-tiebreak-table.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIEBREAK_DIR = ROOT / "results" / "kober-role-tiebreak"
PRECISION_TABLE_PATH = ROOT / "results" / "kober-precision-table.json"
CONTEXT_TABLE_PATH = ROOT / "results" / "kober-context-table.json"
JSON_OUT = ROOT / "results" / "kober-tiebreak-table.json"
MD_OUT = ROOT / "results" / "kober-tiebreak-table.md"


def _full_files() -> list[Path]:
    return sorted(TIEBREAK_DIR / f"kober-damos-seed{s}.json" for s in (0, 1))


def _type_988_files() -> list[Path]:
    return sorted(TIEBREAK_DIR.glob("kober-damos-seed0-sub988-s*.json"))


def _tablet_988_files() -> list[Path]:
    return sorted(TIEBREAK_DIR.glob("kober-damos-seed0-docs*-s*.json"))


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


def score_model(files: list[Path]) -> dict:
    reports = _load(files)
    n_runs = len(reports)

    top_three_all_matched_count = 0
    at_least_two_of_top_three_count = 0
    top10_exceeds_null_p99_count = 0
    chance_rates: list[float] = []
    positions_changed: list[int] = []

    for d in reports:
        rt = d["role_tiebreak"]
        top3 = rt["top_3"]
        matched = sum(1 for e in top3 if e["rule"] is not None)
        if len(top3) == 3 and matched == 3:
            top_three_all_matched_count += 1
        if matched >= 2:
            at_least_two_of_top_three_count += 1
        n10 = rt["grammar_match_null_role_tiebreak"]["10"]
        if n10["real_value"] > n10["p99"]:
            top10_exceeds_null_p99_count += 1
        chance_rates.append(rt["top_three_all_matched_chance_rate"])
        positions_changed.append(rt["positions_changed_vs_0_3"])

    return {
        "n_runs": n_runs,
        "files": [f.name for f in files],
        "top_three_all_matched_count": {"pass": top_three_all_matched_count, "of": n_runs},
        "chance_rate_median_range": _median_range(chance_rates),
        "at_least_two_of_top_three_count": {"pass": at_least_two_of_top_three_count, "of": n_runs},
        "top10_exceeds_null_p99_count": {"pass": top10_exceeds_null_p99_count, "of": n_runs},
        "positions_changed_median_range": _median_range(positions_changed),
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
            "at_least_two_of_top_three_count": {"pass": b["3_2"]["pass"], "of": b["3_2"]["of"]},
            "top10_exceeds_null_p99_count": {"pass": a_strict["10"]["pass"], "of": a_strict["10"]["of"]},
        }
    return out


def _result_04(context_table: dict) -> dict:
    """The 0.4 result, quoted (not recomputed) from
    results/kober-context-table.json, per model. 0.4's own table has no "at
    least two of top three" cell (it reports "four of top five" instead), so
    that cell is null here."""
    out: dict[str, dict] = {}
    for name, m in context_table["models"].items():
        out[name] = {
            "top_three_all_matched_count": m["top_three_all_matched_count"],
            "chance_rate_median_range": m["chance_rate_median_range"],
            "at_least_two_of_top_three_count": None,  # not reported at 0.4
            "top10_exceeds_null_p99_count": m["top10_exceeds_null_p99_count"],
        }
    return out


def build_table() -> dict:
    if not PRECISION_TABLE_PATH.exists():
        print(f"missing {PRECISION_TABLE_PATH}; run scripts/kober_precision_table.py first", file=sys.stderr)
        raise SystemExit(1)
    if not CONTEXT_TABLE_PATH.exists():
        print(f"missing {CONTEXT_TABLE_PATH}; run scripts/kober_context_table.py first", file=sys.stderr)
        raise SystemExit(1)
    precision_table = json.loads(PRECISION_TABLE_PATH.read_text())
    context_table = json.loads(CONTEXT_TABLE_PATH.read_text())
    return {
        "protocol": "Kober 0.5, entry-role tie-break (CHANGELOG '0.5')",
        "source_dir": str(TIEBREAK_DIR.relative_to(ROOT)),
        "baseline_0_3_source": str(PRECISION_TABLE_PATH.relative_to(ROOT)),
        "result_0_4_source": str(CONTEXT_TABLE_PATH.relative_to(ROOT)),
        "models": {name: score_model(get_files()) for name, get_files in MODELS.items()},
        "baseline_0_3": _baseline_03(precision_table),
        "result_0_4": _result_04(context_table),
    }


def _fmt_mr(mr: dict | None) -> str:
    if mr is None or mr["median"] is None:
        return "n/a"
    lo, hi = mr["range"]
    return f"{mr['median']:.3f} ({lo:.3f} to {hi:.3f})" if isinstance(lo, float) else f"{mr['median']} ({lo} to {hi})"


def _fmt_pass(p: dict | None) -> str:
    return "n/a" if p is None else f"{p['pass']}/{p['of']}"


def render_markdown(table: dict) -> str:
    lines = [
        "# Kober 0.5 role-tiebreak calibration table",
        "",
        table["protocol"] + ".",
        "",
        f"Source: `{table['source_dir']}/`. 0.3 baseline quoted from "
        f"`{table['baseline_0_3_source']}`; 0.4 result quoted from `{table['result_0_4_source']}`.",
        "",
        "## 0.5 (role-tiebreak ordering)",
        "",
        "| model | N | strict top 3 all matched | chance rate median (range) | "
        "at least 2 of top 3 | top-10 > null p99 | positions changed vs 0.3 median (range) |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for name, m in table["models"].items():
        lines.append(
            f"| {name} | {m['n_runs']} | {_fmt_pass(m['top_three_all_matched_count'])} | "
            f"{_fmt_mr(m['chance_rate_median_range'])} | "
            f"{_fmt_pass(m['at_least_two_of_top_three_count'])} | "
            f"{_fmt_pass(m['top10_exceeds_null_p99_count'])} | "
            f"{_fmt_mr(m['positions_changed_median_range'])} |"
        )
    lines += [
        "",
        "## 0.3 baseline (quoted from kober-precision-table.json, not recomputed)",
        "",
        "| model | strict top 3 all matched | chance rate median (range) | "
        "at least 2 of top 3 | top-10 > null p99 |",
        "|---|---:|---|---:|---:|",
    ]
    for name, b in table["baseline_0_3"].items():
        lines.append(
            f"| {name} | {_fmt_pass(b['top_three_all_matched_count'])} | "
            f"{_fmt_mr(b['chance_rate_median_range'])} | "
            f"{_fmt_pass(b['at_least_two_of_top_three_count'])} | "
            f"{_fmt_pass(b['top10_exceeds_null_p99_count'])} |"
        )
    lines += [
        "",
        "## 0.4 result (quoted from kober-context-table.json, not recomputed)",
        "",
        "| model | strict top 3 all matched | chance rate median (range) | "
        "at least 2 of top 3 | top-10 > null p99 |",
        "|---|---:|---|---:|---:|",
    ]
    for name, r in table["result_0_4"].items():
        lines.append(
            f"| {name} | {_fmt_pass(r['top_three_all_matched_count'])} | "
            f"{_fmt_mr(r['chance_rate_median_range'])} | "
            f"{_fmt_pass(r['at_least_two_of_top_three_count'])} | "
            f"{_fmt_pass(r['top10_exceeds_null_p99_count'])} |"
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
