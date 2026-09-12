#!/usr/bin/env python3
"""Calibration table for Kober 0.6, the reference-list revision (CHANGELOG "0.6";
design docs/ai_context/kober-method.md).

Per model (full, type-988, tablet-988), reads:

    - ``results/kober-grammar-null/`` (v1; the same files
      ``kober_precision_table.py`` reads) for the strict top-three and
      "at least two of three" counts under version 1, computed directly from
      each file's own ``ending_channel.top_20_alternations``; and, regrading
      the same stored alternations under ``reference.is_grammar(..., version=2)``,
      the same two counts under version 2 (the rescore this task's step 2
      already wrote into a ``reference_v2`` block is not read here -- the
      version-2 grade is one line, so it is recomputed directly rather than
      trusted to match);
    - ``results/kober-grammar-null-v2/`` (Kober 0.6's own rerun,
      ``--reference-version 2``, CHANGELOG "0.6" step 3) for whether the real
      strict top ten exceeds its own version-2 null 99th percentile, and for
      the version-2 null's own mean matched count at n in (3, 5, 10) -- the
      rate a shuffled corpus matches "by chance" under the wider rule
      (CHANGELOG: "the null rate, which can also rise because the new rule
      admits more chance pairs").

Also computed directly from the corpus (stage 1 is deterministic; no nulls,
no permutation draws, so this is not a rerun of anything random): the full
corpus's top fifty ending alternations, regraded at both versions, and which
of them gain a rule under version 2 that they did not have under version 1.

No criterion is chosen here; that reading belongs to the session.

    .venv/bin/python scripts/kober_reference_v2_table.py

Writes results/kober-reference-v2-table.json and results/kober-reference-v2-table.md.
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
GRAMMAR_NULL_V2_DIR = ROOT / "results" / "kober-grammar-null-v2"
JSON_OUT = ROOT / "results" / "kober-reference-v2-table.json"
MD_OUT = ROOT / "results" / "kober-reference-v2-table.md"

GRAMMAR_NS = (3, 5, 10)
TOP_50_LIMIT = 50


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
    v2_files = MODEL_FILE_FNS[name](GRAMMAR_NULL_V2_DIR)
    v1_reports = _load(v1_files)
    v2_reports = _load(v2_files)
    n_runs = len(v1_reports)

    top3_v1 = top3_v2 = 0
    atleast2_v1 = atleast2_v2 = 0
    for d in v1_reports:
        top3 = _strict_top_n(d["ending_channel"], 3)
        if _all_match(top3, version=1):
            top3_v1 += 1
        if _all_match(top3, version=2):
            top3_v2 += 1
        if _count_matched(top3, version=1) >= 2:
            atleast2_v1 += 1
        if _count_matched(top3, version=2) >= 2:
            atleast2_v2 += 1

    top10_exceeds_null_p99_v2 = 0
    null_mean_by_n: dict[int, list[float]] = {n: [] for n in GRAMMAR_NS}
    null_p99_by_n: dict[int, list[float]] = {n: [] for n in GRAMMAR_NS}
    real_matched_v2_by_n: dict[int, list[float]] = {n: [] for n in GRAMMAR_NS}
    for d in v2_reports:
        gms = d["ending_channel"]["grammar_match_null_strict"]
        n10 = gms["10"]
        if n10["real_value"] > n10["p99"]:
            top10_exceeds_null_p99_v2 += 1
        for n in GRAMMAR_NS:
            null_mean_by_n[n].append(gms[str(n)]["mean"])
            null_p99_by_n[n].append(gms[str(n)]["p99"])
            real_matched_v2_by_n[n].append(gms[str(n)]["real_value"])

    return {
        "n_runs": n_runs,
        "v1_files": [f.name for f in v1_files],
        "v2_files": [f.name for f in v2_files],
        "strict_top3_all_grammar": {
            "v1": {"pass": top3_v1, "of": n_runs},
            "v2": {"pass": top3_v2, "of": n_runs},
        },
        "at_least_two_of_three": {
            "v1": {"pass": atleast2_v1, "of": n_runs},
            "v2": {"pass": atleast2_v2, "of": n_runs},
        },
        "top10_exceeds_null_p99_v2": {"pass": top10_exceeds_null_p99_v2, "of": n_runs},
        # "chance rate": the v2 null's own mean matched-by-chance count at each
        # n (CHANGELOG "0.6": "the null rate, which can also rise"), median and
        # range across this model's runs; the null p99 (the bar a real value
        # must clear) is reported alongside it.
        "null_mean_matched_v2_by_n": {str(n): _median_range(null_mean_by_n[n]) for n in GRAMMAR_NS},
        "null_p99_v2_by_n": {str(n): _median_range(null_p99_by_n[n]) for n in GRAMMAR_NS},
        "real_matched_v2_by_n": {str(n): _median_range(real_matched_v2_by_n[n]) for n in GRAMMAR_NS},
    }


def full_corpus_top_50() -> list[dict]:
    """The full Linear B corpus's top 50 ending alternations (stage 1, stem_min
    2, no subsampling -- exactly what produced ``kober-damos-seed0/1.json``'s
    real values, which are seed-independent since a null seed touches only the
    permutation draws), each regraded at version 1 and version 2. Deterministic:
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
            }
        )
    return out


def build_table() -> dict:
    top50 = full_corpus_top_50()
    gained = [a for a in top50 if a["rule_v1"] is None and a["rule_v2"] is not None]
    return {
        "protocol": "Kober 0.6, reference-list revision (CHANGELOG '0.6')",
        "grammar_match_ns": list(GRAMMAR_NS),
        "v1_source_dir": str(GRAMMAR_NULL_DIR.relative_to(ROOT)),
        "v2_source_dir": str(GRAMMAR_NULL_V2_DIR.relative_to(ROOT)),
        "models": {name: score_model(name) for name in MODEL_FILE_FNS},
        "full_corpus_top_50": top50,
        "full_corpus_top_50_gained_rule_under_v2": gained,
        "full_corpus_top_50_gained_rule_count": len(gained),
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
        "# Kober 0.6 reference-list-revision calibration table",
        "",
        table["protocol"] + ".",
        "",
        f"v1 source: `{table['v1_source_dir']}/`. v2 source: `{table['v2_source_dir']}/`.",
        "",
        "## Strict top three all grammar, v1 vs v2",
        "",
        "| model | N | v1 | v2 |",
        "|---|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        t3 = m["strict_top3_all_grammar"]
        lines.append(f"| {name} | {m['n_runs']} | {_fmt_pass(t3['v1'])} | {_fmt_pass(t3['v2'])} |")
    lines += [
        "",
        "## At least two of top three, v1 vs v2",
        "",
        "| model | N | v1 | v2 |",
        "|---|---:|---:|---:|",
    ]
    for name, m in table["models"].items():
        a2 = m["at_least_two_of_three"]
        lines.append(f"| {name} | {m['n_runs']} | {_fmt_pass(a2['v1'])} | {_fmt_pass(a2['v2'])} |")
    lines += [
        "",
        "## Top ten matched above its own v2 null 99th percentile (results/kober-grammar-null-v2/)",
        "",
        "| model | N | pass |",
        "|---|---:|---:|",
    ]
    for name, m in table["models"].items():
        lines.append(f"| {name} | {m['n_runs']} | {_fmt_pass(m['top10_exceeds_null_p99_v2'])} |")
    lines += [
        "",
        "## v2 null: mean matched by chance (median, range across the model's runs)",
        "",
        "| model | n=3 | n=5 | n=10 |",
        "|---|---|---|---|",
    ]
    for name, m in table["models"].items():
        mm = m["null_mean_matched_v2_by_n"]
        lines.append(f"| {name} | {_fmt_mr(mm['3'])} | {_fmt_mr(mm['5'])} | {_fmt_mr(mm['10'])} |")
    lines += [
        "",
        "## v2 null: 99th percentile (median, range across the model's runs)",
        "",
        "| model | n=3 | n=5 | n=10 |",
        "|---|---|---|---|",
    ]
    for name, m in table["models"].items():
        pp = m["null_p99_v2_by_n"]
        lines.append(f"| {name} | {_fmt_mr(pp['3'])} | {_fmt_mr(pp['5'])} | {_fmt_mr(pp['10'])} |")
    lines += [
        "",
        f"## Full corpus: top {TOP_50_LIMIT} alternations gaining a rule under v2",
        "",
        f"{table['full_corpus_top_50_gained_rule_count']} of {TOP_50_LIMIT}.",
        "",
        "| rank | ending pair | support | rule (v2) |",
        "|---:|---|---:|---|",
    ]
    for a in table["full_corpus_top_50_gained_rule_under_v2"]:
        lines.append(f"| {a['rank']} | {a['e1_label']} / {a['e2_label']} | {a['support']} | {a['rule_v2']} |")
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
