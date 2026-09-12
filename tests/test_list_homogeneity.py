"""List homogeneity on Linear B (CHANGELOG "Kober method" -> "List homogeneity
on Linear B"). Read-only diagnostic, not part of src/kober/. Run:
``.venv/bin/python -m pytest tests/test_list_homogeneity.py -q``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts"))

from aegean.core.model import Document, DocumentMeta, ReadingStatus, Token, TokenKind  # noqa: E402

import kober_list_homogeneity as klh  # noqa: E402
from kober.lists import homogeneous_forms  # noqa: E402


def _tok(
    text: str,
    kind: TokenKind,
    signs: tuple[str, ...] = (),
    status: ReadingStatus = ReadingStatus.CERTAIN,
) -> Token:
    return Token(text=text, kind=kind, signs=signs, status=status)


def _build_document() -> Document:
    # Line A: A1-A2 before a logogram (listed); a separator then A3-A4 before
    # a numeral (listed, separator skipped); B1-B2 before a plain WORD (not
    # listed, next token is neither logogram nor numeral); a 1-sign word
    # before a logogram (ineligible token, never listed); an UNCLEAR word
    # before a logogram (ineligible, never listed).
    # Line B: a lone word at line end (not listed, no next token).
    tokens = [
        _tok("A1-A2", TokenKind.WORD, ("A1", "A2")),                              # 0
        _tok("VIR", TokenKind.LOGOGRAM),                                          # 1
        _tok(",", TokenKind.SEPARATOR),                                           # 2
        _tok("A3-A4", TokenKind.WORD, ("A3", "A4")),                              # 3
        _tok("5", TokenKind.NUMERAL),                                             # 4
        _tok("B1-B2", TokenKind.WORD, ("B1", "B2")),                              # 5
        _tok("C1-C2", TokenKind.WORD, ("C1", "C2")),                              # 6: not listed
        _tok("U1", TokenKind.WORD, ("U1",)),                                      # 7: 1 sign, ineligible
        _tok("VIR", TokenKind.LOGOGRAM),                                          # 8
        _tok("W1-W2", TokenKind.WORD, ("W1", "W2"), status=ReadingStatus.UNCLEAR),  # 9: ineligible
        _tok("VIR", TokenKind.LOGOGRAM),                                          # 10
        _tok("D1-D2", TokenKind.WORD, ("D1", "D2")),                              # 11
    ]
    doc_a = Document(
        id="KN Fp 1",
        script_id="damos",
        tokens=tokens,
        lines=[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [11]],
        meta=DocumentMeta(support="tablet"),
    )
    return doc_a


def test_listed_word_detection():
    doc = _build_document()
    records = klh.extract_listed_words([doc])
    assert len(records) == 1
    listed = records[0].listed

    # Word before a logogram counts.
    assert ("A1", "A2") in listed
    # Word before a separator then a numeral counts (separator skipped).
    assert ("A3", "A4") in listed
    # Word before another WORD token does not count.
    assert ("B1", "B2") not in listed
    assert ("C1", "C2") not in listed
    # Ineligible tokens (1 sign, UNCLEAR status) are never listed, regardless
    # of what follows them.
    assert ("U1",) not in listed
    assert ("W1", "W2") not in listed
    # Word at line end does not count (no next token at all).
    assert ("D1", "D2") not in listed

    assert listed == (("A1", "A2"), ("A3", "A4"))


def _doc_with_listed(words_and_finals: list[tuple[str, ...]], doc_id: str = "KN Fp 2") -> Document:
    """Build a document whose listed words are exactly the given word tuples,
    each followed immediately by a logogram."""
    tokens: list[Token] = []
    for w in words_and_finals:
        tokens.append(_tok("-".join(w), TokenKind.WORD, w))
        tokens.append(_tok("VIR", TokenKind.LOGOGRAM))
    lines = [list(range(len(tokens)))]
    return Document(id=doc_id, script_id="damos", tokens=tokens, lines=lines, meta=DocumentMeta(support="tablet"))


def test_homogeneity_of_a_hand_built_document():
    # Five listed words, final signs: SO, SO, SO, SI, JO -- modal sign SO at
    # count 3, homogeneity 3/5.
    words = [
        ("A1", "SO"),
        ("A2", "SO"),
        ("A3", "SO"),
        ("A4", "SI"),
        ("A5", "JO"),
    ]
    doc = _doc_with_listed(words)
    records = klh.extract_listed_words([doc])
    assert len(records[0].listed) == 5

    summary = klh.summarise_documents(records)
    assert summary["n_documents_eligible"] == 1
    assert summary["count_homogeneity_ge_half"] == 1
    assert summary["median_homogeneity"] == 3 / 5
    assert summary["pooled_homogeneity"] == 3 / 5


def test_documents_below_three_listed_words_are_excluded():
    # Two listed words: below the eligibility bar, so excluded from the
    # per-document statistic even though the words themselves exist.
    words = [("A1", "SO"), ("A2", "SO")]
    doc = _doc_with_listed(words)
    records = klh.extract_listed_words([doc])
    assert len(records[0].listed) == 2

    summary = klh.summarise_documents(records)
    assert summary["n_documents_eligible"] == 0
    assert summary["count_homogeneity_ge_half"] == 0
    assert summary["median_homogeneity"] is None
    assert summary["pooled_homogeneity"] == 0.0

    # But the words are still in the pool: the occurrence pool used by the
    # null keeps this document's two tokens and its token count.
    doc_idx, signs = klh.build_occurrence_pool(records)
    assert len(doc_idx) == 2
    assert len(signs) == 2


def test_homogeneous_forms_assumption_7_on_a_hand_built_document():
    # Same document as test_homogeneity_of_a_hand_built_document: modal sign
    # SO at count 3 of 5 (Kober 0.7, CHANGELOG "0.7", A-116).
    words = [
        ("A1", "SO"),
        ("A2", "SO"),
        ("A3", "SO"),
        ("A4", "SI"),
        ("A5", "JO"),
    ]
    doc = _doc_with_listed(words)
    hf = homogeneous_forms([doc])

    # A form ending in the document's modal sign satisfies Assumption 7: its
    # own final sign is a member of its own set.
    assert ("A1", "SO")[-1] in hf[("A1", "SO")]
    assert ("A2", "SO")[-1] in hf[("A2", "SO")]
    assert ("A3", "SO")[-1] in hf[("A3", "SO")]
    # A form ending in a non-modal sign does not, even though it is listed
    # (present in the mapping) -- its own final sign is not the doc's modal
    # one.
    assert ("A4", "SI")[-1] not in hf[("A4", "SI")]
    assert ("A5", "JO")[-1] not in hf[("A5", "JO")]
    # A word that never occurs as a listed word at all is absent from the
    # mapping, so it satisfies nothing (Mapping.get default).
    assert hf.get(("Z1", "Z2"), frozenset()) == frozenset()


def test_three_listed_words_is_the_eligibility_floor():
    words = [("A1", "SO"), ("A2", "SO"), ("A3", "SI")]
    doc = _doc_with_listed(words)
    records = klh.extract_listed_words([doc])
    summary = klh.summarise_documents(records)
    assert summary["n_documents_eligible"] == 1
    assert summary["pooled_homogeneity"] == 2 / 3


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
