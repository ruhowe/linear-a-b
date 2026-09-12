"""Stage 2, the grid: bridging pairs, the consonant-sharing statistic, and sign
classes by union-find (CHANGELOG "0.1 stage 2, the grid"; A-048 onward).

**Bridging pairs.** For every stem in the ending channel (``paradigms.py``,
``stem_min`` 2) with two or more distinct endings, every unordered pair of those
endings whose first signs differ yields the unordered pair of first signs (a
**bridging pair**): in X-so / X-si-jo the pair is (so, si). A pair's *support*
is the number of distinct stems that yield it, at most one unit of support per
stem regardless of how many ending-pairs at that stem produce the same first
signs. Endings with the same first sign (X-si-jo / X-si-ja) contribute no
bridging pair between themselves.

**Consonant-sharing statistic.** For k in (1, 2, 3), among bridging pairs with
support >= k, the fraction whose two signs share a consonant under the known
Linear B values (``values.py``, consulted only here, after the pairs and their
support are already fixed). A pair with either sign excluded (``values.py``'s
``consonant_of`` returns ``None``) is dropped from both the numerator and the
denominator of the fraction and counted separately as excluded. Also reported,
for information only: the fraction expected by chance if consonants were
assigned independently with the frequency of each consonant among the scored
signs at that k (the sum of squared proportions, i.e. the probability that two
signs drawn independently from that frequency distribution would match).

**Null.** N1, the position-matched shuffle (``nulls.py``), 200 draws under a
stream independent of every other stream on the same seed (A-045, A-048): the
bridging pairs and the fraction at each k are recomputed on each drawn word
set, using the same known values throughout, since only the *pairing*, not the
sign identities, is scrambled by N1.

**Grid.** Union-find over the real bridging pairs with support >= 2 gives sign
classes. A class is reported as pure when every sign in it with a known
consonant shares that one consonant; classes are printed as sign labels, which
CHANGELOG and ``kober-method.md`` both note are sign identities, not corpus
words, and so may appear in the results file.

**Anchored bridging pairs, stage 2 version 0.2** (CHANGELOG "0.1 stage 2,
version 0.2, anchored bridging pairs"; A-053 onward). Change from the stage
above: bridging pairs are taken only from stems that support one of the top
ten ending alternations by support (``paradigms.alternation_support`` on the
ending channel) -- in the real corpus, and, on each N1 draw, in that draw's
own top ten. A stem "supports" an alternation when both of the alternation's
endings are in the stem's own ending set (this is exactly how
``alternation_support`` itself is counted). Ties at the tenth-ranked support
value are all included (A-053), so "top ten" can select more than ten
alternations. Everything else is unchanged: the same bridging-pair definition,
the same consonant function consulted last, the same N1 null (a separate
independent stream, A-056), 200 draws, both seeds. The fraction is computed
over every anchored bridging pair, with no further support threshold (A-054);
union-find over the anchored pairs uses the same support >= 2 rule as the
stage above (A-055).

**Alternations' own bridging pairs, stage 2 version 0.3** (CHANGELOG "0.3";
A-059 onward). Change from version 0.2: a bridging pair is no longer drawn
from a stem's endings at all. It comes directly from a top-ten ending
alternation itself: the pair of first signs of that alternation's own two
endings, kept only when the two first signs differ. One pair per qualifying
alternation, weighted by nothing -- unlike ``bridging_pairs``, there is no
stem support to count, and two different alternations that happen to yield
the same first-sign pair each still contribute their own entry rather than
collapsing into one (``alternation_bridging_pairs``,
``consonant_fraction_from_pairs``). The top ten (ties included, A-053, reusing
``top_n_alternations_with_ties``) is taken from the real corpus, and, on each
N1 draw, from that draw's own top ten, under a fifth independent N1-style
stream, ``grid_alternations`` (A-060). Union-find over the real pairs uses
every pair with no minimum (A-061): each pair already comes from exactly one
top-ten alternation, so, unlike ``build_grid``'s support >= 2 rule over
stems, there is no stem-derived multiplicity here to threshold on -- a
pair's only "support" is that its alternation made the top ten at all.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping

from .nulls import NullDistribution, _sub_seed, _summarise, n1_draw
from .paradigms import ChannelResult, Word, ending_channel, top_n_alternations_with_ties
from .values import consonant_of

__all__ = [
    "bridging_pairs",
    "ConsonantFraction",
    "consonant_fraction",
    "SignClass",
    "build_grid",
    "GridReport",
    "build_grid_report",
    "render_grid_markdown",
    "top_n_alternations_with_ties",
    "anchored_stems",
    "AnchoredGridReport",
    "build_anchored_grid_report",
    "render_anchored_grid_markdown",
    "alternation_bridging_pairs",
    "consonant_fraction_from_pairs",
    "AlternationGridReport",
    "build_alternation_grid_report",
    "render_alternation_grid_markdown",
]


def bridging_pairs(
    channel: ChannelResult, stems: Iterable[Word] | None = None
) -> dict[tuple[str, str], int]:
    """Bridging pairs and their support, from an ending channel's paradigm table.

    ``channel.anchors`` already contains only stems with two or more endings
    (``paradigms.build_channel``'s invariant), so every anchor here contributes
    by default. ``stems``, when given, restricts the stems considered to that
    set (stage 2 version 0.2's anchoring); a stem not present in
    ``channel.anchors`` is silently skipped.
    """
    support: dict[tuple[str, str], int] = defaultdict(int)
    items = (
        channel.anchors.items()
        if stems is None
        else ((s, channel.anchors[s]) for s in stems if s in channel.anchors)
    )
    for _stem, endings in items:
        pairs_this_stem: set[tuple[str, str]] = set()
        for e1, e2 in combinations(sorted(endings), 2):
            if e1[0] == e2[0]:
                continue
            pairs_this_stem.add(tuple(sorted((e1[0], e2[0]))))
        for pair in pairs_this_stem:
            support[pair] += 1
    return dict(support)


@dataclass(frozen=True, slots=True)
class ConsonantFraction:
    """The shared-consonant statistic among bridging pairs with support >= k."""

    k: int
    pair_count: int
    excluded_count: int
    scored_count: int
    shared_count: int
    fraction: float
    chance_fraction: float

    def as_dict(self) -> dict:
        return {
            "k": self.k,
            "pair_count": self.pair_count,
            "excluded_count": self.excluded_count,
            "scored_count": self.scored_count,
            "shared_count": self.shared_count,
            "fraction": self.fraction,
            "chance_fraction": self.chance_fraction,
        }


def consonant_fraction(pairs: Mapping[tuple[str, str], int], k: int) -> ConsonantFraction:
    """The k-thresholded shared-consonant fraction, and the chance figure, for one set of pairs."""
    at_k = [pair for pair, support in pairs.items() if support >= k]
    excluded = 0
    shared = 0
    consonants: list[str] = []
    for s1, s2 in at_k:
        c1, c2 = consonant_of(s1), consonant_of(s2)
        if c1 is None or c2 is None:
            excluded += 1
            continue
        consonants.append(c1)
        consonants.append(c2)
        if c1 == c2:
            shared += 1
    scored = len(at_k) - excluded
    fraction = shared / scored if scored else 0.0
    if consonants:
        total = len(consonants)
        chance = sum((n / total) ** 2 for n in Counter(consonants).values())
    else:
        chance = 0.0
    return ConsonantFraction(
        k=k,
        pair_count=len(at_k),
        excluded_count=excluded,
        scored_count=scored,
        shared_count=shared,
        fraction=fraction,
        chance_fraction=chance,
    )


class _UnionFind:
    """Minimal union-find over sign labels, path-compressed."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[ra] = rb


@dataclass(frozen=True, slots=True)
class SignClass:
    """One union-find class: the signs in it, and its purity under the known values."""

    signs: tuple[str, ...]
    size: int
    pure: bool
    consonants: tuple[str, ...]
    excluded_signs: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "signs": list(self.signs),
            "size": self.size,
            "pure": self.pure,
            "consonants": list(self.consonants),
            "excluded_signs": list(self.excluded_signs),
        }


def build_grid(pairs: Mapping[tuple[str, str], int], min_support: int = 2) -> list[SignClass]:
    """Union-find sign classes over bridging pairs with support >= ``min_support``.

    The union-find step uses sign identity only; the known values are consulted
    only afterwards, per sign, to report each class's purity.
    """
    uf = _UnionFind()
    signs_seen: set[str] = set()
    for (s1, s2), support in pairs.items():
        if support < min_support:
            continue
        uf.union(s1, s2)
        signs_seen.add(s1)
        signs_seen.add(s2)

    groups: dict[str, set[str]] = defaultdict(set)
    for s in signs_seen:
        groups[uf.find(s)].add(s)

    classes: list[SignClass] = []
    for members in groups.values():
        known_consonants: set[str] = set()
        excluded: list[str] = []
        for s in members:
            c = consonant_of(s)
            if c is None:
                excluded.append(s)
            else:
                known_consonants.add(c)
        classes.append(
            SignClass(
                signs=tuple(sorted(members)),
                size=len(members),
                pure=len(known_consonants) <= 1,
                consonants=tuple(sorted(known_consonants)),
                excluded_signs=tuple(sorted(excluded)),
            )
        )
    classes.sort(key=lambda c: (-c.size, c.signs))
    return classes


@dataclass(frozen=True, slots=True)
class KFractionResult:
    """One k's real statistic plus its N1 null distribution."""

    fraction: ConsonantFraction
    null: NullDistribution

    def as_dict(self) -> dict:
        return {**self.fraction.as_dict(), "null": self.null.as_dict()}


@dataclass(frozen=True, slots=True)
class GridReport:
    stem_min: int
    perms: int
    seed: int
    bridging_pair_count: int
    fractions: tuple[KFractionResult, KFractionResult, KFractionResult]
    classes: tuple[SignClass, ...]

    def as_dict(self) -> dict:
        return {
            "version": "0.1",  # A-090: stage 2 version 0.1
            "stem_min": self.stem_min,
            "perms": self.perms,
            "seed": self.seed,
            "bridging_pair_count": self.bridging_pair_count,
            "fractions": [f.as_dict() for f in self.fractions],
            "class_count": len(self.classes),
            "classes": [c.as_dict() for c in self.classes],
        }


def build_grid_report(
    words: Iterable[Word],
    ending: ChannelResult,
    stem_min: int,
    perms: int,
    seed: int,
) -> GridReport:
    """Build the full stage-2 report: real statistic, N1 null, and the grid.

    ``ending`` is the already-built ending channel for ``words`` at
    ``stem_min`` (report.py passes the one it already computed for stage 1, so
    this does not rebuild it). ``words`` is redrawn under N1 for the null.
    """
    words = list(words)
    real_pairs = bridging_pairs(ending)
    real_fracs = {k: consonant_fraction(real_pairs, k) for k in (1, 2, 3)}

    rng = random.Random(_sub_seed(seed, "grid"))
    null_values: dict[int, list[float]] = {1: [], 2: [], 3: []}
    for _ in range(perms):
        drawn = n1_draw(words, rng)
        drawn_pairs = bridging_pairs(ending_channel(drawn, stem_min=stem_min))
        for k in (1, 2, 3):
            null_values[k].append(consonant_fraction(drawn_pairs, k).fraction)

    fractions = tuple(
        KFractionResult(
            fraction=real_fracs[k],
            null=_summarise(null_values[k], real_fracs[k].fraction),
        )
        for k in (1, 2, 3)
    )

    classes = tuple(build_grid(real_pairs, min_support=2))

    return GridReport(
        stem_min=stem_min,
        perms=perms,
        seed=seed,
        bridging_pair_count=len(real_pairs),
        fractions=fractions,
        classes=classes,
    )


def _fmt_nd(nd: NullDistribution) -> str:
    return (
        f"real {nd.real_value:.3f} (percentile {nd.real_percentile:.1f}), "
        f"null mean {nd.mean:.3f} sd {nd.sd:.3f}, p95 {nd.p95:.3f}, p99 {nd.p99:.3f}"
    )


def render_grid_markdown(report: GridReport) -> str:
    lines = [
        "## Grid (stage 2)",
        "",
        f"Bridging pairs: {report.bridging_pair_count}. stem_min {report.stem_min}, "
        f"{report.perms} N1 draws.",
        "",
        "| k | pairs | excluded | scored | fraction sharing consonant | chance fraction | N1 null |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for f in report.fractions:
        cf = f.fraction
        lines.append(
            f"| {cf.k} | {cf.pair_count} | {cf.excluded_count} | {cf.scored_count} | "
            f"{cf.fraction:.3f} | {cf.chance_fraction:.3f} | {_fmt_nd(f.null)} |"
        )
    lines += [
        "",
        f"Sign classes (union-find, support >= 2): {len(report.classes)}.",
        "",
        "| class | size | pure | consonants mixed | excluded signs |",
        "|---|---:|---|---|---|",
    ]
    for c in report.classes:
        cons = ", ".join(c.consonants) if c.consonants else "-"
        exc = ", ".join(c.excluded_signs) if c.excluded_signs else "-"
        lines.append(
            f"| {', '.join(c.signs)} | {c.size} | {'yes' if c.pure else 'no'} | {cons} | {exc} |"
        )
    lines.append("")
    return "\n".join(lines)


def anchored_stems(
    channel: ChannelResult, top_alternations: frozenset[tuple[Word, Word]]
) -> frozenset[Word]:
    """Stems whose own ending set contains both endings of some alternation in
    ``top_alternations`` -- i.e. stems that *support* one of those alternations,
    in the same sense ``paradigms.build_channel`` counts support.
    """
    out: set[Word] = set()
    for stem, endings in channel.anchors.items():
        for pair in combinations(sorted(endings), 2):
            if pair in top_alternations:
                out.add(stem)
                break
    return frozenset(out)


@dataclass(frozen=True, slots=True)
class AnchoredGridReport:
    """Stage 2 version 0.2: bridging pairs anchored to the top ten ending
    alternations, real and per N1 draw (A-053 to A-056)."""

    stem_min: int
    perms: int
    seed: int
    top_n: int
    anchor_alternation_count: int
    anchor_stem_count: int
    anchored_pair_count: int
    fraction: ConsonantFraction
    null: NullDistribution
    classes: tuple[SignClass, ...]

    def as_dict(self) -> dict:
        return {
            "version": "0.2",  # A-090: stage 2 version 0.2
            "stem_min": self.stem_min,
            "perms": self.perms,
            "seed": self.seed,
            "top_n": self.top_n,
            "anchor_alternation_count": self.anchor_alternation_count,
            "anchor_stem_count": self.anchor_stem_count,
            "anchored_pair_count": self.anchored_pair_count,
            **self.fraction.as_dict(),
            "null": self.null.as_dict(),
            "class_count": len(self.classes),
            "classes": [c.as_dict() for c in self.classes],
        }


def build_anchored_grid_report(
    words: Iterable[Word],
    ending: ChannelResult,
    stem_min: int,
    perms: int,
    seed: int,
    top_n: int = 10,
) -> AnchoredGridReport:
    """Build the stage 2 version 0.2 report.

    ``ending`` is the already-built ending channel for ``words`` at
    ``stem_min`` (the same one stage 1 and stage 2 version 0.1 use), so this
    does not rebuild it for the real corpus. Each N1 draw rebuilds its own
    ending channel and anchors to *that draw's own* top ``top_n`` alternations
    (by ties-included support), per the pre-registration.
    """
    words = list(words)
    real_top_alts = top_n_alternations_with_ties(ending.alternation_support, top_n)
    real_stems = anchored_stems(ending, real_top_alts)
    real_pairs = bridging_pairs(ending, stems=real_stems)
    real_fraction = consonant_fraction(real_pairs, k=1)

    rng = random.Random(_sub_seed(seed, "grid_anchored"))
    null_values: list[float] = []
    for _ in range(perms):
        drawn = n1_draw(words, rng)
        drawn_channel = ending_channel(drawn, stem_min=stem_min)
        drawn_top_alts = top_n_alternations_with_ties(drawn_channel.alternation_support, top_n)
        drawn_stems = anchored_stems(drawn_channel, drawn_top_alts)
        drawn_pairs = bridging_pairs(drawn_channel, stems=drawn_stems)
        null_values.append(consonant_fraction(drawn_pairs, k=1).fraction)

    null = _summarise(null_values, real_fraction.fraction)
    classes = tuple(build_grid(real_pairs, min_support=2))

    return AnchoredGridReport(
        stem_min=stem_min,
        perms=perms,
        seed=seed,
        top_n=top_n,
        anchor_alternation_count=len(real_top_alts),
        anchor_stem_count=len(real_stems),
        anchored_pair_count=len(real_pairs),
        fraction=real_fraction,
        null=null,
        classes=classes,
    )


def render_anchored_grid_markdown(report: AnchoredGridReport) -> str:
    f = report.fraction
    lines = [
        "## Grid, anchored bridging pairs (stage 2 version 0.2)",
        "",
        f"Top {report.top_n} ending alternations (ties included): "
        f"{report.anchor_alternation_count} alternations, {report.anchor_stem_count} "
        f"anchor stems, {report.anchored_pair_count} anchored bridging pairs. "
        f"stem_min {report.stem_min}, {report.perms} N1 draws.",
        "",
        "| pairs | excluded | scored | fraction sharing consonant | chance fraction | N1 null |",
        "|---:|---:|---:|---:|---:|---|",
        f"| {f.pair_count} | {f.excluded_count} | {f.scored_count} | {f.fraction:.3f} | "
        f"{f.chance_fraction:.3f} | {_fmt_nd(report.null)} |",
        "",
        f"Sign classes (union-find, support >= 2): {len(report.classes)}.",
        "",
        "| class | size | pure | consonants mixed | excluded signs |",
        "|---|---:|---|---|---|",
    ]
    for c in report.classes:
        cons = ", ".join(c.consonants) if c.consonants else "-"
        exc = ", ".join(c.excluded_signs) if c.excluded_signs else "-"
        lines.append(
            f"| {', '.join(c.signs)} | {c.size} | {'yes' if c.pure else 'no'} | {cons} | {exc} |"
        )
    lines.append("")
    return "\n".join(lines)


def alternation_bridging_pairs(
    top_alternations: Iterable[tuple[Word, Word]],
) -> list[tuple[str, str]]:
    """One bridging pair per top-ten ending alternation itself (CHANGELOG "0.3").

    For each alternation ``(e1, e2)`` in ``top_alternations``, the pair of the
    two endings' own first signs, kept only when they differ -- an alternation
    whose two endings begin with the same sign (e.g. -si-jo / -si-ja) yields no
    pair. Weighted by nothing: this is a flat list, one entry per qualifying
    alternation, not a support-counted mapping like ``bridging_pairs``. Two
    different alternations that happen to yield the same first-sign pair each
    still contribute their own entry rather than collapsing into one.
    """
    pairs: list[tuple[str, str]] = []
    for e1, e2 in top_alternations:
        if e1[0] == e2[0]:
            continue
        pairs.append(tuple(sorted((e1[0], e2[0]))))
    return pairs


def consonant_fraction_from_pairs(pairs: Iterable[tuple[str, str]]) -> ConsonantFraction:
    """The shared-consonant fraction over ``pairs`` taken literally (CHANGELOG "0.3").

    Unlike ``consonant_fraction``, ``pairs`` is a flat list, not a support-
    counted mapping: every entry counts once towards the numerator and
    denominator, with no ``k`` threshold to apply (``k`` is reported as 1 for
    interface consistency with ``ConsonantFraction`` only; it plays no
    filtering role here, since there is nothing to threshold). A pair with an
    excluded sign (``values.consonant_of`` returns ``None``) is dropped from
    both the numerator and the denominator and counted separately, as in
    ``consonant_fraction``.
    """
    pairs = list(pairs)
    excluded = 0
    shared = 0
    consonants: list[str] = []
    for s1, s2 in pairs:
        c1, c2 = consonant_of(s1), consonant_of(s2)
        if c1 is None or c2 is None:
            excluded += 1
            continue
        consonants.append(c1)
        consonants.append(c2)
        if c1 == c2:
            shared += 1
    scored = len(pairs) - excluded
    fraction = shared / scored if scored else 0.0
    if consonants:
        total = len(consonants)
        chance = sum((n / total) ** 2 for n in Counter(consonants).values())
    else:
        chance = 0.0
    return ConsonantFraction(
        k=1,
        pair_count=len(pairs),
        excluded_count=excluded,
        scored_count=scored,
        shared_count=shared,
        fraction=fraction,
        chance_fraction=chance,
    )


@dataclass(frozen=True, slots=True)
class AlternationGridReport:
    """Stage 2 version 0.3: bridging pairs are the top-ten ending alternations'
    own first-sign pairs, not pairs drawn from their stems' full ending sets
    (A-059 onward)."""

    stem_min: int
    perms: int
    seed: int
    top_n: int
    alternation_count: int
    fraction: ConsonantFraction
    null: NullDistribution
    classes: tuple[SignClass, ...]

    def as_dict(self) -> dict:
        return {
            "version": "0.3",  # A-090: stage 2 version 0.3
            "stem_min": self.stem_min,
            "perms": self.perms,
            "seed": self.seed,
            "top_n": self.top_n,
            "alternation_count": self.alternation_count,
            **self.fraction.as_dict(),
            "null": self.null.as_dict(),
            "class_count": len(self.classes),
            "classes": [c.as_dict() for c in self.classes],
        }


def build_alternation_grid_report(
    words: Iterable[Word],
    ending: ChannelResult,
    stem_min: int,
    perms: int,
    seed: int,
    top_n: int = 10,
) -> AlternationGridReport:
    """Build the stage 2 version 0.3 report.

    ``ending`` is the already-built ending channel for ``words`` at
    ``stem_min`` (the same one stage 1 and stage 2 versions 0.1/0.2 use), so
    this does not rebuild it for the real corpus. Each N1 draw rebuilds its
    own ending channel and takes its bridging pairs from *that draw's own*
    top ``top_n`` alternations (by ties-included support), per the
    pre-registration.
    """
    words = list(words)
    real_top_alts = top_n_alternations_with_ties(ending.alternation_support, top_n)
    real_pairs = alternation_bridging_pairs(real_top_alts)
    real_fraction = consonant_fraction_from_pairs(real_pairs)

    rng = random.Random(_sub_seed(seed, "grid_alternations"))
    null_values: list[float] = []
    for _ in range(perms):
        drawn = n1_draw(words, rng)
        drawn_channel = ending_channel(drawn, stem_min=stem_min)
        drawn_top_alts = top_n_alternations_with_ties(drawn_channel.alternation_support, top_n)
        drawn_pairs = alternation_bridging_pairs(drawn_top_alts)
        null_values.append(consonant_fraction_from_pairs(drawn_pairs).fraction)

    null = _summarise(null_values, real_fraction.fraction)
    classes = tuple(build_grid(Counter(real_pairs), min_support=1))

    return AlternationGridReport(
        stem_min=stem_min,
        perms=perms,
        seed=seed,
        top_n=top_n,
        alternation_count=len(real_top_alts),
        fraction=real_fraction,
        null=null,
        classes=classes,
    )


def render_alternation_grid_markdown(report: AlternationGridReport) -> str:
    f = report.fraction
    lines = [
        "## Grid, alternations' own bridging pairs (stage 2 version 0.3)",
        "",
        f"Top {report.top_n} ending alternations (ties included): "
        f"{report.alternation_count} alternations, {f.pair_count} bridging pairs "
        f"(one per alternation whose two endings' first signs differ). "
        f"stem_min {report.stem_min}, {report.perms} N1 draws.",
        "",
        "| pairs | excluded | scored | fraction sharing consonant | chance fraction | N1 null |",
        "|---:|---:|---:|---:|---:|---|",
        f"| {f.pair_count} | {f.excluded_count} | {f.scored_count} | {f.fraction:.3f} | "
        f"{f.chance_fraction:.3f} | {_fmt_nd(report.null)} |",
        "",
        f"Sign classes (union-find, every real pair): {len(report.classes)}.",
        "",
        "| class | size | pure | consonants mixed | excluded signs |",
        "|---|---:|---|---|---|",
    ]
    for c in report.classes:
        cons = ", ".join(c.consonants) if c.consonants else "-"
        exc = ", ".join(c.excluded_signs) if c.excluded_signs else "-"
        lines.append(
            f"| {', '.join(c.signs)} | {c.size} | {'yes' if c.pure else 'no'} | {cons} | {exc} |"
        )
    lines.append("")
    return "\n".join(lines)
