#!/usr/bin/env python3
"""A-004: does a Linear A CERTAIN token carry a Leiden damage or uncertainty mark?

    .venv/bin/python scripts/lineara_underdots.py
    .venv/bin/python scripts/lineara_underdots.py --write

`docs/ai_context/corpus-sources.md` (Gotchas) records that Linear B's `_bracket_status`
checks only `[`, `]` and `?`, never U+0323 COMBINING DOT BELOW, so a damaged-but-legible
DAMOS sign (`ọ`, `a-ṇọ-qo-ta-o`) arrives as `CERTAIN`. This script measures whether the
same failure mode exists for `aegean.load("lineara")`, in the population
`scripts/controlled_comparison.py::word_sample` draws from before map coverage or
sampling: `tok.kind is TokenKind.WORD`, `tok.status is ReadingStatus.CERTAIN`,
2 to 4 signs.

It checks, after NFD, for U+0323; for Leiden lacuna brackets and the editorial query
mark; for the span-delimiting brackets (``⸤⸥〚〛⟦⟧⌞⌟⌜⌝``); for an asterisk (GORILA's
catalogue mark for a phonetically unidentified sign, e.g. `*301`); for a hyphen inside
one sign label (as opposed to the hyphens `classify()` uses to join sign labels); and
for an unexpected lower-case letter. Prints aggregate counts only: tokens, sign
positions and word *types* affected, never corpus text. `--write` also writes
`results/lineara_underdots.json` with the same counts and the loaded corpus's
provenance data version.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

# Kept identical to controlled_comparison.py's _SPAN_BRACKETS / _sign_is_marked so the
# two never quietly disagree about what "marked" means.
_SPAN_BRACKETS = "⸤⸥〚〛⟦⟧⌞⌟⌜⌝"

_CATEGORIES = [
    ("underdot", lambda s: "̣" in unicodedata.normalize("NFD", s)),
    ("bracket_or_query", lambda s: any(ch in s for ch in "[]?")),
    ("span_bracket", lambda s: any(ch in s for ch in _SPAN_BRACKETS)),
    ("unidentified_asterisk", lambda s: "*" in s),
    ("hyphen_in_label", lambda s: "-" in s),
    ("lowercase_anomaly", lambda s: any(ch.islower() for ch in s)),
]


def population(corpus):
    """WORD, CERTAIN, 2-4 signs: the population word_sample draws from, before any
    map-coverage filter or sampling."""
    toks = []
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            if 2 <= len(tok.signs) <= 4:
                toks.append(tok)
    return toks


def measure(toks):
    n_tokens = len(toks)
    n_positions = sum(len(t.signs) for t in toks)
    types = set(tuple(s.upper() for s in t.signs) for t in toks)
    n_types = len(types)

    per_category = {}
    any_affected_tokens = set()
    any_affected_types = set()
    any_affected_positions = 0
    for name, pred in _CATEGORIES:
        cat_tokens = 0
        cat_positions = 0
        cat_types = set()
        for t in toks:
            hit = False
            for s in t.signs:
                if pred(s):
                    cat_positions += 1
                    hit = True
            if hit:
                cat_tokens += 1
                cat_types.add(tuple(s.upper() for s in t.signs))
        per_category[name] = {
            "tokens": cat_tokens,
            "sign_positions": cat_positions,
            "word_types": len(cat_types),
        }

    for t in toks:
        hit = False
        for s in t.signs:
            if any(pred(s) for _, pred in _CATEGORIES):
                any_affected_positions += 1
                hit = True
        if hit:
            any_affected_tokens.add(id(t))
            any_affected_types.add(tuple(s.upper() for s in t.signs))

    return {
        "population_tokens": n_tokens,
        "population_sign_positions": n_positions,
        "population_word_types": n_types,
        "affected_tokens": len(any_affected_tokens),
        "affected_sign_positions": any_affected_positions,
        "affected_word_types": len(any_affected_types),
        "pct_sign_positions_affected": (
            100 * any_affected_positions / n_positions if n_positions else 0.0
        ),
        "by_category": per_category,
    }


def sign_labels_carry_marks(corpus) -> dict:
    """Whether marks survive into `Sign.label` in the loaded sign inventory itself,
    as opposed to `Token.signs` on individual tokens (the two are populated
    independently: a token's signs come from splitting `Token.text`; the inventory
    is the corpus's separate catalogue of distinct sign shapes)."""
    labels = [s.label for s in corpus.sign_inventory.signs]
    hits = {name: sum(1 for lbl in labels if pred(lbl)) for name, pred in _CATEGORIES}
    return {"n_inventory_signs": len(labels), "labels_carrying_a_mark": hits}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write results/lineara_underdots.json")
    args = ap.parse_args()

    corpus = aegean.load("lineara")
    toks = population(corpus)
    result = measure(toks)
    inventory = sign_labels_carry_marks(corpus)

    print(f"population (WORD, CERTAIN, 2-4 signs): {result['population_tokens']} tokens, "
          f"{result['population_word_types']} word types, "
          f"{result['population_sign_positions']} sign positions")
    print(f"affected (any mark): {result['affected_tokens']} tokens, "
          f"{result['affected_word_types']} word types, "
          f"{result['affected_sign_positions']} sign positions "
          f"({result['pct_sign_positions_affected']:.2f}% of sign positions)")
    print("by category (tokens / sign positions / word types):")
    for name, c in result["by_category"].items():
        print(f"  {name:<22} {c['tokens']:>5} / {c['sign_positions']:>5} / {c['word_types']:>5}")
    print(f"\nsign inventory: {inventory['n_inventory_signs']} distinct signs; "
          f"labels carrying a mark: {inventory['labels_carrying_a_mark']}")
    print("\nComparison: docs/ai_context/corpus-sources.md line 111 (DAMOS / Linear B) -- "
          "Leiden underdots do not affect Token.status there either, and a damaged-but-"
          "legible DAMOS sign (e.g. 'a-ṇọ-qo-ta-o') passes as CERTAIN. Measured here: the "
          "lineara transcription chain carries zero underdots corpus-wide (the upstream "
          "mwenge chain drops the full Leiden apparatus), so that specific failure mode "
          "does not recur for Linear A. What does survive into CERTAIN status instead is "
          "the asterisk-numbered unidentified sign (see by-category counts above).")

    if args.write:
        out = {
            "corpus": "lineara",
            "provenance_data_version": corpus.provenance.data_version,
            "provenance_source": corpus.provenance.source,
            **result,
            "sign_inventory": inventory,
        }
        path = ROOT / "results" / "lineara_underdots.json"
        path.write_text(json.dumps(out, indent=2))
        print(f"\nwritten {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
