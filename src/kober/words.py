"""Word types from a corpus, for the Kober method (A-038, A-039).

**Unit.** Word *types*, not tokens (A-038): a stem attested by one token 51 times
counts once, the same as a hapax. Only tokens with ``kind is TokenKind.WORD`` and
``status is ReadingStatus.CERTAIN`` are eligible — this is the same status filter as
``linearb_restore.extract``, but here it is applied per-token across the whole corpus
rather than per-line, since paradigm induction has no notion of a restorable sequence.

**Normalisation.** Each sign label (``Token.signs`` is already hyphen-split) goes
through ``linearb_restore.normalise.normalise_text``, which returns a 3-tuple
``(normalised, had_underdot, had_span)``; only the first element is used here. This
merges underdotted labels with their plain form (``ṬỌ`` and ``TO`` both become ``TO``
after upper-casing) — the design page names this the most consequential preprocessing
decision, measured there as inflating a 75-sign vocabulary to 118 if skipped. A-039
notes this normaliser was built for DĀMOS and is untested for Linear A; this module
does not gate on corpus identity, so the caller is responsible for that (see
``scripts/kober_run.py``, which refuses Linear A without ``--allow-lineara``).

Words of one sign are dropped: a one-sign "stem" cannot carry an ending under A-035.

**Homophone merge (Kober 0.9, CHANGELOG "0.9"; A-144), optional, default off.**
``extract_word_types(..., merge_homophones=True)`` maps a fixed set of Linear B
homophone-index labels to their plain form after normalisation, before the
two-or-more-sign filter: a2->A, ai2->AI, pa2->PA, pu2->PU, ra2->RA, ra3->RA,
ro2->RO, ta2->TA (Ventris and Chadwick 1973 section 13; *118 and similar
unidentified signs are left unchanged, per the design page). This is a
sensitivity on sign *identity*, applied once at extraction so every
downstream statistic (paradigms, nulls, grid, medial) runs unchanged on
whichever word-type set it receives; it does not affect ``labels_changed``/
``labels_seen``, which describe normalisation's effect on the signary only
(A-046), not this merge's.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

from aegean.core.model import Document, ReadingStatus, TokenKind

from linearb_restore.normalise import normalise_text

__all__ = [
    "WordTypes",
    "HOMOPHONE_MERGE_MAP",
    "extract_word_types",
    "subsample_word_types",
    "subsample_document_ids",
    "restrict_to_shared",
]

# Kober 0.9 (CHANGELOG "0.9", A-144): homophone-index labels merged into their
# plain form when extract_word_types(..., merge_homophones=True) is used.
# Keys are already upper-cased normalised labels, matching what
# _normalise_label produces.
HOMOPHONE_MERGE_MAP: dict[str, str] = {
    "A2": "A",
    "AI2": "AI",
    "PA2": "PA",
    "PU2": "PU",
    "RA2": "RA",
    "RA3": "RA",
    "RO2": "RO",
    "TA2": "TA",
}


@dataclass(frozen=True, slots=True)
class WordTypes:
    """The word-type set and what normalisation did to reach it.

    ``labels_changed`` counts sign labels (not tokens, not words) where
    normalisation produced a different upper-cased string than the raw label
    carried — underdot strips, span-bracket strips, or subscript conversion. It is
    counted over every sign in every CERTAIN WORD token, including one-sign words
    that are then dropped from ``words``, because the quantity being reported is the
    normaliser's effect on the labelled signary, not on the final word set.
    """

    words: frozenset[tuple[str, ...]]
    labels_changed: int
    labels_seen: int


def _normalise_label(label: str) -> tuple[str, bool]:
    normalised, _had_underdot, _had_span = normalise_text(label)
    upper = normalised.upper()
    return upper, upper != label.upper()


def extract_word_types(
    documents: Iterable[Document], merge_homophones: bool = False
) -> WordTypes:
    """CERTAIN WORD tokens, normalised, upper-cased, words of >= 2 signs.

    Returns the set of distinct sign-label tuples ("word types") plus the count of
    sign labels normalisation changed, over every sign seen in a CERTAIN WORD token
    (see ``WordTypes.labels_changed``).

    ``merge_homophones`` (Kober 0.9, A-144), default off: after normalisation,
    each label is looked up in ``HOMOPHONE_MERGE_MAP`` and replaced by its
    plain form when present. Applied before the two-or-more-sign filter, so a
    word that becomes a duplicate of another only after merging (e.g. a word
    spelled with RA2 and the same word spelled with RA) collapses to one word
    type, as intended. ``labels_changed``/``labels_seen`` count normalisation
    only, not this merge (A-144).
    """
    words: set[tuple[str, ...]] = set()
    labels_changed = 0
    labels_seen = 0
    for doc in documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            labels: list[str] = []
            for label in tok.signs:
                labels_seen += 1
                norm, changed = _normalise_label(label)
                if changed:
                    labels_changed += 1
                if merge_homophones:
                    norm = HOMOPHONE_MERGE_MAP.get(norm, norm)
                labels.append(norm)
            if len(labels) >= 2:
                words.add(tuple(labels))
    return WordTypes(words=frozenset(words), labels_changed=labels_changed, labels_seen=labels_seen)


def subsample_word_types(word_types: WordTypes, n: int, seed: int) -> WordTypes:
    """A seeded random subset of ``n`` word types, no other change (A-057, A-058).

    Draws without replacement from the *sorted* word-type list (A-057: a
    ``frozenset``'s iteration order depends on the process hash seed, not the
    RNG seed, so sorting first is what makes ``(n, seed)`` reproducible).
    ``labels_changed`` and ``labels_seen`` are carried through unchanged: they
    describe what normalisation did to the full corpus's signary (A-046), not
    to this particular subsample (A-058).
    """
    pool = sorted(word_types.words)
    rng = random.Random(seed)
    sampled = rng.sample(pool, n)
    return WordTypes(
        words=frozenset(sampled),
        labels_changed=word_types.labels_changed,
        labels_seen=word_types.labels_seen,
    )


def subsample_document_ids(doc_ids: Iterable[str], n: int, seed: int) -> list[str]:
    """A seeded random subset of ``n`` document ids (the "tablet model", CHANGELOG
    "Floor sweep on Linear B"), for use with ``Corpus.subset`` before word types are
    extracted.

    Sorts the id pool (A-057's reproducibility device: a plain ``list`` or ``set``
    of ids can iterate in an order that depends on the process hash seed, not just
    the RNG seed, so sorting first is what makes ``(n, seed)`` reproducible across
    processes), then draws a *single* seeded full permutation of that pool and
    returns its first ``n`` ids, rather than calling ``random.Random.sample`` fresh
    for each ``n``.  A-063 records why: the floor sweep's bisection on document
    count needs the resulting word-type count to be non-decreasing in ``n`` at a
    fixed seed (more documents can only add word types, never remove them), which
    holds for a prefix of one fixed permutation but not for independent
    ``sample(pool, n)`` draws at different ``n``, which are not nested in one
    another. A-063 also records this choice over ``linearb_restore.split``'s
    sha256 stable-key scheme, which serves a different purpose (a deterministic
    partition into k folds, not a random subset of a given size).
    """
    pool = sorted(set(doc_ids))
    rng = random.Random(seed)
    rng.shuffle(pool)
    return pool[:n]


def restrict_to_shared(
    word_types: WordTypes, other_words: frozenset[tuple[str, ...]]
) -> WordTypes:
    """Restrict ``word_types`` to its intersection with ``other_words`` (A-002, the
    GORILA/SigLA edition comparison in CHANGELOG "Segmentation sensitivity on Linear
    A"). "Shared" means an identical normalised sign tuple in both editions' word-type
    sets, so the intersection is symmetric: restricting GORILA's word types to what
    SigLA also has and restricting SigLA's to what GORILA also has yield the same
    frozenset of words, by construction, regardless of which side calls this function.
    ``labels_changed`` and ``labels_seen`` are carried through from ``word_types``
    unchanged, the same pattern ``subsample_word_types`` uses (A-058): they describe
    normalisation's effect on the calling corpus's own full signary, not on the
    shared subset, so the two directions' reports differ in that metadata even though
    every stage 1 statistic computed from the word set itself is identical.
    """
    shared = frozenset(word_types.words & other_words)
    return WordTypes(
        words=shared,
        labels_changed=word_types.labels_changed,
        labels_seen=word_types.labels_seen,
    )
