#!/usr/bin/env python3
"""S-001: mirror Linear B and test the Kober prefix channel as a positive control.

    .venv/bin/python spikes/S-001-mirror-linear-b/run.py

See BRIEF.md for the question, the two readings and why this sits outside the main
line. Per spikes/README.md rule 4, this script imports from ``src/`` (read-only)
and edits nothing there.

**The mirror.** Every Linear B word type from ``kober.words.extract_word_types`` on
``aegean.load("damos")`` is reversed sign-by-sign (``tuple(reversed(w))``), giving a
synthetic corpus of the same size and the same length distribution. Reversal is a
bijection on sign-label tuples, and ``kober.paradigms.splits_for_word``'s ending
split at k is ``(word[:n-k], word[n-k:])`` while its prefix split is ``(word[k:],
word[:k])``. Writing ``w`` for a real word and ``w' = reverse(w)`` for its mirror,
``w'[:n-k] = reverse(w[k:])`` and ``w'[n-k:] = reverse(w[:k])``: the ending channel's
split of ``w'`` is exactly the prefix channel's split of ``w``, with both the anchor
and the affix reversed. So a paradigm (an anchor with 2+ affixes) or an alternation's
support on one side is, by construction, identical to the matching value on the
other side once every affix is reversed back to real orientation -- not
approximately, exactly, because the map anchor -> reverse(anchor) is one-to-one.
Only the two nulls can differ, and only by Monte Carlo noise: N1 and N2 draw from
independent ``random.Random`` streams seeded once per run, over each word set's own
*sorted* order (``kober.nulls._group_by_length``), and the real and mirrored word
sets sort differently, so the specific shuffles applied are not the same draws
relabelled -- only, by the same symmetry argument, draws from the same underlying
null distribution.

**Stage 1 only, both directions, no --grid, no --context.** stem_min 2, 200 draws,
seed 0 throughout -- the same parameters as ``results/kober-damos-seed0.json``
(F-016). This script does not read that file; it rebuilds the real channels and
nulls itself from ``kober.paradigms``/``kober.nulls`` directly (``kober.report``'s
``build_report`` takes documents, not a bare word set, and the mirrored side has no
documents), so the real-side numbers here stand on their own rather than being
copied in, and an exact-match check (below) confirms they still agree with F-016's
reported figures.

**Grammar matching.** The strict top-ten count uses ``reference.is_grammar`` version
3 (Kober 0.8's full rule list, the current one) throughout, both real and mirrored
sides, so the two sides of each comparison are graded identically. F-016 itself used
version 1 and is not recomputed here; its own paradigm-count and support figures are
reproduced (see ``exact_match_checks`` and comparison 2 below), but its "9 of 10"
grammar count is a version-1 number and is not expected to match this run's
version-3 count exactly. On a mirrored channel, each ending is reversed back to its
real-word orientation before the call, per the brief -- this is what turns "a
reversed prefix" back into the prefix as it actually reads in the word.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

from kober.nulls import N2Result, NullDistribution, run_n1, run_n2  # noqa: E402
from kober.paradigms import (  # noqa: E402
    ChannelResult,
    Word,
    ending_channel,
    prefix_channel,
    ranked_alternations,
)
from kober.reference import is_grammar  # noqa: E402
from kober.words import extract_word_types  # noqa: E402

STEM_MIN = 2
DRAWS = 200
SEED = 0
GRAMMAR_VERSION = 3


def reverse_word(w: Word) -> Word:
    return tuple(reversed(w))


def mirror_words(words) -> frozenset:
    return frozenset(reverse_word(w) for w in words)


def word_str(w: Word) -> str:
    return "-".join(w)


def reversed_support_map(support) -> dict:
    """``support`` with every ending reversed back to real orientation, keyed by
    the reversed pair in sorted order (matching ``paradigms.build_channel``'s own
    key convention: ``combinations(sorted(affixes), 2)``)."""
    out: dict = {}
    for (a1, a2), sup in support.items():
        pair = tuple(sorted((reverse_word(a1), reverse_word(a2))))
        out[pair] = sup
    return out


def compare_supports(mirrored_support, real_support) -> dict:
    """Exact-match check (A-047's prediction): the mirrored channel's alternation
    support, with every ending reversed back, against the real channel it should
    equal pair-for-pair and value-for-value."""
    reversed_mirrored = reversed_support_map(mirrored_support)
    keys = set(reversed_mirrored) | set(real_support)
    mismatched = {
        k: [reversed_mirrored.get(k), real_support.get(k)]
        for k in keys
        if reversed_mirrored.get(k) != real_support.get(k)
    }
    return {
        "n_alternations_mirrored": len(reversed_mirrored),
        "n_alternations_real": len(real_support),
        "identical": not mismatched,
        "n_mismatched": len(mismatched),
        "example_mismatches": list(mismatched.items())[:5],
    }


def strict_top10(support, reverse: bool, version: int = GRAMMAR_VERSION) -> tuple[list[dict], int]:
    """The strict (exactly ten, tie-broken) top alternations by support
    (``paradigms.ranked_alternations``), each ending reversed back to real
    orientation first when ``reverse`` is set, then graded against
    ``reference.is_grammar`` at ``version``. Returns the rows and the matched
    count."""
    rows = []
    matched = 0
    for (e1, e2), sup in ranked_alternations(support, 10):
        d1, d2 = (reverse_word(e1), reverse_word(e2)) if reverse else (e1, e2)
        label1, label2 = sorted((word_str(d1), word_str(d2)))
        rule = is_grammar(d1, d2, version=version)
        if rule is not None:
            matched += 1
        rows.append({"e1": label1, "e2": label2, "support": sup, "rule": rule})
    return rows, matched


def nd(dist: NullDistribution) -> dict:
    return dist.as_dict()


def main() -> dict:
    corpus = aegean.load("damos")
    documents = corpus.documents

    real_types = extract_word_types(documents)
    real_words = real_types.words
    mirror = mirror_words(real_words)
    assert len(mirror) == len(real_words), "reversal must be a bijection on the word-type set"

    ending_R: ChannelResult = ending_channel(real_words, stem_min=STEM_MIN)
    prefix_R: ChannelResult = prefix_channel(real_words, stem_min=STEM_MIN)
    ending_M: ChannelResult = ending_channel(mirror, stem_min=STEM_MIN)
    prefix_M: ChannelResult = prefix_channel(mirror, stem_min=STEM_MIN)

    check_1 = compare_supports(ending_M.alternation_support, prefix_R.alternation_support)
    check_2 = compare_supports(prefix_M.alternation_support, ending_R.alternation_support)

    n1_R = run_n1(real_words, STEM_MIN, DRAWS, SEED, ending_R, prefix_R)
    n1_M = run_n1(mirror, STEM_MIN, DRAWS, SEED, ending_M, prefix_M)

    n2_R_ending: N2Result = run_n2(real_words, STEM_MIN, DRAWS, SEED, mirror=False, real_channel=ending_R)
    n2_R_prefix: N2Result = run_n2(real_words, STEM_MIN, DRAWS, SEED, mirror=True, real_channel=prefix_R)
    n2_M_ending: N2Result = run_n2(mirror, STEM_MIN, DRAWS, SEED, mirror=False, real_channel=ending_M)
    n2_M_prefix: N2Result = run_n2(mirror, STEM_MIN, DRAWS, SEED, mirror=True, real_channel=prefix_M)

    top10_mirrored_ending, matched_mirrored_ending = strict_top10(ending_M.alternation_support, reverse=True)
    top10_real_prefix, matched_real_prefix = strict_top10(prefix_R.alternation_support, reverse=False)
    top10_mirrored_prefix, matched_mirrored_prefix = strict_top10(prefix_M.alternation_support, reverse=True)
    top10_real_ending, matched_real_ending = strict_top10(ending_R.alternation_support, reverse=False)

    payload = {
        "question": (
            "Does the Kober prefix channel, read as the ending channel on a mirrored "
            "(reversed) Linear B corpus, recover the same stems, support and grammar "
            "as the real prefix/ending channels do directly (A-047)?"
        ),
        "protocol": {
            "corpus": "damos",
            "stem_min": STEM_MIN,
            "draws": DRAWS,
            "seed": SEED,
            "grammar_reference_version": GRAMMAR_VERSION,
            "word_types": len(real_words),
        },
        "exact_match_checks": {
            "mirrored_ending_vs_real_prefix": check_1,
            "mirrored_prefix_vs_real_ending": check_2,
        },
        "comparison_1_mirrored_ending_vs_real_prefix": {
            "paradigm_count": {
                "mirrored_ending": ending_M.paradigm_count_total,
                "real_prefix": prefix_R.paradigm_count_total,
                "difference": ending_M.paradigm_count_total - prefix_R.paradigm_count_total,
            },
            "n1_paradigm_count_null": {
                "mirrored_ending": nd(n1_M.ending_paradigm_count),
                "real_prefix": nd(n1_R.prefix_paradigm_count),
            },
            "max_support": {
                "mirrored_ending": nd(n2_M_ending.max_support),
                "real_prefix": nd(n2_R_prefix.max_support),
            },
            "top_10_alternations": {
                "mirrored_ending_as_real_prefixes": top10_mirrored_ending,
                "real_prefix": top10_real_prefix,
            },
            "strict_top_10_grammar_count_v3": {
                "mirrored_ending": matched_mirrored_ending,
                "real_prefix": matched_real_prefix,
            },
        },
        "comparison_2_mirrored_prefix_vs_real_ending": {
            "paradigm_count": {
                "mirrored_prefix": prefix_M.paradigm_count_total,
                "real_ending": ending_R.paradigm_count_total,
                "difference": prefix_M.paradigm_count_total - ending_R.paradigm_count_total,
            },
            "n1_paradigm_count_null": {
                "mirrored_prefix": nd(n1_M.prefix_paradigm_count),
                "real_ending": nd(n1_R.ending_paradigm_count),
            },
            "max_support": {
                "mirrored_prefix": nd(n2_M_prefix.max_support),
                "real_ending": nd(n2_R_ending.max_support),
            },
            "top_10_alternations": {
                "mirrored_prefix_as_real_endings": top10_mirrored_prefix,
                "real_ending": top10_real_ending,
            },
            "strict_top_10_grammar_count_v3": {
                "mirrored_prefix": matched_mirrored_prefix,
                "real_ending": matched_real_ending,
            },
        },
    }

    out_dir = Path(__file__).resolve().parent
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return payload


if __name__ == "__main__":
    data = main()
    print(json.dumps(data["protocol"], indent=2))
    print(json.dumps(data["exact_match_checks"], indent=2, default=str))
    for key in ("comparison_1_mirrored_ending_vs_real_prefix", "comparison_2_mirrored_prefix_vs_real_ending"):
        c = data[key]
        print(f"\n== {key}")
        print("paradigm_count:", c["paradigm_count"])
        print("strict_top_10_grammar_count_v3:", c["strict_top_10_grammar_count_v3"])
