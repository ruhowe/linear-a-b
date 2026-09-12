"""Normalise DĀMOS Linear B tokens, and recover the classes the loader's regexes miss.

Three facts about DĀMOS drive this module. Each was measured, not assumed; the
counts are for the Knossos D family (1,016 documents) and are re-derived by
:func:`audit` on every run.

1. **Underdots do not affect ``ReadingStatus``.** ``loader._bracket_status`` inspects
   only ``[``, ``]`` and ``?`` — never U+0323 COMBINING DOT BELOW, the Leiden mark for
   "damaged but legible". So ``ọ`` and ``a-ṇọ-qo-ta-o`` arrive as ``CERTAIN``. A naive
   CERTAIN-only ground truth therefore includes damaged signs, and leaving the dots in
   inflates the sign vocabulary from 75 to 118 by creating variants (``ṇọ``, ``ṭọ``).
   This is the most consequential preprocessing decision in the pipeline.
2. **One-sign syllabic tokens are typed ``UNKNOWN``.** ``loader.classify`` only emits
   ``WORD`` when the token contains ``-``, and ``_IDEOGRAM_RE`` requires an initial
   capital, so lowercase single syllabograms (``o``, ``ki``, ``pa``, ``pe``) fall
   through to ``UNKNOWN``. These are real adjuncts on the sheep tablets and belong in
   the text stream. Measured: 419 such tokens in the D family.
3. **``Token.form_state`` is ``None`` throughout.** The DĀMOS loader never constructs a
   ``TokenFormState``, so sub-token ``FormSegment`` damage handling is *inapplicable*
   here, not merely deferred.

Reclassification is decided by **membership in the Linear B sign inventory**, not by a
hand-rolled regex: a single-sign token is a syllabogram if its normalised, upper-cased
label is one of the 211 signs DĀMOS attests. Every reclassification is counted and
reported by :func:`audit` — silently retyping a third of a corpus is exactly the
unstated-assumption failure the project's invariants guard against.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Mapping

from aegean.core.model import ReadingStatus, Token, TokenKind
from aegean.core.numerals import parse_value
from aegean.scripts.linearb.loader import (
    _IDEOGRAM_RE,
    _QUALIFIED_IDEOGRAM_RE,
)

__all__ = [
    "UNDERDOT",
    "SPAN_BRACKETS",
    "NormalisedToken",
    "normalise_text",
    "reclassify",
    "normalise_document_tokens",
    "audit",
]

UNDERDOT = "̣"  # combining dot below — Leiden "damaged but legible"
# Brackets delimiting a stretch the edition *does* give (scribal erasure, half-brackets).
# The reading lives on the tokens inside, so the delimiter itself carries no loss.
SPAN_BRACKETS = "⟦⟧⌞⌟⌜⌝"
# DĀMOS word dividers. The loader's own _SEP covers only the Unicode Aegean dividers.
DIVIDERS = {",", "/", ",/", "\U00010100", "\U00010101"}
_SUBSCRIPTS = {chr(0x2080 + i): str(i) for i in range(10)}


@dataclass(frozen=True, slots=True)
class NormalisedToken:
    """One token after normalisation, carrying what normalisation changed.

    ``signs`` is the decomposed sign sequence *after* normalisation, so it is the
    unit the masking protocol operates on. ``damaged_but_read`` is True when the
    original carried an underdot anywhere — such signs stay usable as context but
    are ineligible as masking targets (see the eligibility rules in ``extract``).
    """

    text: str  # normalised surface form
    original: str  # exactly as DĀMOS gave it
    kind: TokenKind
    status: ReadingStatus
    signs: tuple[str, ...]
    damaged_but_read: bool = False
    had_span_bracket: bool = False
    reclassified_from: TokenKind | None = None
    is_apparatus: bool = False
    line_no: int | None = None
    position: int | None = None

    @property
    def changed(self) -> bool:
        return self.damaged_but_read or self.had_span_bracket or self.reclassified_from is not None


def normalise_text(text: str) -> tuple[str, bool, bool]:
    """``(normalised, had_underdot, had_span_bracket)``.

    Order matters: decompose, strip the combining dot, recompose, *then* remove span
    brackets — residue such as ``ra⌞`` survives underdot stripping alone. Lacuna
    brackets ``[`` ``]`` are deliberately **kept**, because they carry the editorial
    status the loader assigned and removing them would silently upgrade an uncertain
    reading to a certain one.
    """
    decomposed = unicodedata.normalize("NFD", text)
    had_underdot = UNDERDOT in decomposed
    stripped = unicodedata.normalize("NFC", decomposed.replace(UNDERDOT, ""))
    had_span = any(b in stripped for b in SPAN_BRACKETS)
    for bracket in SPAN_BRACKETS:
        stripped = stripped.replace(bracket, "")
    # Linear B labels are ASCII-digit (RA2); Linear A uses subscripts (RA₂). Harmless
    # here, kept so a shared code path cannot silently mis-key a cross-script lookup.
    normalised = "".join(_SUBSCRIPTS.get(ch, ch) for ch in stripped)
    return normalised, had_underdot, had_span


def reclassify(token: Token, sign_labels: frozenset[str]) -> NormalisedToken:
    """Normalise one token and, where the loader's regexes missed it, restore its class.

    ``sign_labels`` is the attested Linear B signary (``corpus.sign_inventory``),
    upper-cased. Only tokens the loader typed ``UNKNOWN`` are candidates for
    reclassification — a token the loader already typed confidently is never retyped,
    so this can only add classes, never overrule the edition.
    """
    text, had_underdot, had_span = normalise_text(token.text)
    is_apparatus = "apparatus" in (token.annotations or {})
    kind, signs, reclassified_from = token.kind, token.signs, None

    if token.kind is TokenKind.UNKNOWN and not is_apparatus and text:
        bare = text.strip("[]")
        if bare in DIVIDERS:
            kind, signs, reclassified_from = TokenKind.SEPARATOR, (bare,), TokenKind.UNKNOWN
        elif bare.upper() in sign_labels and "-" not in bare:
            # A single syllabogram the loader dropped for lacking a hyphen.
            kind, signs, reclassified_from = TokenKind.WORD, (bare,), TokenKind.UNKNOWN
        elif parse_value(bare) is not None:
            kind, signs, reclassified_from = TokenKind.NUMERAL, (bare,), TokenKind.UNKNOWN
        elif _QUALIFIED_IDEOGRAM_RE.match(bare) or _IDEOGRAM_RE.match(bare):
            kind, signs, reclassified_from = TokenKind.LOGOGRAM, (bare,), TokenKind.UNKNOWN
    elif token.kind is TokenKind.WORD:
        # Re-split on the normalised form so underdotted signs lose their dots.
        bare = text.strip("[]")
        signs = tuple(s for s in bare.split("-") if s)

    return NormalisedToken(
        text=text,
        original=token.text,
        kind=kind,
        status=token.status,
        signs=signs,
        damaged_but_read=had_underdot,
        had_span_bracket=had_span,
        reclassified_from=reclassified_from,
        is_apparatus=is_apparatus,
        line_no=token.line_no,
        position=token.position,
    )


def normalise_document_tokens(
    tokens: Iterable[Token], sign_labels: frozenset[str]
) -> list[NormalisedToken]:
    return [reclassify(t, sign_labels) for t in tokens]


@dataclass
class AuditTable:
    """Counts-by-rule for everything normalisation changed. Safe to publish.

    Deliberately counts only — no token lists — so the table can live in the repo
    without redistributing NonCommercial corpus content.
    """

    total_tokens: int = 0
    underdotted_tokens: int = 0
    underdotted_sign_positions: int = 0
    span_bracket_tokens: int = 0
    reclassified: dict[str, int] = field(default_factory=dict)
    vocabulary_raw: int = 0
    vocabulary_normalised: int = 0

    def as_rows(self) -> list[tuple[str, int]]:
        rows = [
            ("tokens seen", self.total_tokens),
            ("tokens carrying an underdot", self.underdotted_tokens),
            ("sign positions carrying an underdot", self.underdotted_sign_positions),
            ("tokens carrying a span bracket", self.span_bracket_tokens),
            ("sign vocabulary before normalisation", self.vocabulary_raw),
            ("sign vocabulary after normalisation", self.vocabulary_normalised),
        ]
        rows += [(f"reclassified UNKNOWN → {k}", v) for k, v in sorted(self.reclassified.items())]
        return rows


def audit(
    raw: Iterable[Token], normalised: Iterable[NormalisedToken]
) -> AuditTable:
    """Build the counts-by-rule table for a normalisation pass."""
    table = AuditTable()
    raw_vocab: set[str] = set()
    norm_vocab: set[str] = set()

    for token in raw:
        if token.kind is TokenKind.WORD:
            raw_vocab.update(token.signs)

    for tok in normalised:
        table.total_tokens += 1
        if tok.damaged_but_read:
            table.underdotted_tokens += 1
            table.underdotted_sign_positions += len(tok.signs)
        if tok.had_span_bracket:
            table.span_bracket_tokens += 1
        if tok.reclassified_from is not None:
            key = tok.kind.name
            table.reclassified[key] = table.reclassified.get(key, 0) + 1
        if tok.kind is TokenKind.WORD:
            norm_vocab.update(tok.signs)

    table.vocabulary_raw = len(raw_vocab)
    table.vocabulary_normalised = len(norm_vocab)
    return table


def sign_label_set(corpus: object) -> frozenset[str]:
    """The attested Linear B signary, upper-cased, for reclassification lookups.

    DĀMOS transliterates in lowercase (``pa-ro``) while the inventory labels are
    upper-case (``PA``, ``RO``), so every membership test goes through ``.upper()``.
    """
    inventory: Mapping = getattr(corpus, "sign_inventory")
    return frozenset(s.label.upper() for s in inventory.signs)
