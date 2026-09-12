"""The candidate set a ranker chooses from, frozen per run.

Every baseline answers the same question: given a masked position, rank all candidate
signs. The candidate set must therefore be fixed and stated, because **top-k accuracy is
meaningless without it** — top-20 over a 75-sign inventory covers 27% of all candidates,
so it sits close to what frequency alone achieves. This is the single most important
caveat on the published figures this project is reproducing, and freezing the vocabulary
here is what makes it measurable.

The candidate set is built from **training data only**. Building it from the whole
corpus would leak: a sign attested solely in the test fold would be rankable, and in the
degenerate case a rare sign's only occurrence would be its own answer.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

__all__ = ["Vocabulary", "build_vocabulary"]


@dataclass(frozen=True, slots=True)
class Vocabulary:
    """The frozen candidate set, with the unigram counts a frequency prior needs."""

    signs: tuple[str, ...]
    counts: dict[str, int] = field(default_factory=dict)
    word_types: frozenset[str] = frozenset()
    word_counts: dict[str, int] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.signs)

    @property
    def by_frequency(self) -> tuple[str, ...]:
        """Candidates most-frequent first — the B0a prior, and every ranker's tiebreak."""
        return tuple(
            sorted(self.signs, key=lambda s: (-self.counts.get(s, 0), s))
        )

    def top_k_share(self, k: int) -> float:
        """What fraction of the candidate set a top-k metric admits.

        Report this next to every top-k number. At k=20 over 77 signs it is 0.26, which
        is why top-20 is close to uninformative here.
        """
        return min(k, len(self.signs)) / len(self.signs) if self.signs else 0.0

    def seen_word(self, word_text: str) -> bool:
        """Whether this word type occurred in training — the stratification key.

        The seen/unseen split is the difference between measuring memorisation of
        recurring place names and measuring generalisation to new material.
        """
        return word_text in self.word_types


def build_vocabulary(train_items: Iterable) -> Vocabulary:
    """Build the candidate set from training items only.

    **Candidates are exactly the signs that can be masked** — the signs of word tokens,
    including each item's own answer, which in a *training* item is observed data. The
    surrounding stream is deliberately not a source of candidates: it carries logogram
    labels (``OVIS:m``), ``<NUM>`` and ``<SEP>``, none of which is ever a prediction
    target, and admitting them would inflate the candidate set and silently depress
    every top-k figure.

    Never call this on test items: the candidate set would then include signs attested
    only in the test fold, and a rare sign's sole occurrence could be its own answer.
    """
    counts: Counter[str] = Counter()
    word_counts: Counter[str] = Counter()

    for item in train_items:
        for sign in item.word_signs:
            if sign != "<MASK>":
                counts[sign] += 1
        for sign in item.answers:
            counts[sign] += 1
        word_counts[item.word_text] += 1

    return Vocabulary(
        signs=tuple(sorted(counts)),
        counts=dict(counts),
        word_types=frozenset(word_counts),
        word_counts=dict(word_counts),
    )
