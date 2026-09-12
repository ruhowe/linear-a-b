"""N1 and N2 nulls for the Kober method (A-036), seeded and reproducible.

The protocol 1.0 null (relabelling sign identities within frequency bands) is
rejected here: a consistent relabelling preserves every shared prefix exactly, so
the paradigm count would be unchanged by construction. Both nulls below destroy
structure while holding marginals fixed, at two different grades.

**N1, position-matched shuffle.** Within each word-length class, the signs at each
position are shuffled independently across the words of that class. Preserves the
length distribution and every positional sign frequency; destroys shared prefixes
and stem-ending pairing alike. Reassembling shuffled columns can produce the same
word twice, so the result is a *set* of word tuples — duplicates collapse, and the
resulting type count is itself reported as a diagnostic of how much the shuffle
degenerates the vocabulary. This is the null for the paradigm count.

**N2, ending shuffle.** Within each word-length class, the first ``n - k`` signs
are held fixed per word and the final ``k``-sign tails are shuffled across the
words of that class, ``k = min(2, n - stem_min)``. Words too short to have any
valid split at all (``n - stem_min < 1``) pass through unshuffled — see A-043. This
preserves which stems exist and how many words head them, so the paradigm count is
nearly unchanged by construction; it destroys which ending goes with which stem.
This is the null for alternation support. The prefix channel runs the mirror: the
final ``n - k`` signs (the base) are held fixed and the initial ``k``-sign heads
(the prefixes) are shuffled.

Both nulls are drawn ``draws`` times (200 by default) under one integer seed. The
null streams used by a report (N1, N2 ending, N2 prefix, stage 2's grid
stream, stage 2 version 0.2's grid_anchored stream, and stage 2 version 0.3's
grid_alternations stream, all of which reuse ``n1_draw`` for their own
independent 200 draws) are independent `random.Random` instances derived
deterministically from that one seed (A-045, A-056, A-060), so a run is fully
reproducible without one stream's draw count affecting another's.

**Grammar-match null (CHANGELOG "Null rate of the grammar match, and precision
criteria").** The N2 ending stream's per-draw ``support`` mapping (already built
for ``max_support``/``tenth_support``) is reused, not redrawn, to also grade
each draw's own top-n alternations (n in ``GRAMMAR_MATCH_NS``, ties at the n-th
place included per A-053) against ``reference.is_grammar``
(``grammar_matched_count``, ``run_n2``'s ``track_grammar_match``). This adds no
draws and consumes no extra randomness, so it leaves every other statistic
bit-identical to a run without it.

**Strict grammar-match null (A-072).** The ties-included top-n can hold far more
than n alternations when support is degenerate (a 988-word-type subsample can tie
dozens of alternations at the tenth-ranked support value), so its matched count is
partly a property of the tie set's size rather than of grammar (A-069). The strict
variant (``grammar_matched_count_strict``) cuts at exactly n under a deterministic
tie-break -- support descending, then the alternation's ending pair in sorted
lexicographic order, i.e. ``paradigms.ranked_alternations`` -- applied identically
to the real corpus and to every N2 draw's own support mapping, still reusing the
same per-draw ``support`` with no extra randomness. ``run_n2`` also records, at
each n, the *size* of the ties-included top-n set (real value and null mean only,
not a full percentile spread) alongside the strict matched-count distribution, so
a reader can see how much the ties-included set was inflated by ties without
recomputing it.

**N3, interior-position shuffle (Kober 0.9, CHANGELOG "0.9", A-142).** The null for
``medial.py``'s ranked pairs: within each word-length class, exactly as ``n1_draw``,
except only the *interior* position columns (index 1 to n-2; positions 2 to n-1 in
the design page's 1-based wording) are shuffled. The first and last position of
each word -- the "flanking signs" the medial-pair definition holds fixed -- are
never touched, so ``n3_draw`` is ``n1_draw`` restricted to a subset of columns, not
a different mechanism. A word of length < 3 has no interior column and passes
through unchanged, the same way a word too short for N2 passes through unchanged
(A-043). Drawn separately from ``medial.pair_count``'s own null, which reuses
plain ``n1_draw`` (full-word shuffle, as stage 1's paradigm count uses it) under
its own stream key.
"""

from __future__ import annotations

import random
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from .context import ContextClass
from .lists import DocListing, homogeneous_forms_from_listings
from .paradigms import (
    ChannelResult,
    Word,
    build_channel,
    build_channel_context_restricted,
    list_support_counts,
    ranked_alternations,
    role_sharing_counts,
    top_n_alternations_with_ties,
)
from .reference import is_grammar

__all__ = [
    "n1_draw",
    "n2_draw",
    "n3_draw",
    "NullDistribution",
    "TiesSizeStat",
    "N1Result",
    "N2Result",
    "NullResults",
    "run_n1",
    "run_n2",
    "run_nulls",
    "GRAMMAR_MATCH_NS",
    "grammar_matched_count",
    "grammar_matched_count_strict",
    "rule_firing_counts_strict",
    "top_three_all_matched",
    "n1_draw_stratified",
    "n2_draw_stratified",
    "N1ContextResult",
    "N2ContextResult",
    "run_n1_context",
    "run_n2_context",
]

# n values at which the grammar-match null is measured (CHANGELOG "Null rate of
# the grammar match, and precision criteria"; TODO item 8, prerequisite 1).
GRAMMAR_MATCH_NS: tuple[int, ...] = (3, 5, 10)


def grammar_matched_count(support: Mapping[tuple[Word, Word], int], n: int, version: int = 1) -> int:
    """Count of the top-``n`` alternations by support (ties at the ``n``-th place
    included, A-053, via ``paradigms.top_n_alternations_with_ties``) for which
    ``reference.is_grammar`` returns a rule.

    Used both on the real ending channel's alternation support and, per draw, on
    each N2 ending-null draw's own support, so a draw's own top-``n`` is graded
    against the same reference list the real corpus is.

    ``version`` (Kober 0.6, CHANGELOG "0.6") is forwarded to ``is_grammar``;
    default 1 reproduces the pre-0.6 grading exactly.
    """
    top = top_n_alternations_with_ties(support, n)
    return sum(1 for e1, e2 in top if is_grammar(e1, e2, version=version) is not None)


def grammar_matched_count_strict(
    support: Mapping[tuple[Word, Word], int],
    n: int,
    role_sharing: Mapping[tuple[Word, Word], int] | None = None,
    list_support: Mapping[tuple[Word, Word], int] | None = None,
    version: int = 1,
) -> int:
    """Count of the top-``n`` alternations by support under a *strict* cut (A-072):
    exactly ``n`` entries (or fewer if there are not ``n`` alternations at all),
    broken by the deterministic tie-break support descending then the ending
    pair in sorted lexicographic order -- ``paradigms.ranked_alternations``, the
    same ranking ``report.py``'s ``top_10_matched_to_rule`` already uses -- for
    which ``reference.is_grammar`` returns a rule.

    Applied identically to the real ending channel's alternation support and to
    each N2 ending-null draw's own support, so the real and null counts are
    computed the same way (the point of the strict variant: A-069's ties-included
    top-n can hold far more than ``n`` alternations at low support, which is a
    property of the tie set's size, not of grammar).

    ``role_sharing`` (Kober 0.5, CHANGELOG "0.5") and ``list_support`` (Kober
    0.7, CHANGELOG "0.7"), when given, are forwarded to ``ranked_alternations``
    as its ordering keys, so the "top ``n``" being graded is the role- and/or
    list-tiebreak-ordered one rather than the plain support ranking. Default
    ``None`` for both reproduces the 0.3/A-072 ordering exactly; ``role_sharing``
    alone reproduces 0.5's.

    ``version`` (Kober 0.6, CHANGELOG "0.6") is forwarded to ``is_grammar``;
    default 1 reproduces the pre-0.6 grading exactly.
    """
    top = ranked_alternations(support, n, role_sharing=role_sharing, list_support=list_support)
    return sum(1 for (e1, e2), _support in top if is_grammar(e1, e2, version=version) is not None)


def rule_firing_counts_strict(
    support: Mapping[tuple[Word, Word], int], n: int, version: int = 1
) -> dict[str, int]:
    """Counter of rule names among the strict top-``n`` alternations by
    support (the same tie-break ``grammar_matched_count_strict`` uses,
    ``paradigms.ranked_alternations``): each matched pair contributes one to
    its rule name's count, an unmatched pair contributes nothing. Used to
    answer "which rules fire under the null" (CHANGELOG "0.8") by summing
    this over every N2 draw's own top-``n``, reusing the same per-draw
    ``support`` mapping already built for every other grammar-match variant.
    """
    top = ranked_alternations(support, n)
    counts: dict[str, int] = {}
    for (e1, e2), _support in top:
        rule = is_grammar(e1, e2, version=version)
        if rule is not None:
            counts[rule] = counts.get(rule, 0) + 1
    return counts


# n at which the rule-firing-counts null is measured (CHANGELOG "0.8": "each
# N2 draw's strict top ten").
_RULE_FIRING_N = 10


def top_three_all_matched(
    support: Mapping[tuple[Word, Word], int],
    role_sharing: Mapping[tuple[Word, Word], int] | None = None,
    list_support: Mapping[tuple[Word, Word], int] | None = None,
    version: int = 1,
) -> bool:
    """Kober 0.4's criterion indicator: the strict top three alternations by
    support (``paradigms.ranked_alternations``'s tie-break, A-072) all match a
    reference rule. False when there are fewer than three alternations at all.
    Used both on the real (context-restricted) ending channel and, per draw,
    on the stratified N2 null, whose per-draw rate is the criterion's chance
    rate (CHANGELOG "0.4").

    ``role_sharing`` (Kober 0.5) and ``list_support`` (Kober 0.7), when given,
    are forwarded to ``ranked_alternations`` so the strict top three read is
    the role- and/or list-tiebreak-ordered one; default ``None`` for both is
    the 0.3/0.4 ordering. ``version`` (Kober 0.6) is forwarded to
    ``is_grammar``; default 1 reproduces the pre-0.6/0.7 grading exactly.
    """
    top = ranked_alternations(support, 3, role_sharing=role_sharing, list_support=list_support)
    if len(top) < 3:
        return False
    return all(is_grammar(e1, e2, version=version) is not None for (e1, e2), _support in top)


# Deterministic per-stream seed offsets (A-045). Arbitrary but fixed, so the same
# top-level seed always yields the same independent draw sequences. "grid" is
# stage 2's own N1-style stream (A-048): it reuses n1_draw but must not consume
# from the same sequence as the "n1" stream above, or a report built with
# --grid would draw different N1 results than one built without it. "grid_anchored"
# is stage 2 version 0.2's own such stream (A-056), independent of "grid" for the
# same reason: a --grid-anchored run must not change the --grid stream's draws.
# "grid_alternations" is stage 2 version 0.3's own such stream (A-060), independent
# of both, so a --grid-alternations run leaves --grid and --grid-anchored bit-identical.
_STREAM_OFFSETS = {
    "n1": 0,
    "n2_ending": 1_000_003,
    "n2_prefix": 2_000_003,
    "grid": 3_000_003,
    "grid_anchored": 4_000_004,
    "grid_alternations": 5_000_005,
    # Kober 0.4 (A-084): three more independent streams for the stratified
    # (length, class) nulls, following the same "own stream per null usage"
    # pattern as every stream above, so a --context run's N1/N2 draws never
    # share randomness with the unstratified ones on the same seed.
    "n1_context": 6_000_006,
    "n2_ending_context": 7_000_007,
    "n2_prefix_context": 8_000_008,
    # Kober 0.9 (CHANGELOG "0.9", A-142): the medial channel's own two null
    # streams, independent of every stream above so a --medial run leaves
    # every other block bit-identical to the same seed's run without it.
    # "medial_n1" is plain n1_draw (full-word shuffle) reused for the pair
    # count, as stage 1's paradigm count already reuses n1_draw under its own
    # stream ("n1" above is a different stream, not shared); "medial_n3" is
    # the interior-position-only shuffle for the ranked pairs.
    "medial_n1": 9_000_009,
    "medial_n3": 10_000_010,
}


def _sub_seed(seed: int, stream: str) -> int:
    return seed + _STREAM_OFFSETS[stream]


def _group_by_length(words: Iterable[Word]) -> dict[int, list[Word]]:
    """Words grouped by sign count, each group sorted for a deterministic draw order.

    Sorting is necessary for reproducibility: ``words`` is normally a ``frozenset``,
    and Python's set iteration order for strings depends on the process hash seed,
    not just on the RNG seed. Sorting the tuples (plain lexicographic string
    comparison, unaffected by hash randomisation) fixes the order the shuffle is
    applied to, so a given seed reproduces the same draw across processes.

    The groups themselves are returned in ascending length order (Kober 0.9.1).
    Until 0.9.1 the dict kept the order in which lengths were first met while
    iterating the set, which also depends on the hash seed; the draws consume
    the RNG group by group, so two processes with the same RNG seed could
    produce different draws (found by spike S-013).
    """
    by_length: dict[int, list[Word]] = defaultdict(list)
    for w in words:
        by_length[len(w)].append(w)
    return {n: sorted(by_length[n]) for n in sorted(by_length)}


def _group_by_length_and_class(
    words: Iterable[Word], word_class: Mapping[Word, ContextClass]
) -> dict[tuple[int, ContextClass], list[Word]]:
    """Words grouped by (length, context class), each group sorted for a
    deterministic draw order (A-084; same reproducibility reasoning as
    ``_group_by_length``, A-057)."""
    by_stratum: dict[tuple[int, ContextClass], list[Word]] = defaultdict(list)
    for w in words:
        by_stratum[(len(w), word_class[w])].append(w)
    return {key: sorted(by_stratum[key]) for key in sorted(by_stratum)}


def n1_draw_stratified(
    words: Iterable[Word], word_class: Mapping[Word, ContextClass], rng: random.Random
) -> tuple[frozenset[Word], dict[Word, ContextClass]]:
    """N1, stratified by (length, class) (Kober 0.4). Within each stratum,
    signs at each position are shuffled independently across the stratum's
    words, exactly as ``n1_draw`` does within each length class alone. A
    stratum of fewer than two words passes through unshuffled (A-077).

    Every word a stratum's shuffle can produce is a recombination of that
    stratum's own members, so it shares the stratum's class by construction;
    the returned dict records that class for every drawn word, alongside the
    drawn word set, so a caller can rebuild a context-restricted channel on
    the draw without a second lookup.
    """
    new_words: set[Word] = set()
    drawn_class: dict[Word, ContextClass] = {}
    for (_n, cls), group in _group_by_length_and_class(words, word_class).items():
        if not group:
            continue
        if len(group) < 2:
            for w in group:
                new_words.add(w)
                drawn_class[w] = cls
            continue
        columns = [list(col) for col in zip(*group)]
        for col in columns:
            rng.shuffle(col)
        for w in zip(*columns):
            new_words.add(w)
            drawn_class[w] = cls
    return frozenset(new_words), drawn_class


def n2_draw_stratified(
    words: Iterable[Word],
    word_class: Mapping[Word, ContextClass],
    stem_min: int,
    rng: random.Random,
    mirror: bool = False,
) -> tuple[frozenset[Word], dict[Word, ContextClass]]:
    """N2, stratified by (length, class) (Kober 0.4): within each stratum, the
    final (or, mirrored, initial) k-sign run is shuffled across the stratum's
    own words, exactly as ``n2_draw`` does within each length class alone. A
    stratum of fewer than two words, or one with nothing shuffleable
    (``n - stem_min < 1``, A-043), passes through unshuffled (A-077); either
    way the stratum's multiset of the fixed part is preserved, since only the
    assignment of the moving part to it is permuted.
    """
    new_words: set[Word] = set()
    drawn_class: dict[Word, ContextClass] = {}
    for (n, cls), group in _group_by_length_and_class(words, word_class).items():
        if len(group) < 2 or n - stem_min < 1:
            for w in group:
                new_words.add(w)
                drawn_class[w] = cls
            continue
        k = min(2, n - stem_min)
        if mirror:
            fixed = [w[k:] for w in group]  # base, held fixed
            moving = [w[:k] for w in group]  # prefix, shuffled
            rng.shuffle(moving)
            combined = [pre + base for pre, base in zip(moving, fixed)]
        else:
            fixed = [w[: n - k] for w in group]  # stem, held fixed
            moving = [w[n - k :] for w in group]  # ending, shuffled
            rng.shuffle(moving)
            combined = [stem + ending for stem, ending in zip(fixed, moving)]
        for w in combined:
            new_words.add(w)
            drawn_class[w] = cls
    return frozenset(new_words), drawn_class


def n1_draw(words: Iterable[Word], rng: random.Random) -> frozenset[Word]:
    """One N1 draw: shuffle each position's signs independently within each length class."""
    new_words: set[Word] = set()
    for _n, group in _group_by_length(words).items():
        if not group:
            continue
        columns = [list(col) for col in zip(*group)]
        for col in columns:
            rng.shuffle(col)
        new_words.update(zip(*columns))
    return frozenset(new_words)


def n3_draw(words: Iterable[Word], rng: random.Random) -> frozenset[Word]:
    """One N3 draw (Kober 0.9, CHANGELOG "0.9"): ``n1_draw`` restricted to
    interior position columns (index 1 to n-2). The first and last position
    of each word are the "flanking signs" the medial-pair definition holds
    fixed, so they are left attached to their own word, unshuffled; every
    interior column is shuffled independently across the words of its length
    class, exactly as every column is in ``n1_draw``. A word of length < 3
    has no interior column (``range(1, n - 1)`` is empty for n <= 2) and
    passes through with its own columns unchanged.
    """
    new_words: set[Word] = set()
    for n, group in _group_by_length(words).items():
        if not group:
            continue
        columns = [list(col) for col in zip(*group)]
        for i in range(1, n - 1):
            rng.shuffle(columns[i])
        new_words.update(zip(*columns))
    return frozenset(new_words)


def _n2_draw_and_map(
    words: Iterable[Word], stem_min: int, rng: random.Random, mirror: bool = False
) -> tuple[frozenset[Word], dict[Word, Word]]:
    """One N2 draw, as ``n2_draw``, plus the ``{original word: drawn word}``
    mapping the draw implies (Kober 0.7, CHANGELOG "0.7", A-116): each
    length-class group's ``fixed``/``moving`` construction is order-preserving
    (``group[i]``'s fixed part pairs with the shuffled ``moving[i]`` to make
    ``combined[i]``), so zipping ``group`` with ``combined`` gives, for every
    real word, which drawn word "gets its ending" under this draw. A word in a
    length class with nothing to shuffle (``n - stem_min < 1``, A-043) maps to
    itself.

    ``n2_draw`` delegates here and discards the map, so it consumes the same
    RNG calls in the same order as before this function existed -- this
    refactor changes no existing draw's output (regression pins unaffected).
    """
    new_words: set[Word] = set()
    word_map: dict[Word, Word] = {}
    for n, group in _group_by_length(words).items():
        if n - stem_min < 1:
            for w in group:
                new_words.add(w)
                word_map[w] = w
            continue
        k = min(2, n - stem_min)
        if mirror:
            fixed = [w[k:] for w in group]  # base, held fixed
            moving = [w[:k] for w in group]  # prefix, shuffled
            rng.shuffle(moving)
            combined = [pre + base for pre, base in zip(moving, fixed)]
        else:
            fixed = [w[: n - k] for w in group]  # stem, held fixed
            moving = [w[n - k :] for w in group]  # ending, shuffled
            rng.shuffle(moving)
            combined = [stem + ending for stem, ending in zip(fixed, moving)]
        for orig, drawn in zip(group, combined):
            new_words.add(drawn)
            word_map[orig] = drawn
    return frozenset(new_words), word_map


def n2_draw(
    words: Iterable[Word], stem_min: int, rng: random.Random, mirror: bool = False
) -> frozenset[Word]:
    """One N2 draw: shuffle the final (or, mirrored, initial) k-sign run across words.

    ``k = min(2, n - stem_min)`` per length class ``n``. A class with ``n - stem_min
    < 1`` has no signs it could shuffle while keeping ``stem_min`` fixed — such
    words never contributed a split in the real data either, so they pass through
    unchanged (A-043).
    """
    drawn, _word_map = _n2_draw_and_map(words, stem_min, rng, mirror=mirror)
    return drawn


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * (pct / 100)
    lo, hi = int(pos), min(int(pos) + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def _percentile_rank(value: float, values: list[float]) -> float:
    """Share of the null draws at or below ``value``, as a percentage."""
    if not values:
        return 0.0
    return 100.0 * sum(1 for v in values if v <= value) / len(values)


@dataclass(frozen=True, slots=True)
class NullDistribution:
    draws: int
    mean: float
    sd: float
    p95: float
    p99: float
    real_value: float
    real_percentile: float

    def as_dict(self) -> dict:
        return {
            "draws": self.draws,
            "mean": self.mean,
            "sd": self.sd,
            "p95": self.p95,
            "p99": self.p99,
            "real_value": self.real_value,
            "real_percentile": self.real_percentile,
        }


@dataclass(frozen=True, slots=True)
class TiesSizeStat:
    """Size of the ties-included top-n alternation set (A-072): the real value and
    the null mean only, not a full ``NullDistribution`` -- this accompanies the
    strict grammar-match null to show how much the ties-included set was inflated
    by ties at each n, not to be read as its own criterion."""

    mean: float
    real_value: int

    def as_dict(self) -> dict:
        return {"mean": self.mean, "real_value": self.real_value}


def _summarise(values: list[float], real_value: float) -> NullDistribution:
    sv = sorted(values)
    return NullDistribution(
        draws=len(values),
        mean=statistics.mean(values) if values else 0.0,
        sd=statistics.pstdev(values) if len(values) > 1 else 0.0,
        p95=_percentile(sv, 95),
        p99=_percentile(sv, 99),
        real_value=real_value,
        real_percentile=_percentile_rank(real_value, values),
    )


def _kth_highest(support: Mapping[tuple[Word, Word], int], k: int) -> int:
    """The k-th largest support value, or 0 if fewer than k alternations exist."""
    values = sorted(support.values(), reverse=True)
    return values[k - 1] if len(values) >= k else 0


@dataclass(frozen=True, slots=True)
class N1Result:
    type_count_mean: float
    type_count_sd: float
    ending_paradigm_count: NullDistribution
    prefix_paradigm_count: NullDistribution


@dataclass(frozen=True, slots=True)
class N2Result:
    max_support: NullDistribution
    tenth_support: NullDistribution
    grammar_match: Mapping[int, NullDistribution] | None = None
    grammar_match_strict: Mapping[int, NullDistribution] | None = None
    ties_included_top_n_size: Mapping[int, TiesSizeStat] | None = None
    # Kober 0.8 (CHANGELOG "0.8"): a Counter of rule names among each draw's
    # own strict top ten (the same tie-break as grammar_matched_count_strict),
    # summed over all draws -- "the rules that fire most under the null"
    # (CHANGELOG "0.8"). Graded at the same ``reference_version`` as
    # ``grammar_match``/``grammar_match_strict``; None unless
    # ``track_grammar_match`` was set (ending channel only).
    rule_firing_counts_null: Mapping[str, int] | None = None
    # Kober 0.8 (CHANGELOG "0.8"): the chance rate of "strict top three all
    # matched" under the plain (0.3) ordering, graded at ``reference_version``
    # -- the null companion to ``top_three_all_matched`` on the real channel,
    # not tracked anywhere before 0.8 since only the role- and list-tiebreak
    # orderings tracked a per-draw "all three matched" flag. None unless
    # ``track_grammar_match`` was set (ending channel only).
    top_three_all_matched_chance_rate: float | None = None
    # Kober 0.5 (CHANGELOG "0.5"): the strict grammar-match null recomputed
    # under the role-tiebreak ordering, and the chance rate of "strict top
    # three all matched" under that same ordering -- both None unless
    # ``run_n2`` was called with ``word_roles`` set (ending channel only).
    grammar_match_role_tiebreak: Mapping[int, NullDistribution] | None = None
    top_three_all_matched_chance_rate_role_tiebreak: float | None = None
    # Kober 0.7 (CHANGELOG "0.7", A-116): the strict grammar-match null
    # recomputed under the four-level (support, role-sharing, list-support,
    # lexicographic) ordering, and the chance rate of "strict top three all
    # matched" under it, at both reference versions (1, 2) -- all None unless
    # ``run_n2`` was called with ``listings`` set (ending channel only).
    grammar_match_list_tiebreak_v1: Mapping[int, NullDistribution] | None = None
    grammar_match_list_tiebreak_v2: Mapping[int, NullDistribution] | None = None
    top_three_all_matched_chance_rate_list_tiebreak_v1: float | None = None
    top_three_all_matched_chance_rate_list_tiebreak_v2: float | None = None


@dataclass(frozen=True, slots=True)
class NullResults:
    n1: N1Result
    n2_ending: N2Result
    n2_prefix: N2Result


def run_n1(
    words: Iterable[Word],
    stem_min: int,
    draws: int,
    seed: int,
    real_ending: ChannelResult,
    real_prefix: ChannelResult,
) -> N1Result:
    rng = random.Random(_sub_seed(seed, "n1"))
    words = list(words)
    type_counts: list[int] = []
    ending_counts: list[int] = []
    prefix_counts: list[int] = []
    for _ in range(draws):
        drawn = n1_draw(words, rng)
        type_counts.append(len(drawn))
        ending_counts.append(build_channel(drawn, stem_min, mirror=False).paradigm_count_total)
        prefix_counts.append(build_channel(drawn, stem_min, mirror=True).paradigm_count_total)
    return N1Result(
        type_count_mean=statistics.mean(type_counts) if type_counts else 0.0,
        type_count_sd=statistics.pstdev(type_counts) if len(type_counts) > 1 else 0.0,
        ending_paradigm_count=_summarise(ending_counts, real_ending.paradigm_count_total),
        prefix_paradigm_count=_summarise(prefix_counts, real_prefix.paradigm_count_total),
    )


def run_n2(
    words: Iterable[Word],
    stem_min: int,
    draws: int,
    seed: int,
    mirror: bool,
    real_channel: ChannelResult,
    track_grammar_match: bool = False,
    word_roles: Mapping[Word, frozenset] | None = None,
    reference_version: int = 1,
    listings: Sequence[DocListing] | None = None,
) -> N2Result:
    """Run the N2 null (ending shuffle, or its prefix mirror).

    ``reference_version`` (Kober 0.6, CHANGELOG "0.6") is forwarded to
    ``grammar_matched_count``/``grammar_matched_count_strict`` wherever
    ``track_grammar_match`` grades a draw's or the real channel's own top-n
    against ``reference.is_grammar``; it does not touch anything else this
    function computes (``max_values``/``tenth_values``, the role-tiebreak
    variants, or the drawn words themselves). Default 1 reproduces the
    pre-0.6 grading exactly.

    ``track_grammar_match`` (the ending channel only, CHANGELOG "Null rate of
    the grammar match, and precision criteria") computes, from the *same*
    per-draw ``support`` mapping already built for ``max_values``/
    ``tenth_values``, each draw's own top-n matched count for n in
    ``GRAMMAR_MATCH_NS``, both ties-included (``grammar_matched_count``) and
    strict (``grammar_matched_count_strict``, A-072), plus the ties-included
    top-n set's own size at each n. It consumes no extra randomness and calls
    ``n2_draw`` no differently, so every other statistic in the report stays
    bit-identical whether or not this is enabled (prerequisite 1's "must reuse
    the existing N2 draws").

    ``word_roles`` (Kober 0.5, CHANGELOG "0.5", ending channel only -- callers
    never pass it for the prefix mirror) computes, from the same per-draw
    ``drawn_channel`` already built, that draw's own role-sharing counts
    (``paradigms.role_sharing_counts``) and, from them, the strict
    grammar-match count at each n and the "strict top three all matched"
    indicator under the role-tiebreak ordering. Roles stay attached to word
    types: the per-draw role-sharing count is computed on that draw's own
    stem pairs, not redrawn or reshuffled, and no extra randomness is
    consumed -- the same draw already used for ``max_values``/
    ``tenth_values``/the grammar-match variants above. Default ``None``
    leaves every other field, and the whole function's behaviour when this
    argument is omitted, exactly as before (A-072's regression pins stay
    green).

    ``listings`` (Kober 0.7, CHANGELOG "0.7", A-116, ending channel only --
    callers never pass it for the prefix mirror, following A-070/A-074/A-085's
    ending-channel scoping) computes, per draw, that draw's own list-support
    counts (``paradigms.list_support_counts``) under a per-draw
    ``kober.lists.homogeneous_forms_from_listings`` recomputed from the same
    draw's ``{original word: drawn word}`` map (``_n2_draw_and_map``, reused
    from the same call already producing ``drawn_channel`` -- no extra
    randomness): "a draw's word gets the draw's ending; its documents and
    their modal final signs are recomputed from the shuffled words"
    (CHANGELOG "0.7"), unlike roles, which stay attached to word types by
    literal-identity lookup (A-098). From this, the strict grammar-match null
    is recomputed under the four-level (support, role-sharing, list-support,
    lexicographic) ordering at each n, under *both* reference versions (1 and
    2), plus the "strict top three all matched" chance rate under it, both
    versions. Default ``None`` leaves every other field unaffected.
    """
    stream = "n2_prefix" if mirror else "n2_ending"
    rng = random.Random(_sub_seed(seed, stream))
    words = list(words)
    max_values: list[int] = []
    tenth_values: list[int] = []
    grammar_values: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if track_grammar_match else {}
    grammar_values_strict: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if track_grammar_match else {}
    ties_size_values: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if track_grammar_match else {}
    rule_firing_null_counts: dict[str, int] = {}
    top_three_plain_flags: list[bool] = []
    role_tiebreak_values: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if word_roles is not None else {}
    top_three_role_flags: list[bool] = []
    list_tiebreak_values_v1: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if listings is not None else {}
    list_tiebreak_values_v2: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS} if listings is not None else {}
    top_three_list_flags_v1: list[bool] = []
    top_three_list_flags_v2: list[bool] = []
    real_role_sharing = role_sharing_counts(real_channel, word_roles, mirror=mirror) if word_roles is not None else None
    real_homogeneous_forms = homogeneous_forms_from_listings(listings) if listings is not None else None
    real_list_support = (
        list_support_counts(real_channel, real_homogeneous_forms, mirror=mirror)
        if real_homogeneous_forms is not None
        else None
    )
    for _ in range(draws):
        drawn, word_map = _n2_draw_and_map(words, stem_min, rng, mirror=mirror)
        drawn_channel = build_channel(drawn, stem_min, mirror=mirror)
        support = drawn_channel.alternation_support
        max_values.append(_kth_highest(support, 1))
        tenth_values.append(_kth_highest(support, 10))
        if track_grammar_match:
            for n in GRAMMAR_MATCH_NS:
                grammar_values[n].append(grammar_matched_count(support, n, version=reference_version))
                grammar_values_strict[n].append(
                    grammar_matched_count_strict(support, n, version=reference_version)
                )
                ties_size_values[n].append(len(top_n_alternations_with_ties(support, n)))
            for rule, count in rule_firing_counts_strict(support, _RULE_FIRING_N, version=reference_version).items():
                rule_firing_null_counts[rule] = rule_firing_null_counts.get(rule, 0) + count
            top_three_plain_flags.append(top_three_all_matched(support, version=reference_version))
        draw_role_sharing = None
        if word_roles is not None:
            draw_role_sharing = role_sharing_counts(drawn_channel, word_roles, mirror=mirror)
            for n in GRAMMAR_MATCH_NS:
                role_tiebreak_values[n].append(
                    grammar_matched_count_strict(support, n, role_sharing=draw_role_sharing)
                )
            top_three_role_flags.append(top_three_all_matched(support, role_sharing=draw_role_sharing))
        if listings is not None:
            draw_homogeneous_forms = homogeneous_forms_from_listings(listings, word_map=word_map)
            draw_list_support = list_support_counts(drawn_channel, draw_homogeneous_forms, mirror=mirror)
            for n in GRAMMAR_MATCH_NS:
                list_tiebreak_values_v1[n].append(
                    grammar_matched_count_strict(
                        support, n, role_sharing=draw_role_sharing, list_support=draw_list_support, version=1
                    )
                )
                list_tiebreak_values_v2[n].append(
                    grammar_matched_count_strict(
                        support, n, role_sharing=draw_role_sharing, list_support=draw_list_support, version=2
                    )
                )
            top_three_list_flags_v1.append(
                top_three_all_matched(support, role_sharing=draw_role_sharing, list_support=draw_list_support, version=1)
            )
            top_three_list_flags_v2.append(
                top_three_all_matched(support, role_sharing=draw_role_sharing, list_support=draw_list_support, version=2)
            )
    grammar_match = None
    grammar_match_strict = None
    ties_included_top_n_size = None
    rule_firing_counts_null_out = None
    top_three_all_matched_chance_rate_out = None
    if track_grammar_match:
        rule_firing_counts_null_out = dict(rule_firing_null_counts)
        top_three_all_matched_chance_rate_out = (
            statistics.mean(top_three_plain_flags) if top_three_plain_flags else 0.0
        )
        grammar_match = {
            n: _summarise(
                grammar_values[n],
                grammar_matched_count(real_channel.alternation_support, n, version=reference_version),
            )
            for n in GRAMMAR_MATCH_NS
        }
        grammar_match_strict = {
            n: _summarise(
                grammar_values_strict[n],
                grammar_matched_count_strict(real_channel.alternation_support, n, version=reference_version),
            )
            for n in GRAMMAR_MATCH_NS
        }
        ties_included_top_n_size = {
            n: TiesSizeStat(
                mean=statistics.mean(ties_size_values[n]) if ties_size_values[n] else 0.0,
                real_value=len(top_n_alternations_with_ties(real_channel.alternation_support, n)),
            )
            for n in GRAMMAR_MATCH_NS
        }
    grammar_match_role_tiebreak = None
    top_three_all_matched_chance_rate_role_tiebreak = None
    if word_roles is not None:
        grammar_match_role_tiebreak = {
            n: _summarise(
                role_tiebreak_values[n],
                grammar_matched_count_strict(real_channel.alternation_support, n, role_sharing=real_role_sharing),
            )
            for n in GRAMMAR_MATCH_NS
        }
        top_three_all_matched_chance_rate_role_tiebreak = (
            statistics.mean(top_three_role_flags) if top_three_role_flags else 0.0
        )
    grammar_match_list_tiebreak_v1 = None
    grammar_match_list_tiebreak_v2 = None
    top_three_all_matched_chance_rate_list_tiebreak_v1 = None
    top_three_all_matched_chance_rate_list_tiebreak_v2 = None
    if listings is not None:
        grammar_match_list_tiebreak_v1 = {
            n: _summarise(
                list_tiebreak_values_v1[n],
                grammar_matched_count_strict(
                    real_channel.alternation_support,
                    n,
                    role_sharing=real_role_sharing,
                    list_support=real_list_support,
                    version=1,
                ),
            )
            for n in GRAMMAR_MATCH_NS
        }
        grammar_match_list_tiebreak_v2 = {
            n: _summarise(
                list_tiebreak_values_v2[n],
                grammar_matched_count_strict(
                    real_channel.alternation_support,
                    n,
                    role_sharing=real_role_sharing,
                    list_support=real_list_support,
                    version=2,
                ),
            )
            for n in GRAMMAR_MATCH_NS
        }
        top_three_all_matched_chance_rate_list_tiebreak_v1 = (
            statistics.mean(top_three_list_flags_v1) if top_three_list_flags_v1 else 0.0
        )
        top_three_all_matched_chance_rate_list_tiebreak_v2 = (
            statistics.mean(top_three_list_flags_v2) if top_three_list_flags_v2 else 0.0
        )
    return N2Result(
        max_support=_summarise(max_values, _kth_highest(real_channel.alternation_support, 1)),
        tenth_support=_summarise(tenth_values, _kth_highest(real_channel.alternation_support, 10)),
        grammar_match=grammar_match,
        grammar_match_strict=grammar_match_strict,
        ties_included_top_n_size=ties_included_top_n_size,
        rule_firing_counts_null=rule_firing_counts_null_out,
        top_three_all_matched_chance_rate=top_three_all_matched_chance_rate_out,
        grammar_match_role_tiebreak=grammar_match_role_tiebreak,
        top_three_all_matched_chance_rate_role_tiebreak=top_three_all_matched_chance_rate_role_tiebreak,
        grammar_match_list_tiebreak_v1=grammar_match_list_tiebreak_v1,
        grammar_match_list_tiebreak_v2=grammar_match_list_tiebreak_v2,
        top_three_all_matched_chance_rate_list_tiebreak_v1=top_three_all_matched_chance_rate_list_tiebreak_v1,
        top_three_all_matched_chance_rate_list_tiebreak_v2=top_three_all_matched_chance_rate_list_tiebreak_v2,
    )


def run_nulls(
    words: Iterable[Word],
    stem_min: int,
    draws: int,
    seed: int,
    real_ending: ChannelResult,
    real_prefix: ChannelResult,
    word_roles: Mapping[Word, frozenset] | None = None,
    reference_version: int = 1,
    listings: Sequence[DocListing] | None = None,
) -> NullResults:
    """``word_roles`` (Kober 0.5), when given, is forwarded only to the
    ending channel's N2 run (A-070/A-074/A-085's ending-channel scoping,
    which the grammar-match null and the context criterion already follow);
    the prefix channel never receives it. Default ``None`` leaves both N2
    runs exactly as before.

    ``reference_version`` (Kober 0.6, CHANGELOG "0.6") is forwarded only to
    the ending channel's N2 run, the only one that tracks the grammar-match
    null; the prefix channel's run never grades against ``reference.is_grammar``
    and so never receives it. Default 1 reproduces the pre-0.6 grading exactly.

    ``listings`` (Kober 0.7, CHANGELOG "0.7") is forwarded only to the ending
    channel's N2 run, matching ``word_roles``'s scoping; the prefix channel
    never receives it. Default ``None`` leaves both N2 runs exactly as before.
    """
    words = list(words)
    return NullResults(
        n1=run_n1(words, stem_min, draws, seed, real_ending, real_prefix),
        n2_ending=run_n2(
            words,
            stem_min,
            draws,
            seed,
            mirror=False,
            real_channel=real_ending,
            track_grammar_match=True,
            word_roles=word_roles,
            reference_version=reference_version,
            listings=listings,
        ),
        n2_prefix=run_n2(words, stem_min, draws, seed, mirror=True, real_channel=real_prefix),
    )


# --------------------------------------------------------------------------- #
# Kober 0.4: context-restricted statistics under the stratified nulls
# (A-076, A-077, A-085 -- ending channel only, following A-070/A-074's
# scoping of the grammar-match null to the ending channel; the reference
# rules are written from Mycenaean suffixes, and 0.4's criterion is an
# ending-channel criterion, CHANGELOG "0.4").
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class N1ContextResult:
    """Stratified-N1 paradigm-count null for the context-restricted ending
    channel (Kober 0.4)."""

    ending_paradigm_count: NullDistribution


@dataclass(frozen=True, slots=True)
class N2ContextResult:
    """Stratified-N2 alternation-support and grammar-match null for the
    context-restricted ending channel (Kober 0.4). ``top_three_all_matched_chance_rate``
    is the fraction of draws whose own strict top three (by context-restricted
    support) all match a reference rule -- the criterion's chance rate under
    this null (CHANGELOG "0.4")."""

    max_support: NullDistribution
    tenth_support: NullDistribution
    grammar_match_strict: Mapping[int, NullDistribution]
    top_three_all_matched_chance_rate: float


def run_n1_context(
    words: Iterable[Word],
    word_class: Mapping[Word, ContextClass],
    stem_min: int,
    draws: int,
    seed: int,
    real_ending: ChannelResult,
) -> N1ContextResult:
    """Stratified-N1 null for the context-restricted ending channel's
    paradigm count. ``real_ending`` is the already-built context-restricted
    ending channel (``paradigms.ending_channel_context_restricted``) for the
    real corpus, so this does not rebuild it.
    """
    rng = random.Random(_sub_seed(seed, "n1_context"))
    words = list(words)
    counts: list[int] = []
    for _ in range(draws):
        drawn, drawn_class = n1_draw_stratified(words, word_class, rng)
        counts.append(
            build_channel_context_restricted(drawn, drawn_class, stem_min, mirror=False).paradigm_count_total
        )
    return N1ContextResult(
        ending_paradigm_count=_summarise(counts, real_ending.paradigm_count_total)
    )


def run_n2_context(
    words: Iterable[Word],
    word_class: Mapping[Word, ContextClass],
    stem_min: int,
    draws: int,
    seed: int,
    real_ending: ChannelResult,
) -> N2ContextResult:
    """Stratified-N2 null for the context-restricted ending channel: max and
    tenth-highest alternation support, the strict grammar-match null at
    n in ``GRAMMAR_MATCH_NS``, and the chance rate of the 0.4 criterion
    itself ("strict top three all matched"), all from the same per-draw
    context-restricted ``support`` mapping so no extra draws are consumed.
    ``real_ending`` is the already-built context-restricted ending channel
    for the real corpus.
    """
    rng = random.Random(_sub_seed(seed, "n2_ending_context"))
    words = list(words)
    max_values: list[int] = []
    tenth_values: list[int] = []
    grammar_values_strict: dict[int, list[int]] = {n: [] for n in GRAMMAR_MATCH_NS}
    top_three_flags: list[bool] = []
    for _ in range(draws):
        drawn, drawn_class = n2_draw_stratified(words, word_class, stem_min, rng, mirror=False)
        support = build_channel_context_restricted(drawn, drawn_class, stem_min, mirror=False).alternation_support
        max_values.append(_kth_highest(support, 1))
        tenth_values.append(_kth_highest(support, 10))
        for n in GRAMMAR_MATCH_NS:
            grammar_values_strict[n].append(grammar_matched_count_strict(support, n))
        top_three_flags.append(top_three_all_matched(support))

    real_support = real_ending.alternation_support
    grammar_match_strict = {
        n: _summarise(grammar_values_strict[n], grammar_matched_count_strict(real_support, n))
        for n in GRAMMAR_MATCH_NS
    }
    chance_rate = statistics.mean(top_three_flags) if top_three_flags else 0.0
    return N2ContextResult(
        max_support=_summarise(max_values, _kth_highest(real_support, 1)),
        tenth_support=_summarise(tenth_values, _kth_highest(real_support, 10)),
        grammar_match_strict=grammar_match_strict,
        top_three_all_matched_chance_rate=chance_rate,
    )
