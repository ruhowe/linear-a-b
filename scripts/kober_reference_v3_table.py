#!/usr/bin/env python3
"""Calibration table for Kober 0.8, the reference-list v3 revision
(CHANGELOG "0.8"; design docs/ai_context/kober-method.md).

Per model (full, type-988, tablet-988), reads:

    - ``results/kober-grammar-null/`` (v1; the same files
      ``kober_precision_table.py`` and ``kober_reference_v2_table.py`` read)
      for the strict top-three and "at least two of three" counts under
      version 1, computed directly from each file's own
      ``ending_channel.top_20_alternations``, and, regrading the same stored
      alternations under ``reference.is_grammar(..., version=2)`` and
      ``version=3``, the same two counts under versions 2 and 3 (the grades
      are one line each, so they are recomputed directly rather than trusted
      to match a rescore block, following A-108's precedent);
    - ``results/kober-grammar-null-v3/`` (Kober 0.8's own rerun,
      ``--reference-version 3``) for whether the real strict top ten exceeds
      its own version-3 null 99th percentile, the version-3 null's own 99th
      percentile at n in (3, 5, 10), the chance rate of "strict top three all
      matched" under version 3, and the rule-firing counts under the null
      summed per model.

Also computed directly from the corpus (stage 1 is deterministic; no nulls,
no permutation draws, so this is not a rerun of anything random): the full
corpus's top fifty ending alternations, regraded at all three versions, and
which of them gain a rule under version 3 that they did not have under
version 2 (version 1 and 2's own gains are already F-031's; this table's own
reading is the *further* gain from v2 to v3).

No criterion is chosen here; that reading belongs to the session. The
CHANGELOG "0.8" pre-registered bar (informational only, not applied by this
script): v3 is "too permissive to serve as a criterion" if the full-corpus
v3 null's 99th percentile at n = 10 exceeds 3, or the 988 "top three all
grammar" chance rate exceeds one in twenty in more than two subsamples of
the twenty tablet-model (or twenty type-model) runs.

    .venv/bin/python scripts/kober_reference_v3_table.py

Writes results/kober-reference-v3-table.json and results/kober-reference-v3-table.md.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kober.reference import is_grammar  # noqa: E402

GRAMMAR_NULL_DIR = ROOT / "results" / "kober-grammar-null"
GRAMMAR_NULL_V3_DIR = ROOT / "results" / "kober-grammar-null-v3"
JSON_OUT = ROOT / "results" / "kober-reference-v3-table.json"
MD_OUT = ROOT / "results" / "kober-reference-v3-table.md"

GRAMMAR_NS = (3, 5, 10)
TOP_50_LIMIT = 50
CHANCE_RATE_BAR = 0.05  # CHANGELOG "0.8": "exceeds one in twenty"


def _full_files(d: Path) -> list[Path]:
    return sorted(d / f"kober-damos-seed{s}.json" for s in (0, 1))


def _type_988_files(d: Path) -> list[Path]:
    return sorted(d.glob("kober-damos-seed0-sub988-s*.json"))


def _tablet_988_files(d: Path) -> list[Path]:
    return sorted(d.glob("kober-damos-seed0-docs*-s*.json"))


MODEL_FILE_FNS = {
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


def _strict_top_n(ending_channel: dict, n: int) -> list[dict]:
    return ending_channel["top_20_alternations"][:n]


def _all_match(top: list[dict], version: int) -> bool:
    if not top:
        return False
    return all(is_grammar(tuple(a["e1"]), tuple(a["e2"]), version=version) is not None for a in top)


def _count_matched(top: list[dict], version: int) -> int:
    return sum(1 for a in top if is_grammar(tuple(a["e1"]), tuple(a["e2"]), version=version) is not None)


def score_model(name: str) -> dict:
    v1_files = MODEL_FILE_FNS[name](GRAMMAR_NULL_DIR)
    v3_files = MODEL_FILE_FNS[name](GRAMMAR_NULL_V3_DIR)
    v1_reports = _load(v1_files)
    v3_reports = _load(v3_files)
    n_runs = len(v1_reports)

    top3_pass = {1: 0, 2: 0, 3: 0}
    atleast2_pass = {1: 0, 2: 0, 3: 0}
    for d in v1_reports:
        top3 = _strict_top_n(d["ending_channel"], 3)
        for version in (1, 2, 3):
            if _all_match(top3, version=version):
                top3_pass[version] += 1
            if _count_matched(top3, version=version) >= 2:
                atleast2_pass[version] += 1

    top10_exceeds_null_p99_v3 = 0
    null_p99_by_n: dict[int, list[float]] = {n: [] for n in GRAMMAR_NS}
    real_matched_v3_by_n: dict[int, list[float]] = {n: [] for n in GRAMMAR_NS}
    chance_rates: list[float] = []
    rule_firing_totals: dict[str, int] = {}
    for d in v3_reports:
        gms = d["ending_channel"]["grammar_match_null_strict"]
        n10 = gms["10"]
        if n10["real_value"] > n10["p99"]:
            top10_exceeds_null_p99_v3 += 1
        for n in GRAMMAR_NS:
            null_p99_by_n[n].append(gms[str(n)]["p99"])
            real_matched_v3_by_n[n].append(gms[str(n)]["real_value"])
        chance_rates.append(d["ending_channel"]["top_three_all_matched_chance_rate"])
        for rule, count in d["ending_channel"]["rule_firing_counts_null"]["counts"].items():
            rule_firing_totals[rule] = rule_firing_totals.get(rule, 0) + count

    chance_rate_exceeds_bar = sum(1 for r in chance_rates if r > CHANCE_RATE_BAR)

    return {
        "n_runs": n_runs,
        "v1_files": [f.name for f in v1_files],
        "v3_files": [f.name for f in v3_files],
        "strict_top3_all_grammar": {
            "v1": {"pass": top3_pass[1], "of": n_runs},
            "v2": {"pass": top3_pass[2], "of": n_runs},
            "v3": {"pass": top3_pass[3], "of": n_runs},
        },
        "at_least_two_of_three": {
            "v1": {"pass": atleast2_pass[1], "of": n_runs},
            "v2": {"pass": atleast2_pass[2], "of": n_runs},
            "v3": {"pass": atleast2_pass[3], "of": n_runs},
        },
        "top10_exceeds_null_p99_v3": {"pass": top10_exceeds_null_p99_v3, "of": n_runs},
        "null_p99_v3_by_n": {str(n): _median_range(null_p99_by_n[n]) for n in GRAMMAR_NS},
        "real_matched_v3_by_n": {str(n): _median_range(real_matched_v3_by_n[n]) for n in GRAMMAR_NS},
        "top_three_all_matched_chance_rate_v3": _median_range(chance_rates),
        "top_three_all_matched_chance_rate_v3_exceeds_bar": {
            "pass": chance_rate_exceeds_bar,
            "of": n_runs,
            "bar": CHANCE_RATE_BAR,
        },
        "rule_firing_counts_null_v3": dict(
            sorted(rule_firing_totals.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
    }


def full_corpus_top_50() -> list[dict]:
    """The full Linear B corpus's top 50 ending alternations (stage 1, stem_min
    2, no subsampling -- exactly what produced ``kober-damos-seed0/1.json``'s
    real values, which are seed-independent since a null seed touches only the
    permutation draws), each regraded at versions 1, 2 and 3. Deterministic:
    no permutation draws, so this is not a rerun of anything random, only of
    stage 1's own ranking past the depth (20) the committed files stored."""
    import aegean

    from kober.paradigms import ending_channel, ranked_alternations
    from kober.words import extract_word_types

    corpus = aegean.load("damos")
    word_types = extract_word_types(corpus.documents)
    channel = ending_channel(word_types.words, stem_min=2)
    top50 = ranked_alternations(channel.alternation_support, limit=TOP_50_LIMIT)
    out = []
    for rank, ((e1, e2), support) in enumerate(top50, start=1):
        out.append(
            {
                "rank": rank,
                "e1_label": "-".join(e1),
                "e2_label": "-".join(e2),
                "support": support,
                "rule_v1": is_grammar(e1, e2, version=1),
                "rule_v2": is_grammar(e1, e2, version=2),
                "rule_v3": is_grammar(e1, e2, version=3),
            }
        )
    return out


def build_table() -> dict:
    top50 = full_corpus_top_50()
    # "Gain a rule under v3" is read two ways, both reported: the increment
    # over v2 alone (rules 12 to 22's own contribution) and the total gain
    # since v1 (rules 11 to 22 together, comparable to F-031's v1-to-v2 count
    # of 2 on this same top 50).
    gained_v3_over_v2 = [a for a in top50 if a["rule_v2"] is None and a["rule_v3"] is not None]
    gained_v3_over_v1 = [a for a in top50 if a["rule_v1"] is None and a["rule_v3"] is not None]
    return {
        "protocol": "Kober 0.8, reference-list v3 revision (CHANGELOG '0.8')",
        "grammar_match_ns": list(GRAMMAR_NS),
        "chance_rate_bar": CHANCE_RATE_BAR,
        "v1_source_dir": str(GRAMMAR_NULL_DIR.relative_to(ROOT)),
        "v3_source_dir": str(GRAMMAR_NULL_V3_DIR.relative_to(ROOT)),
        "models": {name: score_model(name) for name in MODEL_FILE_FNS},
        "full_corpus_top_50": top50,
        "full_corpus_top_50_gained_rule_under_v3_over_v2": gained_v3_over_v2,
        "full_corpus_top_50_gained_rule_under_v3_over_v2_count": len(gained_v3_over_v2),
        "full_corpus_top_50_gained_rule_under_v3_over_v1": gained_v3_over_v1,
        "full_corpus_top_50_gained_rule_under_v3_over_v1_count": len(gained_v3_over_v1),
    }


def _fmt_mr(mr: dict) -> str:
    if mr["median"] is None:
        return "n/a"
    lo, hi = mr["range"]
    return f"{mr['median']:.3g} ({lo:.3g} to {hi:.3g})"


def _fmt_pass(p: dict) -> str:
    return f"{p['pass']}/{p['of']}"


def render_markdown(table: dict) -> str:
    lines = [
        "# Kober 0.8 reference-list-v3 calibration table",
        "",
        table["protocol"] + ".",
        "",
        f"v1 source: `{table['v1_source_dir']}/`. v3 source: `{table['v3_source_dir']}/`.",
        "",
        "## Strict top three all grammar, v1 vs v2 vs v3",
        "",
        "| model | N | v1 | v2 | v3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        t3 = m["strict_top3_all_grammar"]
        lines.append(
            f"| {name} | {m['n_runs']} | {_fmt_pass(t3['v1'])} | {_fmt_pass(t3['v2'])} | {_fmt_pass(t3['v3'])} |"
        )
    lines += [
        "",
        "## At least two of top three, v1 vs v2 vs v3",
        "",
        "| model | N | v1 | v2 | v3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        a2 = m["at_least_two_of_three"]
        lines.append(
            f"| {name} | {m['n_runs']} | {_fmt_pass(a2['v1'])} | {_fmt_pass(a2['v2'])} | {_fmt_pass(a2['v3'])} |"
        )
    lines += [
        "",
        "## Top ten matched above its own v3 null 99th percentile (results/kober-grammar-null-v3/)",
        "",
        "| model | N | pass |",
        "|---|---:|---:|",
    ]
    for name, m in table["models"].items():
        lines.append(f"| {name} | {m['n_runs']} | {_fmt_pass(m['top10_exceeds_null_p99_v3'])} |")
    lines += [
        "",
        "## v3 null: 99th percentile (median, range across the model's runs)",
        "",
        "| model | n=3 | n=5 | n=10 |",
        "|---|---|---|---|",
    ]
    for name, m in table["models"].items():
        pp = m["null_p99_v3_by_n"]
        lines.append(f"| {name} | {_fmt_mr(pp['3'])} | {_fmt_mr(pp['5'])} | {_fmt_mr(pp['10'])} |")
    lines += [
        "",
        "## Real strict matched count under v3 (median, range across the model's runs)",
        "",
        "| model | n=3 | n=5 | n=10 |",
        "|---|---|---|---|",
    ]
    for name, m in table["models"].items():
        rm = m["real_matched_v3_by_n"]
        lines.append(f"| {name} | {_fmt_mr(rm['3'])} | {_fmt_mr(rm['5'])} | {_fmt_mr(rm['10'])} |")
    lines += [
        "",
        "## Chance rate of \"strict top three all matched\" under v3 (median, range; count exceeding "
        f"{table['chance_rate_bar']:g})",
        "",
        "| model | N | median | range | count > bar |",
        "|---|---:|---:|---|---:|",
    ]
    for name, m in table["models"].items():
        cr = m["top_three_all_matched_chance_rate_v3"]
        eb = m["top_three_all_matched_chance_rate_v3_exceeds_bar"]
        rng = "n/a" if cr["range"] is None else f"{cr['range'][0]:.3g} to {cr['range'][1]:.3g}"
        median = "n/a" if cr["median"] is None else f"{cr['median']:.3g}"
        lines.append(f"| {name} | {m['n_runs']} | {median} | {rng} | {_fmt_pass(eb)} |")
    lines += [
        "",
        "## Rule-firing counts under the null, v3, summed over all draws and runs per model",
        "",
    ]
    for name, m in table["models"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| rule | count |")
        lines.append("|---|---:|")
        for rule, count in m["rule_firing_counts_null_v3"].items():
            lines.append(f"| {rule} | {count} |")
        lines.append("")
    lines += [
        f"## Full corpus: top {TOP_50_LIMIT} alternations gaining a rule under v3 that they did not have under v2",
        "",
        f"{table['full_corpus_top_50_gained_rule_under_v3_over_v2_count']} of {TOP_50_LIMIT}.",
        "",
        "| rank | ending pair | support | rule (v3) |",
        "|---:|---|---:|---|",
    ]
    for a in table["full_corpus_top_50_gained_rule_under_v3_over_v2"]:
        lines.append(f"| {a['rank']} | {a['e1_label']} / {a['e2_label']} | {a['support']} | {a['rule_v3']} |")
    lines += [
        "",
        f"## Full corpus: top {TOP_50_LIMIT} alternations gaining a rule under v3 that they did not have under v1",
        "",
        f"{table['full_corpus_top_50_gained_rule_under_v3_over_v1_count']} of {TOP_50_LIMIT} "
        "(includes the 0.6/v2 gains, rules 11's ethnic derivation, plus rules 12 to 22's own).",
        "",
        "| rank | ending pair | support | rule (v3) |",
        "|---:|---|---:|---|",
    ]
    for a in table["full_corpus_top_50_gained_rule_under_v3_over_v1"]:
        lines.append(f"| {a['rank']} | {a['e1_label']} / {a['e2_label']} | {a['support']} | {a['rule_v3']} |")
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
