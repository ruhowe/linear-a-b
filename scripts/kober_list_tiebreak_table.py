#!/usr/bin/env python3
"""Calibration table for Kober 0.7, the list-support tie-break (CHANGELOG "0.7";
design docs/ai_context/kober-method.md).

Reads ``results/kober-list-tiebreak/`` (full Linear B seeds 0 and 1; twenty
type-model and twenty tablet-model 988-word-type subsamples, ``--list-tiebreak``
(implies ``--role-tiebreak``), null seed 0, 200 draws) and, per model, reports,
at *both* reference versions (1 and 2):

    (1) the count of twenty where the real strict top three (list-tiebreak
        ordering) are all on the reference list;
    (2) the count of twenty where at least two of the real top three are;
    (3) the count of twenty where the strict top-ten matched count (under
        the list-tiebreak ordering) exceeds its own null 99th percentile;
    (4) the median and range, across the twenty subsamples, of that
        ordering's own chance rate under the list-tiebreak N2
        (``list_tiebreak.top_three_all_matched_chance_rate_v{1,2}``);

and, not versioned (the real top ten's own composition), the median and
range of positions changed vs the 0.5 ordering.

No criterion is chosen here; that reading belongs to the session. Beside the
0.7 figures, three earlier tables are quoted, not recomputed:

    - 0.3 (``results/kober-precision-table.json``): the plain-ordering
      criterion (b) raw counts, version 1 only (that table predates Kober 0.6);
    - 0.5 (``results/kober-tiebreak-table.json``): the role-tiebreak-ordering
      counts, version 1 only (ditto);
    - 0.6 (``results/kober-reference-v2-table.json``): the *plain* (0.3, not
      role- or list-tiebreak) ordering's strict top three and at-least-two-of-
      three, scored at both reference versions -- the "0.3 ordering, v1 vs v2"
      comparison F-031 reports.

    .venv/bin/python scripts/kober_list_tiebreak_table.py

Writes results/kober-list-tiebreak-table.json and results/kober-list-tiebreak-table.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST_TIEBREAK_DIR = ROOT / "results" / "kober-list-tiebreak"
PRECISION_TABLE_PATH = ROOT / "results" / "kober-precision-table.json"
TIEBREAK_TABLE_PATH = ROOT / "results" / "kober-tiebreak-table.json"
REFERENCE_V2_TABLE_PATH = ROOT / "results" / "kober-reference-v2-table.json"
JSON_OUT = ROOT / "results" / "kober-list-tiebreak-table.json"
MD_OUT = ROOT / "results" / "kober-list-tiebreak-table.md"

GRAMMAR_NS = (3, 5, 10)


def _full_files() -> list[Path]:
    return sorted(LIST_TIEBREAK_DIR / f"kober-damos-seed{s}.json" for s in (0, 1))


def _type_988_files() -> list[Path]:
    return sorted(LIST_TIEBREAK_DIR.glob("kober-damos-seed0-sub988-s*.json"))


def _tablet_988_files() -> list[Path]:
    return sorted(LIST_TIEBREAK_DIR.glob("kober-damos-seed0-docs*-s*.json"))


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

    top3 = {1: 0, 2: 0}
    atleast2 = {1: 0, 2: 0}
    top10 = {1: 0, 2: 0}
    chance_rates: dict[int, list[float]] = {1: [], 2: []}
    positions_changed: list[int] = []

    for d in reports:
        lt = d["list_tiebreak"]
        top_3 = lt["top_3"]
        for v in (1, 2):
            matched = sum(1 for e in top_3 if e[f"rule_v{v}"] is not None)
            if len(top_3) == 3 and matched == 3:
                top3[v] += 1
            if matched >= 2:
                atleast2[v] += 1
            n10 = lt[f"grammar_match_null_list_tiebreak_v{v}"]["10"]
            if n10["real_value"] > n10["p99"]:
                top10[v] += 1
            chance_rates[v].append(lt[f"top_three_all_matched_chance_rate_v{v}"])
        positions_changed.append(lt["positions_changed_vs_0_5"])

    return {
        "n_runs": n_runs,
        "files": [f.name for f in files],
        "strict_top3_all_grammar": {
            "v1": {"pass": top3[1], "of": n_runs},
            "v2": {"pass": top3[2], "of": n_runs},
        },
        "at_least_two_of_three": {
            "v1": {"pass": atleast2[1], "of": n_runs},
            "v2": {"pass": atleast2[2], "of": n_runs},
        },
        "top10_exceeds_null_p99": {
            "v1": {"pass": top10[1], "of": n_runs},
            "v2": {"pass": top10[2], "of": n_runs},
        },
        "chance_rate_median_range": {
            "v1": _median_range(chance_rates[1]),
            "v2": _median_range(chance_rates[2]),
        },
        "positions_changed_vs_0_5_median_range": _median_range(positions_changed),
    }


def _baseline_03(precision_table: dict) -> dict:
    """The 0.3 baseline, quoted (not recomputed) from
    results/kober-precision-table.json, per model, version 1 only (that
    table predates Kober 0.6)."""
    out: dict[str, dict] = {}
    for name, m in precision_table["models"].items():
        b = m["criterion_b_raw_k_of_top_n"]
        a_strict = m["criterion_a_strict_real_above_null_p99"]
        out[name] = {
            "strict_top3_all_grammar": {"pass": b["3_3"]["pass"], "of": b["3_3"]["of"]},
            "at_least_two_of_three": {"pass": b["3_2"]["pass"], "of": b["3_2"]["of"]},
            "top10_exceeds_null_p99": {"pass": a_strict["10"]["pass"], "of": a_strict["10"]["of"]},
        }
    return out


def _result_05(tiebreak_table: dict) -> dict:
    """The 0.5 result, quoted (not recomputed) from
    results/kober-tiebreak-table.json, per model, version 1 only (that table
    predates Kober 0.6)."""
    out: dict[str, dict] = {}
    for name, m in tiebreak_table["models"].items():
        out[name] = {
            "strict_top3_all_grammar": m["top_three_all_matched_count"],
            "at_least_two_of_three": m["at_least_two_of_top_three_count"],
            "top10_exceeds_null_p99": m["top10_exceeds_null_p99_count"],
            "chance_rate_median_range": m["chance_rate_median_range"],
        }
    return out


def _result_06(reference_v2_table: dict) -> dict:
    """The 0.6 result, quoted (not recomputed) from
    results/kober-reference-v2-table.json, per model: the *plain* (0.3, not
    role- or list-tiebreak) ordering's strict top three and
    at-least-two-of-three, scored at both reference versions."""
    out: dict[str, dict] = {}
    for name, m in reference_v2_table["models"].items():
        out[name] = {
            "strict_top3_all_grammar": m["strict_top3_all_grammar"],
            "at_least_two_of_three": m["at_least_two_of_three"],
            "top10_exceeds_null_p99_v2": m["top10_exceeds_null_p99_v2"],
        }
    return out


def build_table() -> dict:
    for path, script in (
        (PRECISION_TABLE_PATH, "kober_precision_table.py"),
        (TIEBREAK_TABLE_PATH, "kober_tiebreak_table.py"),
        (REFERENCE_V2_TABLE_PATH, "kober_reference_v2_table.py"),
    ):
        if not path.exists():
            print(f"missing {path}; run scripts/{script} first", file=sys.stderr)
            raise SystemExit(1)
    precision_table = json.loads(PRECISION_TABLE_PATH.read_text())
    tiebreak_table = json.loads(TIEBREAK_TABLE_PATH.read_text())
    reference_v2_table = json.loads(REFERENCE_V2_TABLE_PATH.read_text())
    return {
        "protocol": "Kober 0.7, list-support tie-break (CHANGELOG '0.7')",
        "source_dir": str(LIST_TIEBREAK_DIR.relative_to(ROOT)),
        "baseline_0_3_source": str(PRECISION_TABLE_PATH.relative_to(ROOT)),
        "result_0_5_source": str(TIEBREAK_TABLE_PATH.relative_to(ROOT)),
        "result_0_6_source": str(REFERENCE_V2_TABLE_PATH.relative_to(ROOT)),
        "models": {name: score_model(get_files()) for name, get_files in MODELS.items()},
        "baseline_0_3": _baseline_03(precision_table),
        "result_0_5": _result_05(tiebreak_table),
        "result_0_6": _result_06(reference_v2_table),
    }


def _fmt_mr(mr: dict | None) -> str:
    if mr is None or mr["median"] is None:
        return "n/a"
    lo, hi = mr["range"]
    return f"{mr['median']:.3g} ({lo:.3g} to {hi:.3g})"


def _fmt_pass(p: dict | None) -> str:
    return "n/a" if p is None else f"{p['pass']}/{p['of']}"


def render_markdown(table: dict) -> str:
    lines = [
        "# Kober 0.7 list-tiebreak calibration table",
        "",
        table["protocol"] + ".",
        "",
        f"Source: `{table['source_dir']}/`. 0.3 baseline quoted from "
        f"`{table['baseline_0_3_source']}`; 0.5 result quoted from "
        f"`{table['result_0_5_source']}`; 0.6 result quoted from "
        f"`{table['result_0_6_source']}`.",
        "",
        "## 0.7 (list-tiebreak ordering: support, role-sharing, list-support, lexicographic)",
        "",
        "| model | N | top3 all grammar v1 | v2 | >=2 of 3 v1 | v2 | top10 > null p99 v1 | v2 | "
        "chance rate v1 (range) | v2 (range) | positions changed vs 0.5 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for name, m in table["models"].items():
        t3, a2, t10, cr = (
            m["strict_top3_all_grammar"],
            m["at_least_two_of_three"],
            m["top10_exceeds_null_p99"],
            m["chance_rate_median_range"],
        )
        lines.append(
            f"| {name} | {m['n_runs']} | {_fmt_pass(t3['v1'])} | {_fmt_pass(t3['v2'])} | "
            f"{_fmt_pass(a2['v1'])} | {_fmt_pass(a2['v2'])} | "
            f"{_fmt_pass(t10['v1'])} | {_fmt_pass(t10['v2'])} | "
            f"{_fmt_mr(cr['v1'])} | {_fmt_mr(cr['v2'])} | "
            f"{_fmt_mr(m['positions_changed_vs_0_5_median_range'])} |"
        )
    lines += [
        "",
        "## 0.3 baseline (quoted from kober-precision-table.json, version 1 only, not recomputed)",
        "",
        "| model | strict top 3 all grammar | at least 2 of 3 | top-10 > null p99 |",
        "|---|---:|---:|---:|",
    ]
    for name, b in table["baseline_0_3"].items():
        lines.append(
            f"| {name} | {_fmt_pass(b['strict_top3_all_grammar'])} | "
            f"{_fmt_pass(b['at_least_two_of_three'])} | {_fmt_pass(b['top10_exceeds_null_p99'])} |"
        )
    lines += [
        "",
        "## 0.5 result (quoted from kober-tiebreak-table.json, version 1 only, not recomputed)",
        "",
        "| model | strict top 3 all grammar | at least 2 of 3 | top-10 > null p99 | chance rate median (range) |",
        "|---|---:|---:|---:|---|",
    ]
    for name, r in table["result_0_5"].items():
        lines.append(
            f"| {name} | {_fmt_pass(r['strict_top3_all_grammar'])} | "
            f"{_fmt_pass(r['at_least_two_of_three'])} | {_fmt_pass(r['top10_exceeds_null_p99'])} | "
            f"{_fmt_mr(r['chance_rate_median_range'])} |"
        )
    lines += [
        "",
        "## 0.6 result (quoted from kober-reference-v2-table.json, plain 0.3 ordering scored "
        "at v1 vs v2, not recomputed)",
        "",
        "| model | top3 all grammar v1 | v2 | >=2 of 3 v1 | v2 | top10 > null p99 (v2 null) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, r in table["result_0_6"].items():
        t3, a2 = r["strict_top3_all_grammar"], r["at_least_two_of_three"]
        lines.append(
            f"| {name} | {_fmt_pass(t3['v1'])} | {_fmt_pass(t3['v2'])} | "
            f"{_fmt_pass(a2['v1'])} | {_fmt_pass(a2['v2'])} | {_fmt_pass(r['top10_exceeds_null_p99_v2'])} |"
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
