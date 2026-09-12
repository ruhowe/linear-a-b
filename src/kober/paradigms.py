"""Stems, endings, prefixes, paradigms and alternation support (A-033, A-035).

**Splits.** A word of length ``n`` (signs) contributes candidate splits at ending
length ``k`` in ``(1, 2)``, provided the remaining anchor keeps at least ``stem_min``
signs (``n - k >= stem_min``, A-035). The **ending channel** anchors on the
word-initial run (the stem) and takes the word-final ``k`` signs as the ending. The
**prefix channel** mirrors this on the reversed word: the anchor is the word-final
run (the base) and the affix is the word-initial ``k`` signs (the prefix). Both
channels share one implementation (``mirror=False`` / ``mirror=True``) because the
split rule is the same rule read from the other end, but per the design they are
reported and never merged (A-033: only suffixal or only prefixal structure is
visible to either channel, never both on the same word split).

**Paradigm.** A stem (or base) attested with two or more distinct endings (or
prefixes) *of any length* — a one-sign ending on one word and a two-sign ending on
another, both anchored at the same stem, count as one paradigm with two endings.

**Alternation support.** For every paradigm, every unordered pair of its endings is
one attestation; support for a pair is the number of distinct stems where both
endings of the pair occur. This is the quantity Kober read by eye as her triplets.

**Context-restricted mode (Kober 0.4, A-076).**
``build_channel_context_restricted`` is the same splitting rule, but a stem
counts toward an alternation only when the two words it heads share a
``context.ContextClass``; a stem is a (context-restricted) paradigm when at
least two of its endings' words share a class, i.e. when it supports at least
one context-restricted alternation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping

from .context import ContextClass

__all__ = [
    "Word",
    "ChannelResult",
    "splits_for_word",
    "build_channel",
    "ending_channel",
    "prefix_channel",
    "ranked_alternations",
    "top_n_alternations_with_ties",
    "build_channel_context_restricted",
    "ending_channel_context_restricted",
    "prefix_channel_context_restricted",
    "role_sharing_counts",
    "list_support_counts",
]

Word = tuple[str, ...]


def splits_for_word(word: Word, stem_min: int, mirror: bool) -> list[tuple[Word, Word]]:
    """``(anchor, affix)`` pairs for one word, for ending length ``k`` in ``(1, 2)``.

    ``mirror=False``: anchor is the word-initial stem, affix is the word-final
    ending. ``mirror=True``: anchor is the word-final base, affix is the
    word-initial prefix. A split is only yielded when the anchor keeps at least
    ``stem_min`` signs.
    """
    n = len(word)
    out: list[tuple[Word, Word]] = []
    for k in (1, 2):
        if n - k < stem_min:
            continue
        if mirror:
            affix, anchor = word[:k], word[k:]
        else:
            anchor, affix = word[: n - k], word[n - k :]
        out.append((anchor, affix))
    return out


@dataclass(frozen=True, slots=True)
class ChannelResult:
    """One channel's paradigms and alternation support.

    ``anchors`` maps every stem (or base, for the mirror channel) with two or more
    distinct affixes to the frozenset of those affixes — this *is* the paradigm
    table. ``alternation_support`` maps a sorted pair of affixes to the number of
    distinct anchors attested with both.
    """

    anchors: Mapping[Word, frozenset[Word]]
    paradigm_count_total: int
    paradigm_count_by_stem_length: Mapping[int, int]
    alternation_support: Mapping[tuple[Word, Word], int]


def build_channel(words: Iterable[Word], stem_min: int = 2, mirror: bool = False) -> ChannelResult:
    """Build the paradigm table and alternation support for one channel.

    ``words`` is any iterable of sign-label tuples (word types). Words shorter than
    ``stem_min + 1`` signs contribute no splits and are silently ignored — this is a
    consequence of the ``stem_min`` rule, not a separate filter.
    """
    affixes_by_anchor: dict[Word, set[Word]] = defaultdict(set)
    for word in words:
        for anchor, affix in splits_for_word(word, stem_min, mirror):
            affixes_by_anchor[anchor].add(affix)

    paradigms = {
        anchor: frozenset(affixes)
        for anchor, affixes in affixes_by_anchor.items()
        if len(affixes) >= 2
    }

    by_length: dict[int, int] = defaultdict(int)
    for anchor in paradigms:
        by_length[len(anchor)] += 1

    support: dict[tuple[Word, Word], int] = defaultdict(int)
    for affixes in paradigms.values():
        for a1, a2 in combinations(sorted(affixes), 2):
            support[(a1, a2)] += 1

    return ChannelResult(
        anchors=paradigms,
        paradigm_count_total=len(paradigms),
        paradigm_count_by_stem_length=dict(by_length),
        alternation_support=dict(support),
    )


def ending_channel(words: Iterable[Word], stem_min: int = 2) -> ChannelResult:
    return build_channel(words, stem_min=stem_min, mirror=False)


def prefix_channel(words: Iterable[Word], stem_min: int = 2) -> ChannelResult:
    return build_channel(words, stem_min=stem_min, mirror=True)


def build_channel_context_restricted(
    words: Iterable[Word],
    word_class: Mapping[Word, ContextClass],
    stem_min: int = 2,
    mirror: bool = False,
) -> ChannelResult:
    """Kober 0.4's context-restricted channel (A-076): a stem counts toward an
    alternation only if the two words it heads (``anchor + a1``, ``anchor +
    a2``, or their mirror) share a context class. A stem is counted as a
    (context-restricted) paradigm exactly when at least two of its endings'
    words share a class (A-076's own wording) -- equivalently, when it
    supports at least one context-restricted alternation, since a shared-class
    pair of endings *is* what "two of its endings' words share a class" means.

    Splitting is identical to ``build_channel``; only which pairs count is
    different. An affix whose combined word is not in ``word_class`` (should
    not happen when ``word_class`` was built from the same ``words``, but not
    assumed) contributes to no pair.
    """
    affixes_by_anchor: dict[Word, set[Word]] = defaultdict(set)
    for word in words:
        for anchor, affix in splits_for_word(word, stem_min, mirror):
            affixes_by_anchor[anchor].add(affix)

    paradigms: dict[Word, frozenset[Word]] = {}
    support: dict[tuple[Word, Word], int] = defaultdict(int)

    for anchor, affixes in affixes_by_anchor.items():
        if len(affixes) < 2:
            continue
        affix_class: dict[Word, ContextClass] = {}
        for affix in affixes:
            word = (affix + anchor) if mirror else (anchor + affix)
            cls = word_class.get(word)
            if cls is not None:
                affix_class[affix] = cls

        shared_pairs: list[tuple[Word, Word]] = []
        for a1, a2 in combinations(sorted(affixes), 2):
            c1, c2 = affix_class.get(a1), affix_class.get(a2)
            if c1 is not None and c1 == c2:
                shared_pairs.append((a1, a2))

        if not shared_pairs:
            continue
        paradigms[anchor] = frozenset(affixes)
        for pair in shared_pairs:
            support[pair] += 1

    by_length: dict[int, int] = defaultdict(int)
    for anchor in paradigms:
        by_length[len(anchor)] += 1

    return ChannelResult(
        anchors=paradigms,
        paradigm_count_total=len(paradigms),
        paradigm_count_by_stem_length=dict(by_length),
        alternation_support=dict(support),
    )


def ending_channel_context_restricted(
    words: Iterable[Word], word_class: Mapping[Word, ContextClass], stem_min: int = 2
) -> ChannelResult:
    return build_channel_context_restricted(words, word_class, stem_min=stem_min, mirror=False)


def prefix_channel_context_restricted(
    words: Iterable[Word], word_class: Mapping[Word, ContextClass], stem_min: int = 2
) -> ChannelResult:
    return build_channel_context_restricted(words, word_class, stem_min=stem_min, mirror=True)


def ranked_alternations(
    support: Mapping[tuple[Word, Word], int],
    limit: int | None = None,
    role_sharing: Mapping[tuple[Word, Word], int] | None = None,
    list_support: Mapping[tuple[Word, Word], int] | None = None,
) -> list[tuple[tuple[Word, Word], int]]:
    """Alternation pairs ranked by support, descending; ties broken
    lexicographically. ``role_sharing`` (Kober 0.5, CHANGELOG "0.5", A-072)
    and ``list_support`` (Kober 0.7, CHANGELOG "0.7") are optional ordering
    keys, each consulted *before* the lexicographic tie-break and *after*
    support, in that order: support descending, then (if given) role-sharing
    count descending, then (if given) list-support count descending, then the
    ending pair in sorted lexicographic order. Either key defaults to 0 for a
    pair not present in its mapping (``Mapping.get``).

    Default ``role_sharing=None, list_support=None`` leaves the ordering, and
    every existing caller's numbers, byte-identical to 0.3: support
    descending, then lexicographic. ``role_sharing`` given alone reproduces
    0.5's ordering byte-identically (a 3-tuple key, unchanged in shape and
    values from before this parameter existed). Both given together is
    Kober 0.7's four-level ordering.
    """
    key_fields: list = [lambda kv: -kv[1]]
    if role_sharing is not None:
        key_fields.append(lambda kv: -role_sharing.get(kv[0], 0))
    if list_support is not None:
        key_fields.append(lambda kv: -list_support.get(kv[0], 0))
    key_fields.append(lambda kv: kv[0])

    def key(kv: tuple[tuple[Word, Word], int]) -> tuple:
        return tuple(f(kv) for f in key_fields)

    ranked = sorted(support.items(), key=key)
    return ranked if limit is None else ranked[:limit]


def role_sharing_counts(
    channel: ChannelResult,
    word_roles: Mapping[Word, frozenset],
    mirror: bool = False,
) -> dict[tuple[Word, Word], int]:
    """For each alternation in ``channel``, the number of supporting stems
    (anchors) whose two forms -- the whole words the anchor and each affix
    combine into -- share at least one role in ``word_roles`` (Kober 0.5,
    CHANGELOG "0.5").

    ``word_roles`` is looked up by word-type identity only (``Mapping.get``,
    default the empty set): it is not recomputed here, so a word a null
    draw's ending shuffle recombines (an anchor paired with an affix drawn
    from a different real word) carries whatever role set that exact sign
    sequence happens to have in ``word_roles`` -- typically none, since most
    such recombinations are not themselves real corpus words. This is the
    "roles stay attached to word types while endings shuffle" rule the
    CHANGELOG entry states: the null does not carry a donor word's roles
    along with its shuffled ending.
    """
    counts: dict[tuple[Word, Word], int] = defaultdict(int)
    for anchor, affixes in channel.anchors.items():
        for a1, a2 in combinations(sorted(affixes), 2):
            w1 = (a1 + anchor) if mirror else (anchor + a1)
            w2 = (a2 + anchor) if mirror else (anchor + a2)
            if word_roles.get(w1, frozenset()) & word_roles.get(w2, frozenset()):
                counts[(a1, a2)] += 1
    return dict(counts)


def _satisfies_assumption7(word: Word, homogeneous_forms: Mapping[Word, frozenset]) -> bool:
    """kober1946's Assumption 7 (CHANGELOG "0.7"): ``word``'s own final sign
    is a member of its modal-sign set (``kober.lists.homogeneous_forms``).
    Empty ``word`` (should not occur) satisfies nothing."""
    if not word:
        return False
    return word[-1] in homogeneous_forms.get(word, frozenset())


def list_support_counts(
    channel: ChannelResult,
    homogeneous_forms: Mapping[Word, frozenset],
    mirror: bool = False,
) -> dict[tuple[Word, Word], int]:
    """For each alternation in ``channel``, the number of supporting stems
    (anchors) whose two forms -- the whole words the anchor and each affix
    combine into -- both satisfy kober1946's Assumption 7 (Kober 0.7,
    CHANGELOG "0.7"; ``kober.lists.homogeneous_forms``).

    ``homogeneous_forms`` is looked up by word-type identity only
    (``Mapping.get``, default the empty frozenset), the same pattern
    ``role_sharing_counts`` uses (A-098): a word absent from the mapping --
    never occurs as a listed word in an eligible document, or, under the N2
    null, a synthetic recombination not itself a real corpus word --
    satisfies nothing.
    """
    counts: dict[tuple[Word, Word], int] = defaultdict(int)
    for anchor, affixes in channel.anchors.items():
        for a1, a2 in combinations(sorted(affixes), 2):
            w1 = (a1 + anchor) if mirror else (anchor + a1)
            w2 = (a2 + anchor) if mirror else (anchor + a2)
            if _satisfies_assumption7(w1, homogeneous_forms) and _satisfies_assumption7(w2, homogeneous_forms):
                counts[(a1, a2)] += 1
    return dict(counts)


def top_n_alternations_with_ties(
    support: Mapping[tuple[Word, Word], int], n: int = 10
) -> frozenset[tuple[Word, Word]]:
    """The alternations ranked 1..``n`` by support, extended to include every
    alternation tied with the ``n``-th value (A-053: "top ten" can therefore
    select more than ten alternations).

    Moved here from ``grid.py`` (stage 2 version 0.2's original home) so the
    grammar-match null (``nulls.py``) can use the same ranking rule without a
    circular import, since ``grid.py`` itself imports from ``nulls.py``.
    ``grid.py`` re-exports this name for backward compatibility.
    """
    if not support:
        return frozenset()
    ranked = sorted(support.items(), key=lambda kv: -kv[1])
    if len(ranked) <= n:
        return frozenset(pair for pair, _support in ranked)
    threshold = ranked[n - 1][1]
    return frozenset(pair for pair, sup in ranked if sup >= threshold)
