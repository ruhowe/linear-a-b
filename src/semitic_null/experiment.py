"""The test: does the real sign-value assignment beat fictitious ones?

Protocol, following Packard (1974) and the validation criteria Raghavendra (2026) sets
out for the Indus script:

1. Take the Linear A lexical words (multi-sign, `CERTAIN`, excluding logogram chains).
2. Under a sign→consonant-set map, expand each word to the cross-product of its per-sign
   consonant options — every Hebrew skeleton the word *could* represent.
3. Score the word a **hit** if any of those skeletons is an attested Hebrew root.
4. Report the corpus-wide hit rate.
5. Repeat with the sign→value assignment **permuted** many times. Word shapes, sign
   frequencies and candidate-set sizes are unchanged; only which sound belongs to which
   sign is destroyed.

The real assignment is evidence only to the extent that it beats the permuted ones. The
p-value is the fraction of permutations scoring at least as high as the real map, which
is a one-sided permutation test with no distributional assumption.

Two secondary measures, because the hit rate alone can mislead:

- **Candidate breadth**: how many distinct Hebrew skeletons each word can reach. This is
  the degrees of freedom the method is spending, stated as a number.
- **Length stratification**: two-sign words reach short skeletons where the root space is
  denser, so they are separated out.
"""

from __future__ import annotations

import itertools
import random
import statistics
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .lexicon import Lexicon
from .phonology import ConsonantMap

__all__ = ["WordResult", "ScoreResult", "NullResult", "score_words", "run_null"]


@dataclass(frozen=True, slots=True)
class WordResult:
    word: str
    n_signs: int
    n_candidates: int
    hit: bool
    matched: tuple[str, ...] = ()


@dataclass
class ScoreResult:
    """One assignment's performance over the whole word list."""

    label: str
    words: list[WordResult] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.words)

    @property
    def hit_rate(self) -> float:
        return statistics.fmean([w.hit for w in self.words]) if self.words else 0.0

    @property
    def mean_candidates(self) -> float:
        return statistics.fmean([w.n_candidates for w in self.words]) if self.words else 0.0

    def by_length(self) -> dict[int, float]:
        buckets: dict[int, list[bool]] = {}
        for w in self.words:
            buckets.setdefault(w.n_signs, []).append(w.hit)
        return {k: statistics.fmean(v) for k, v in sorted(buckets.items())}

    def counts_by_length(self) -> dict[int, int]:
        buckets: dict[int, int] = {}
        for w in self.words:
            buckets[w.n_signs] = buckets.get(w.n_signs, 0) + 1
        return dict(sorted(buckets.items()))


def _skeletons(signs: Sequence[str], cmap: ConsonantMap, cap: int = 20000):
    """Every Hebrew consonant skeleton this sign sequence could write.

    A pure-vowel sign contributes a laryngeal *or* nothing at all — Semitic ʾ/ʿ/h are
    frequently unwritten in an Aegean spelling, and the tested reading relies on that
    (``A-TA-I-*301-WA-JA`` → ``ʾatainawaya`` treats the initial A as ʾ, while medial
    vowels drop). Allowing both is the more permissive and therefore fairer reading of
    the method.
    """
    options: list[tuple[str, ...]] = []
    for sign in signs:
        allowed = cmap.get(sign)
        if allowed is None:
            return None
        opts = tuple(sorted(allowed))
        options.append(opts + ("",) if len(opts) == 4 and "ʾ" in allowed else opts)
    total = 1
    for opt in options:
        total *= len(opt)
        if total > cap:
            return None
    return {"".join(combo) for combo in itertools.product(*options)}


def score_words(
    words: Iterable[Sequence[str]],
    cmap: ConsonantMap,
    lex: Lexicon,
    *,
    label: str = "real",
    min_len: int = 2,
    max_len: int = 4,
) -> ScoreResult:
    """Score one assignment. ``words`` is an iterable of sign-label sequences."""
    result = ScoreResult(label=label)
    for signs in words:
        skels = _skeletons(signs, cmap)
        if skels is None:
            continue
        usable = {s for s in skels if min_len <= len(s) <= max_len}
        if not usable:
            continue
        matched = tuple(sorted(s for s in usable if lex.attested(s)))
        result.words.append(
            WordResult(
                word="-".join(signs),
                n_signs=len(signs),
                n_candidates=len(usable),
                hit=bool(matched),
                matched=matched[:5],
            )
        )
    return result


@dataclass
class NullResult:
    """The real assignment against N fictitious ones."""

    real: ScoreResult
    null_rates: list[float]
    n_permutations: int

    @property
    def p_value(self) -> float:
        """One-sided: how often a fictitious decipherment does at least as well.

        Add-one smoothing, so with 999 permutations the floor is 1/1000 rather than 0.
        """
        at_least = sum(1 for r in self.null_rates if r >= self.real.hit_rate)
        return (at_least + 1) / (self.n_permutations + 1)

    @property
    def null_mean(self) -> float:
        return statistics.fmean(self.null_rates) if self.null_rates else 0.0

    @property
    def null_sd(self) -> float:
        return statistics.pstdev(self.null_rates) if len(self.null_rates) > 1 else 0.0

    @property
    def z(self) -> float:
        return (self.real.hit_rate - self.null_mean) / self.null_sd if self.null_sd else 0.0

    def summary(self) -> dict:
        return {
            "real_hit_rate": self.real.hit_rate,
            "null_mean": self.null_mean,
            "null_sd": self.null_sd,
            "null_min": min(self.null_rates) if self.null_rates else 0.0,
            "null_max": max(self.null_rates) if self.null_rates else 0.0,
            "z": self.z,
            "p_value": self.p_value,
            "n_permutations": self.n_permutations,
            "n_words": self.real.n,
            "mean_candidates_per_word": self.real.mean_candidates,
            "hit_rate_by_length": self.real.by_length(),
            "words_by_length": self.real.counts_by_length(),
        }


def run_null(
    words: Sequence[Sequence[str]],
    cmap: ConsonantMap,
    lex: Lexicon,
    *,
    n_permutations: int = 999,
    seed: int = 0,
) -> NullResult:
    real = score_words(words, cmap, lex, label="real")
    rng = random.Random(seed)
    rates: list[float] = []
    for i in range(n_permutations):
        permuted = cmap.permute(rng)
        rates.append(score_words(words, permuted, lex, label=f"null{i}").hit_rate)
    return NullResult(real=real, null_rates=rates, n_permutations=n_permutations)
