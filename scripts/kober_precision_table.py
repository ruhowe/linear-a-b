#!/usr/bin/env python3
"""Precision-criterion table for the grammar-match null (TODO item 8, prerequisite 1;
CHANGELOG "Null rate of the grammar match, and precision criteria").

Reads the results this task's runs wrote to ``results/kober-grammar-null/`` (full
Linear B, seeds 0 and 1; the twenty type-model and twenty tablet-model 988-word-type
subsamples from F-022) and, per model, scores two families of candidate precision
criterion against the ending channel's top-n ending alternations, without choosing
one:

    (a) "real matched count at top-n exceeds the null 99th percentile", for
        n in (3, 5, 10), scored under *both* top-n readings (A-072): ties-included
        (``ending_channel.grammar_match_null``, A-053, the original reading) and
        strict (``ending_channel.grammar_match_null_strict``, a deterministic cut
        at exactly n applied identically to the real corpus and to every null
        draw). The two can disagree near a tie (A-069): the real and null counts
        must be computed the same way, and both ways are reported here.
    (b) the raw "k of top-n on the list", for (n, k) in
        ((3, 3), (3, 2), (5, 4), (10, 7)) -- computed here from
        ``ending_channel.top_20_alternations`` sliced to a *strict* top-n (the same
        lexicographic tie-break ``top_10_matched_to_rule`` already uses in the
        results files), which is the same reading as (a)'s strict variant and is
        not the same set as (a)'s ties-included top-n (A-069).

No criterion is chosen here; that choice is Kober 0.4's, made from this table
(CHANGELOG). Also reported per model, at each n: the median and range of the null
99th percentile and of the real matched count, under both the ties-included
``grammar_match_null`` block and the strict ``grammar_match_null_strict`` block;
and the median ties-included top-n set size (A-072), for real and for the null
mean, at n=10.

    .venv/bin/python scripts/kober_precision_table.py

Writes results/kober-precision-table.json and results/kober-precision-table.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_NULL_DIR = ROOT / "results" / "kober-grammar-null"
JSON_OUT = ROOT / "results" / "kober-precision-table.json"
MD_OUT = ROOT / "results" / "kober-precision-table.md"

GRAMMAR_NS = (3, 5, 10)
CRITERION_B = ((3, 3), (3, 2), (5, 4), (10, 7))


def _full_files() -> list[Path]:
    return sorted(GRAMMAR_NULL_DIR / f"kober-damos-seed{s}.json" for s in (0, 1))


def _type_988_files() -> list[Path]:
    return sorted(GRAMMAR_NULL_DIR.glob("kober-damos-seed0-sub988-s*.json"))


def _tablet_988_files() -> list[Path]:
    return sorted(GRAMMAR_NULL_DIR.glob("kober-damos-seed0-docs*-s*.json"))


MODELS: dict[str, Callable[[], list[Path]]] = {
    "full": _full_files,
    "type-988": _type_988_files,
    "tablet-988": _tablet_988_files,
}


def _strict_top_n_matched(ending_channel: dict, n: int) -> int:
    """Raw "k of top-n on the list": a strict cut at n (lexicographic tie-break,
    the same ranking ``top_20_alternations`` and ``top_10_matched_to_rule`` already
    use), not the ties-included top-n ``grammar_match_null`` reports (A-069)."""
    top = ending_channel["top_20_alternations"][:n]
    return sum(1 for a in top if a["rule"] is not None)


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

    criteria_a: dict[str, dict] = {}
    criteria_a_strict: dict[str, dict] = {}
    for n in GRAMMAR_NS:
        gm = [d["ending_channel"]["grammar_match_null"][str(n)] for d in reports]
        passed = sum(1 for g in gm if g["real_value"] > g["p99"])
        criteria_a[str(n)] = {"pass": passed, "of": n_runs}

        gms = [d["ending_channel"]["grammar_match_null_strict"][str(n)] for d in reports]
        passed_strict = sum(1 for g in gms if g["real_value"] > g["p99"])
        criteria_a_strict[str(n)] = {"pass": passed_strict, "of": n_runs}

    criteria_b: dict[str, dict] = {}
    for n, k in CRITERION_B:
        matched = [_strict_top_n_matched(d["ending_channel"], n) for d in reports]
        passed = sum(1 for m in matched if m >= k)
        criteria_b[f"{n}_{k}"] = {"pass": passed, "of": n_runs, "n": n, "k": k}

    null_p99: dict[str, dict] = {}
    real_matched: dict[str, dict] = {}
    null_p99_strict: dict[str, dict] = {}
    real_matched_strict: dict[str, dict] = {}
    for n in GRAMMAR_NS:
        gm = [d["ending_channel"]["grammar_match_null"][str(n)] for d in reports]
        null_p99[str(n)] = _median_range([g["p99"] for g in gm])
        real_matched[str(n)] = _median_range([g["real_value"] for g in gm])

        gms = [d["ending_channel"]["grammar_match_null_strict"][str(n)] for d in reports]
        null_p99_strict[str(n)] = _median_range([g["p99"] for g in gms])
        real_matched_strict[str(n)] = _median_range([g["real_value"] for g in gms])

    # Ties-included top-n set size (A-072), at n=10: median across runs of the
    # real set size and of each run's own null mean set size.
    ties_10 = [d["ending_channel"]["grammar_match_null_strict"]["10"]["ties_included_top_n_size"] for d in reports]
    ties_included_top_10_size = {
        "real_median": statistics.median(t["real_value"] for t in ties_10),
        "null_mean_median": statistics.median(t["mean"] for t in ties_10),
    }

    return {
        "n_runs": n_runs,
        "files": [f.name for f in files],
        "criterion_a_real_above_null_p99": criteria_a,
        "criterion_a_strict_real_above_null_p99": criteria_a_strict,
        "criterion_b_raw_k_of_top_n": criteria_b,
        "null_p99_by_n": null_p99,
        "real_matched_by_n": real_matched,
        "null_p99_strict_by_n": null_p99_strict,
        "real_matched_strict_by_n": real_matched_strict,
        "ties_included_top_10_size": ties_included_top_10_size,
    }


def build_table() -> dict:
    return {
        "protocol": (
            "Kober 0.3 stage 1, grammar-match null (CHANGELOG 'Null rate of the "
            "grammar match, and precision criteria'); TODO item 8, prerequisite 1"
        ),
        "grammar_match_ns": list(GRAMMAR_NS),
        "criterion_b_n_k_pairs": [list(pair) for pair in CRITERION_B],
        "models": {name: score_model(get_files()) for name, get_files in MODELS.items()},
    }


def render_markdown(table: dict) -> str:
    lines = [
        "# Kober grammar-match null: precision-criterion table",
        "",
        table["protocol"] + ".",
        "",
        "## Criterion (a): real matched count at top-n exceeds the null 99th percentile",
        "",
        "### Ties-included top-n (A-053)",
        "",
        "| model | N | n=3 pass | n=5 pass | n=10 pass |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        a = m["criterion_a_real_above_null_p99"]
        lines.append(
            f"| {name} | {m['n_runs']} | {a['3']['pass']}/{a['3']['of']} | "
            f"{a['5']['pass']}/{a['5']['of']} | {a['10']['pass']}/{a['10']['of']} |"
        )
    lines += [
        "",
        "### Strict top-n (A-072)",
        "",
        "| model | N | n=3 pass | n=5 pass | n=10 pass |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        a = m["criterion_a_strict_real_above_null_p99"]
        lines.append(
            f"| {name} | {m['n_runs']} | {a['3']['pass']}/{a['3']['of']} | "
            f"{a['5']['pass']}/{a['5']['of']} | {a['10']['pass']}/{a['10']['of']} |"
        )
    lines += [
        "",
        "## Criterion (b): raw k of top-n on the reference list",
        "",
        "| model | N | (3,3) | (3,2) | (5,4) | (10,7) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        b = m["criterion_b_raw_k_of_top_n"]
        lines.append(
            f"| {name} | {m['n_runs']} | {b['3_3']['pass']}/{b['3_3']['of']} | "
            f"{b['3_2']['pass']}/{b['3_2']['of']} | {b['5_4']['pass']}/{b['5_4']['of']} | "
            f"{b['10_7']['pass']}/{b['10_7']['of']} |"
        )
    lines += [
        "",
        "## Null 99th percentile and real matched count, ties-included top-n (median, range)",
        "",
        "| model | n | null p99 median | null p99 range | real matched median | real matched range |",
        "|---|---:|---:|---|---:|---|",
    ]
    for name, m in table["models"].items():
        for n in table["grammar_match_ns"]:
            p99 = m["null_p99_by_n"][str(n)]
            real = m["real_matched_by_n"][str(n)]
            lines.append(
                f"| {name} | {n} | {p99['median']} | {p99['range']} | "
                f"{real['median']} | {real['range']} |"
            )
    lines += [
        "",
        "## Null 99th percentile and real matched count, strict top-n (median, range)",
        "",
        "| model | n | null p99 median | null p99 range | real matched median | real matched range |",
        "|---|---:|---:|---|---:|---|",
    ]
    for name, m in table["models"].items():
        for n in table["grammar_match_ns"]:
            p99 = m["null_p99_strict_by_n"][str(n)]
            real = m["real_matched_strict_by_n"][str(n)]
            lines.append(
                f"| {name} | {n} | {p99['median']} | {p99['range']} | "
                f"{real['median']} | {real['range']} |"
            )
    lines += [
        "",
        "## Ties-included top-10 set size (median across runs, A-072)",
        "",
        "| model | real median | null mean median |",
        "|---|---:|---:|",
    ]
    for name, m in table["models"].items():
        t = m["ties_included_top_10_size"]
        lines.append(f"| {name} | {t['real_median']} | {t['null_mean_median']} |")
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
