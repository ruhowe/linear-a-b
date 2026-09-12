#!/usr/bin/env python3
"""List homogeneity on Linear B (CHANGELOG "Kober method" -> "List homogeneity
on Linear B", 2026-09-11). Pre-registered, read-only, no instrument: measures
Kober's Assumptions 4, 6 and 7 (docs/works/kober1946.md, "The method, as she
states it") directly on Linear B, before any list-anchored statistic is built
on top of the paradigm code. Imports from ``src/kober/`` are read-only; this
script does not modify anything under ``src/kober/`` or ``scripts/kober_run.py``.
Nothing here runs on Linear A. No interpretation: this script reports numbers
only, the readings live in CHANGELOG and any finding written from this file.

    .venv/bin/python scripts/kober_list_homogeneity.py

Statistic 1, listed words (quoted from the CHANGELOG entry). A listed word is
a WORD, CERTAIN, normalised, two-or-more-sign token that is followed on its line, skipping
SEPARATOR tokens, by a LOGOGRAM or NUMERAL token. A document's listed words
are its listed-word tokens in document (line, then token) order. Entry
eligibility reuses ``kober.roles._word_from_token`` (A-092 to A-097's
eligibility filter: kind WORD, status CERTAIN, normalised labels, two or more
signs) and the line-walk convention ``kober.roles.build_entries_and_roles``
and ``scripts/kober_entry_roles.py`` already use for entry segmentation. Final
sign = the token's last normalised sign label.

Statistic 2, per-document homogeneity. For each document with at least three
listed words, homogeneity is the fraction of its listed words whose final
sign equals the document's modal final sign (a tie among final signs at the
maximum count is read as "the largest fraction", which every tied sign
produces identically, so the homogeneity *value* never depends on which tied
sign is treated as "the" mode -- only statistic 4's per-form check needs the
full set of tied modal signs, see below). Reported: count of documents at or
above three listed words; median and quartiles of homogeneity; count at
homogeneity >= 0.5; pooled homogeneity (sum of per-document modal counts,
divided by the sum of per-document listed-word counts); each of those also
restricted to documents of one series prefix letter (first character of
``aegean.analysis.hands.series_of(doc)``), for the ten letters with the most
eligible documents (A-103).

Statistic 3, the null. 200 seeded draws (default; ``--draws``) shuffle the
final signs of every listed-word token in the corpus across tokens, holding
each document's listed-word count and its tokens' non-final signs fixed (a
document below the three-word bar still contributes its tokens to the shuffle
pool and keeps its token count, per the CHANGELOG spec, even though it is
excluded from every reported per-document statistic). The same
per-document and pooled statistics are recomputed per draw; mean, sd, 95th
and 99th percentile and the real value's percentile are reported for the
pooled homogeneity and for the count of documents at homogeneity >= 0.5.

Statistic 4, Assumption 7 as a number. The top twenty ending alternations by
support from ``kober.paradigms.ending_channel`` on the full Linear B
word-type set (stem_min 2); supporting stems read from
``ChannelResult.anchors``, the same convention
``scripts/kober_entry_roles.py::alternations_with_stems`` uses. For each
alternation and each of its supporting stems, the two forms (stem + each
ending) are word types; a form "has a homogeneous list" if it occurs as a
listed-word token in at least one document (>= 3 listed words) whose modal
final sign includes that form's own final sign (using the full tied-modal-sign
set, not an arbitrary single mode, so a form matching any tied winner counts;
A-101).
An alternation's fraction is the share of its supporting stem pairs where
*both* forms have a homogeneous list; reported per alternation with support
and ``kober.reference.is_grammar``'s rule name, pooled over the twenty
(matches summed over the twenty, divided by stems summed over the twenty),
and split grammar vs not grammar (same pooling, real values only; A-104).
Null: the same fraction under the shuffled final signs, 200 draws -- the same
draws statistic 3 uses (A-102), since both statistics are read off the same
per-draw per-document modal-sign map and no extra randomness is needed (the
modal signs change per draw; the forms' own final signs, read from the fixed
word type, do not) -- with mean, p99 and real percentile per alternation and
pooled.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import Document  # noqa: E402

from kober.lists import DocListing, doc_modal, extract_listed_words  # noqa: E402
from kober.paradigms import ChannelResult, Word, ending_channel, ranked_alternations  # noqa: E402
from kober.reference import is_grammar  # noqa: E402
from kober.words import extract_word_types  # noqa: E402

PROTOCOL_REFERENCE = (
    'CHANGELOG.md, "Kober method" -> "List homogeneity on Linear B", '
    "2026-09-11 -- pre-registered, read-only, no instrument; docs/works/kober1946.md "
    '"The method, as she states it" for Assumptions 4, 6 and 7; ASSUMPTIONS.md '
    "section F, A-101 onward, for the mechanics the CHANGELOG entry leaves unstated."
)


# --------------------------------------------------------------------------- #
# Statistic 1: listed words, per document.
# --------------------------------------------------------------------------- #


# DocListing, extract_listed_words and doc_modal moved 2026-09-11 to
# kober.lists (CHANGELOG "0.7", A-116): Kober 0.7's list-support tie-break
# (paradigms.list_support_counts, nulls.run_n2) needs the same listed-word
# and per-document modal-final-sign logic this diagnostic already computed.
# Straight move, not a rewrite -- this script's own results file
# (results/kober-list-homogeneity-damos.json) is reproduced byte-for-byte on
# every real value.


# --------------------------------------------------------------------------- #
# Statistic 2: per-document and pooled homogeneity, overall and by letter.
# --------------------------------------------------------------------------- #


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * (pct / 100)
    lo, hi = int(pos), min(int(pos) + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def _percentile_rank(value: float, values: list[float]) -> float:
    if not values:
        return 0.0
    return 100.0 * sum(1 for v in values if v <= value) / len(values)


def _summarise(real_value: float, draws: list[float]) -> dict:
    sv = sorted(draws)
    return {
        "draws": len(draws),
        "mean": statistics.mean(draws) if draws else 0.0,
        "sd": statistics.pstdev(draws) if len(draws) > 1 else 0.0,
        "p95": _percentile(sv, 95),
        "p99": _percentile(sv, 99),
        "real_value": real_value,
        "real_percentile": _percentile_rank(real_value, draws),
    }


def summarise_documents(records: Sequence[DocListing]) -> dict:
    """Document-level homogeneity statistics, restricted to documents with
    at least three listed words."""
    eligible = [r for r in records if len(r.listed) >= 3]
    homogeneities: list[float] = []
    modal_counts: list[int] = []
    totals: list[int] = []
    ge_half = 0
    for r in eligible:
        final_signs = [w[-1] for w in r.listed]
        max_count, _modal = doc_modal(final_signs)
        total = len(r.listed)
        homog = max_count / total
        homogeneities.append(homog)
        modal_counts.append(max_count)
        totals.append(total)
        if homog >= 0.5:
            ge_half += 1
    pooled = (sum(modal_counts) / sum(totals)) if totals else 0.0
    sh = sorted(homogeneities)
    return {
        "n_documents_eligible": len(eligible),
        "median_homogeneity": statistics.median(homogeneities) if homogeneities else None,
        "q1_homogeneity": _percentile(sh, 25) if homogeneities else None,
        "q3_homogeneity": _percentile(sh, 75) if homogeneities else None,
        "count_homogeneity_ge_half": ge_half,
        "pooled_homogeneity": pooled,
    }


def by_series_letter(records: Sequence[DocListing], top_n: int = 10) -> dict[str, dict]:
    """Document-level statistics restricted to each series prefix letter, for
    the ``top_n`` letters with the most eligible (>= 3 listed words)
    documents (A-103: documents with no series, ``series_of`` returning
    ``None``, are excluded from this breakdown only, not from the overall
    statistics)."""
    eligible = [r for r in records if len(r.listed) >= 3 and r.series_letter is not None]
    groups: dict[str, list[DocListing]] = defaultdict(list)
    for r in eligible:
        groups[r.series_letter].append(r)
    ranked_letters = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:top_n]
    return {letter: summarise_documents(recs) for letter, recs in ranked_letters}


# --------------------------------------------------------------------------- #
# Statistic 4: top twenty ending alternations and Assumption 7 as a number.
# --------------------------------------------------------------------------- #


def top20_with_stems(
    word_types: frozenset[Word], stem_min: int = 2
) -> tuple[ChannelResult, list[tuple[tuple[Word, Word], list[Word]]]]:
    """The top twenty ending alternations by support, each with its
    supporting stems read from ``ChannelResult.anchors`` (the convention
    ``scripts/kober_entry_roles.py::alternations_with_stems`` uses)."""
    channel = ending_channel(word_types, stem_min=stem_min)
    ranked = ranked_alternations(channel.alternation_support, limit=20)
    result: list[tuple[tuple[Word, Word], list[Word]]] = []
    for pair, support in ranked:
        e1, e2 = pair
        stems = sorted(
            anchor for anchor, affixes in channel.anchors.items() if e1 in affixes and e2 in affixes
        )
        assert len(stems) == support, (pair, len(stems), support)
        result.append((pair, stems))
    return channel, result


def build_form_doc_index(records: Sequence[DocListing]) -> dict[Word, set[int]]:
    """form -> indices of eligible (>= 3 listed words) documents where the
    form occurs as a listed-word token, from the real (unshuffled) corpus."""
    out: dict[Word, set[int]] = defaultdict(set)
    for idx, r in enumerate(records):
        if len(r.listed) < 3:
            continue
        for w in r.listed:
            out[w].add(idx)
    return out


def real_doc_modal_signs(records: Sequence[DocListing]) -> dict[int, frozenset[str]]:
    out: dict[int, frozenset[str]] = {}
    for idx, r in enumerate(records):
        if len(r.listed) < 3:
            continue
        final_signs = [w[-1] for w in r.listed]
        _max_count, modal = doc_modal(final_signs)
        out[idx] = modal
    return out


def form_has_homogeneous_list(
    form: Word,
    form_doc_index: Mapping[Word, set[int]],
    doc_modal_signs: Mapping[int, frozenset[str]],
) -> bool:
    doc_ids = form_doc_index.get(form)
    if not doc_ids:
        return False
    target = form[-1]
    return any(target in doc_modal_signs.get(i, frozenset()) for i in doc_ids)


def compute_alternation_stats(
    top20: Sequence[tuple[tuple[Word, Word], list[Word]]],
    form_doc_index: Mapping[Word, set[int]],
    doc_modal_signs: Mapping[int, frozenset[str]],
) -> dict:
    entries = []
    total_matches = total_stems = 0
    grammar_matches = grammar_stems = 0
    not_grammar_matches = not_grammar_stems = 0
    for pair, stems in top20:
        e1, e2 = pair
        matches = 0
        for stem in stems:
            w1, w2 = stem + e1, stem + e2
            if form_has_homogeneous_list(w1, form_doc_index, doc_modal_signs) and form_has_homogeneous_list(
                w2, form_doc_index, doc_modal_signs
            ):
                matches += 1
        support = len(stems)
        rule = is_grammar(e1, e2)
        entries.append(
            {
                "e1": "-".join(e1),
                "e2": "-".join(e2),
                "support": support,
                "matches": matches,
                "fraction": (matches / support) if support else 0.0,
                "rule": rule,
            }
        )
        total_matches += matches
        total_stems += support
        if rule is not None:
            grammar_matches += matches
            grammar_stems += support
        else:
            not_grammar_matches += matches
            not_grammar_stems += support
    return {
        "entries": entries,
        "pooled": {
            "matches": total_matches,
            "stem_pairs": total_stems,
            "fraction": (total_matches / total_stems) if total_stems else 0.0,
        },
        "grammar_vs_not": {
            "grammar": {
                "matches": grammar_matches,
                "stem_pairs": grammar_stems,
                "fraction": (grammar_matches / grammar_stems) if grammar_stems else 0.0,
            },
            "not_grammar": {
                "matches": not_grammar_matches,
                "stem_pairs": not_grammar_stems,
                "fraction": (not_grammar_matches / not_grammar_stems) if not_grammar_stems else 0.0,
            },
        },
    }


# --------------------------------------------------------------------------- #
# The null: 200 shared draws feeding statistics 3 and 4.
# --------------------------------------------------------------------------- #


def build_occurrence_pool(records: Sequence[DocListing]) -> tuple[list[int], list[str]]:
    """(doc index, final sign) per listed-word occurrence corpus-wide,
    including documents below the three-word eligibility bar: they still
    contribute tokens to the shuffle pool and keep their token count, per the
    CHANGELOG's "each document keeps its token count" and "their words are
    still in the pool"."""
    doc_idx: list[int] = []
    signs: list[str] = []
    for idx, r in enumerate(records):
        for w in r.listed:
            doc_idx.append(idx)
            signs.append(w[-1])
    return doc_idx, signs


def run_null(
    records: Sequence[DocListing],
    form_doc_index: Mapping[Word, set[int]],
    top20: Sequence[tuple[tuple[Word, Word], list[Word]]],
    seed: int,
    draws: int,
) -> dict:
    doc_idx, signs = build_occurrence_pool(records)
    eligible_idx = [i for i, r in enumerate(records) if len(r.listed) >= 3]
    eligible_total = {i: len(records[i].listed) for i in eligible_idx}
    total_stem_pairs = sum(len(stems) for _pair, stems in top20)

    rng = random.Random(seed)
    pooled_homog_draws: list[float] = []
    count_ge_half_draws: list[float] = []
    per_alt_draws: dict[tuple[Word, Word], list[float]] = {pair: [] for pair, _stems in top20}
    pooled_alt_draws: list[float] = []

    for _draw in range(draws):
        shuffled = signs.copy()
        rng.shuffle(shuffled)
        doc_counters: dict[int, Counter] = defaultdict(Counter)
        for di, sign in zip(doc_idx, shuffled):
            doc_counters[di][sign] += 1

        doc_modal_signs: dict[int, frozenset[str]] = {}
        total_modal = 0
        total_listed = 0
        ge_half = 0
        for i in eligible_idx:
            counter = doc_counters.get(i, Counter())
            total = eligible_total[i]
            max_count = max(counter.values()) if counter else 0
            modal = frozenset(s for s, c in counter.items() if c == max_count) if counter else frozenset()
            doc_modal_signs[i] = modal
            homog = (max_count / total) if total else 0.0
            total_modal += max_count
            total_listed += total
            if homog >= 0.5:
                ge_half += 1
        pooled_homog_draws.append((total_modal / total_listed) if total_listed else 0.0)
        count_ge_half_draws.append(ge_half)

        draw_total_matches = 0
        for pair, stems in top20:
            e1, e2 = pair
            matches = 0
            for stem in stems:
                w1, w2 = stem + e1, stem + e2
                if form_has_homogeneous_list(w1, form_doc_index, doc_modal_signs) and form_has_homogeneous_list(
                    w2, form_doc_index, doc_modal_signs
                ):
                    matches += 1
            per_alt_draws[pair].append((matches / len(stems)) if stems else 0.0)
            draw_total_matches += matches
        pooled_alt_draws.append((draw_total_matches / total_stem_pairs) if total_stem_pairs else 0.0)

    return {
        "pooled_homogeneity": pooled_homog_draws,
        "count_ge_half": count_ge_half_draws,
        "per_alternation": per_alt_draws,
        "pooled_alternations": pooled_alt_draws,
    }


# --------------------------------------------------------------------------- #
# Assembly.
# --------------------------------------------------------------------------- #


def build_report(documents: Sequence[Document], seed: int, draws: int, stem_min: int = 2) -> dict:
    t0 = time.time()

    records = extract_listed_words(documents)
    doc_overall = summarise_documents(records)
    doc_by_letter = by_series_letter(records, top_n=10)

    word_types = extract_word_types(documents)
    _channel, top20 = top20_with_stems(word_types.words, stem_min=stem_min)

    form_doc_index = build_form_doc_index(records)
    doc_modal_signs_real = real_doc_modal_signs(records)
    alt_stats = compute_alternation_stats(top20, form_doc_index, doc_modal_signs_real)

    null = run_null(records, form_doc_index, top20, seed, draws)

    document_null = {
        "pooled_homogeneity": _summarise(doc_overall["pooled_homogeneity"], null["pooled_homogeneity"]),
        "count_ge_half": _summarise(float(doc_overall["count_homogeneity_ge_half"]), null["count_ge_half"]),
    }

    alt_entries_with_null = []
    for entry, (pair, _stems) in zip(alt_stats["entries"], top20):
        alt_entries_with_null.append(
            {**entry, "null": _summarise(entry["fraction"], null["per_alternation"][pair])}
        )

    pooled_alt_null = _summarise(alt_stats["pooled"]["fraction"], null["pooled_alternations"])

    total_listed = sum(len(r.listed) for r in records)
    total_listed_eligible = sum(len(r.listed) for r in records if len(r.listed) >= 3)

    elapsed = time.time() - t0

    return {
        "protocol_reference": PROTOCOL_REFERENCE,
        "corpus": "damos",
        "stem_min": stem_min,
        "draws": draws,
        "seed": seed,
        "counts": {
            "documents": len(records),
            "documents_eligible": doc_overall["n_documents_eligible"],
            "listed_word_tokens_total": total_listed,
            "listed_word_tokens_in_eligible_documents": total_listed_eligible,
            "word_types": len(word_types.words),
        },
        "document_level": {
            "overall": doc_overall,
            "by_series_letter": doc_by_letter,
        },
        "document_level_null": document_null,
        "alternations": {
            "top_20": alt_entries_with_null,
            "pooled": {**alt_stats["pooled"], "null": pooled_alt_null},
            "grammar_vs_not": alt_stats["grammar_vs_not"],
        },
        "wall_time_seconds": elapsed,
    }


# --------------------------------------------------------------------------- #
# Markdown printout.
# --------------------------------------------------------------------------- #


def render_markdown(report: dict) -> str:
    c = report["counts"]
    dl = report["document_level"]["overall"]
    dn = report["document_level_null"]
    alt = report["alternations"]

    def fmt(nd: dict) -> str:
        return (
            f"real {nd['real_value']:.3f} (percentile {nd['real_percentile']:.1f}), "
            f"null mean {nd['mean']:.3f} sd {nd['sd']:.3f}, p95 {nd['p95']:.3f}, p99 {nd['p99']:.3f}"
        )

    lines = [
        f"# List homogeneity — {report['corpus']}, seed {report['seed']}",
        "",
        report["protocol_reference"],
        "",
        f"Documents: {c['documents']} ({c['documents_eligible']} with >= 3 listed words). "
        f"Listed-word tokens: {c['listed_word_tokens_total']} "
        f"({c['listed_word_tokens_in_eligible_documents']} in eligible documents). "
        f"Word types: {c['word_types']}.",
        "",
        "## Document-level homogeneity, overall",
        "",
        f"n = {dl['n_documents_eligible']}, median {dl['median_homogeneity']:.3f}, "
        f"q1 {dl['q1_homogeneity']:.3f}, q3 {dl['q3_homogeneity']:.3f}, "
        f"count >= 0.5: {dl['count_homogeneity_ge_half']}, "
        f"pooled homogeneity {dl['pooled_homogeneity']:.3f}",
        "",
        "## Document-level homogeneity, by series letter (top 10 by eligible document count)",
        "",
        "| letter | n | median | q1 | q3 | count >= 0.5 | pooled |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for letter, s in report["document_level"]["by_series_letter"].items():
        lines.append(
            f"| {letter} | {s['n_documents_eligible']} | {s['median_homogeneity']:.3f} | "
            f"{s['q1_homogeneity']:.3f} | {s['q3_homogeneity']:.3f} | "
            f"{s['count_homogeneity_ge_half']} | {s['pooled_homogeneity']:.3f} |"
        )

    lines += [
        "",
        "## Null, pooled statistics",
        "",
        f"Pooled homogeneity: {fmt(dn['pooled_homogeneity'])}",
        "",
        f"Count of documents >= 0.5: {fmt(dn['count_ge_half'])}",
        "",
        "## Top twenty ending alternations, Assumption 7 fraction",
        "",
        "| rank | endings | support | rule | fraction | null |",
        "|---:|---|---:|---|---:|---|",
    ]
    for rank, e in enumerate(alt["top_20"], start=1):
        rule = e["rule"] or "-"
        lines.append(
            f"| {rank} | {e['e1']} / {e['e2']} | {e['support']} | {rule} | "
            f"{e['fraction']:.3f} | {fmt(e['null'])} |"
        )

    lines += [
        "",
        f"Pooled over the twenty: {alt['pooled']['matches']}/{alt['pooled']['stem_pairs']} = "
        f"{alt['pooled']['fraction']:.3f}. Null: {fmt(alt['pooled']['null'])}",
        "",
        f"Grammar ({alt['grammar_vs_not']['grammar']['stem_pairs']} pairs): "
        f"{alt['grammar_vs_not']['grammar']['fraction']:.3f}. "
        f"Not grammar ({alt['grammar_vs_not']['not_grammar']['stem_pairs']} pairs): "
        f"{alt['grammar_vs_not']['not_grammar']['fraction']:.3f}",
        "",
        f"Wall time: {report['wall_time_seconds']:.1f}s",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Entry point.
# --------------------------------------------------------------------------- #

_RESULTS_PATH = ROOT / "results" / "kober-list-homogeneity-damos.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem-min", type=int, default=2)
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    corpus = aegean.load("damos")  # Linear B only; nothing here runs on Linear A
    documents = corpus.documents

    report = build_report(documents, seed=args.seed, draws=args.draws, stem_min=args.stem_min)

    _RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    print(render_markdown(report))
    print(f"\nWrote {_RESULTS_PATH}")


if __name__ == "__main__":
    main()
