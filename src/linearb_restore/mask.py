"""Turn eligible sequences into evaluable masked-prediction items.

**Why synthetic masking rather than real lacunae.** A genuinely ``LOST`` sign has no
ground truth — that is what makes it lost. Accuracy can only be measured where the
answer is known, so evaluation items are made by hiding a sign that *is* securely read
and asking the model to recover it. Real lacunae are what a trained model is later
pointed at, in the clearly-labelled EXPLORATORY pass; they are never part of a headline
metric.

**Regimes.** ``leave_one_out`` is the headline: every eligible sign position becomes one
item, so the item set is deterministic, maximally efficient on a small corpus, and each
item is independently resamplable by a bootstrap. Two harder regimes are reported
separately because they are closer to real damage: ``span`` hides 2–3 adjacent signs
(removing the left-and-right anchoring that makes a bigram look strong), and
``word_final`` hides the last sign of a word (the commonest real case, a broken right
edge).

**No augmentation and no duplication.** The published series-D dataset reached 2,565
sequences from 513 real ones by adding 725 augmented and 1,327 duplicated sequences.
Duplication adds no information, inflates apparent training size, and risks the same
sequence landing on both sides of a split. This is a deliberate, stated departure.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Literal, Sequence as Seq

from aegean.core.model import TokenKind

from .extract import NUM, SEP, SequenceRecord

__all__ = ["MASK", "MaskedItem", "make_items", "Regime"]

MASK = "<MASK>"
Regime = Literal["leave_one_out", "span", "word_final"]


@dataclass(frozen=True, slots=True)
class MaskedItem:
    """One prediction problem: a context with holes, and the signs that filled them.

    ``left`` and ``right`` are the flat symbol streams either side of the masked span,
    so a model can use as much or as little context as it wants. ``word_signs`` keeps
    the target word's own signs with the masked positions replaced by ``MASK``, since
    the within-word pattern is what the lexicon and bigram baselines key on.
    """

    doc_id: str
    line_no: int
    subseries: str
    scribe: str | None
    findspot: str | None
    regime: str

    answers: tuple[str, ...]  # the hidden sign(s), in order
    left: tuple[str, ...]  # sequence context before the masked span
    right: tuple[str, ...]  # sequence context after it
    word_signs: tuple[str, ...]  # the target word, masked
    word_text: str  # the target word's surface form, unmasked
    word_index: int  # which token in the sequence
    sign_index: int  # first masked sign's index within the word

    @property
    def single_sign_word(self) -> bool:
        """True when the target word has no within-word context at all.

        These are a genuinely different prediction problem — the bigram baseline
        cannot even train on them, since ``train_sign_bigram_model`` skips words
        with no ``-`` — so they are reported as their own stratum.
        """
        return len(self.word_signs) == 1

    @property
    def n_masked(self) -> int:
        return len(self.answers)


def _flatten(record: SequenceRecord) -> tuple[list[str], list[tuple[int, int]]]:
    """The sequence as a symbol stream, plus a map from stream index to (token, sign).

    Non-word tokens occupy one stream slot each and map to ``(-1, -1)``, so context is
    preserved without ever being maskable.
    """
    stream: list[str] = []
    origin: list[tuple[int, int]] = []
    for ti, tok in enumerate(record.tokens):
        if tok.kind is TokenKind.WORD:
            for si, sign in enumerate(tok.signs):
                stream.append(sign)
                origin.append((ti, si))
        elif tok.kind is TokenKind.NUMERAL:
            stream.append(NUM)
            origin.append((-1, -1))
        elif tok.kind is TokenKind.SEPARATOR:
            stream.append(SEP)
            origin.append((-1, -1))
        elif tok.kind is TokenKind.LOGOGRAM:
            for sign in tok.signs or (tok.text,):
                stream.append(sign)
                origin.append((-1, -1))
    return stream, origin


def _item(
    record: SequenceRecord,
    stream: Seq[str],
    origin: Seq[tuple[int, int]],
    stream_positions: Seq[int],
    regime: str,
) -> MaskedItem | None:
    """Build one item hiding the given stream positions (which must be one word's)."""
    if not stream_positions:
        return None
    first, last = stream_positions[0], stream_positions[-1]
    ti, si = origin[first]
    if ti < 0:
        return None
    token = record.tokens[ti]

    masked_sign_indices = {origin[p][1] for p in stream_positions}
    word_signs = tuple(
        MASK if i in masked_sign_indices else s for i, s in enumerate(token.signs)
    )

    return MaskedItem(
        doc_id=record.doc_id,
        line_no=record.line_no,
        subseries=record.subseries,
        scribe=record.scribe,
        findspot=record.findspot,
        regime=regime,
        answers=tuple(stream[p] for p in stream_positions),
        left=tuple(stream[:first]),
        right=tuple(stream[last + 1 :]),
        word_signs=word_signs,
        word_text=token.text,
        word_index=ti,
        sign_index=si,
    )


def make_items(
    records: Iterable[SequenceRecord],
    *,
    regime: Regime = "leave_one_out",
    span: int = 2,
    seed: int = 0,
) -> list[MaskedItem]:
    """Build the evaluation items for one masking regime.

    ``leave_one_out`` yields one item per eligible sign position. ``span`` yields one
    item per eligible start position that has ``span`` consecutive eligible positions
    inside the same word. ``word_final`` yields one item per eligible word, hiding its
    last sign (single-sign words are skipped: hiding their only sign leaves nothing).
    """
    rng = random.Random(seed)  # reserved for future sampling regimes; unused here
    del rng
    items: list[MaskedItem] = []

    for record in records:
        if not record.eligible:
            continue
        maskable = record.maskable_positions()
        if not maskable:
            continue
        allowed = {(ti, si) for ti, si, _ in maskable}
        stream, origin = _flatten(record)
        by_token: dict[int, list[int]] = {}
        for p, (ti, si) in enumerate(origin):
            if (ti, si) in allowed:
                by_token.setdefault(ti, []).append(p)

        for ti, positions in by_token.items():
            if regime == "leave_one_out":
                for p in positions:
                    item = _item(record, stream, origin, [p], regime)
                    if item:
                        items.append(item)
            elif regime == "span":
                for start in range(len(positions) - span + 1):
                    window = positions[start : start + span]
                    if window[-1] - window[0] != span - 1:
                        continue  # not contiguous in the stream
                    item = _item(record, stream, origin, window, f"span{span}")
                    if item:
                        items.append(item)
            elif regime == "word_final":
                token = record.tokens[ti]
                if len(token.signs) < 2:
                    continue
                last_position = positions[-1]
                if origin[last_position][1] != len(token.signs) - 1:
                    continue  # the word's final sign was not eligible
                item = _item(record, stream, origin, [last_position], regime)
                if item:
                    items.append(item)
            else:  # pragma: no cover - guarded by the Literal type
                raise ValueError(f"unknown regime {regime!r}")

    return items
