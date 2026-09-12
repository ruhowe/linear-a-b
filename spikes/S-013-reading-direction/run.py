#!/usr/bin/env python3
"""S-013: does reversing one support type's words raise the paradigm-count ratio?

    .venv/bin/python spikes/S-013-reading-direction/run.py

See BRIEF.md for the question and the two readings. Per spikes/README.md rule 4,
this script imports from ``src/`` (read-only) and edits nothing there.

**Grouping.** Every document has one support type (``kober.context.support_type_of``,
lower-cased ``doc.meta.support`` or ``"unknown"``). A support type qualifies for its
own reversed run when its documents contribute at least 50 eligible word tokens
(``kind WORD``, ``status CERTAIN``, normalised, >= 2 signs -- the same eligibility
``kober.words.extract_word_types`` applies, counted here per token rather than per
type since the brief's threshold is on tokens).

**Reversal.** For a target support type, every eligible token belonging to a
document of that type has its own sign-label tuple reversed (``tuple(reversed(...))``)
before the corpus-wide word-type set is built; tokens from every other document are
left alone. This is the token-level generalisation of S-001's whole-corpus mirror
(``spikes/S-001-mirror-linear-b``): reversing every support type at once (the
"all-reversed" condition below) must reduce to S-001's mirror and, by F-037's
bijection, the resulting ending channel must equal the unreversed corpus's prefix
channel exactly. That equality is checked directly, not assumed.

**Statistic.** Stage 1's ending-channel paradigm count against its N1 null (100
draws, ``kober.nulls.run_n1``), reported as the ratio real/N1-mean. The unreversed
corpus's own ratio is the baseline; its Monte Carlo noise is measured by rerunning
N1 (100 draws each) at seeds 0-19 on the *same* unreversed word set and taking the
population standard deviation of the resulting 20 ratios (the real value is fixed,
so only the null mean varies with seed). Seed 0 is both the primary seed used for
every reversed condition's ratio and one of the 20 noise seeds, so the reversed and
baseline ratios being compared are drawn under matching conditions.

**Hash-seed reproducibility, found while running this spike.** ``kober.nulls``'s
``_group_by_length`` sorts the words *within* each length class but builds the
class dict by iterating the input word set directly, so the class dict's own key
order (and, with one shared ``rng`` object drawing across classes in sequence,
the order the RNG stream is consumed in) depends on ``frozenset`` iteration order
over sign-label tuples -- which depends on Python's per-process string hash
randomisation, not on the ``seed`` argument. Two runs of this script with the
same seed gave different numbers before this was found (confirmed by diffing
``results.json`` across two runs). Not a bug to fix here (nothing under ``src/``
is touched by this spike), but this script pins ``PYTHONHASHSEED=0`` by
re-executing itself once if unset, so its own results are reproducible run to
run; the observation is worth a CHANGELOG/ASSUMPTIONS note independent of this
spike's own question.
"""

from __future__ import annotations

import os
import sys

if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import json  # noqa: E402
import statistics  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

from aegean.core.model import Document, ReadingStatus, TokenKind  # noqa: E402

from kober.context import support_type_of  # noqa: E402
from kober.nulls import N1Result, run_n1  # noqa: E402
from kober.paradigms import ChannelResult, Word, ending_channel, prefix_channel  # noqa: E402
from kober.words import _normalise_label, extract_word_types  # noqa: E402

STEM_MIN = 2
DRAWS = 100
PRIMARY_SEED = 0
NOISE_SEEDS = list(range(20))
MIN_TOKENS = 50


def eligible_labels(tok) -> Word | None:
    if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
        return None
    labels = tuple(_normalise_label(label)[0] for label in tok.signs)
    return labels if len(labels) >= 2 else None


def token_counts_by_support(documents: list[Document]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for doc in documents:
        st = support_type_of(doc)
        for tok in doc.tokens:
            if eligible_labels(tok) is not None:
                counts[st] = counts.get(st, 0) + 1
    return counts


def build_words(documents: list[Document], target_support: str | None, reverse_all: bool = False) -> frozenset[Word]:
    """The corpus's word-type set with reversal applied to every eligible token
    whose document's support type is ``target_support`` (or every document, if
    ``reverse_all``); every other token is untouched. ``target_support=None`` and
    ``reverse_all=False`` is the plain unreversed extraction."""
    words: set[Word] = set()
    for doc in documents:
        st = support_type_of(doc)
        reverse = reverse_all or (target_support is not None and st == target_support)
        for tok in doc.tokens:
            labels = eligible_labels(tok)
            if labels is None:
                continue
            words.add(tuple(reversed(labels)) if reverse else labels)
    return frozenset(words)


def nd(dist) -> dict:
    return dist.as_dict()


def ratio_at_seed(words: frozenset[Word], ending: ChannelResult, prefix: ChannelResult, seed: int) -> tuple[float, N1Result]:
    n1 = run_n1(words, STEM_MIN, DRAWS, seed, ending, prefix)
    mean = n1.ending_paradigm_count.mean
    ratio = ending.paradigm_count_total / mean if mean else float("inf")
    return ratio, n1


def run_corpus(name: str, documents: list[Document]) -> dict:
    token_counts = token_counts_by_support(documents)
    qualifying = sorted(st for st, n in token_counts.items() if n >= MIN_TOKENS)

    base_words = build_words(documents, target_support=None)
    check_words = extract_word_types(documents).words
    assert base_words == check_words, "unreversed extraction must match kober.words.extract_word_types exactly"

    base_ending = ending_channel(base_words, stem_min=STEM_MIN)
    base_prefix = prefix_channel(base_words, stem_min=STEM_MIN)

    noise_ratios: list[float] = []
    primary_n1: N1Result | None = None
    for seed in NOISE_SEEDS:
        ratio, n1 = ratio_at_seed(base_words, base_ending, base_prefix, seed)
        noise_ratios.append(ratio)
        if seed == PRIMARY_SEED:
            primary_n1 = n1
    assert primary_n1 is not None
    noise_sd = statistics.pstdev(noise_ratios) if len(noise_ratios) > 1 else 0.0
    baseline_ratio = noise_ratios[NOISE_SEEDS.index(PRIMARY_SEED)]

    # Prefix-channel baseline, for the all-reversed sanity check (F-037's bijection).
    prefix_n1 = run_n1(base_words, STEM_MIN, DRAWS, PRIMARY_SEED, base_ending, base_prefix)
    prefix_mean = prefix_n1.prefix_paradigm_count.mean
    prefix_ratio = base_prefix.paradigm_count_total / prefix_mean if prefix_mean else float("inf")

    # All-reversed sanity check.
    all_words = build_words(documents, target_support=None, reverse_all=True)
    all_ending = ending_channel(all_words, stem_min=STEM_MIN)
    all_prefix = prefix_channel(all_words, stem_min=STEM_MIN)
    all_ratio, all_n1 = ratio_at_seed(all_words, all_ending, all_prefix, PRIMARY_SEED)
    exact_match = all_ending.paradigm_count_total == base_prefix.paradigm_count_total
    # F-037's bijection compares like orientations: the all-reversed ending channel's
    # own endings are reversed relative to the real corpus (S-001's own check reverses
    # them back before comparing; done the same way here).
    reversed_all_ending_support = {
        tuple(sorted((tuple(reversed(a1)), tuple(reversed(a2))))): sup
        for (a1, a2), sup in all_ending.alternation_support.items()
    }
    exact_match_support = reversed_all_ending_support == dict(base_prefix.alternation_support)

    support_results: dict[str, dict] = {}
    for st in qualifying:
        words = build_words(documents, target_support=st)
        ending = ending_channel(words, stem_min=STEM_MIN)
        prefix = prefix_channel(words, stem_min=STEM_MIN)
        ratio, n1 = ratio_at_seed(words, ending, prefix, PRIMARY_SEED)
        change = ratio - baseline_ratio
        change_in_noise_units = change / noise_sd if noise_sd else float("inf")
        support_results[st] = {
            "token_count": token_counts[st],
            "word_type_count": len(words),
            "ending_paradigm_count": ending.paradigm_count_total,
            "n1_ending_null": nd(n1.ending_paradigm_count),
            "ratio": ratio,
            "ratio_change_vs_baseline": change,
            "ratio_change_in_noise_units": change_in_noise_units,
        }

    return {
        "corpus": name,
        "word_type_count": len(base_words),
        "support_type_token_counts": token_counts,
        "min_tokens_to_qualify": MIN_TOKENS,
        "qualifying_support_types": qualifying,
        "baseline": {
            "ending_paradigm_count": base_ending.paradigm_count_total,
            "n1_ending_null_seed0": nd(primary_n1.ending_paradigm_count),
            "ratio_seed0": baseline_ratio,
            "ratio_noise_20_seeds": {
                "seeds": NOISE_SEEDS,
                "ratios": noise_ratios,
                "mean": statistics.mean(noise_ratios),
                "sd": noise_sd,
            },
        },
        "prefix_baseline": {
            "prefix_paradigm_count": base_prefix.paradigm_count_total,
            "n1_prefix_null_seed0": nd(prefix_n1.prefix_paradigm_count),
            "ratio_seed0": prefix_ratio,
        },
        "all_reversed_sanity_check": {
            "word_type_count": len(all_words),
            "ending_paradigm_count": all_ending.paradigm_count_total,
            "matches_baseline_prefix_paradigm_count_exactly": exact_match,
            "matches_baseline_prefix_alternation_support_exactly": exact_match_support,
            "n1_ending_null_seed0": nd(all_n1.ending_paradigm_count),
            "ratio_seed0": all_ratio,
            "prefix_baseline_ratio_seed0_for_comparison": prefix_ratio,
        },
        "support_type_reversed": support_results,
    }


def main() -> dict:
    damos = aegean.load("damos").documents
    lineara = aegean.load("lineara").documents

    payload = {
        "question": (
            "Does reversing one support type's words, sign by sign, raise the stage-1 "
            "ending-channel paradigm-count ratio (real / N1 null mean) above the "
            "unreversed corpus's own ratio, beyond that ratio's seed-to-seed noise?"
        ),
        "protocol": {
            "stem_min": STEM_MIN,
            "draws": DRAWS,
            "primary_seed": PRIMARY_SEED,
            "noise_seeds": NOISE_SEEDS,
            "min_tokens_to_qualify": MIN_TOKENS,
        },
        "damos": run_corpus("damos", damos),
        "lineara": run_corpus("lineara", lineara),
    }

    out_dir = Path(__file__).resolve().parent
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return payload


if __name__ == "__main__":
    data = main()
    for corpus in ("damos", "lineara"):
        c = data[corpus]
        print(f"\n== {corpus} ==")
        print("qualifying support types:", c["qualifying_support_types"])
        print("baseline ratio (seed 0):", c["baseline"]["ratio_seed0"])
        print("baseline noise sd (20 seeds):", c["baseline"]["ratio_noise_20_seeds"]["sd"])
        print(
            "all-reversed exact match vs prefix baseline:",
            c["all_reversed_sanity_check"]["matches_baseline_prefix_paradigm_count_exactly"],
        )
        for st, r in c["support_type_reversed"].items():
            print(f"  {st}: ratio={r['ratio']:.3f} change_in_noise_units={r['ratio_change_in_noise_units']:.2f}")
