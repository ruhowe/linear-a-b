"""Assemble and write the Kober-method report: JSON plus a markdown summary.

Aggregate numbers only. No word lists, no stems: the one exception is the top-20
alternation entries, which are pairs of endings (one or two signs each) — sign
pairs, not words, and explicitly allowed by the design page. Nothing here decides
whether the pre-registered criterion (``docs/ai_context/kober-method.md``) is met;
that reading belongs to the session, not to this module.

**Versioning (A-090).** Each block carries its own ``version`` field, stamped
where the block is built: ``ending_channel``/``prefix_channel`` "0.1"
(``_channel_dict``); ``grammar_match_null``/``grammar_match_null_strict``
"0.3" (unconditional, since the grammar-match null runs on every report,
CHANGELOG "Null rate of the grammar match"); ``grid`` "0.1", ``grid_anchored``
"0.2", ``grid_alternations`` "0.3" (``grid.py``); ``context`` "0.4"
(``ContextReport``). The file-level ``protocol_version`` (``KoberReport.as_dict``,
bumped further by ``write_report`` when an optional block is attached) is the
*highest* block version actually present in that file, not a fixed constant --
"0.3" is always the floor (stage 1 plus the unconditional grammar-match null),
and only an attached grid or context block can raise it. Existing committed
results files predate this rule and are not rewritten; only new runs get the
new stamps.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .context import ContextClass, WordContexts
from .grid import (
    AlternationGridReport,
    AnchoredGridReport,
    GridReport,
    render_alternation_grid_markdown,
    render_anchored_grid_markdown,
    render_grid_markdown,
)
from .lists import DocListing, homogeneous_forms_from_listings
from .medial import MedialReport, build_medial_report, render_medial_markdown
from .nulls import (
    N1ContextResult,
    N1Result,
    N2ContextResult,
    N2Result,
    NullDistribution,
    NullResults,
    TiesSizeStat,
    run_n1_context,
    run_n2_context,
    run_nulls,
)
from .paradigms import (
    ChannelResult,
    Word,
    ending_channel,
    ending_channel_context_restricted,
    list_support_counts,
    prefix_channel,
    ranked_alternations,
    role_sharing_counts,
)
from .reference import REFERENCE_ALTERNATIONS, is_grammar
from .words import WordTypes, extract_word_types, restrict_to_shared, subsample_word_types

__all__ = [
    "PROTOCOL_VERSION",
    "BASE_PROTOCOL_VERSION",
    "KoberReport",
    "build_report",
    "write_report",
    "render_markdown",
    "ContextReport",
    "build_context_report",
    "render_context_markdown",
    "RoleTiebreakReport",
    "build_role_tiebreak_report",
    "render_role_tiebreak_markdown",
    "ListTiebreakReport",
    "build_list_tiebreak_report",
    "render_list_tiebreak_markdown",
    "build_medial_report",
    "render_medial_markdown",
]

PROTOCOL_VERSION = "0.1"  # stage 1's own block version (A-090)

# Per-block versions (A-090), and the file-level version they combine into.
_GRAMMAR_MATCH_VERSION = "0.3"
_GRID_VERSION = "0.1"
_GRID_ANCHORED_VERSION = "0.2"
_GRID_ALTERNATIONS_VERSION = "0.3"
_CONTEXT_VERSION = "0.4"
_ROLE_TIEBREAK_VERSION = "0.5"
_LIST_TIEBREAK_VERSION = "0.7"
_MEDIAL_VERSION = "0.9"
_VERSION_ORDER = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.7", "0.9"]


def _max_version(versions: Iterable[str]) -> str:
    return max(versions, key=_VERSION_ORDER.index)


# Stage 1 ("0.1") plus the unconditional grammar-match null ("0.3") are present
# in every report, so this is the file-level floor before any optional block.
BASE_PROTOCOL_VERSION = _max_version([PROTOCOL_VERSION, _GRAMMAR_MATCH_VERSION])


def _bumped_protocol_version(
    base: str,
    grid_report: "GridReport | None",
    anchored_grid_report: "AnchoredGridReport | None",
    alternation_grid_report: "AlternationGridReport | None",
    context_report: "ContextReport | None",
    role_tiebreak_report: "RoleTiebreakReport | None" = None,
    list_tiebreak_report: "ListTiebreakReport | None" = None,
    medial_report: "MedialReport | None" = None,
    merge_homophones: bool = False,
) -> str:
    """The file-level ``protocol_version``: ``base`` (A-090's floor), raised to
    the version of any optional block actually attached. Kober 0.9 (CHANGELOG
    "0.9", A-146) bumps to "0.9" when either the medial block is attached or
    ``merge_homophones`` was used, whichever or both -- there is one 0.9
    version, not one per flag."""
    versions = [base]
    if grid_report is not None:
        versions.append(_GRID_VERSION)
    if anchored_grid_report is not None:
        versions.append(_GRID_ANCHORED_VERSION)
    if alternation_grid_report is not None:
        versions.append(_GRID_ALTERNATIONS_VERSION)
    if context_report is not None:
        versions.append(_CONTEXT_VERSION)
    if role_tiebreak_report is not None:
        versions.append(_ROLE_TIEBREAK_VERSION)
    if list_tiebreak_report is not None:
        versions.append(_LIST_TIEBREAK_VERSION)
    if medial_report is not None or merge_homophones:
        versions.append(_MEDIAL_VERSION)
    return _max_version(versions)


_RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def _word_str(w: Word) -> str:
    return "-".join(w)


def _alternation_entries(channel: ChannelResult, limit: int = 20) -> list[dict]:
    entries = []
    for (e1, e2), support in ranked_alternations(channel.alternation_support, limit):
        entries.append(
            {
                "e1": list(e1),
                "e2": list(e2),
                "e1_label": _word_str(e1),
                "e2_label": _word_str(e2),
                "support": support,
                "rule": is_grammar(e1, e2),
            }
        )
    return entries


def _null_dist_dict(nd: NullDistribution) -> dict:
    return nd.as_dict()


def _n1_dict(n1: N1Result) -> dict:
    return {
        "type_count_mean": n1.type_count_mean,
        "type_count_sd": n1.type_count_sd,
        "ending_paradigm_count": _null_dist_dict(n1.ending_paradigm_count),
        "prefix_paradigm_count": _null_dist_dict(n1.prefix_paradigm_count),
    }


def _n2_dict(n2: N2Result) -> dict:
    return {
        "max_support": _null_dist_dict(n2.max_support),
        "tenth_support": _null_dist_dict(n2.tenth_support),
    }


def _grammar_match_dict(grammar_match: Mapping[int, NullDistribution] | None) -> dict:
    """``grammar_match_null`` block (ending channel only, CHANGELOG "Null rate of
    the grammar match, and precision criteria"): per n, the real matched count,
    the null distribution and the real percentile, all already carried by
    ``NullDistribution``."""
    if grammar_match is None:
        return {}
    return {
        "version": _GRAMMAR_MATCH_VERSION,
        **{str(n): _null_dist_dict(nd) for n, nd in sorted(grammar_match.items())},
    }


_RULE_FIRING_VERSION = "0.8"


def _rule_firing_counts_null_dict(counts: Mapping[str, int] | None, draws: int) -> dict:
    """``rule_firing_counts_null`` (ending channel only, CHANGELOG "0.8"):
    a Counter of rule names among each N2 draw's own strict top ten, summed
    over every draw -- "the rules that fire most under the null". Reuses the
    same per-draw ``support`` the other grammar-match variants already build
    (``nulls.rule_firing_counts_strict``), so this consumes no extra draws.
    """
    if counts is None:
        return {}
    return {
        "version": _RULE_FIRING_VERSION,
        "draws": draws,
        "n": 10,
        "counts": dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def _grammar_match_strict_dict(
    grammar_match_strict: Mapping[int, NullDistribution] | None,
    ties_included_top_n_size: Mapping[int, TiesSizeStat] | None,
) -> dict:
    """``grammar_match_null_strict`` block (ending channel only, A-072): the same
    fields as ``grammar_match_null``, but the matched count is computed under a
    strict top-n cut (deterministic tie-break, ``paradigms.ranked_alternations``)
    applied identically to the real corpus and to every N2 draw, rather than the
    ties-included top-n (A-053) ``grammar_match_null`` uses. Each n's entry also
    carries ``ties_included_top_n_size`` (null mean and real value only) so the
    two readings of "top-n" can be compared directly."""
    if grammar_match_strict is None:
        return {}
    out: dict[str, dict] = {"version": _GRAMMAR_MATCH_VERSION}
    for n, nd in sorted(grammar_match_strict.items()):
        entry = _null_dist_dict(nd)
        if ties_included_top_n_size is not None:
            entry["ties_included_top_n_size"] = ties_included_top_n_size[n].as_dict()
        out[str(n)] = entry
    return out


def _channel_dict(channel: ChannelResult, alternations: list[dict]) -> dict:
    return {
        "version": PROTOCOL_VERSION,
        "paradigm_count_total": channel.paradigm_count_total,
        "paradigm_count_by_stem_length": {
            str(k): v for k, v in sorted(channel.paradigm_count_by_stem_length.items())
        },
        "top_20_alternations": alternations,
        "top_10_matched_to_rule": sum(1 for a in alternations[:10] if a["rule"] is not None),
    }


@dataclass(frozen=True, slots=True)
class KoberReport:
    corpus: str
    stem_min: int
    perms: int
    seed: int
    word_types: WordTypes
    ending: ChannelResult
    prefix: ChannelResult
    nulls: NullResults
    ending_alternations: list[dict]
    prefix_alternations: list[dict]
    # Kober 0.6 (CHANGELOG "0.6"): the reference version the grammar-match
    # null (ending_channel.grammar_match_null/grammar_match_null_strict) was
    # graded under. Default 1 reproduces every pre-0.6 file exactly; stage 1's
    # own "rule" fields (top_20_alternations, top_10_matched_to_rule) always
    # use is_grammar's default (version=1) regardless of this field, so they
    # stay bit-identical across a --reference-version rerun (CHANGELOG "0.6").
    reference_version: int = 1
    # Kober 0.9 (CHANGELOG "0.9", A-145): whether extract_word_types merged
    # homophone-index labels before this report's word set was built. Default
    # False reproduces every pre-0.9 file's word set exactly.
    merge_homophones: bool = False

    def as_dict(self) -> dict:
        return {
            "protocol_version": BASE_PROTOCOL_VERSION,
            "corpus": self.corpus,
            "stem_min": self.stem_min,
            "perms": self.perms,
            "seed": self.seed,
            "reference_version": self.reference_version,
            "merge_homophones": self.merge_homophones,
            "word_types": {
                "count": len(self.word_types.words),
                "labels_changed": self.word_types.labels_changed,
                "labels_seen": self.word_types.labels_seen,
            },
            "n1_type_count": {
                "mean": self.nulls.n1.type_count_mean,
                "sd": self.nulls.n1.type_count_sd,
            },
            "ending_channel": {
                **_channel_dict(self.ending, self.ending_alternations),
                "n1_paradigm_count": _null_dist_dict(self.nulls.n1.ending_paradigm_count),
                "n2_alternation_support": _n2_dict(self.nulls.n2_ending),
                "grammar_match_null": _grammar_match_dict(self.nulls.n2_ending.grammar_match),
                "grammar_match_null_strict": _grammar_match_strict_dict(
                    self.nulls.n2_ending.grammar_match_strict, self.nulls.n2_ending.ties_included_top_n_size
                ),
                "rule_firing_counts_null": _rule_firing_counts_null_dict(
                    self.nulls.n2_ending.rule_firing_counts_null, self.perms
                ),
                "top_three_all_matched_chance_rate": self.nulls.n2_ending.top_three_all_matched_chance_rate,
            },
            "prefix_channel": {
                **_channel_dict(self.prefix, self.prefix_alternations),
                "n1_paradigm_count": _null_dist_dict(self.nulls.n1.prefix_paradigm_count),
                "n2_alternation_support": _n2_dict(self.nulls.n2_prefix),
            },
            "reference_alternations": [
                {"alternation": r.alternation, "grammar": r.grammar} for r in REFERENCE_ALTERNATIONS
            ],
        }


def build_report(
    documents: Iterable,
    corpus: str,
    stem_min: int = 2,
    perms: int = 200,
    seed: int = 0,
    subsample_n: int | None = None,
    subsample_seed: int = 0,
    restrict_to_shared_words: frozenset[Word] | None = None,
    word_roles: Mapping[Word, frozenset] | None = None,
    reference_version: int = 1,
    listings: "Sequence[DocListing] | None" = None,
    merge_homophones: bool = False,
) -> KoberReport:
    """``word_roles`` (Kober 0.5, CHANGELOG "0.5"), when given, is a word
    type's role set over whatever documents it was computed from (the full
    corpus, or already doc-subsampled for the tablet model -- the same
    "computed before any word-type-level restriction" pattern
    ``build_context_report``'s ``full_contexts`` already follows, A-089); it
    is restricted here to this run's own final word set (after any
    ``--subsample``/``--restrict-to-shared-with``) and forwarded only to the
    ending channel's N2 null (``run_nulls``). Default ``None`` leaves
    ``build_report``'s behaviour, and every existing regression pin, exactly
    as before.

    ``reference_version`` (Kober 0.6, CHANGELOG "0.6") is forwarded only to
    ``run_nulls``, so it grades the grammar-match null alone
    (``ending_channel.grammar_match_null``/``grammar_match_null_strict``);
    ``ending``/``prefix`` (stage 1's paradigm count, alternation support, and
    each top-20 alternation's own ``rule`` field) are built before this
    parameter is used at all and never see it, so they and every regression
    pin stay bit-identical to a ``reference_version=1`` run. Default 1
    reproduces every existing file exactly.

    ``listings`` (Kober 0.7, CHANGELOG "0.7", A-116), when given, is the
    listed-word extraction (``kober.lists.extract_listed_words``) over the
    same ``documents`` ``word_roles`` is computed from (A-089's pattern: the
    tablet model's own document subset, or the full/type-model set); unlike
    ``word_roles`` it is forwarded to ``run_nulls`` *unrestricted*, since a
    document's modal final sign depends on every one of its listed words, not
    only the ones surviving a word-type-level subsample (A-117). Default
    ``None`` leaves every existing regression pin unaffected.

    ``merge_homophones`` (Kober 0.9, CHANGELOG "0.9", A-144) is forwarded to
    ``extract_word_types`` alone, before any subsample or restriction; every
    channel, null and grid built afterwards runs unchanged on whichever word
    set results (CHANGELOG "0.9": "everything downstream unchanged"). Default
    False reproduces every existing file exactly.
    """
    word_types = extract_word_types(documents, merge_homophones=merge_homophones)
    if subsample_n is not None:
        word_types = subsample_word_types(word_types, subsample_n, subsample_seed)
    if restrict_to_shared_words is not None:
        word_types = restrict_to_shared(word_types, restrict_to_shared_words)
    ending = ending_channel(word_types.words, stem_min=stem_min)
    prefix = prefix_channel(word_types.words, stem_min=stem_min)
    ending_word_roles = None
    if word_roles is not None:
        ending_word_roles = {w: word_roles.get(w, frozenset()) for w in word_types.words}
    nulls = run_nulls(
        word_types.words,
        stem_min,
        perms,
        seed,
        ending,
        prefix,
        word_roles=ending_word_roles,
        reference_version=reference_version,
        listings=listings,
    )
    return KoberReport(
        corpus=corpus,
        stem_min=stem_min,
        perms=perms,
        seed=seed,
        word_types=word_types,
        ending=ending,
        prefix=prefix,
        nulls=nulls,
        ending_alternations=_alternation_entries(ending, 20),
        prefix_alternations=_alternation_entries(prefix, 20),
        reference_version=reference_version,
        merge_homophones=merge_homophones,
    )


@dataclass(frozen=True, slots=True)
class ContextReport:
    """Kober 0.4's context block (CHANGELOG "0.4"; A-085: ending channel only,
    following A-070/A-074's scoping of the grammar-match null): the class
    census, the context-restricted ending channel's paradigm count under a
    stratified N1, its alternation support under a stratified N2 (including
    the strict grammar-match null and the criterion's own chance rate), and
    the real strict top ten and top three alternations. ``census`` is scoped
    to this run's own (possibly subsampled) word set, not the full corpus's
    (A-083). ``top_3`` is the first three entries of ``top_10``, not a
    separately computed ranking (A-087).
    """

    census: Mapping[ContextClass, int]
    ending_context: ChannelResult
    n1_context: N1ContextResult
    n2_context: N2ContextResult
    top_10: list[dict]
    top_3: list[dict]

    def as_dict(self) -> dict:
        return {
            "version": _CONTEXT_VERSION,
            "class_census": [
                {
                    "support_type": cls[0],
                    "line_initial": cls[1],
                    "next_kind": cls[2],
                    "count": count,
                }
                for cls, count in sorted(self.census.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
            "paradigm_count_context_restricted": self.ending_context.paradigm_count_total,
            "n1_paradigm_count_stratified": self.n1_context.ending_paradigm_count.as_dict(),
            "n2_alternation_support_stratified": {
                "max_support": self.n2_context.max_support.as_dict(),
                "tenth_support": self.n2_context.tenth_support.as_dict(),
            },
            "grammar_match_null_strict_stratified": {
                str(n): nd.as_dict() for n, nd in sorted(self.n2_context.grammar_match_strict.items())
            },
            "top_three_all_matched_chance_rate": self.n2_context.top_three_all_matched_chance_rate,
            "top_10": self.top_10,
            "top_3": self.top_3,
        }


def _context_alternation_entries(
    ending_context: ChannelResult, unrestricted_ending: ChannelResult, limit: int
) -> list[dict]:
    entries = []
    for (e1, e2), support in ranked_alternations(ending_context.alternation_support, limit):
        # A-091: the unrestricted (0.1-style) support for the *same* ending
        # pair, from the full ending channel already built for stage 1 (not
        # a lookup truncated to its stored top-20) -- always >= the
        # context-restricted `support`, since restriction only removes
        # qualifying stems, never adds one, so this is never zero here.
        unrestricted_support = unrestricted_ending.alternation_support.get((e1, e2), 0)
        entries.append(
            {
                "e1": list(e1),
                "e2": list(e2),
                "e1_label": _word_str(e1),
                "e2_label": _word_str(e2),
                "support": support,
                # A-086: under 0.4's context-restricted definition, a stem's
                # support for an alternation already requires its two words
                # to share a class, so "how many stems agree in class" and
                # "support" are the same count; reported under its own name
                # (per the task's field list) rather than left implicit.
                "class_agreement_count": support,
                # A-091: fraction of this pair's total (unrestricted) stem
                # support that agrees in class -- how much of the evidence
                # for this alternation the context restriction kept.
                "class_agreement_fraction": (support / unrestricted_support) if unrestricted_support else None,
                "rule": is_grammar(e1, e2),
            }
        )
    return entries


def build_context_report(
    word_types: WordTypes,
    full_contexts: WordContexts,
    unrestricted_ending: ChannelResult,
    stem_min: int = 2,
    perms: int = 200,
    seed: int = 0,
) -> ContextReport:
    """Build the Kober 0.4 context report for ``word_types`` (the run's final
    word set: the full corpus, or an already doc- or type-subsampled one).

    ``full_contexts`` is ``context.extract_word_contexts`` run over whatever
    documents fed ``word_types``' extraction *before* any word-type-level
    (``--subsample``) restriction (A-089): its ``word_class`` is restricted
    here to ``word_types.words``, the same carry-and-restrict pattern
    ``words.subsample_word_types`` and ``words.restrict_to_shared`` already
    use for ``labels_changed``/``labels_seen`` (A-058). For a document-level
    (``--subsample-docs``) or unrestricted run, ``word_types.words`` already
    equals ``full_contexts.word_class``'s domain, so the restriction is a
    no-op.

    ``unrestricted_ending`` is the plain (0.1-style) ending channel already
    built for the same ``word_types.words`` (``report.ending`` from
    ``build_report``), used only to compute each top-alternation's
    ``class_agreement_fraction`` (A-091); nothing else here reads it.
    """
    words = word_types.words
    word_class = {w: full_contexts.word_class[w] for w in words}
    census = Counter(word_class.values())  # A-083: scoped to `words`, not the full corpus

    ending_context = ending_channel_context_restricted(words, word_class, stem_min=stem_min)
    n1_context = run_n1_context(words, word_class, stem_min, perms, seed, ending_context)
    n2_context = run_n2_context(words, word_class, stem_min, perms, seed, ending_context)

    top_10 = _context_alternation_entries(ending_context, unrestricted_ending, 10)
    top_3 = top_10[:3]  # A-087: a slice of top_10, not a separate ranking

    return ContextReport(
        census=dict(census),
        ending_context=ending_context,
        n1_context=n1_context,
        n2_context=n2_context,
        top_10=top_10,
        top_3=top_3,
    )


@dataclass(frozen=True, slots=True)
class RoleTiebreakReport:
    """Kober 0.5's role-tiebreak block (CHANGELOG "0.5"): the real strict top
    ten and top three ending alternations under the role-sharing-aware
    ordering (``paradigms.ranked_alternations``'s ``role_sharing`` key), the
    strict grammar-match null at n in ``nulls.GRAMMAR_MATCH_NS`` recomputed
    under that ordering, the chance rate of "strict top three all matched"
    under it, and how many of the real top ten changed position relative to
    the 0.3 ordering (support descending, then lexicographic alone).
    """

    top_10: list[dict]
    top_3: list[dict]
    grammar_match_null_role_tiebreak: Mapping[int, NullDistribution]
    top_three_all_matched_chance_rate: float
    positions_changed_vs_0_3: int

    def as_dict(self) -> dict:
        return {
            "version": _ROLE_TIEBREAK_VERSION,
            "top_10": self.top_10,
            "top_3": self.top_3,
            "grammar_match_null_role_tiebreak": {
                str(n): nd.as_dict() for n, nd in sorted(self.grammar_match_null_role_tiebreak.items())
            },
            "top_three_all_matched_chance_rate": self.top_three_all_matched_chance_rate,
            "positions_changed_vs_0_3": self.positions_changed_vs_0_3,
        }


def build_role_tiebreak_report(
    report: "KoberReport",
    word_roles: Mapping[Word, frozenset],
) -> RoleTiebreakReport:
    """Build the Kober 0.5 role-tiebreak block from an already-built
    ``KoberReport`` (``build_report``, called with ``word_roles`` set so
    ``report.nulls.n2_ending`` already carries the role-tiebreak null --
    A-072's "reuse the existing N2 draws": this function consumes no extra
    randomness of its own).

    ``word_roles`` here is the same full (pre-restriction) mapping already
    passed to ``build_report``; it is restricted again to
    ``report.word_types.words`` for the real top-ten/top-three computation,
    matching what ``build_report`` did internally for the null (A-089's
    carry-and-restrict pattern).
    """
    words = report.word_types.words
    restricted_roles = {w: word_roles.get(w, frozenset()) for w in words}
    unrestricted_ending = report.ending

    real_role_sharing = role_sharing_counts(unrestricted_ending, restricted_roles)
    ranked_new = ranked_alternations(unrestricted_ending.alternation_support, limit=10, role_sharing=real_role_sharing)
    ranked_old = ranked_alternations(unrestricted_ending.alternation_support, limit=10)  # the 0.3 ordering
    old_position = {pair: i for i, (pair, _support) in enumerate(ranked_old)}

    top_10: list[dict] = []
    positions_changed = 0
    for rank, (pair, support) in enumerate(ranked_new, start=1):
        e1, e2 = pair
        prior = old_position.get(pair)
        if prior is None or prior != rank - 1:
            positions_changed += 1
        top_10.append(
            {
                "e1_label": _word_str(e1),
                "e2_label": _word_str(e2),
                "support": support,
                "role_sharing_count": real_role_sharing.get(pair, 0),
                "rule": is_grammar(e1, e2),
            }
        )
    top_3 = top_10[:3]

    n2e = report.nulls.n2_ending
    if n2e.grammar_match_role_tiebreak is None:
        raise ValueError(
            "build_role_tiebreak_report requires build_report to have been called "
            "with word_roles set, so report.nulls.n2_ending carries the "
            "role-tiebreak null"
        )
    return RoleTiebreakReport(
        top_10=top_10,
        top_3=top_3,
        grammar_match_null_role_tiebreak=n2e.grammar_match_role_tiebreak,
        top_three_all_matched_chance_rate=n2e.top_three_all_matched_chance_rate_role_tiebreak,
        positions_changed_vs_0_3=positions_changed,
    )


@dataclass(frozen=True, slots=True)
class ListTiebreakReport:
    """Kober 0.7's list-support tie-break block (CHANGELOG "0.7", A-116): the
    real strict top ten and top three ending alternations under the
    four-level ordering (support, role-sharing, list-support, lexicographic --
    ``paradigms.ranked_alternations``'s ``role_sharing`` and ``list_support``
    keys together), the strict grammar-match null at n in
    ``nulls.GRAMMAR_MATCH_NS`` recomputed under that ordering at both
    reference versions (1 and 2), the chance rate of "strict top three all
    matched" under it at both versions, and how many of the real top ten
    changed position relative to the 0.5 ordering (support, then
    role-sharing, then lexicographic -- *not* the plain 0.3 ordering,
    A-116).
    """

    top_10: list[dict]
    top_3: list[dict]
    grammar_match_null_list_tiebreak_v1: Mapping[int, NullDistribution]
    grammar_match_null_list_tiebreak_v2: Mapping[int, NullDistribution]
    top_three_all_matched_chance_rate_v1: float
    top_three_all_matched_chance_rate_v2: float
    positions_changed_vs_0_5: int

    def as_dict(self) -> dict:
        return {
            "version": _LIST_TIEBREAK_VERSION,
            "top_10": self.top_10,
            "top_3": self.top_3,
            "grammar_match_null_list_tiebreak_v1": {
                str(n): nd.as_dict() for n, nd in sorted(self.grammar_match_null_list_tiebreak_v1.items())
            },
            "grammar_match_null_list_tiebreak_v2": {
                str(n): nd.as_dict() for n, nd in sorted(self.grammar_match_null_list_tiebreak_v2.items())
            },
            "top_three_all_matched_chance_rate_v1": self.top_three_all_matched_chance_rate_v1,
            "top_three_all_matched_chance_rate_v2": self.top_three_all_matched_chance_rate_v2,
            "positions_changed_vs_0_5": self.positions_changed_vs_0_5,
        }


def build_list_tiebreak_report(
    report: "KoberReport",
    word_roles: Mapping[Word, frozenset],
    listings: "Sequence[DocListing]",
) -> ListTiebreakReport:
    """Build the Kober 0.7 list-tiebreak block from an already-built
    ``KoberReport`` (``build_report``, called with both ``word_roles`` and
    ``listings`` set, so ``report.nulls.n2_ending`` already carries the
    list-tiebreak null -- A-072/A-116's "reuse the existing N2 draws": this
    function consumes no extra randomness of its own).

    ``word_roles`` and ``listings`` here are the same full (pre-restriction)
    values already passed to ``build_report``; both are restricted again to
    ``report.word_types.words`` for the real top-ten/top-three computation
    (A-116, matching A-099's pattern for roles): ``listings`` itself is never
    filtered (a document's modal final sign needs every one of its listed
    words), only the resulting ``homogeneous_forms`` mapping's keys are.
    """
    words = report.word_types.words
    restricted_roles = {w: word_roles.get(w, frozenset()) for w in words}
    full_homogeneous_forms = homogeneous_forms_from_listings(listings)
    restricted_homogeneous_forms = {w: full_homogeneous_forms.get(w, frozenset()) for w in words}
    unrestricted_ending = report.ending

    real_role_sharing = role_sharing_counts(unrestricted_ending, restricted_roles)
    real_list_support = list_support_counts(unrestricted_ending, restricted_homogeneous_forms)
    ranked_new = ranked_alternations(
        unrestricted_ending.alternation_support,
        limit=10,
        role_sharing=real_role_sharing,
        list_support=real_list_support,
    )
    ranked_05 = ranked_alternations(
        unrestricted_ending.alternation_support, limit=10, role_sharing=real_role_sharing
    )  # the 0.5 ordering (A-116: compared against 0.5, not the plain 0.3 ordering)
    old_position = {pair: i for i, (pair, _support) in enumerate(ranked_05)}

    top_10: list[dict] = []
    positions_changed = 0
    for rank, (pair, support) in enumerate(ranked_new, start=1):
        e1, e2 = pair
        prior = old_position.get(pair)
        if prior is None or prior != rank - 1:
            positions_changed += 1
        top_10.append(
            {
                "e1_label": _word_str(e1),
                "e2_label": _word_str(e2),
                "support": support,
                "role_sharing_count": real_role_sharing.get(pair, 0),
                "list_support_count": real_list_support.get(pair, 0),
                "rule_v1": is_grammar(e1, e2, version=1),
                "rule_v2": is_grammar(e1, e2, version=2),
            }
        )
    top_3 = top_10[:3]

    n2e = report.nulls.n2_ending
    if n2e.grammar_match_list_tiebreak_v1 is None or n2e.grammar_match_list_tiebreak_v2 is None:
        raise ValueError(
            "build_list_tiebreak_report requires build_report to have been called "
            "with listings set, so report.nulls.n2_ending carries the "
            "list-tiebreak null at both reference versions"
        )
    return ListTiebreakReport(
        top_10=top_10,
        top_3=top_3,
        grammar_match_null_list_tiebreak_v1=n2e.grammar_match_list_tiebreak_v1,
        grammar_match_null_list_tiebreak_v2=n2e.grammar_match_list_tiebreak_v2,
        top_three_all_matched_chance_rate_v1=n2e.top_three_all_matched_chance_rate_list_tiebreak_v1,
        top_three_all_matched_chance_rate_v2=n2e.top_three_all_matched_chance_rate_list_tiebreak_v2,
        positions_changed_vs_0_5=positions_changed,
    )


def render_role_tiebreak_markdown(role_tiebreak_report: RoleTiebreakReport) -> str:
    lines = [
        "## Role tie-break (0.5)",
        "",
        "### Real strict top ten, role-tiebreak ordering",
        "",
        "| rank | endings | support | role-sharing | rule |",
        "|---:|---|---:|---:|---|",
    ]
    for i, e in enumerate(role_tiebreak_report.top_10, 1):
        rule = e["rule"] or "-"
        lines.append(
            f"| {i} | {e['e1_label']} / {e['e2_label']} | {e['support']} | "
            f"{e['role_sharing_count']} | {rule} |"
        )
    lines += [
        "",
        f"Positions changed vs the 0.3 ordering: {role_tiebreak_report.positions_changed_vs_0_3} "
        f"of {len(role_tiebreak_report.top_10)}.",
        "",
        "### Grammar-match null under the role-tiebreak ordering",
        "",
        "| n | real | null mean | p99 | real percentile |",
        "|---:|---:|---:|---:|---:|",
    ]
    for n, nd in sorted(role_tiebreak_report.grammar_match_null_role_tiebreak.items()):
        lines.append(f"| {n} | {nd.real_value:g} | {nd.mean:.1f} | {nd.p99:.1f} | {nd.real_percentile:.1f} |")
    lines += [
        "",
        f"Top-three-all-matched chance rate under the role-tiebreak ordering: "
        f"{role_tiebreak_report.top_three_all_matched_chance_rate:.3f}",
        "",
    ]
    return "\n".join(lines)


def render_list_tiebreak_markdown(list_tiebreak_report: ListTiebreakReport) -> str:
    lines = [
        "## List-support tie-break (0.7)",
        "",
        "### Real strict top ten, list-tiebreak ordering (support, role-sharing, list-support, lexicographic)",
        "",
        "| rank | endings | support | role-sharing | list-support | rule v1 | rule v2 |",
        "|---:|---|---:|---:|---:|---|---|",
    ]
    for i, e in enumerate(list_tiebreak_report.top_10, 1):
        rule_v1 = e["rule_v1"] or "-"
        rule_v2 = e["rule_v2"] or "-"
        lines.append(
            f"| {i} | {e['e1_label']} / {e['e2_label']} | {e['support']} | "
            f"{e['role_sharing_count']} | {e['list_support_count']} | {rule_v1} | {rule_v2} |"
        )
    lines += [
        "",
        f"Positions changed vs the 0.5 ordering: {list_tiebreak_report.positions_changed_vs_0_5} "
        f"of {len(list_tiebreak_report.top_10)}.",
        "",
        "### Grammar-match null under the list-tiebreak ordering, version 1",
        "",
        "| n | real | null mean | p99 | real percentile |",
        "|---:|---:|---:|---:|---:|",
    ]
    for n, nd in sorted(list_tiebreak_report.grammar_match_null_list_tiebreak_v1.items()):
        lines.append(f"| {n} | {nd.real_value:g} | {nd.mean:.1f} | {nd.p99:.1f} | {nd.real_percentile:.1f} |")
    lines += [
        "",
        "### Grammar-match null under the list-tiebreak ordering, version 2",
        "",
        "| n | real | null mean | p99 | real percentile |",
        "|---:|---:|---:|---:|---:|",
    ]
    for n, nd in sorted(list_tiebreak_report.grammar_match_null_list_tiebreak_v2.items()):
        lines.append(f"| {n} | {nd.real_value:g} | {nd.mean:.1f} | {nd.p99:.1f} | {nd.real_percentile:.1f} |")
    lines += [
        "",
        f"Top-three-all-matched chance rate, version 1: "
        f"{list_tiebreak_report.top_three_all_matched_chance_rate_v1:.3f}",
        "",
        f"Top-three-all-matched chance rate, version 2: "
        f"{list_tiebreak_report.top_three_all_matched_chance_rate_v2:.3f}",
        "",
    ]
    return "\n".join(lines)


def _results_path(corpus: str, seed: int, tag: str = "", results_dir: Path | None = None) -> Path:
    return (results_dir if results_dir is not None else _RESULTS_DIR) / f"kober-{corpus}-seed{seed}{tag}.json"


def write_report(
    report: KoberReport,
    grid_report: GridReport | None = None,
    anchored_grid_report: AnchoredGridReport | None = None,
    alternation_grid_report: AlternationGridReport | None = None,
    tag: str = "",
    subsample_docs: dict | None = None,
    results_dir: Path | None = None,
    context_report: ContextReport | None = None,
    role_tiebreak_report: RoleTiebreakReport | None = None,
    list_tiebreak_report: ListTiebreakReport | None = None,
    medial_report: MedialReport | None = None,
) -> Path:
    """Write the results JSON. ``tag`` (e.g. ``-sub988-s3`` or ``-docs512-s3``) is
    appended to the filename so a ``--subsample`` or ``--subsample-docs`` run never
    overwrites the untagged full-corpus results for the same corpus and seed.
    ``subsample_docs``, when given, is the document-subsample metadata (requested
    count, seed, documents actually used) from a ``--subsample-docs`` run; the
    resulting word-type count is already in ``word_types.count`` either way.
    ``results_dir``, when given, replaces the default ``results/`` directory (e.g.
    ``results/kober-grammar-null/`` for TODO item 8's prerequisite-1 runs), so a
    rerun of an existing corpus/seed/tag combination for a different purpose does
    not overwrite the original file there; the filename itself is unchanged."""
    path = _results_path(report.corpus, report.seed, tag, results_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    d = report.as_dict()
    if grid_report is not None:
        d["grid"] = grid_report.as_dict()
    if anchored_grid_report is not None:
        d["grid_anchored"] = anchored_grid_report.as_dict()
    if alternation_grid_report is not None:
        d["grid_alternations"] = alternation_grid_report.as_dict()
    if subsample_docs is not None:
        d["subsample_docs"] = subsample_docs
    if context_report is not None:
        d["context"] = context_report.as_dict()
    if role_tiebreak_report is not None:
        d["role_tiebreak"] = role_tiebreak_report.as_dict()
    if list_tiebreak_report is not None:
        d["list_tiebreak"] = list_tiebreak_report.as_dict()
    if medial_report is not None:
        d["medial"] = medial_report.as_dict()
    d["protocol_version"] = _bumped_protocol_version(
        d["protocol_version"],
        grid_report,
        anchored_grid_report,
        alternation_grid_report,
        context_report,
        role_tiebreak_report,
        list_tiebreak_report,
        medial_report,
        report.merge_homophones,
    )
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return path


def _fmt_nd(nd: NullDistribution) -> str:
    return (
        f"real {nd.real_value:g} (percentile {nd.real_percentile:.1f}), "
        f"null mean {nd.mean:.1f} sd {nd.sd:.1f}, p95 {nd.p95:.1f}, p99 {nd.p99:.1f}"
    )


def _fmt_alt_table(entries: list[dict]) -> str:
    lines = ["| rank | endings | support | rule |", "|---:|---|---:|---|"]
    for i, e in enumerate(entries, 1):
        rule = e["rule"] or "-"
        lines.append(f"| {i} | {e['e1_label']} / {e['e2_label']} | {e['support']} | {rule} |")
    return "\n".join(lines)


def render_context_markdown(context_report: ContextReport) -> str:
    n1c = context_report.n1_context
    n2c = context_report.n2_context
    lines = [
        "## Context (stage 0.4)",
        "",
        "### Class census",
        "",
        "| support type | line-initial | next kind | word types |",
        "|---|---|---|---:|",
    ]
    for row in context_report.as_dict()["class_census"]:
        lines.append(
            f"| {row['support_type']} | {row['line_initial']} | {row['next_kind']} | {row['count']} |"
        )
    lines += [
        "",
        f"Context-restricted paradigm count: {context_report.ending_context.paradigm_count_total}.",
        "",
        f"N1 stratified (paradigm count null): {_fmt_nd(n1c.ending_paradigm_count)}",
        "",
        f"N2 stratified max alternation support: {_fmt_nd(n2c.max_support)}",
        "",
        f"N2 stratified tenth-highest alternation support: {_fmt_nd(n2c.tenth_support)}",
        "",
        f"Top-three-all-matched chance rate under the stratified N2: "
        f"{n2c.top_three_all_matched_chance_rate:.3f}",
        "",
        "### Real strict top ten (context-restricted)",
        "",
        _fmt_alt_table(context_report.top_10),
        "",
    ]
    return "\n".join(lines)


def render_markdown(
    report: KoberReport,
    grid_report: GridReport | None = None,
    anchored_grid_report: AnchoredGridReport | None = None,
    alternation_grid_report: AlternationGridReport | None = None,
    context_report: ContextReport | None = None,
    role_tiebreak_report: RoleTiebreakReport | None = None,
    list_tiebreak_report: ListTiebreakReport | None = None,
    medial_report: MedialReport | None = None,
) -> str:
    n1 = report.nulls.n1
    n2e = report.nulls.n2_ending
    n2p = report.nulls.n2_prefix
    file_version = _bumped_protocol_version(
        BASE_PROTOCOL_VERSION,
        grid_report,
        anchored_grid_report,
        alternation_grid_report,
        context_report,
        role_tiebreak_report,
        list_tiebreak_report,
        medial_report,
        report.merge_homophones,
    )
    parts = [
        f"# Kober method {file_version} — {report.corpus}, seed {report.seed}",
        "",
        f"Word types: {len(report.word_types.words)} "
        f"(labels changed by normalisation: {report.word_types.labels_changed} of "
        f"{report.word_types.labels_seen}). stem_min {report.stem_min}, {report.perms} draws per null."
        + (" Homophones merged (Kober 0.9)." if report.merge_homophones else ""),
        "",
        "## Ending channel",
        "",
        f"Paradigm count: {report.ending.paradigm_count_total} total, by stem length "
        f"{dict(sorted(report.ending.paradigm_count_by_stem_length.items()))}.",
        "",
        f"N1 (paradigm count null): {_fmt_nd(n1.ending_paradigm_count)}",
        "",
        f"N2 max alternation support: {_fmt_nd(n2e.max_support)}",
        "",
        f"N2 tenth-highest alternation support: {_fmt_nd(n2e.tenth_support)}",
        "",
        f"Top-10 alternations matched to a reference rule: "
        f"{sum(1 for a in report.ending_alternations[:10] if a['rule'] is not None)} of 10",
        "",
        "### Top 20 ending alternations",
        "",
        _fmt_alt_table(report.ending_alternations),
        "",
        "## Prefix channel",
        "",
        f"Paradigm count: {report.prefix.paradigm_count_total} total, by stem length "
        f"{dict(sorted(report.prefix.paradigm_count_by_stem_length.items()))}.",
        "",
        f"N1 (paradigm count null): {_fmt_nd(n1.prefix_paradigm_count)}",
        "",
        f"N2 max alternation support: {_fmt_nd(n2p.max_support)}",
        "",
        f"N2 tenth-highest alternation support: {_fmt_nd(n2p.tenth_support)}",
        "",
        f"Top-10 alternations matched to a reference rule: "
        f"{sum(1 for a in report.prefix_alternations[:10] if a['rule'] is not None)} of 10",
        "",
        "### Top 20 prefix alternations",
        "",
        _fmt_alt_table(report.prefix_alternations),
        "",
        f"N1 null type count: mean {n1.type_count_mean:.1f}, sd {n1.type_count_sd:.1f}.",
        "",
    ]
    if grid_report is not None:
        parts.append(render_grid_markdown(grid_report))
    if anchored_grid_report is not None:
        parts.append(render_anchored_grid_markdown(anchored_grid_report))
    if alternation_grid_report is not None:
        parts.append(render_alternation_grid_markdown(alternation_grid_report))
    if context_report is not None:
        parts.append(render_context_markdown(context_report))
    if role_tiebreak_report is not None:
        parts.append(render_role_tiebreak_markdown(role_tiebreak_report))
    if list_tiebreak_report is not None:
        parts.append(render_list_tiebreak_markdown(list_tiebreak_report))
    if medial_report is not None:
        parts.append(render_medial_markdown(medial_report))
    return "\n".join(parts)
