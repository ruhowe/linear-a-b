"""Word-type entry roles (F-028; CHANGELOG "Entry-role diagnostic on Linear B",
"0.5"). Moved 2026-09-11 from ``scripts/kober_entry_roles.py``, which is now a
thin caller of ``build_entries_and_roles`` below: this is a straight move, not
a rewrite, so the script's results file
(``results/kober-entry-roles-damos.json``) is reproduced byte-for-byte. Kober
0.5's role-sharing tie-break (``paradigms.role_sharing_counts``,
``nulls.run_n2``) needs the same role assignment the diagnostic already
computes, hence ``word_roles`` below.

Role definition, quoted from the CHANGELOG entry. A tablet is a sequence of
entries; an entry is a maximal run of tokens on one line ending at a logogram
or numeral or at the line's end. A word's role is the tuple (series of the
document, as ``aegean.analysis.hands.series_of``; index of its entry on the
tablet, capped at 3; position of the word within its entry, first, middle or
last; the logogram that closes the entry, or "none"). A word type's roles are
the multiset of roles of its tokens (here, the *set* -- ``word_roles`` returns
a ``frozenset`` per word type, since duplicate role tuples across tokens carry
no extra information for a set-intersection role-sharing test).

Unstated mechanics (ASSUMPTIONS.md section F, A-092 to A-097, carried over
unchanged by the move): SEPARATOR tokens are skipped and never join an entry
or end one; UNKNOWN tokens sit inside an entry as non-word content; entry
index is 0-based, counted across the whole tablet in line then token order,
saturating at 3; "position among the WORD tokens of its entry" counts only the
entry's eligible WORD tokens (kind WORD, status CERTAIN, normalised label
tuple of two or more signs -- the same filter ``kober.words.extract_word_types``
applies); a role's series component is the string "none" when ``series_of``
returns ``None``.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping

from aegean.analysis import hands
from aegean.core.model import Document, ReadingStatus, Token, TokenKind

from .paradigms import Word
from .words import _normalise_label

__all__ = ["Role", "build_entries_and_roles", "word_roles"]

Role = tuple[str, int, str, str]


def _word_from_token(tok: Token) -> Word | None:
    """Same eligibility as ``kober.words.extract_word_types``: kind WORD,
    status CERTAIN, normalised sign labels, two or more signs."""
    if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
        return None
    labels = []
    for label in tok.signs:
        norm, _changed = _normalise_label(label)
        labels.append(norm)
    return tuple(labels) if len(labels) >= 2 else None


def _finalize_entry(
    entry_tokens: list[Token],
    closing_kind: TokenKind | None,
    closing_text: str | None,
    series: str,
    entry_index: int,
    roles_by_word: dict[Word, set[Role]],
    distinct_roles: set[Role],
) -> int:
    """Assign a role to each eligible WORD token in one finalized entry.
    Returns the number of roles assigned (A-093: position is counted among
    the entry's eligible WORD tokens only)."""
    words_in_order: list[Word] = []
    for tok in entry_tokens:
        w = _word_from_token(tok)
        if w is not None:
            words_in_order.append(w)
    n = len(words_in_order)
    # A-094: only a LOGOGRAM-closed entry carries a closing label.
    closing_label = closing_text if closing_kind is TokenKind.LOGOGRAM else "none"
    for i, word in enumerate(words_in_order):
        if i == 0:
            position = "first"
        elif i == n - 1:
            position = "last"
        else:
            position = "middle"
        role: Role = (series, entry_index, position, closing_label)
        roles_by_word[word].add(role)
        distinct_roles.add(role)
    return n


def build_entries_and_roles(
    documents,
) -> tuple[dict[Word, set[Role]], set[Role], int, int]:
    """Walk every document's lines, segment into entries, and assign roles to
    eligible WORD tokens. Returns (roles_by_word, distinct_roles, entries_total,
    roles_total)."""
    roles_by_word: dict[Word, set[Role]] = defaultdict(set)
    distinct_roles: set[Role] = set()
    entries_total = 0
    roles_total = 0

    for doc in documents:
        series = hands.series_of(doc) or "none"
        entry_index = 0
        for line in doc.line_tokens:
            current: list[Token] = []
            for tok in line:
                if tok.kind is TokenKind.SEPARATOR:
                    continue  # skipped, not a boundary
                current.append(tok)
                if tok.kind in (TokenKind.LOGOGRAM, TokenKind.NUMERAL):
                    idx = min(entry_index, 3)  # A-092: 0-based, saturating at 3
                    roles_total += _finalize_entry(
                        current, tok.kind, tok.text, series, idx, roles_by_word, distinct_roles
                    )
                    entries_total += 1
                    entry_index += 1
                    current = []
            if current:
                idx = min(entry_index, 3)
                roles_total += _finalize_entry(
                    current, None, None, series, idx, roles_by_word, distinct_roles
                )
                entries_total += 1
                entry_index += 1

    return dict(roles_by_word), distinct_roles, entries_total, roles_total


def word_roles(documents: "list[Document] | object") -> Mapping[Word, frozenset]:
    """A word type's role set (CHANGELOG "0.5"): ``word_roles(documents) ->
    Mapping[Word, frozenset[Role]]``. Thin wrapper around
    ``build_entries_and_roles``, freezing each word's role set. A word type
    with no eligible occurrence in ``documents`` is simply absent, matching
    ``build_entries_and_roles``'s own domain (every eligible WORD token
    contributes at least one role, per A-093)."""
    roles_by_word, _distinct_roles, _entries_total, _roles_total = build_entries_and_roles(documents)
    return {word: frozenset(roles) for word, roles in roles_by_word.items()}
