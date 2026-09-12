"""Word-token context classes for the Kober method, version 0.4 (A-075 onward).

Script-agnostic: nothing here reads a sign value, and the same code runs on
either corpus's ``Document`` objects (A-078 records that what a context *means*
may still differ between them).

**Context class of a token.** A 3-tuple ``(support_type, line_initial,
next_kind)`` (``ContextClass``):

- ``support_type``: ``doc.meta.support``, stripped and lower-cased, or
  ``"unknown"`` when empty (A-079).
- ``line_initial``: whether the token is the first token of its physical line,
  per ``doc.line_tokens`` (not ``doc.tokens``, which is document-flat).
- ``next_kind``: the ``TokenKind`` *name* (e.g. ``"WORD"``, ``"LOGOGRAM"``) of
  the following token on the same line, or the string ``"none"`` when the
  token is last on its line (A-080). The next token is whatever follows in the
  line's own token list, of any kind, including a separator or punctuation
  token when the edition tokenises one.

**Word type's class.** A word type's class is the most frequent context class
across its own CERTAIN WORD token occurrences (in whatever documents are
passed in), ties broken by taking the smallest class under tuple sort order
(A-075, A-081) -- the same tie-break style ``paradigms.ranked_alternations``
already uses for alternation pairs.

**Eligibility.** Exactly the extraction path ``words.py`` uses: ``kind is
TokenKind.WORD``, ``status is ReadingStatus.CERTAIN``, each sign label passed
through ``words._normalise_label`` (the same normaliser ``extract_word_types``
uses, imported directly per the precedent ``grid.py`` already set for reusing
a sibling module's private helpers), kept only when the normalised word has
two or more signs.

**Class census.** ``WordContexts.census`` counts word *types* by their
dominant class (A-082), not token occurrences -- the same unit every Kober
statistic uses (A-038).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping

from aegean.core.model import Document, ReadingStatus, TokenKind

from .words import _normalise_label

__all__ = [
    "ContextClass",
    "WordContexts",
    "support_type_of",
    "token_context_class",
    "extract_word_contexts",
]

ContextClass = tuple[str, bool, str]

Word = tuple[str, ...]


def support_type_of(doc: Document) -> str:
    """``doc.meta.support``, normalised to a short string (A-079).

    Stripped and lower-cased; ``"unknown"`` when empty. DĀMOS's own values
    (``tablet``, ``stirrup jar``, ``nodule, sealed``, ...) are already short,
    so no further canonicalisation is applied.
    """
    raw = (doc.meta.support or "").strip().lower()
    return raw if raw else "unknown"


def token_context_class(support_type: str, line: list, index: int) -> ContextClass:
    """The context class of the token at ``index`` in ``line`` (a list of
    ``Token``, e.g. one element of ``doc.line_tokens``), given the document's
    already-computed ``support_type``."""
    line_initial = index == 0
    next_kind = line[index + 1].kind.name if index + 1 < len(line) else "none"
    return (support_type, line_initial, next_kind)


@dataclass(frozen=True, slots=True)
class WordContexts:
    """A word type's dominant context class, and the class census (A-082)."""

    word_class: Mapping[Word, ContextClass]
    census: Mapping[ContextClass, int]


def extract_word_contexts(documents: Iterable[Document]) -> WordContexts:
    """Per-word-type dominant context class and the class census, over
    ``documents`` (CERTAIN WORD tokens, normalised, >= 2 signs -- the same
    eligibility ``words.extract_word_types`` applies, A-081).
    """
    class_counts: dict[Word, Counter] = defaultdict(Counter)
    for doc in documents:
        support_type = support_type_of(doc)
        for line in doc.line_tokens:
            for i, tok in enumerate(line):
                if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                    continue
                labels: list[str] = []
                for label in tok.signs:
                    norm, _changed = _normalise_label(label)
                    labels.append(norm)
                if len(labels) < 2:
                    continue
                word = tuple(labels)
                cls = token_context_class(support_type, line, i)
                class_counts[word][cls] += 1

    word_class: dict[Word, ContextClass] = {}
    for word, counts in class_counts.items():
        best = max(counts.values())
        # A-075/A-081: ties by sorted key among classes at the max count.
        word_class[word] = min(cls for cls, n in counts.items() if n == best)

    census: Counter = Counter(word_class.values())
    return WordContexts(word_class=word_class, census=dict(census))
