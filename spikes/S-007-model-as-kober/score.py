#!/usr/bin/env python3
"""S-007 scorer: score a frontier model's paradigm proposals (BRIEF.md).

Holds no word lists of its own. The corpus file and the proposals file are
both supplied at run time, from ``~/.cache/linear-a-b/s007/`` (the four
corpora and ``PROMPT.md``, never the repo -- see this folder's README.md)
and wherever the coordinating session saves the model's raw JSON output
(also never the repo: "the model's outputs are private", BRIEF.md).

For each proposal: verifies every word exists in the corpus and that
stem + ending reproduces it exactly; for every pair of the proposal's own
(distinct) endings, looks up the alternation support ``kober.paradigms``
already defines -- the number of stems in the whole corpus attested with
both endings of the pair -- and compares it against the 99th percentile of
the N2 null's *maximum*-support distribution (200 draws, seed 0 by
default), the same comparison ``docs/ai_context/kober-method.md`` uses to
read the top of a ranked alternation list against the top of a null list
(see ``kober.report.build_report`` for the exact N2 call this reproduces:
``kober.nulls.run_n2`` on the corpus's own ending channel). Also computes
the instrument's own top-n alternations by support, for the same corpus,
scored the same way, so a proposal's showing can be read against the
instrument's.

Passing ``--reference-version`` additionally grades each alternation pair
against ``kober.reference.is_grammar`` at that version -- pass this only
for the Linear B calibration corpus (corpus D in the brief); on the three
Linear A corpora (A, B, C) the endings are either real Linear A sign
labels or opaque bijection/null labels, and grammar-matching them against
a Mycenaean Greek reference list is meaningless, so BRIEF.md scopes this
check to the calibration corpus alone.

Usage:

    .venv/bin/python spikes/S-007-model-as-kober/score.py \\
        --corpus ~/.cache/linear-a-b/s007/corpus-A-lineara.txt \\
        --proposals /path/to/model-proposals.json \\
        [--reference-version {1,2,3}] [--stem-min 2] [--draws 200] \\
        [--seed 0] [--top-n 10] [--out /path/to/report.json]

Prints the JSON report to stdout (and to ``--out`` if given). Aggregate
numbers and the (small, already-disclosed) proposal/instrument-top-n
content only -- never the full corpus word list.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from kober.nulls import run_n2  # noqa: E402
from kober.paradigms import ChannelResult, Word, ending_channel, ranked_alternations  # noqa: E402
from kober.reference import is_grammar  # noqa: E402

STEM_MIN_DEFAULT = 2
DRAWS_DEFAULT = 200
SEED_DEFAULT = 0
TOP_N_DEFAULT = 10


def load_corpus(path: Path) -> frozenset[Word]:
    """One word per line, hyphen-joined sign labels (S-007's corpus format)."""
    words: set[Word] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        words.add(tuple(line.split("-")))
    return frozenset(words)


def load_proposals(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise SystemExit(f"{path}: expected a JSON list of proposals, got {type(data).__name__}")
    return data


def _as_word(value) -> Word:
    if not isinstance(value, list) or not all(isinstance(s, str) for s in value):
        raise TypeError("expected a list of sign-label strings")
    return tuple(value)


def validate_proposal(
    proposal: dict, corpus_words: frozenset[Word]
) -> tuple[bool, list[str], Word | None, list[Word]]:
    """Structural and corpus-membership checks (BRIEF.md: "verifies every
    proposed word exists in the corpus and every stem+ending equals its
    word"). Returns (valid, reasons, stem, distinct_endings)."""
    reasons: list[str] = []
    try:
        stem = _as_word(proposal["stem"])
        endings = [_as_word(e) for e in proposal["endings"]]
        words = [_as_word(w) for w in proposal["words"]]
    except (KeyError, TypeError, AttributeError):
        return False, ["malformed proposal: stem/endings/words missing or not lists of strings"], None, []

    if len(endings) != len(words):
        reasons.append(f"endings count ({len(endings)}) != words count ({len(words)})")

    for i, (ending, word) in enumerate(zip(endings, words)):
        if stem + ending != word:
            reasons.append(f"word {i}: stem+ending {'-'.join(stem + ending)} != word {'-'.join(word)}")
        if word not in corpus_words:
            reasons.append(f"word {i}: {'-'.join(word)} not found in corpus")

    distinct_endings = sorted(set(endings))
    if len(distinct_endings) < 2:
        reasons.append(f"fewer than two distinct endings ({len(distinct_endings)})")

    return len(reasons) == 0, reasons, stem, distinct_endings


def score_alternation(
    e1: Word,
    e2: Word,
    support_map: Mapping[tuple[Word, Word], int],
    n2_p99: float,
    reference_version: int | None,
) -> dict:
    key = tuple(sorted((e1, e2)))
    support = support_map.get(key, 0)
    entry = {
        "e1": list(key[0]),
        "e2": list(key[1]),
        "support": support,
        "n2_p99": n2_p99,
        "above": support > n2_p99,
    }
    if reference_version is not None:
        entry["grammar_rule"] = is_grammar(key[0], key[1], version=reference_version)
    return entry


def score_proposal(
    index: int,
    proposal: dict,
    corpus_words: frozenset[Word],
    support_map: Mapping[tuple[Word, Word], int],
    n2_p99: float,
    reference_version: int | None,
) -> dict:
    valid, reasons, stem, distinct_endings = validate_proposal(proposal, corpus_words)
    out: dict = {
        "index": index,
        "valid": valid,
        "reasons": reasons,
        "stem": list(stem) if stem is not None else None,
    }
    if not valid or len(distinct_endings) < 2:
        out.update(
            {
                "alternations": [],
                "support": None,
                "n2_p99": n2_p99,
                "above": False,
                "any_above": False,
                "all_above": False,
            }
        )
        return out

    alternations = [
        score_alternation(e1, e2, support_map, n2_p99, reference_version)
        for e1, e2 in combinations(distinct_endings, 2)
    ]
    supports = [a["support"] for a in alternations]
    out.update(
        {
            "alternations": alternations,
            # "support" is the worst-supported pair among the proposal's own
            # endings (>2 endings, Kober's triplets, give >1 pair): a
            # paradigm is only as strong as its weakest alternation.
            "support": min(supports),
            "n2_p99": n2_p99,
            "above": all(a["above"] for a in alternations),
            "any_above": any(a["above"] for a in alternations),
            "all_above": all(a["above"] for a in alternations),
        }
    )
    return out


def instrument_top_n(
    support_map: Mapping[tuple[Word, Word], int],
    n2_p99: float,
    reference_version: int | None,
    n: int,
) -> list[dict]:
    ranked = ranked_alternations(support_map, limit=n)
    out = []
    for (e1, e2), support in ranked:
        entry = {
            "e1": list(e1),
            "e2": list(e2),
            "support": support,
            "n2_p99": n2_p99,
            "above": support > n2_p99,
        }
        if reference_version is not None:
            entry["grammar_rule"] = is_grammar(e1, e2, version=reference_version)
        out.append(entry)
    return out


def build_report(
    corpus_words: frozenset[Word],
    proposals: list[dict],
    stem_min: int,
    draws: int,
    seed: int,
    top_n: int,
    reference_version: int | None,
) -> dict:
    channel: ChannelResult = ending_channel(corpus_words, stem_min=stem_min)
    n2 = run_n2(
        corpus_words,
        stem_min=stem_min,
        draws=draws,
        seed=seed,
        mirror=False,
        real_channel=channel,
        track_grammar_match=False,
    )
    n2_p99 = n2.max_support.p99

    scored = [
        score_proposal(i, p, corpus_words, channel.alternation_support, n2_p99, reference_version)
        for i, p in enumerate(proposals)
    ]
    top = instrument_top_n(channel.alternation_support, n2_p99, reference_version, n=top_n)

    n_valid = sum(1 for s in scored if s["valid"])
    n_proposals_above = sum(1 for s in scored if s["valid"] and s["above"])
    n_top_above = sum(1 for e in top if e["above"])

    return {
        "corpus_word_type_count": len(corpus_words),
        "stem_min": stem_min,
        "n2_draws": draws,
        "n2_seed": seed,
        "n2_max_support_p99": n2_p99,
        "reference_version": reference_version,
        "proposals": scored,
        "instrument_top_n": top,
        "summary": {
            "n_proposals": len(proposals),
            "n_valid": n_valid,
            "n_invalid": len(proposals) - n_valid,
            "n_valid_above_n2_p99": n_proposals_above,
            "fraction_valid_above_n2_p99": (n_proposals_above / n_valid) if n_valid else None,
            "instrument_top_n_count": len(top),
            "instrument_top_n_above_n2_p99": n_top_above,
            "instrument_top_n_fraction_above_n2_p99": (n_top_above / len(top)) if top else None,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Score S-007 model paradigm proposals against a corpus and its N2 null."
    )
    ap.add_argument("--corpus", required=True, type=Path, help="corpus word-list file (one word per line)")
    ap.add_argument("--proposals", required=True, type=Path, help="model's proposals, as a JSON list")
    ap.add_argument("--stem-min", type=int, default=STEM_MIN_DEFAULT)
    ap.add_argument("--draws", type=int, default=DRAWS_DEFAULT, help="N2 null draws (default 200)")
    ap.add_argument("--seed", type=int, default=SEED_DEFAULT, help="N2 null seed (default 0)")
    ap.add_argument("--top-n", type=int, default=TOP_N_DEFAULT, help="instrument's own top-n for comparison")
    ap.add_argument(
        "--reference-version",
        type=int,
        choices=(1, 2, 3),
        default=None,
        help="grade alternations against kober.reference.is_grammar at this version "
        "(pass this for the Linear B calibration corpus only, per BRIEF.md)",
    )
    ap.add_argument("--out", type=Path, default=None, help="also write the report JSON here")
    args = ap.parse_args()

    corpus_words = load_corpus(args.corpus)
    proposals = load_proposals(args.proposals)

    report = build_report(
        corpus_words,
        proposals,
        stem_min=args.stem_min,
        draws=args.draws,
        seed=args.seed,
        top_n=args.top_n,
        reference_version=args.reference_version,
    )
    report["corpus_file"] = str(args.corpus)
    report["proposals_file"] = str(args.proposals)

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(text + "\n")
        print(f"Wrote {args.out}", file=sys.stderr)
    print(text)


if __name__ == "__main__":
    main()
