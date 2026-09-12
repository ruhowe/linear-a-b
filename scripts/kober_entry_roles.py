#!/usr/bin/env python3
"""Entry-role diagnostic on Linear B, CHANGELOG "Kober method" -> "Entry-role
diagnostic on Linear B" (2026-09-11). Pre-registered, read-only, no instrument:
this script does not import or modify anything that writes to results/ under a
Kober protocol version, and it does not touch ``src/kober/``. It runs on Linear
B only (``aegean.load("damos")``); nothing here runs on Linear A (ASSUMPTIONS.md
A-041 and A-078 do not extend to this diagnostic, which was never pre-registered
for Linear A).

    .venv/bin/python scripts/kober_entry_roles.py

Question (quoted from the CHANGELOG entry). Do the two forms of a real Linear B
paradigm occupy the same *role* on parallel tablets more often than chance?

Role definition (quoted). A tablet is a sequence of entries; an entry is a
maximal run of tokens on one line ending at a logogram or numeral or at the
line's end. A word's role is the tuple (series of the document, as
``aegean.analysis.hands.series_of``; index of its entry on the tablet, capped
at 3; position of the word within its entry, first, middle or last; the
logogram that closes the entry, or "none"). A word type's roles are the set of
roles of its tokens.

Unstated mechanics fixed here (ASSUMPTIONS.md section F, A-092 onward):
SEPARATOR tokens are skipped and never join an entry or end one; UNKNOWN
tokens sit inside an entry as non-word content; entry index is 0-based,
counted across the whole tablet in line then token order, saturating at 3;
"position among the WORD tokens of its entry" counts only the entry's
eligible WORD tokens (kind WORD, status CERTAIN, normalised label tuple of
two or more signs -- the same filter ``kober.words.extract_word_types``
applies); a role's series component is the string "none" when
``series_of`` returns ``None``, and "none" never counts as a shared series.

Statistic (quoted). For each ending alternation with support of three or more
in Kober 0.3 stage 1, and for each stem supporting it, the two forms' role
sets are compared: (a) same-role rate, the fraction of stem pairs whose two
forms share at least one role; (b) same-series rate, sharing at least one
series. Reported per alternation for the top ten and pooled over all with
support >= 3, with the real value, and beside it the rate under a null that
pairs each form with a random word type of the same length and the same
corpus frequency band (four bands), 200 draws.

Entry segmentation and role assignment (``Role``, ``build_entries_and_roles``,
and the token-eligibility filter ``_word_from_token``) moved into
``kober.roles`` 2026-09-11 (CHANGELOG "0.5"), since Kober 0.5's role-sharing
tie-break needs the same code. This script is now a caller: nothing below
changes, so this file's results
(``results/kober-entry-roles-damos.json``) are reproduced byte-for-byte.
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
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

from kober.paradigms import ChannelResult, Word, ending_channel, ranked_alternations  # noqa: E402
from kober.reference import is_grammar  # noqa: E402
from kober.roles import Role, _word_from_token, build_entries_and_roles  # noqa: E402
from kober.words import extract_word_types  # noqa: E402

PROTOCOL_REFERENCE = (
    'CHANGELOG.md, "Kober method" -> "Entry-role diagnostic on Linear B", '
    "2026-09-11 -- pre-registered, read-only, no instrument; ASSUMPTIONS.md "
    "A-092 to A-097 for the mechanics the CHANGELOG entry leaves unstated."
)

ROLE_DEFINITION = (
    "A tablet is a sequence of entries; an entry is a maximal run of tokens on "
    "one line ending at a LOGOGRAM or NUMERAL token or at the line's end (the "
    "closing token belongs to the entry; SEPARATOR tokens are skipped, not "
    "boundaries; UNKNOWN tokens are non-word content inside an entry). A word "
    "token's role is the tuple (series of the document via "
    "aegean.analysis.hands.series_of, or \"none\"; index of its entry on the "
    "tablet, 0-based, capped at 3; position of the word among the entry's "
    "eligible WORD tokens, first/middle/last, \"first\" if it is the only one; "
    "the closing token's text if it is a LOGOGRAM, else \"none\"). A word "
    "type's role set is the set of roles of its tokens. Word-token eligibility "
    "matches kober.words.extract_word_types: kind WORD, status CERTAIN, "
    "normalised labels, two or more signs."
)


# --------------------------------------------------------------------------- #
# Entries and roles: Role, _word_from_token, build_entries_and_roles now live
# in kober.roles (imported above), moved there 2026-09-11 for Kober 0.5.
# --------------------------------------------------------------------------- #


def build_word_freq(documents) -> Counter:
    """Token-occurrence frequency of every eligible word type, over the same
    filter ``_word_from_token`` applies (the same domain ``extract_word_types``
    extracts as a set)."""
    freq: Counter = Counter()
    for doc in documents:
        for tok in doc.tokens:
            w = _word_from_token(tok)
            if w is not None:
                freq[w] += 1
    return freq


# --------------------------------------------------------------------------- #
# Corpus-frequency bands (A-096) and the null's replacement pools.
# --------------------------------------------------------------------------- #


def build_frequency_bands(word_freq: Counter) -> tuple[dict[Word, int], tuple[int, int, int]]:
    """Four quartile bands of token-occurrence frequency, over all word types
    (A-096). Band 0 is freq <= p25, band 1 <= p50, band 2 <= p75, band 3 the
    rest; ties at a boundary fall in the lower band."""
    freqs_sorted = sorted(word_freq.values())
    n = len(freqs_sorted)

    def q(p: float) -> int:
        i = min(max(round(p * (n - 1)), 0), n - 1)
        return freqs_sorted[i]

    q25, q50, q75 = q(0.25), q(0.5), q(0.75)

    def band_of(f: int) -> int:
        if f <= q25:
            return 0
        if f <= q50:
            return 1
        if f <= q75:
            return 2
        return 3

    return {w: band_of(f) for w, f in word_freq.items()}, (q25, q50, q75)


def build_pools(word_freq: Counter, word_band: Mapping[Word, int]) -> dict[tuple[int, int], list[Word]]:
    """Word types grouped by (sign length, frequency band); each pool sorted
    for reproducible ``random.Random.choice`` draws (A-097: the pool includes
    the word type itself)."""
    pools: dict[tuple[int, int], list[Word]] = defaultdict(list)
    for w in word_freq:
        pools[(len(w), word_band[w])].append(w)
    for k in pools:
        pools[k].sort()
    return pools


# --------------------------------------------------------------------------- #
# Alternations and stem pairs (reusing paradigms.ending_channel; the stems
# behind an alternation are read from ChannelResult.anchors, which already
# exposes stem -> endings, so splits_for_word does not need recomputing).
# --------------------------------------------------------------------------- #


def alternations_with_stems(
    word_types: frozenset,
    stem_min: int,
    support_min: int,
) -> tuple[ChannelResult, dict[tuple[Word, Word], list[Word]]]:
    channel = ending_channel(word_types, stem_min=stem_min)
    qualifying = {pair: supp for pair, supp in channel.alternation_support.items() if supp >= support_min}
    stems_by_alt: dict[tuple[Word, Word], list[Word]] = {}
    for pair in qualifying:
        e1, e2 = pair
        stems = sorted(
            anchor for anchor, affixes in channel.anchors.items() if e1 in affixes and e2 in affixes
        )
        assert len(stems) == qualifying[pair], (pair, len(stems), qualifying[pair])
        stems_by_alt[pair] = stems
    return channel, stems_by_alt


# --------------------------------------------------------------------------- #
# Statistics: real values and the frequency-band-matched null.
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


def _series_set(roles: set[Role]) -> set[str]:
    return {r[0] for r in roles if r[0] != "none"}


def run_diagnostic(
    documents,
    stem_min: int,
    support_min: int,
    draws: int,
    seed: int,
) -> dict:
    t0 = time.time()

    roles_by_word, distinct_roles, entries_total, roles_total = build_entries_and_roles(documents)
    word_freq = build_word_freq(documents)

    word_types = extract_word_types(documents)  # canonical set, for parity/metadata
    assert set(word_freq.keys()) == word_types.words, "frequency-pass domain does not match extract_word_types"
    assert set(roles_by_word.keys()) == word_types.words, "role-pass domain does not match extract_word_types"

    word_band, quartiles = build_frequency_bands(word_freq)
    pools = build_pools(word_freq, word_band)

    _channel, stems_by_alt = alternations_with_stems(word_types.words, stem_min, support_min)

    # Ranked alternations (support desc, lexicographic tie-break), restricted
    # to support >= support_min, then the top ten of those.
    qualifying_support = {pair: len(stems) for pair, stems in stems_by_alt.items()}
    ranked = ranked_alternations(qualifying_support, limit=None)
    top_ranked = ranked[:10]

    # Flatten every (alternation, stem) into one ordered list of stem pairs,
    # fixed iteration order (alternation rank, then sorted stem) so the null's
    # single RNG stream is reproducible.
    order: list[tuple[Word, Word]] = [pair for pair, _supp in ranked]
    all_pairs: list[tuple[tuple[Word, Word], Word, Word]] = []  # (alt_pair, form1, form2)
    alt_pair_indices: dict[tuple[Word, Word], list[int]] = {}
    for pair in order:
        e1, e2 = pair
        idxs = []
        for stem in stems_by_alt[pair]:
            idxs.append(len(all_pairs))
            all_pairs.append((pair, stem + e1, stem + e2))
        alt_pair_indices[pair] = idxs

    # Real values.
    real_same_role = [bool(roles_by_word.get(f1, set()) & roles_by_word.get(f2, set())) for _p, f1, f2 in all_pairs]
    real_same_series = [
        bool(_series_set(roles_by_word.get(f1, set())) & _series_set(roles_by_word.get(f2, set())))
        for _p, f1, f2 in all_pairs
    ]

    def rate(flags: list[bool], idxs: list[int] | None = None) -> float:
        if idxs is None:
            vals = flags
        else:
            vals = [flags[i] for i in idxs]
        return (sum(vals) / len(vals)) if vals else 0.0

    pooled_real_same_role = rate(real_same_role)
    pooled_real_same_series = rate(real_same_series)

    # Grammar vs not, pooled, real only (A-098 not needed: spec asks for
    # information only, no null for this split).
    grammar_idx = [i for i, (pair, _f1, _f2) in enumerate(all_pairs) if is_grammar(*pair) is not None]
    not_grammar_idx = [i for i in range(len(all_pairs)) if i not in set(grammar_idx)]

    # Null: 200 draws, one seeded RNG stream over the fixed pair order.
    rng = random.Random(seed)
    pooled_null_same_role: list[float] = []
    pooled_null_same_series: list[float] = []
    per_alt_null_same_role: dict[tuple[Word, Word], list[float]] = {pair: [] for pair, _s in top_ranked}
    per_alt_null_same_series: dict[tuple[Word, Word], list[float]] = {pair: [] for pair, _s in top_ranked}

    for _draw in range(draws):
        draw_same_role: list[bool] = [False] * len(all_pairs)
        draw_same_series: list[bool] = [False] * len(all_pairs)
        for i, (_pair, f1, f2) in enumerate(all_pairs):
            key = (len(f2), word_band[f2])
            replacement = rng.choice(pools[key])
            r1 = roles_by_word.get(f1, set())
            r2 = roles_by_word.get(replacement, set())
            draw_same_role[i] = bool(r1 & r2)
            draw_same_series[i] = bool(_series_set(r1) & _series_set(r2))
        pooled_null_same_role.append(rate(draw_same_role))
        pooled_null_same_series.append(rate(draw_same_series))
        for pair, idxs in alt_pair_indices.items():
            if pair in per_alt_null_same_role:
                per_alt_null_same_role[pair].append(rate(draw_same_role, idxs))
                per_alt_null_same_series[pair].append(rate(draw_same_series, idxs))

    # Median role-set size by frequency band.
    sizes_by_band: dict[int, list[int]] = defaultdict(list)
    for w in word_freq:
        sizes_by_band[word_band[w]].append(len(roles_by_word.get(w, set())))
    role_set_size_by_band = {
        band: {
            "word_type_count": len(sizes_by_band.get(band, [])),
            "median_role_set_size": statistics.median(sizes_by_band[band]) if sizes_by_band.get(band) else 0,
        }
        for band in range(4)
    }

    top_10_entries = []
    for rank, (pair, supp) in enumerate(top_ranked, start=1):
        e1, e2 = pair
        idxs = alt_pair_indices[pair]
        top_10_entries.append(
            {
                "rank": rank,
                "e1_label": "-".join(e1),
                "e2_label": "-".join(e2),
                "support": supp,
                "rule": is_grammar(e1, e2),
                "same_role": _summarise(rate(real_same_role, idxs), per_alt_null_same_role[pair]),
                "same_series": _summarise(rate(real_same_series, idxs), per_alt_null_same_series[pair]),
            }
        )

    elapsed = time.time() - t0

    return {
        "protocol_reference": PROTOCOL_REFERENCE,
        "role_definition": ROLE_DEFINITION,
        "corpus": "damos",
        "stem_min": stem_min,
        "support_min": support_min,
        "draws": draws,
        "seed": seed,
        "counts": {
            "documents": len(documents) if hasattr(documents, "__len__") else None,
            "word_types": len(word_types.words),
            "entries": entries_total,
            "roles": roles_total,
            "distinct_roles": len(distinct_roles),
            "alternations_support_ge_min": len(stems_by_alt),
            "stem_pairs_pooled": len(all_pairs),
        },
        "frequency_bands": {
            "quartile_boundaries": {"p25": quartiles[0], "p50": quartiles[1], "p75": quartiles[2]},
            "role_set_size_by_band": {
                str(band): role_set_size_by_band[band] for band in range(4)
            },
        },
        "pooled": {
            "same_role": _summarise(pooled_real_same_role, pooled_null_same_role),
            "same_series": _summarise(pooled_real_same_series, pooled_null_same_series),
        },
        "grammar_vs_not_pooled": {
            "grammar": {
                "stem_pairs": len(grammar_idx),
                "same_role_rate": rate(real_same_role, grammar_idx),
            },
            "not_grammar": {
                "stem_pairs": len(not_grammar_idx),
                "same_role_rate": rate(real_same_role, not_grammar_idx),
            },
        },
        "top_10_alternations": top_10_entries,
        "wall_time_seconds": elapsed,
    }


# --------------------------------------------------------------------------- #
# Markdown printout.
# --------------------------------------------------------------------------- #


def render_markdown(report: dict) -> str:
    c = report["counts"]
    pooled = report["pooled"]
    gvn = report["grammar_vs_not_pooled"]
    fb = report["frequency_bands"]

    def fmt(nd: dict) -> str:
        return (
            f"real {nd['real_value']:.3f} (percentile {nd['real_percentile']:.1f}), "
            f"null mean {nd['mean']:.3f} sd {nd['sd']:.3f}, p95 {nd['p95']:.3f}, p99 {nd['p99']:.3f}"
        )

    lines = [
        f"# Entry-role diagnostic — {report['corpus']}, seed {report['seed']}",
        "",
        report["protocol_reference"],
        "",
        f"Documents: {c['documents']}. Word types: {c['word_types']}. Entries: {c['entries']}. "
        f"Roles assigned: {c['roles']}. Distinct roles: {c['distinct_roles']}.",
        "",
        f"Alternations with support >= {report['support_min']}: {c['alternations_support_ge_min']} "
        f"({c['stem_pairs_pooled']} stem pairs pooled).",
        "",
        "## Pooled",
        "",
        f"Same-role rate: {fmt(pooled['same_role'])}",
        "",
        f"Same-series rate: {fmt(pooled['same_series'])}",
        "",
        "## Grammar vs not, pooled (real only)",
        "",
        f"Grammar ({gvn['grammar']['stem_pairs']} pairs): same-role rate {gvn['grammar']['same_role_rate']:.3f}",
        f"Not grammar ({gvn['not_grammar']['stem_pairs']} pairs): same-role rate {gvn['not_grammar']['same_role_rate']:.3f}",
        "",
        "## Role-set size by frequency band",
        "",
        f"Quartile boundaries (token frequency): p25={fb['quartile_boundaries']['p25']} "
        f"p50={fb['quartile_boundaries']['p50']} p75={fb['quartile_boundaries']['p75']}",
        "",
        "| band | word types | median role-set size |",
        "|---:|---:|---:|",
    ]
    for band in range(4):
        row = fb["role_set_size_by_band"][str(band)]
        lines.append(f"| {band} | {row['word_type_count']} | {row['median_role_set_size']} |")

    lines += ["", "## Top ten alternations by support", "", "| rank | endings | support | rule | same-role | same-series |", "|---:|---|---:|---|---|---|"]
    for e in report["top_10_alternations"]:
        rule = e["rule"] or "-"
        lines.append(
            f"| {e['rank']} | {e['e1_label']} / {e['e2_label']} | {e['support']} | {rule} | "
            f"{fmt(e['same_role'])} | {fmt(e['same_series'])} |"
        )
    lines.append("")
    lines.append(f"Wall time: {report['wall_time_seconds']:.1f}s")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Entry point.
# --------------------------------------------------------------------------- #

_RESULTS_PATH = ROOT / "results" / "kober-entry-roles-damos.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem-min", type=int, default=2)
    ap.add_argument("--support-min", type=int, default=3)
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    corpus = aegean.load("damos")  # Linear B only; nothing here runs on Linear A
    documents = corpus.documents

    report = run_diagnostic(
        documents,
        stem_min=args.stem_min,
        support_min=args.support_min,
        draws=args.draws,
        seed=args.seed,
    )

    _RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    print(render_markdown(report))
    print(f"\nWrote {_RESULTS_PATH}")


if __name__ == "__main__":
    main()
