"""The 25 signs whose Linear A/B value equivalence is demonstrable rather than assumed.

Source: Meißner, Steele (2017), *Linear A and Linear B: structural and contextual
concerns* (docs/works/meissner_steele_preprint.md), Table 1, quoted on line 22 of that
page: "Table 1 lists 25 signs whose value is DEMONSTRABLY shared ... (a i da di ki ma me
mi mu na ni pa po ri ro ru sa se si su ta te ti to tu)". Table 2 lists roughly 60 more
signs that are shape-shared with a value assumed by convention rather than shown; those
are not in this set. A-001 in ASSUMPTIONS.md is the assumption this set exists to test a
sensitivity against: for every OTHER Linear A sign, the transliteration is a Linear B
sound value applied to a graphically similar sign, not a demonstrated equivalence.

Labels are upper-case to match the form `word_sample()` in
`scripts/controlled_comparison.py` builds from a token's signs
(`tuple(s.upper() for s in tok.signs)`). Checked against the loaded sign inventory for
both corpora (`aegean.load("lineara").sign_inventory` and `aegean.load("damos")`
likewise) on 2026-09-11: all 25 labels below are present in both, so no relabelling is
needed before intersecting a word's sign tuple against this set.
"""

from __future__ import annotations

SECURE_SIGNS: frozenset[str] = frozenset({
    "A", "I", "DA", "DI", "KI", "MA", "ME", "MI", "MU", "NA", "NI", "PA", "PO",
    "RI", "RO", "RU", "SA", "SE", "SI", "SU", "TA", "TE", "TI", "TO", "TU",
})

assert len(SECURE_SIGNS) == 25, "Meißner & Steele Table 1 lists exactly 25 signs"

__all__ = ["SECURE_SIGNS"]
