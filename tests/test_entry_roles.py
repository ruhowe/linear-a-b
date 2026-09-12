"""Entry segmentation and role assignment for scripts/kober_entry_roles.py.

Read-only diagnostic (CHANGELOG "Kober method" -> "Entry-role diagnostic on
Linear B"), not part of src/kober/. Run: ``.venv/bin/python -m pytest
tests/test_entry_roles.py -q``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts"))

from aegean.core.model import Document, DocumentMeta, ReadingStatus, Token, TokenKind  # noqa: E402

import kober_entry_roles as ker  # noqa: E402


def _tok(
    text: str,
    kind: TokenKind,
    signs: tuple[str, ...] = (),
    status: ReadingStatus = ReadingStatus.CERTAIN,
) -> Token:
    return Token(text=text, kind=kind, signs=signs, status=status)


def _build_document() -> Document:
    # Line A: entry 0 (X, closed by logogram VIR, a separator skipped inside
    # it); entry 1 (Y, closed by a numeral -> "none"); entry 2 (P, Q, R, with
    # an ineligible 1-sign word and an ineligible UNCLEAR word interleaved,
    # and an UNKNOWN token as non-word content, closed by logogram OVIS).
    # Line B and line C: one lone word each, closed at line end ("none"),
    # entries 3 and 4 -- both capped to entry index 3.
    tokens = [
        _tok("X1-X2", TokenKind.WORD, ("X1", "X2")),                          # 0
        _tok(",", TokenKind.SEPARATOR),                                       # 1
        _tok("VIR", TokenKind.LOGOGRAM),                                      # 2
        _tok("Y1-Y2", TokenKind.WORD, ("Y1", "Y2")),                          # 3
        _tok("5", TokenKind.NUMERAL),                                         # 4
        _tok("P1-P2", TokenKind.WORD, ("P1", "P2")),                          # 5
        _tok("U1", TokenKind.WORD, ("U1",)),                                  # 6: 1 sign, ineligible
        _tok("Q1-Q2", TokenKind.WORD, ("Q1", "Q2")),                          # 7
        _tok("W1-W2", TokenKind.WORD, ("W1", "W2"), status=ReadingStatus.UNCLEAR),  # 8: ineligible
        _tok("R1-R2", TokenKind.WORD, ("R1", "R2")),                          # 9
        _tok("?", TokenKind.UNKNOWN),                                         # 10: non-word content
        _tok("OVIS", TokenKind.LOGOGRAM),                                     # 11
        _tok("S1-S2", TokenKind.WORD, ("S1", "S2")),                          # 12
        _tok("T1-T2", TokenKind.WORD, ("T1", "T2")),                          # 13
    ]
    return Document(
        id="KN Fp 1",
        script_id="damos",
        tokens=tokens,
        lines=[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [12], [13]],
        meta=DocumentMeta(support="tablet"),
    )


def test_entry_segmentation_and_role_assignment():
    doc = _build_document()
    roles_by_word, distinct_roles, entries_total, roles_total = ker.build_entries_and_roles([doc])

    assert entries_total == 5
    # Eligible words: X, Y, P, Q, R, S, T -- seven roles assigned.
    assert roles_total == 7

    series = "Fp"  # aegean.analysis.hands.series_of("KN Fp 1")

    # Entry 0: single word, closed by a logogram; the separator did not
    # split it or count toward it.
    assert roles_by_word[("X1", "X2")] == {(series, 0, "first", "VIR")}

    # Entry 1: single word, closed by a numeral -> closing label "none".
    assert roles_by_word[("Y1", "Y2")] == {(series, 1, "first", "none")}

    # Entry 2: three eligible words in order (the 1-sign word and the
    # UNCLEAR-status word are excluded from both role assignment and from
    # the first/middle/last count; the UNKNOWN token is inert), closed by
    # logogram OVIS.
    assert roles_by_word[("P1", "P2")] == {(series, 2, "first", "OVIS")}
    assert roles_by_word[("Q1", "Q2")] == {(series, 2, "middle", "OVIS")}
    assert roles_by_word[("R1", "R2")] == {(series, 2, "last", "OVIS")}

    # Ineligible tokens never receive a role.
    assert ("U1",) not in roles_by_word
    assert ("W1", "W2") not in roles_by_word or roles_by_word[("W1", "W2")] == set()

    # Entries 3 and 4: lone words ending at line end ("none"); both are
    # capped to entry index 3 (min(entry_index, 3)).
    assert roles_by_word[("S1", "S2")] == {(series, 3, "first", "none")}
    assert roles_by_word[("T1", "T2")] == {(series, 3, "first", "none")}

    # S and T collapse to the same role tuple, so distinct_roles is six, not
    # seven: (0,first,VIR), (1,first,none), (2,first,OVIS), (2,middle,OVIS),
    # (2,last,OVIS), (3,first,none).
    assert len(distinct_roles) == 6


def test_lone_word_entry_position_is_first():
    # A single-word entry (no other words to compare against) is always
    # "first", never "middle" or "last", per the role definition's own
    # wording ("first" if it is the only word).
    doc = _build_document()
    roles_by_word, _distinct, _entries, _roles = ker.build_entries_and_roles([doc])
    for word in (("X1", "X2"), ("Y1", "Y2"), ("S1", "S2"), ("T1", "T2")):
        positions = {role[2] for role in roles_by_word[word]}
        assert positions == {"first"}


def test_word_from_token_eligibility_matches_extract_word_types():
    # Same filter as kober.words.extract_word_types: kind WORD, status
    # CERTAIN, normalised labels, two or more signs.
    eligible = _tok("KU-RO", TokenKind.WORD, ("KU", "RO"))
    one_sign = _tok("KU", TokenKind.WORD, ("KU",))
    unclear = _tok("KU-RO", TokenKind.WORD, ("KU", "RO"), status=ReadingStatus.UNCLEAR)
    logogram = _tok("VIR", TokenKind.LOGOGRAM)

    assert ker._word_from_token(eligible) == ("KU", "RO")
    assert ker._word_from_token(one_sign) is None
    assert ker._word_from_token(unclear) is None
    assert ker._word_from_token(logogram) is None
