"""Listed words and list-level modal-final-sign homogeneity (kober1946
Assumptions 4, 6, 7; CHANGELOG "List homogeneity on Linear B", "0.7").

Moved 2026-09-11 from ``scripts/kober_list_homogeneity.py``, which is now a
thin caller of ``DocListing``/``extract_listed_words``/``doc_modal`` below: a
straight move, not a rewrite, so the script's results file
(``results/kober-list-homogeneity-damos.json``) is reproduced byte-for-byte
on every real (non-null) value. ``homogeneous_forms`` is new: Kober 0.7's
list-support tie-break (``paradigms.list_support_counts``, ``nulls.run_n2``)
needs the per-word-type Assumption-7 set the diagnostic's own per-document,
per-form check (``form_has_homogeneous_list``, still in the script) computes
one document at a time; this is the same fact aggregated by word type.

A *listed word* is a WORD, CERTAIN, normalised, two-or-more-sign token that is
followed on its line, skipping SEPARATOR tokens, by a LOGOGRAM or NUMERAL
token (A-101 to A-104's eligibility, quoted from the CHANGELOG entry).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Mapping, Sequence

from aegean.analysis import hands
from aegean.core.model import Document, TokenKind

from .paradigms import Word
from .roles import _word_from_token

__all__ = [
    "DocListing",
    "extract_listed_words",
    "doc_modal",
    "homogeneous_forms",
    "homogeneous_forms_from_listings",
]


@dataclass(frozen=True, slots=True)
class DocListing:
    doc_id: str
    series_letter: str | None
    listed: tuple[Word, ...]  # occurrence-level, document (line, token) order


def extract_listed_words(documents: Sequence[Document]) -> list[DocListing]:
    """A listed word is a WORD/CERTAIN/normalised/>=2-sign token followed on
    its line, skipping SEPARATOR tokens, by a LOGOGRAM or NUMERAL token."""
    out: list[DocListing] = []
    for doc in documents:
        listed: list[Word] = []
        for line in doc.line_tokens:
            n = len(line)
            for i, tok in enumerate(line):
                word = _word_from_token(tok)
                if word is None:
                    continue
                j = i + 1
                while j < n and line[j].kind is TokenKind.SEPARATOR:
                    j += 1
                if j < n and line[j].kind in (TokenKind.LOGOGRAM, TokenKind.NUMERAL):
                    listed.append(word)
        series = hands.series_of(doc)
        letter = series[0] if series else None
        out.append(DocListing(doc_id=doc.id, series_letter=letter, listed=tuple(listed)))
    return out


def doc_modal(final_signs: Sequence[str]) -> tuple[int, frozenset[str]]:
    """(max_count, modal_signs): every final sign tied at the maximum count,
    not an arbitrary single choice (A-101: needed so a form matching any tied
    winner counts, both for the diagnostic's per-form check and for
    ``homogeneous_forms`` below)."""
    counter = Counter(final_signs)
    if not counter:
        return 0, frozenset()
    max_count = max(counter.values())
    modal = frozenset(s for s, c in counter.items() if c == max_count)
    return max_count, modal


def homogeneous_forms_from_listings(
    listings: Sequence[DocListing],
    word_map: Mapping[Word, Word] | None = None,
) -> Mapping[Word, frozenset[str]]:
    """For each word type, the set of modal final signs of the eligible
    documents (>= 3 listed words) in which it occurs as a listed word (Kober
    0.7, CHANGELOG "0.7"). A form "satisfies Assumption 7" iff its own final
    sign is a member of this set for that word.

    Equivalent to the diagnostic's own per-form, per-document check
    (``form_has_homogeneous_list`` in ``scripts/kober_list_homogeneity.py``):
    "target in some document's modal set" is exactly "target in the union of
    modal sets over every document the word is listed in", which is what this
    function returns per word.

    ``word_map`` (Kober 0.7's N2 null, A-116), when given, is applied to every
    listed word before it contributes to a document's modal-sign count and
    before it is used as the output mapping's key -- "a draw's word gets the
    draw's ending; its documents and their modal final signs are recomputed
    from the shuffled words" (CHANGELOG "0.7"). A word absent from ``word_map``
    passes through unchanged (``dict.get(w, w)``), matching every corpus word
    that participates in the null's own word-type set. Default ``None`` is the
    real, unshuffled reading.
    """
    out: dict[Word, set[str]] = defaultdict(set)
    for r in listings:
        if len(r.listed) < 3:
            continue
        mapped = [word_map.get(w, w) for w in r.listed] if word_map is not None else list(r.listed)
        final_signs = [w[-1] for w in mapped]
        _count, modal = doc_modal(final_signs)
        for w in mapped:
            out[w].update(modal)
    return {w: frozenset(s) for w, s in out.items()}


def homogeneous_forms(documents: Sequence[Document]) -> Mapping[Word, frozenset[str]]:
    """``homogeneous_forms(documents) -> Mapping[Word, frozenset[Sign]]``
    (CHANGELOG "0.7"): the real, unshuffled reading, extracting listed words
    from ``documents`` itself. Callers that already hold the extracted
    listings (e.g. a null that recomputes this 200 times) should call
    ``homogeneous_forms_from_listings`` directly rather than re-extract.
    """
    return homogeneous_forms_from_listings(extract_listed_words(documents))
