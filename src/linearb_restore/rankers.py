"""The four non-neural baselines. Each ranks the frozen candidate set for a masked slot.

They exist in a deliberate order of increasing information, so that what each addition
buys can be measured rather than assumed:

``prior``
    Sign frequency alone. **The floor.** Every top-k figure in this project is quoted
    against it, because on a 77-sign inventory top-20 admits a quarter of all candidates
    and frequency alone therefore scores far higher than intuition suggests. The
    published top-20 numbers this project reproduces sit close to this line.

``bigram``
    Witten-Bell-smoothed sign bigrams, via ``aegean.analysis.surprisal`` — pyaegean's
    own module, used as-is with no new modelling code. Scores a candidate by the mean
    surprisal of the word it would complete, so it uses within-word context only.

``lexicon``
    Look the masked pattern up among word types seen in training and rank by frequency.
    Pure memorisation, and on this corpus that is *strong*, because the D tablets repeat
    a small set of place names constantly. Its collapse on unseen words is the clearest
    evidence that the aggregate figures measure recall of a gazetteer.

``backoff``
    ``lexicon`` where it has an opinion, then ``bigram``, then ``prior``.

A ranker returns candidates best-first. Ties break on frequency then alphabetically, so
a run is reproducible.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence as Seq

from aegean.analysis.surprisal import train_sign_bigram_model, word_surprisal

from .mask import MASK, MaskedItem
from .vocab import Vocabulary

__all__ = ["Ranker", "PriorRanker", "BigramRanker", "LexiconRanker", "BackoffRanker", "build_all"]


class Ranker(Protocol):
    name: str

    def fit(self, train: Seq[MaskedItem], vocab: Vocabulary) -> "Ranker": ...

    def rank(self, item: MaskedItem) -> list[str]: ...


@dataclass
class PriorRanker:
    """B0a — unigram sign frequency. The floor."""

    name: str = "prior"
    _order: tuple[str, ...] = ()

    def fit(self, train: Seq[MaskedItem], vocab: Vocabulary) -> "PriorRanker":
        self._order = vocab.by_frequency
        return self

    def rank(self, item: MaskedItem) -> list[str]:
        return list(self._order)


@dataclass
class BigramRanker:
    """B0b — Witten-Bell sign bigram, reusing ``aegean.analysis.surprisal`` unmodified.

    For each candidate, the masked word is completed and scored; lower mean surprisal
    ranks higher. ``self_count=0`` throughout: the candidate word is hypothetical, so it
    must never receive credit for its own attestation.

    The model trains on hyphen-joined word types with counts, which is exactly what
    ``train_sign_bigram_model`` expects. Single-sign words contribute no transitions and
    are skipped by that function by design.
    """

    name: str = "bigram"
    _model: object | None = None
    _fallback: tuple[str, ...] = ()

    def fit(self, train: Seq[MaskedItem], vocab: Vocabulary) -> "BigramRanker":
        counts: Counter[str] = Counter()
        for item in train:
            filled = tuple(
                item.answers[0] if s == MASK else s for s in item.word_signs
            ) if item.n_masked == 1 else None
            if filled and len(filled) > 1:
                counts["-".join(filled)] += 1
        self._model = train_sign_bigram_model(list(counts.items()))
        self._fallback = vocab.by_frequency
        return self

    def rank(self, item: MaskedItem) -> list[str]:
        if self._model is None or len(item.word_signs) < 2:
            return list(self._fallback)
        scored: list[tuple[float, int, str]] = []
        freq_rank = {s: i for i, s in enumerate(self._fallback)}
        for candidate in self._fallback:
            signs = [candidate if s == MASK else s for s in item.word_signs]
            bits = word_surprisal(self._model, "-".join(signs), self_count=0).mean
            scored.append((bits, freq_rank.get(candidate, 10**6), candidate))
        scored.sort()
        return [c for _, _, c in scored]


@dataclass
class LexiconRanker:
    """B0c — match the masked pattern against training word types.

    Memorisation, and on this corpus a strong baseline: the same place names recur
    across dozens of tablets. Backs off to the frequency prior when the pattern matches
    nothing, which is what happens for genuinely new material.
    """

    name: str = "lexicon"
    _by_pattern: dict[tuple[str, ...], Counter] = None  # type: ignore[assignment]
    _fallback: tuple[str, ...] = ()

    def fit(self, train: Seq[MaskedItem], vocab: Vocabulary) -> "LexiconRanker":
        by_pattern: dict[tuple[str, ...], Counter] = defaultdict(Counter)
        for word, count in vocab.word_counts.items():
            signs = tuple(word.split("-"))
            for i in range(len(signs)):
                pattern = signs[:i] + (MASK,) + signs[i + 1 :]
                by_pattern[pattern][signs[i]] += count
        self._by_pattern = dict(by_pattern)
        self._fallback = vocab.by_frequency
        return self

    def rank(self, item: MaskedItem) -> list[str]:
        matches = self._by_pattern.get(tuple(item.word_signs))
        if not matches:
            return list(self._fallback)
        freq_rank = {s: i for i, s in enumerate(self._fallback)}
        ordered = sorted(matches, key=lambda s: (-matches[s], freq_rank.get(s, 10**6), s))
        rest = [s for s in self._fallback if s not in matches]
        return ordered + rest


@dataclass
class BackoffRanker:
    """B0d — lexicon, then bigram, then prior, concatenated without repetition."""

    name: str = "backoff"
    _lexicon: LexiconRanker | None = None
    _bigram: BigramRanker | None = None

    def fit(self, train: Seq[MaskedItem], vocab: Vocabulary) -> "BackoffRanker":
        self._lexicon = LexiconRanker().fit(train, vocab)
        self._bigram = BigramRanker().fit(train, vocab)
        return self

    def rank(self, item: MaskedItem) -> list[str]:
        assert self._lexicon and self._bigram
        matched = self._lexicon._by_pattern.get(tuple(item.word_signs))
        order = self._lexicon.rank(item) if matched else self._bigram.rank(item)
        seen: set[str] = set()
        out: list[str] = []
        for candidate in order:
            if candidate not in seen:
                seen.add(candidate)
                out.append(candidate)
        return out


def build_all() -> list[Ranker]:
    return [PriorRanker(), BigramRanker(), LexiconRanker(), BackoffRanker()]
