"""The medial channel: word pairs identical except at one interior sign
(Kober 0.9, CHANGELOG "0.9"; A-140 onward).

**Medial pair.** For word types of three or more signs: two words of the same
length are a medial pair when they agree at every position except exactly one
*interior* position (index 1 to n-2, 0-indexed -- "positions 2 to n-1" in the
design page's 1-based wording, i.e. never the first or last sign). This is
Packard's third alternation class, "first and third signs identical, second
differs", generalised from three-sign words to any interior position on a
word of any length >= 3.

**Alternation and support.** The **alternation** a medial pair belongs to is
the unordered pair of its two differing signs; an alternation's **support**
is the number of word pairs found with that differing sign pair, at any
interior position and any word length (A-140: this mirrors how
``paradigms.alternation_support`` groups by the ending pair alone, not by
which stem produced it). The **pair count** reported for the channel is the
total number of medial word pairs found -- the sum of every alternation's
support (A-140) -- the medial channel's analogue of stage 1's paradigm count:
"how much of this structure exists", read against N1.

**Finding pairs without O(n^2) comparison.** For a length class and an
interior position i, two words can only differ at i alone if they are
identical everywhere else. Grouping the class's words by their own sign
tuple with position i removed (a "masked key") puts exactly the words that
agree everywhere but position i into one bucket; since word *types* are
already deduplicated, two words sharing a masked key cannot also share the
value at i (that would make them the same tuple), so every pair within a
bucket of size >= 2 is one medial pair, and no pair is found twice across
different (length, position) buckets, because a pair differing at more than
one position never produces a matching masked key at any single position.

**Null for the pair count: N1**, exactly as stage 1's paradigm count
(``nulls.n1_draw``, full-word position shuffle), under its own independent
stream (``medial_n1``, A-142) so a ``--medial`` run's N1 draws for stage 1
are untouched.

**Null for the ranked pairs: N3** (``nulls.n3_draw``, A-142), which shuffles
only the interior position columns within each length class and leaves the
first and last sign of every word attached to it -- the "flanking signs
held fixed" the design page specifies -- under its own independent stream
(``medial_n3``). Used for the maximum support and for the consonant-sharing
fraction of the top twenty pairs, from the same 200 draws (no extra
randomness, following the pattern ``grid.py`` and ``nulls.run_n2`` already
set of reusing one draw for several statistics).

**Top twenty pairs (A-143).** Ranked by support descending, then the sign
pair in sorted lexicographic order -- a strict cut at exactly 20, the same
tie-break style as ``paradigms.ranked_alternations`` and the plain
``top_20_alternations`` stage 1 already reports, not the ties-included
convention (A-053) stage 2's anchoring uses. The same 20 entries feed both
the display table and the consonant-sharing fraction, on both the real
corpus and every N3 draw.

**Consonant-sharing statistic.** Reuses ``grid.consonant_fraction_from_pairs``
over the top twenty pairs' own sign pairs: the fraction sharing a consonant
under ``values.consonant_of`` (Ventris's known values, consulted only after
the ranking is fixed), and, for information only, the chance fraction (sum
of squared consonant proportions among the scored signs) -- the same
statistic stage 2 reports beside its own fractions.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping

from .grid import ConsonantFraction, consonant_fraction_from_pairs
from .nulls import NullDistribution, _sub_seed, _summarise, n1_draw, n3_draw
from .paradigms import Word
from .values import consonant_of

__all__ = [
    "medial_pairs",
    "ranked_medial_pairs",
    "MedialPairEntry",
    "MedialReport",
    "build_medial_report",
    "render_medial_markdown",
]

_VERSION = "0.9"


def medial_pairs(words: Iterable[Word]) -> dict[tuple[str, str], int]:
    """Medial alternations and their support, over word types of length >= 3.

    Returns a mapping from the unordered pair of differing signs to the
    number of word pairs found with that difference at some interior
    position of some shared length (A-140).
    """
    eligible = [w for w in words if len(w) >= 3]
    support: dict[tuple[str, str], int] = defaultdict(int)
    by_length: dict[int, list[Word]] = defaultdict(list)
    for w in eligible:
        by_length[len(w)].append(w)

    for n, group in by_length.items():
        for i in range(1, n - 1):
            buckets: dict[Word, list[str]] = defaultdict(list)
            for w in group:
                buckets[w[:i] + w[i + 1 :]].append(w[i])
            for signs in buckets.values():
                if len(signs) < 2:
                    continue
                # Words sharing a masked key are, by construction, distinct
                # word types agreeing everywhere but position i, so their
                # values at i are pairwise distinct too (equal values would
                # make the two words identical tuples).
                for s1, s2 in combinations(signs, 2):
                    pair = (s1, s2) if s1 < s2 else (s2, s1)
                    support[pair] += 1
    return dict(support)


def ranked_medial_pairs(
    support: Mapping[tuple[str, str], int], limit: int | None = None
) -> list[tuple[tuple[str, str], int]]:
    """Medial alternations ranked by support descending, ties broken by the
    sign pair in sorted lexicographic order (A-143) -- a strict cut at
    ``limit``, not the ties-included convention (A-053)."""
    ranked = sorted(support.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked if limit is None else ranked[:limit]


@dataclass(frozen=True, slots=True)
class MedialPairEntry:
    s1: str
    s2: str
    support: int
    shares_consonant: bool | None  # None when either sign is excluded from consonant_of

    def as_dict(self) -> dict:
        return {
            "s1": self.s1,
            "s2": self.s2,
            "support": self.support,
            "shares_consonant": self.shares_consonant,
        }


def _entries(ranked: list[tuple[tuple[str, str], int]]) -> list[MedialPairEntry]:
    entries = []
    for (s1, s2), support in ranked:
        c1, c2 = consonant_of(s1), consonant_of(s2)
        shares = (c1 == c2) if (c1 is not None and c2 is not None) else None
        entries.append(MedialPairEntry(s1=s1, s2=s2, support=support, shares_consonant=shares))
    return entries


@dataclass(frozen=True, slots=True)
class MedialReport:
    perms: int
    seed: int
    pair_count: int
    pair_count_null: NullDistribution
    max_support: int
    max_support_null: NullDistribution
    top_20: tuple[MedialPairEntry, ...]
    consonant_fraction: ConsonantFraction
    consonant_fraction_null: NullDistribution

    def as_dict(self) -> dict:
        return {
            "version": _VERSION,
            "perms": self.perms,
            "seed": self.seed,
            "pair_count": self.pair_count,
            "pair_count_null": self.pair_count_null.as_dict(),
            "max_support": self.max_support,
            "max_support_null": self.max_support_null.as_dict(),
            "top_20_pairs": [e.as_dict() for e in self.top_20],
            "consonant_sharing_fraction": self.consonant_fraction.fraction,
            "consonant_sharing_chance_fraction": self.consonant_fraction.chance_fraction,
            "consonant_sharing_scored_count": self.consonant_fraction.scored_count,
            "consonant_sharing_excluded_count": self.consonant_fraction.excluded_count,
            "consonant_sharing_null": self.consonant_fraction_null.as_dict(),
        }


def build_medial_report(words: Iterable[Word], perms: int, seed: int) -> MedialReport:
    """Build the Kober 0.9 medial-channel report for ``words`` (the run's own,
    possibly subsampled or homophone-merged, word-type set)."""
    words = list(words)

    real_pairs = medial_pairs(words)
    pair_count = sum(real_pairs.values())
    real_max_support = max(real_pairs.values()) if real_pairs else 0
    ranked = ranked_medial_pairs(real_pairs, limit=20)
    top_20 = tuple(_entries(ranked))
    real_fraction = consonant_fraction_from_pairs(pair for pair, _support in ranked)

    rng1 = random.Random(_sub_seed(seed, "medial_n1"))
    pair_count_values: list[int] = []
    for _ in range(perms):
        drawn = n1_draw(words, rng1)
        pair_count_values.append(sum(medial_pairs(drawn).values()))
    pair_count_null = _summarise(pair_count_values, pair_count)

    rng3 = random.Random(_sub_seed(seed, "medial_n3"))
    max_support_values: list[int] = []
    fraction_values: list[float] = []
    for _ in range(perms):
        drawn = n3_draw(words, rng3)
        drawn_pairs = medial_pairs(drawn)
        max_support_values.append(max(drawn_pairs.values()) if drawn_pairs else 0)
        drawn_ranked = ranked_medial_pairs(drawn_pairs, limit=20)
        fraction_values.append(
            consonant_fraction_from_pairs(pair for pair, _support in drawn_ranked).fraction
        )
    max_support_null = _summarise(max_support_values, real_max_support)
    consonant_fraction_null = _summarise(fraction_values, real_fraction.fraction)

    return MedialReport(
        perms=perms,
        seed=seed,
        pair_count=pair_count,
        pair_count_null=pair_count_null,
        max_support=real_max_support,
        max_support_null=max_support_null,
        top_20=top_20,
        consonant_fraction=real_fraction,
        consonant_fraction_null=consonant_fraction_null,
    )


def _fmt_nd(nd: NullDistribution) -> str:
    return (
        f"real {nd.real_value:g} (percentile {nd.real_percentile:.1f}), "
        f"null mean {nd.mean:.3f} sd {nd.sd:.3f}, p95 {nd.p95:.3f}, p99 {nd.p99:.3f}"
    )


def render_medial_markdown(report: MedialReport) -> str:
    lines = [
        "## Medial channel (0.9)",
        "",
        f"Pair count: {report.pair_count}. {report.perms} draws per null.",
        "",
        f"N1 (pair count null): {_fmt_nd(report.pair_count_null)}",
        "",
        f"Max support: {report.max_support}.",
        "",
        f"N3 (max support null): {_fmt_nd(report.max_support_null)}",
        "",
        "### Top 20 medial pairs",
        "",
        "| rank | signs | support | shares consonant |",
        "|---:|---|---:|---|",
    ]
    for i, e in enumerate(report.top_20, 1):
        shares = "-" if e.shares_consonant is None else ("yes" if e.shares_consonant else "no")
        lines.append(f"| {i} | {e.s1} / {e.s2} | {e.support} | {shares} |")
    cf = report.consonant_fraction
    lines += [
        "",
        f"Consonant-sharing fraction of the top twenty: {cf.fraction:.3f} "
        f"({cf.shared_count} of {cf.scored_count} scored, {cf.excluded_count} excluded). "
        f"Chance fraction: {cf.chance_fraction:.3f}.",
        "",
        f"N3 (consonant-sharing fraction null): {_fmt_nd(report.consonant_fraction_null)}",
        "",
    ]
    return "\n".join(lines)
