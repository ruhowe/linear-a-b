"""Extract restorable sequences from the Knossos D family of DĀMOS.

**Sequence unit: one physical line** (``Document.line_tokens``). Chosen because it is
the only unit that reproduces the published corpus sizes. Measured against the Patras
group's own figures:

===========================================  =========================  =======
Their figure                                 This extraction            Match
===========================================  =========================  =======
LREC 2020 "308 KN tablets" (series A&B)      225 + 83 = 308             exact
LREC 2020 651 sequences from those           695 lines bearing signs    close
JOCCH 2023 513 complete series-D sequences   536 eligible D lines       close
===========================================  =========================  =======

Whole-document completeness was rejected: it yields 174 for D and 12 for A&B, and 12
cannot underlie their reported 426.

Eligibility, and why each rule is drawn where it is:

* A line qualifies when it carries at least one ``WORD`` token and **every** ``WORD``
  token on it is ``CERTAIN``. Damage confined to a numeral or a broken right edge does
  not disqualify the words — this is what brings 536 close to their 513.
* ``UNCLEAR`` is excluded. In DĀMOS that status conflates partial editorial
  restoration (``da-*22[-to``), lacuna-edge truncation where the word may be incomplete
  (``]ku-ta-to``), and an editorial query. Only the first is "damaged but read"; the
  second is not ground truth at all, and the status field alone cannot separate them.
* Underdotted signs stay as **context** but are ineligible as masking **targets**
  (see ``normalise``). They are damaged-but-legible, so predicting them is not the
  same task as predicting a securely read sign.
* Apparatus tokens (``mut.``, ``vest.``, bare brackets) are dropped from the content
  stream and recorded as the *cause* of incompleteness instead.
* Numerals collapse to a single ``NUM`` context symbol: on these tablets their
  identity is mostly unique integers (noise), while their presence is real signal.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Sequence as Seq

from aegean.analysis.hands import series_of
from aegean.core.model import Document, ReadingStatus, TokenKind

from .normalise import NormalisedToken, normalise_document_tokens, sign_label_set

__all__ = [
    "NUM",
    "SequenceRecord",
    "d_family",
    "extract_sequences",
    "corpus_summary",
]

NUM = "<NUM>"  # numerals collapse to one context symbol
SEP = "<SEP>"


@dataclass(frozen=True, slots=True)
class SequenceRecord:
    """One physical line, normalised, with the metadata a grouped split needs."""

    doc_id: str
    line_no: int
    subseries: str
    site: str | None
    scribe: str | None
    findspot: str | None
    period: str | None
    tokens: tuple[NormalisedToken, ...]
    eligible: bool
    ineligible_reason: str | None = None
    single_sign_words_included: bool = True

    def _counts_as_word(self, tok: NormalisedToken) -> bool:
        if tok.kind is not TokenKind.WORD:
            return False
        if not self.single_sign_words_included and tok.reclassified_from is not None:
            return False
        return True

    @property
    def word_tokens(self) -> tuple[NormalisedToken, ...]:
        return tuple(t for t in self.tokens if self._counts_as_word(t))

    @property
    def context_symbols(self) -> tuple[str, ...]:
        """The sequence as a flat symbol stream: signs, logogram labels, NUM, SEP."""
        out: list[str] = []
        for tok in self.tokens:
            if tok.kind is TokenKind.WORD:
                out.extend(tok.signs)
            elif tok.kind is TokenKind.NUMERAL:
                out.append(NUM)
            elif tok.kind is TokenKind.SEPARATOR:
                out.append(SEP)
            elif tok.kind is TokenKind.LOGOGRAM:
                out.extend(tok.signs or (tok.text,))
        return tuple(out)

    def maskable_positions(self) -> list[tuple[int, int, str]]:
        """``(token_index, sign_index, sign)`` for every eligible masking target.

        Targets are signs of ``CERTAIN`` ``WORD`` tokens that carry no underdot.
        """
        positions: list[tuple[int, int, str]] = []
        if not self.eligible:
            return positions
        for ti, tok in enumerate(self.tokens):
            if not self._counts_as_word(tok):
                continue
            if tok.status is not ReadingStatus.CERTAIN or tok.damaged_but_read:
                continue
            for si, sign in enumerate(tok.signs):
                positions.append((ti, si, sign))
        return positions


def d_family(corpus) -> list[Document]:
    """The Knossos D-family documents: sheep and wool accounts, subseries Da–Dv.

    ``series_of`` parses the alphabetic run of a designation's second field and does
    **not** collapse ``Da``/``Db``/``Dv`` into a shared ``D`` — that grouping is the
    caller's job, done here by prefix. The Patras papers' exact subseries filter is
    unconfirmed by any accessible source, so the whole family is taken: going narrower
    would be a guess dressed as a replication.
    """
    docs = []
    for doc in corpus.documents:
        series = series_of(doc)
        if not series or not series.startswith("D"):
            continue
        if doc.meta.site != "Knossos" or doc.meta.support != "tablet":
            continue
        docs.append(doc)
    return docs


def _line_token_indices(doc: Document) -> list[list[int]]:
    """Physical lines as token-index lists, falling back to one line per document."""
    if doc.lines:
        return [list(line) for line in doc.lines]
    return [list(range(len(doc.tokens)))]


def extract_sequences(
    corpus,
    docs: Iterable[Document] | None = None,
    *,
    include_single_sign_words: bool = True,
) -> list[SequenceRecord]:
    """Normalise and cut the given documents (default: the D family) into line sequences.

    ``include_single_sign_words`` controls whether one-sign syllabic tokens that
    ``normalise.reclassify`` promoted from ``UNKNOWN`` to ``WORD`` count as words for
    eligibility and masking. Both settings are legitimate and both are reported:

    * ``True`` (default) — 596 eligible D sequences. The linguistically correct
      reading: ``o``, ``ki``, ``pa`` are real signs the scribe wrote, and on these
      tablets they are meaningful adjuncts (``o`` abbreviates *o-pe-ro*, "deficit").
    * ``False`` — 536 eligible D sequences, the figure that sits closest to the
      Patras group's published 513, since their extraction came from printed editions
      that do not isolate these as words.

    Single-sign targets are tracked as their own stratum regardless, because a sign
    with no within-word context is a different prediction problem from one flanked by
    its own word's signs — and the bigram baseline cannot even train on them
    (``train_sign_bigram_model`` skips words with no ``-``).
    """
    labels = sign_label_set(corpus)
    documents = list(docs) if docs is not None else d_family(corpus)
    records: list[SequenceRecord] = []

    def is_word(tok: NormalisedToken) -> bool:
        if tok.kind is not TokenKind.WORD:
            return False
        if not include_single_sign_words and tok.reclassified_from is not None:
            return False
        return True

    for doc in documents:
        normalised = normalise_document_tokens(doc.tokens, labels)
        subseries = series_of(doc) or "?"
        for line_no, indices in enumerate(_line_token_indices(doc)):
            line = [normalised[i] for i in indices if i < len(normalised)]
            content = [t for t in line if not t.is_apparatus]
            words = [t for t in content if is_word(t)]

            if not words:
                eligible, reason = False, "no word token"
            elif any(t.status is not ReadingStatus.CERTAIN for t in words):
                eligible, reason = False, "a word token is not CERTAIN"
            else:
                eligible, reason = True, None

            records.append(
                SequenceRecord(
                    doc_id=doc.id,
                    line_no=line_no,
                    subseries=subseries,
                    site=doc.meta.site,
                    scribe=doc.meta.scribe,
                    findspot=doc.meta.findspot,
                    period=doc.meta.period,
                    tokens=tuple(content),
                    eligible=eligible,
                    ineligible_reason=reason,
                    single_sign_words_included=include_single_sign_words,
                )
            )
    return records


@dataclass
class CorpusSummary:
    """Publishable aggregate description of an extraction — counts only, no content."""

    documents: int = 0
    lines: int = 0
    eligible_sequences: int = 0
    sign_vocabulary: int = 0
    maskable_positions: int = 0
    word_tokens: int = 0
    word_types: int = 0
    by_subseries: dict[str, int] = field(default_factory=dict)
    ineligible_reasons: dict[str, int] = field(default_factory=dict)

    def as_rows(self) -> list[tuple[str, int]]:
        return [
            ("documents", self.documents),
            ("physical lines", self.lines),
            ("eligible sequences", self.eligible_sequences),
            ("sign vocabulary (eligible targets)", self.sign_vocabulary),
            ("maskable sign positions", self.maskable_positions),
            ("word tokens (eligible sequences)", self.word_tokens),
            ("word types (eligible sequences)", self.word_types),
        ]


def corpus_summary(records: Seq[SequenceRecord]) -> CorpusSummary:
    summary = CorpusSummary()
    docs: set[str] = set()
    vocab: set[str] = set()
    word_types: set[str] = set()
    subseries: Counter[str] = Counter()
    reasons: Counter[str] = Counter()

    for rec in records:
        docs.add(rec.doc_id)
        summary.lines += 1
        subseries[rec.subseries] += 1
        if not rec.eligible:
            reasons[rec.ineligible_reason or "?"] += 1
            continue
        summary.eligible_sequences += 1
        positions = rec.maskable_positions()
        summary.maskable_positions += len(positions)
        vocab.update(sign for _, _, sign in positions)
        for tok in rec.word_tokens:
            summary.word_tokens += 1
            word_types.add(tok.text)

    summary.documents = len(docs)
    summary.sign_vocabulary = len(vocab)
    summary.word_types = len(word_types)
    summary.by_subseries = dict(subseries.most_common())
    summary.ineligible_reasons = dict(reasons.most_common())
    return summary
