"""Kober method gates: word-type count, null invariants, reference rules.

Run: ``.venv/bin/python -m pytest tests/test_kober.py -q``
(or ``.venv/bin/python tests/test_kober.py``).
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aegean  # noqa: E402
from aegean.core.model import Document, DocumentMeta, ReadingStatus, Token, TokenKind  # noqa: E402

from kober.context import extract_word_contexts  # noqa: E402
from kober.grid import (  # noqa: E402
    alternation_bridging_pairs,
    anchored_stems,
    bridging_pairs,
    build_alternation_grid_report,
    build_grid,
    consonant_fraction,
    consonant_fraction_from_pairs,
    top_n_alternations_with_ties,
)
from kober.lists import DocListing, extract_listed_words, homogeneous_forms_from_listings  # noqa: E402
from kober.medial import (  # noqa: E402
    build_medial_report,
    medial_pairs,
    ranked_medial_pairs,
)
from kober.nulls import (  # noqa: E402
    GRAMMAR_MATCH_NS,
    grammar_matched_count,
    grammar_matched_count_strict,
    n1_draw,
    n2_draw,
    n2_draw_stratified,
    n3_draw,
    run_n2,
    run_n2_context,
    top_three_all_matched,
)
from kober.paradigms import (  # noqa: E402
    build_channel_context_restricted,
    ending_channel,
    ending_channel_context_restricted,
    list_support_counts,
    ranked_alternations,
    role_sharing_counts,
)
from kober.reference import RULE_NAMES_V3, is_grammar  # noqa: E402
from kober.report import build_list_tiebreak_report, build_role_tiebreak_report, build_report  # noqa: E402
from kober.roles import word_roles  # noqa: E402
from kober.values import consonant_of  # noqa: E402
from kober.words import (  # noqa: E402
    HOMOPHONE_MERGE_MAP,
    extract_word_types,
    restrict_to_shared,
    subsample_document_ids,
    subsample_word_types,
)

_CORPUS = None
_SIGLA_CORPUS = None
_LINEARA_CORPUS = None


def corpus():
    global _CORPUS
    if _CORPUS is None:
        _CORPUS = aegean.load("damos")
    return _CORPUS


def sigla_corpus():
    global _SIGLA_CORPUS
    if _SIGLA_CORPUS is None:
        _SIGLA_CORPUS = aegean.load("sigla")
    return _SIGLA_CORPUS


def lineara_corpus():
    global _LINEARA_CORPUS
    if _LINEARA_CORPUS is None:
        _LINEARA_CORPUS = aegean.load("lineara")
    return _LINEARA_CORPUS


# --------------------------------------------------------------------------- #
# Word-type count, pinned
# --------------------------------------------------------------------------- #


def test_linear_b_word_type_count_pinned():
    """Measured 2026-09-11: CERTAIN WORD tokens, normalised, >= 2 signs, 3768 types.

    Down from the unnormalised sizing figure of 4,263 in kober-method.md because
    normalisation merges underdotted sign-label variants with their plain form
    (ṬỌ -> TO) before the word set is built, so pairs that were counted as two
    distinct word types collapse into one.
    """
    wt = extract_word_types(corpus().documents)
    assert len(wt.words) == 3768


def test_labels_changed_is_a_true_subset_of_labels_seen():
    wt = extract_word_types(corpus().documents)
    assert 0 < wt.labels_changed < wt.labels_seen


def test_sigla_word_type_count_pinned():
    """Measured 2026-09-11 (sigla-dividers-report.md feasibility check): the same
    Kober-method filter (CERTAIN WORD tokens, normalised, >= 2 signs, by type) run
    on SigLA's own word division gives 692 types, against GORILA's 988."""
    wt = extract_word_types(sigla_corpus().documents)
    assert len(wt.words) == 692


# --------------------------------------------------------------------------- #
# Shared-types restriction across editions (A-002, "Segmentation sensitivity on
# Linear A"): GORILA and SigLA word types, restricted to what both editions
# attest as an identical normalised sign tuple.
# --------------------------------------------------------------------------- #


def test_shared_word_types_between_editions_pinned():
    """Measured 2026-09-11: 577 word types are identical sign tuples in both
    GORILA's and SigLA's extracted word-type sets."""
    gorila = extract_word_types(lineara_corpus().documents)
    sigla = extract_word_types(sigla_corpus().documents)
    shared = gorila.words & sigla.words
    assert len(shared) == 577


def test_restrict_to_shared_is_symmetric_between_editions():
    """The intersection does not depend on which corpus is primary: restricting
    GORILA's word types to what SigLA also has, and restricting SigLA's to what
    GORILA also has, yield the same frozenset of words."""
    gorila = extract_word_types(lineara_corpus().documents)
    sigla = extract_word_types(sigla_corpus().documents)
    gorila_restricted = restrict_to_shared(gorila, sigla.words)
    sigla_restricted = restrict_to_shared(sigla, gorila.words)
    assert gorila_restricted.words == sigla_restricted.words
    assert len(gorila_restricted.words) == 577


def test_restrict_to_shared_carries_labels_from_the_primary_corpus():
    gorila = extract_word_types(lineara_corpus().documents)
    sigla = extract_word_types(sigla_corpus().documents)
    restricted = restrict_to_shared(gorila, sigla.words)
    assert restricted.labels_changed == gorila.labels_changed
    assert restricted.labels_seen == gorila.labels_seen


# --------------------------------------------------------------------------- #
# Subsampling (A-057, A-058)
# --------------------------------------------------------------------------- #


def test_subsample_word_types_has_the_requested_size():
    wt = extract_word_types(corpus().documents)
    sub = subsample_word_types(wt, n=988, seed=0)
    assert len(sub.words) == 988
    assert sub.words <= wt.words


def test_subsample_word_types_is_deterministic_under_a_seed():
    wt = extract_word_types(corpus().documents)
    a = subsample_word_types(wt, n=988, seed=3)
    b = subsample_word_types(wt, n=988, seed=3)
    assert a.words == b.words


def test_subsample_word_types_differs_across_seeds():
    wt = extract_word_types(corpus().documents)
    a = subsample_word_types(wt, n=988, seed=0)
    b = subsample_word_types(wt, n=988, seed=1)
    assert a.words != b.words


def test_subsample_word_types_carries_label_counts_through_unchanged():
    wt = extract_word_types(corpus().documents)
    sub = subsample_word_types(wt, n=988, seed=0)
    assert sub.labels_changed == wt.labels_changed
    assert sub.labels_seen == wt.labels_seen


# --------------------------------------------------------------------------- #
# Document subsampling (the "tablet model", CHANGELOG "Floor sweep on Linear B")
# --------------------------------------------------------------------------- #


def test_subsample_document_ids_is_deterministic_under_a_seed():
    ids = [d.id for d in corpus().documents]
    a = subsample_document_ids(ids, n=50, seed=3)
    b = subsample_document_ids(ids, n=50, seed=3)
    assert a == b


def test_subsample_document_ids_differs_across_seeds():
    ids = [d.id for d in corpus().documents]
    a = subsample_document_ids(ids, n=50, seed=0)
    b = subsample_document_ids(ids, n=50, seed=1)
    assert a != b


def test_subsample_document_ids_has_the_requested_size():
    ids = [d.id for d in corpus().documents]
    chosen = subsample_document_ids(ids, n=50, seed=0)
    assert len(chosen) == 50
    assert set(chosen) <= set(ids)


def test_subsample_documents_type_count_no_larger_than_full_corpus():
    full = extract_word_types(corpus().documents)
    ids = [d.id for d in corpus().documents]
    chosen = subsample_document_ids(ids, n=50, seed=0)
    subset = corpus().subset(chosen)
    sub = extract_word_types(subset.documents)
    assert sub.words <= full.words
    assert len(sub.words) <= len(full.words)


def test_subsample_document_ids_is_nested_across_n_at_a_fixed_seed():
    """Bisection on document count needs a prefix relationship: the smaller draw
    must be a subset of the larger one at the same seed, so the resulting
    word-type count is non-decreasing in n (A-063)."""
    ids = [d.id for d in corpus().documents]
    small = subsample_document_ids(ids, n=20, seed=0)
    large = subsample_document_ids(ids, n=80, seed=0)
    assert set(small) <= set(large)


def test_subsample_documents_type_count_is_reproducible_for_a_seed():
    ids = [d.id for d in corpus().documents]
    chosen_a = subsample_document_ids(ids, n=50, seed=7)
    chosen_b = subsample_document_ids(ids, n=50, seed=7)
    wt_a = extract_word_types(corpus().subset(chosen_a).documents)
    wt_b = extract_word_types(corpus().subset(chosen_b).documents)
    assert wt_a.words == wt_b.words


# --------------------------------------------------------------------------- #
# N1: position-matched shuffle preserves length distribution and positional
# sign frequency. Test words are built so no two words in the same length class
# can ever collide after an independent per-position shuffle (position 0 is
# unique per word within its class), so the drawn set's size, and hence every
# positional frequency, is checkable exactly rather than approximately.
# --------------------------------------------------------------------------- #

_N1_WORDS = [
    ("W1", "X", "Y"),
    ("W2", "X", "Z"),
    ("W3", "Q", "Y"),
    ("W4", "Q", "Z"),
    ("V1", "M", "N", "P"),
    ("V2", "M", "N", "Q"),
    ("V3", "K", "L", "P"),
]


def test_n1_preserves_length_distribution():
    rng = random.Random(0)
    drawn = n1_draw(_N1_WORDS, rng)
    assert Counter(len(w) for w in drawn) == Counter(len(w) for w in _N1_WORDS)


def test_n1_preserves_positional_sign_frequency():
    rng = random.Random(0)
    drawn = n1_draw(_N1_WORDS, rng)
    for n in {len(w) for w in _N1_WORDS}:
        original = [w for w in _N1_WORDS if len(w) == n]
        result = [w for w in drawn if len(w) == n]
        assert len(result) == len(original), "position-0 uniqueness should prevent collapse"
        for i in range(n):
            assert Counter(w[i] for w in result) == Counter(w[i] for w in original)


def test_n1_is_deterministic_under_a_seed():
    a = n1_draw(_N1_WORDS, random.Random(7))
    b = n1_draw(_N1_WORDS, random.Random(7))
    assert a == b


# --------------------------------------------------------------------------- #
# N2: ending shuffle preserves the multiset of stems per length class. Heads
# (the fixed part) are unique per word within a class, so again no collision is
# possible and the stem multiset can be checked exactly.
# --------------------------------------------------------------------------- #

_N2_WORDS = [
    ("S1", "S1B", "E1"),
    ("S2", "S2B", "E2"),
    ("S3", "S3B", "E3"),
    ("H1", "H1B", "T1", "T1B"),
    ("H2", "H2B", "T2", "T2B"),
    ("H3", "H3B", "T3", "T3B"),
]


def test_n2_preserves_stem_multiset_per_length_class():
    rng = random.Random(0)
    drawn = n2_draw(_N2_WORDS, stem_min=2, rng=rng, mirror=False)
    for n in {len(w) for w in _N2_WORDS}:
        k = min(2, n - 2)
        original = [w for w in _N2_WORDS if len(w) == n]
        result = [w for w in drawn if len(w) == n]
        assert len(result) == len(original)
        assert Counter(w[: n - k] for w in result) == Counter(w[: n - k] for w in original)


def test_n2_mirror_preserves_base_multiset_per_length_class():
    """The prefix-channel mirror null holds the base (word-final run) fixed instead."""
    rng = random.Random(0)
    drawn = n2_draw(_N2_WORDS, stem_min=2, rng=rng, mirror=True)
    for n in {len(w) for w in _N2_WORDS}:
        k = min(2, n - 2)
        original = [w for w in _N2_WORDS if len(w) == n]
        result = [w for w in drawn if len(w) == n]
        assert len(result) == len(original)
        assert Counter(w[k:] for w in result) == Counter(w[k:] for w in original)


def test_n2_leaves_words_too_short_to_split_unchanged():
    """A-043: a length class with n - stem_min < 1 has nothing shuffleable."""
    words = [("A", "B")]  # n=2, stem_min=2 -> n - stem_min == 0
    rng = random.Random(0)
    drawn = n2_draw(words, stem_min=2, rng=rng, mirror=False)
    assert drawn == frozenset(words)


# --------------------------------------------------------------------------- #
# Reference grammar rules
# --------------------------------------------------------------------------- #

_GRAMMAR_PAIRS = [
    (("JO",), ("JA",)),
    (("TO",), ("TA",)),
    (("RO",), ("RO", "JO")),
    (("U",), ("WE",)),
    (("ME", "NO"), ("ME", "NA")),
    (("KE",), ("KO", "SI")),
    (("RA",), ("RA", "QE")),
    (("SI", "JO"), ("SI", "JA")),
    (("TA",), ("TA", "I")),
]

_NON_GRAMMAR_PAIRS = [
    (("KU",), ("MA",)),
    (("SE",), ("TA",)),
    (("JO",), ("QE",)),
]


def test_is_grammar_matches_reference_pairs():
    for e1, e2 in _GRAMMAR_PAIRS:
        assert is_grammar(e1, e2) is not None, f"{e1} / {e2} should match a rule"


def test_is_grammar_rejects_non_grammar_pairs():
    for e1, e2 in _NON_GRAMMAR_PAIRS:
        assert is_grammar(e1, e2) is None, f"{e1} / {e2} should not match any rule"


def test_is_grammar_is_order_independent():
    for e1, e2 in _GRAMMAR_PAIRS:
        assert is_grammar(e1, e2) == is_grammar(e2, e1)


# --------------------------------------------------------------------------- #
# Kober 0.6: rule 11, ethnic derivation (CHANGELOG "0.6")
# --------------------------------------------------------------------------- #

_ETHNIC_DERIVATION_PAIRS = [
    (("SO",), ("SI", "JO")),
    (("TO",), ("TI", "JA")),
    (("KO",), ("KI", "JO")),
]


def test_ethnic_derivation_matches_only_under_version_2():
    for e1, e2 in _ETHNIC_DERIVATION_PAIRS:
        assert is_grammar(e1, e2) is None, f"{e1} / {e2} should not match any v1 rule"
        assert is_grammar(e1, e2, version=1) is None
        assert is_grammar(e1, e2, version=2) == "ethnic_derivation"
        assert is_grammar(e2, e1, version=2) == "ethnic_derivation"


def test_ethnic_derivation_requires_same_consonant():
    # -so / -sa-jo: Ci ("SA") has the wrong vowel (a, not i), so no rule fires
    # under either version even though Co and Ci share a consonant.
    e1, e2 = ("SO",), ("SA", "JO")
    assert is_grammar(e1, e2) is None
    assert is_grammar(e1, e2, version=2) is None


def test_is_grammar_version_1_default_matches_existing_reference_pairs():
    """Existing rule tests are unaffected: version=1 (the default) reproduces
    the pre-0.6 behaviour exactly."""
    for e1, e2 in _GRAMMAR_PAIRS:
        assert is_grammar(e1, e2) == is_grammar(e1, e2, version=1)
    for e1, e2 in _NON_GRAMMAR_PAIRS:
        assert is_grammar(e1, e2) == is_grammar(e1, e2, version=1)


# --------------------------------------------------------------------------- #
# Kober 0.8: reference list version 3, rules 12 to 22 (CHANGELOG "0.8")
# --------------------------------------------------------------------------- #


def _w(word: str) -> tuple[str, ...]:
    """A hyphenated Linear B transliteration ('e-ke-e') to a sign-label tuple
    (('E', 'KE', 'E')), matching how endings/words are represented everywhere
    else in this module."""
    return tuple(part.upper() for part in word.split("-"))


# The chapter's own paradigm forms CHANGELOG "0.8" requires to pass under v3.
# Whole words are passed directly as e1/e2 -- is_grammar's rules operate on any
# Word tuple, not only on the 1- or 2-sign endings the paradigm splitter
# produces, exactly as the pre-existing rules (3, 4, 5, 6, 7...) already do.
_V3_REQUIRED_PASS_PAIRS = [
    ("ko-to-na", "ko-to-na-o"),
    ("te-o", "te-o-jo"),
    ("po-me-ne", "po-me-no"),
    ("wa-na-ka", "wa-na-ka-te"),
    ("pa-we-a", "pa-we-a2"),
    ("ta-ra-nu", "ta-ra-nu-we"),
    ("ka-ke-u", "ka-ke-u-si"),
    ("ko-ma-we", "ko-ma-we-to"),
    ("e-o", "e-o-te"),
    ("e-ke", "e-ke-e"),
    ("i-je-re-u", "i-je-re-ja"),
    ("wi-ri-ne-jo", "wi-ri-ni-jo"),
    ("a-mi-ni-so", "a-mi-ni-si-jo"),
]

_V3_REQUIRED_REJECT_PAIRS = [("ku", "ma"), ("se", "ta"), ("jo", "qe")]


def test_v3_matches_every_required_pass_pair():
    for a, b in _V3_REQUIRED_PASS_PAIRS:
        e1, e2 = _w(a), _w(b)
        assert is_grammar(e1, e2, version=3) is not None, f"{a} / {b} should match a v3 rule"
        assert is_grammar(e2, e1, version=3) == is_grammar(e1, e2, version=3)


def test_v3_rejects_every_required_reject_pair():
    for a, b in _V3_REQUIRED_REJECT_PAIRS:
        e1, e2 = _w(a), _w(b)
        assert is_grammar(e1, e2, version=3) is None, f"{a} / {b} should not match any v3 rule"


def test_v1_and_v2_unchanged_on_required_v3_pairs():
    """v1 and v2 must not have grown a new match from the v3 rules leaking
    into their rule lists: on every pair above, v1's result stays inside the
    pre-0.6 rule names and v2's stays inside the pre-0.8 (v1 + rule 11) names,
    never one of the eleven new v3-only rule names."""
    from kober.reference import RULE_NAMES, RULE_NAMES_V2  # noqa: PLC0415

    v3_only_names = set(RULE_NAMES_V3) - set(RULE_NAMES_V2)
    assert len(v3_only_names) == 11
    for a, b in _V3_REQUIRED_PASS_PAIRS + _V3_REQUIRED_REJECT_PAIRS:
        for e1, e2 in ((_w(a), _w(b)), (_w(b), _w(a))):
            v1_result = is_grammar(e1, e2, version=1)
            assert v1_result is None or v1_result in RULE_NAMES
            v2_result = is_grammar(e1, e2, version=2)
            assert v2_result is None or v2_result in RULE_NAMES_V2
            assert v2_result not in v3_only_names


_V3_NAMED_RULE_PAIRS = [
    ("po-me-ne", "po-me-no", "consonant_stem_case"),
    ("pa-we-a", "pa-we-a2", "s_stem"),
    ("ta-ra-nu", "ta-ra-nu-we", "u_stem"),
    ("i-je-re-u", "i-je-re-ja", "feminine_of_eus"),
    ("wi-ri-ne-jo", "wi-ri-ni-jo", "material_adjective"),
]


def test_v3_named_rules_fire_as_expected():
    """Pairs whose matching rule is not shadowed by an earlier rule (1 to 11,
    or 13/14 -- see A-124) fire under their own name."""
    for a, b, rule in _V3_NAMED_RULE_PAIRS:
        e1, e2 = _w(a), _w(b)
        assert is_grammar(e1, e2, version=3) == rule


def test_rule22_consonant_stem_suffix_directly():
    # wa-na-ka-te's TE also matches the pre-existing particle rule (10, TE is
    # an enclitic sign) first, so the required-pass test above sees "particle",
    # not "consonant_stem_suffix" -- exercise rule 13 on a suffix particle
    # does not shadow (DA), confirming the rule itself works standalone.
    e1, e2 = _w("wa-na-ka"), _w("wa-na-ka-da")
    assert is_grammar(e1, e2, version=3) == "consonant_stem_suffix"


def test_rule21_material_adjective_rejects_unrelated_two_sign_endings():
    # (SI, JO) / (SI, JA) is rule 1 (gender: same consonant J, vowels o/a),
    # tried well before rule 21, so rule 21 is never reached for it.
    e1, e2 = _w("si-jo"), _w("si-ja")
    assert is_grammar(e1, e2, version=3) == "gender"


def test_rule22_does_not_reach_ra2_ri_ja_length_mismatch():
    """A-123: a-ke-ti-ra2 / a-ke-ti-ri-ja is CHANGELOG '0.8' rule 22's other
    cited example (pp. 46-47) but is not in the 'tests must pass' list. RA2
    (one sign) stands for the two-sign spelling RI-JA, so the two endings
    differ in length (4 against 5) and rule 22's elementwise comparison does
    not reach them -- a disclosed limitation, not a bug to bend the rule for."""
    e1, e2 = _w("a-ke-ti-ra2"), _w("a-ke-ti-ri-ja")
    assert is_grammar(e1, e2, version=3) is None


def test_rules_16_to_19_are_unreachable_given_the_fixed_order():
    """A-124: rules 16 (eu-stem plural), 17 (-went-), 18 (participle plural)
    and 19 (infinitive) are each fully preempted by an earlier, broader rule
    (10 particle, 13 consonant-stem suffix, 14 s-stem) under the fixed rule
    order, so they never surface as the reported name -- confirmed directly
    on the chapter's own forms for each."""
    assert is_grammar(_w("ka-ke-u"), _w("ka-ke-u-si"), version=3) == "consonant_stem_suffix"  # not eu_stem_plural
    assert is_grammar(_w("ko-ma-we"), _w("ko-ma-we-to"), version=3) == "consonant_stem_suffix"  # not went
    assert is_grammar(_w("e-o"), _w("e-o-te"), version=3) == "particle"  # not participle_plural
    assert is_grammar(_w("e-ke"), _w("e-ke-e"), version=3) == "s_stem"  # not infinitive


# --------------------------------------------------------------------------- #
# Stage 2, the grid: consonant_of (values.py), bridging pairs, the fraction,
# and union-find classes (grid.py)
# --------------------------------------------------------------------------- #


def test_consonant_of_known_examples():
    assert consonant_of("A") == ""  # pure vowel
    assert consonant_of("TO") == "T"
    assert consonant_of("RA2") == "R"  # trailing digit stripped, then RA -> R
    assert consonant_of("TWO") == "TW"  # remainder longer than one letter, kept whole
    assert consonant_of("JO") == "J"
    assert consonant_of("*18") is None  # excluded: unidentified sign


# A stem is written as its own two-sign run (X1, X2) so it satisfies stem_min 2
# on its own, matching how paradigms.py's ending channel is actually built;
# "X-SO" in the design page's shorthand is the word (X1, X2, SO), and so on.
_GRID_WORDS = [
    ("X1", "X2", "SO"),  # X-SO
    ("X1", "X2", "SI", "JO"),  # X-SI-JO
    ("X1", "X2", "SI", "JA"),  # X-SI-JA
    ("Y1", "Y2", "TA"),  # Y-TA
    ("Y1", "Y2", "TO"),  # Y-TO
]


def test_bridging_pairs_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    pairs = bridging_pairs(channel)
    assert pairs[("SI", "SO")] == 1  # stem (X1, X2): SO vs SI-JO, SO vs SI-JA -> one stem
    assert pairs[("TA", "TO")] == 1  # stem (Y1, Y2)
    assert ("SI", "SI") not in pairs  # same first sign is not a bridging pair


def test_bridging_pairs_support_counts_stems_not_ending_pairs():
    # Stem (X1, X2) has three endings (SO, SI-JO, SI-JA); SO differs from both
    # SI-endings, but that is still one stem, so support stays 1, not 2.
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    pairs = bridging_pairs(channel)
    assert pairs[("SI", "SO")] == 1


def test_consonant_fraction_on_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    pairs = bridging_pairs(channel)
    # SO/T and TA/TO share no consonant issue: SO -> "S", SI -> "S" (share);
    # TA -> "T", TO -> "T" (share). Both pairs at k=1 share a consonant.
    frac = consonant_fraction(pairs, k=1)
    assert frac.scored_count == frac.pair_count  # no excluded signs among SO/SI/TA/TO
    assert frac.shared_count == frac.pair_count
    assert frac.fraction == 1.0


def test_build_grid_union_find_on_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    pairs = bridging_pairs(channel)
    classes = build_grid(pairs, min_support=1)
    by_signs = {c.signs: c for c in classes}
    assert ("SI", "SO") in by_signs
    assert by_signs[("SI", "SO")].pure  # S and S: one consonant
    assert ("TA", "TO") in by_signs
    assert by_signs[("TA", "TO")].pure  # T and T: one consonant


# --------------------------------------------------------------------------- #
# Stage 2 version 0.2, anchored bridging pairs (A-053 to A-056)
# --------------------------------------------------------------------------- #

# Two stems (X1,X2) and (W1,W2) both attest the SO / SI-JO alternation, giving
# it support 2, the corpus maximum; (X1,X2) also attests SI-JO / SI-JA, and
# (Y1,Y2) attests an unrelated TA / TO alternation, both at support 1. With
# top_n=1 (no ties at the top), only the SO/SI-JO alternation anchors a stem.
_ANCHOR_WORDS = [
    ("X1", "X2", "SO"),  # X-SO
    ("X1", "X2", "SI", "JO"),  # X-SI-JO
    ("X1", "X2", "SI", "JA"),  # X-SI-JA
    ("W1", "W2", "SO"),  # W-SO
    ("W1", "W2", "SI", "JO"),  # W-SI-JO
    ("Y1", "Y2", "TA"),  # Y-TA
    ("Y1", "Y2", "TO"),  # Y-TO
]


def test_anchored_stems_keeps_top_alternation_stems():
    channel = ending_channel(_ANCHOR_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=1)
    # The SI-JO / SO alternation (support 2) is the sole top-1 alternation.
    # Key order follows paradigms.py: combinations of the endings sorted as
    # tuples, so ("SI", "JO") precedes ("SO",).
    assert top_alts == {(("SI", "JO"), ("SO",))}
    stems = anchored_stems(channel, top_alts)
    assert stems == {("X1", "X2"), ("W1", "W2")}
    assert ("Y1", "Y2") not in stems


def test_anchoring_keeps_paradigmatic_pairs_drops_unanchored_stem_pair():
    channel = ending_channel(_ANCHOR_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=1)
    stems = anchored_stems(channel, top_alts)
    all_pairs = bridging_pairs(channel)
    anchored_pairs = bridging_pairs(channel, stems=stems)
    # Unrestricted, both the paradigmatic (SI, SO) pair and the unrelated
    # (TA, TO) pair (from the stem supporting no top alternation) appear.
    assert all_pairs[("SI", "SO")] == 2
    assert all_pairs[("TA", "TO")] == 1
    # Anchored to the top alternation, the paradigmatic pair is kept in full
    # (both contributing stems qualify) and the unanchored stem's pair drops.
    assert anchored_pairs[("SI", "SO")] == 2
    assert ("TA", "TO") not in anchored_pairs


def test_top_n_alternations_with_ties_includes_tenth_place_ties():
    # Four alternations tied at support 1: n=2 should still include all four,
    # since the second-place value (1) ties with the third and fourth.
    support = {
        (("A",), ("B",)): 1,
        (("C",), ("D",)): 1,
        (("E",), ("F",)): 1,
        (("G",), ("H",)): 1,
    }
    top = top_n_alternations_with_ties(support, n=2)
    assert top == frozenset(support.keys())


# --------------------------------------------------------------------------- #
# Stage 2 version 0.3, bridging pairs from the alternations themselves
# (A-059 onward). Reuses _GRID_WORDS. Its ending channel has three paradigms:
# stem (X1, X2) with three endings (SO, SI-JO, SI-JA), giving the alternations
# SO/SI-JO and SO/SI-JA (first signs SO/SI, differ) and SI-JO/SI-JA (first
# signs SI/SI, the same-first-sign case); stem (X1, X2, SI), from each SI-word's
# own one-sign split, with endings JO and JA (first signs JO/JA, differ); and
# stem (Y1, Y2) with TA/TO (first signs TA/TO, differ). Five alternations in
# total, all tied at support 1, so a top_n of 10 selects all of them.
# --------------------------------------------------------------------------- #


def test_alternation_bridging_pairs_on_grid_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=10)
    assert len(top_alts) == 5  # every alternation in this toy set ties at support 1
    pairs = alternation_bridging_pairs(top_alts)
    # SO/SI-JO and SO/SI-JA both yield the pair (SI, SO): one entry per
    # alternation, not deduplicated, so the pair appears twice.
    assert sorted(pairs) == sorted([("JA", "JO"), ("SI", "SO"), ("SI", "SO"), ("TA", "TO")])


def test_alternation_bridging_pairs_drops_same_first_sign_alternation():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=10)
    assert (("SI", "JA"), ("SI", "JO")) in top_alts  # the same-first-sign alternation is present
    pairs = alternation_bridging_pairs(top_alts)
    assert ("SI", "SI") not in pairs
    # 5 alternations in, 4 pairs out: SI-JO/SI-JA (both first sign SI) yields none.
    assert len(pairs) == 4


def test_alternation_consonant_fraction_on_grid_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=10)
    pairs = alternation_bridging_pairs(top_alts)
    frac = consonant_fraction_from_pairs(pairs)
    assert frac.pair_count == 4
    assert frac.excluded_count == 0
    assert frac.scored_count == 4
    assert frac.shared_count == 4  # SI/SO -> S (x2), JA/JO -> J, TA/TO -> T: all share
    assert frac.fraction == 1.0


def test_alternation_grid_classes_on_grid_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    top_alts = top_n_alternations_with_ties(channel.alternation_support, n=10)
    pairs = alternation_bridging_pairs(top_alts)
    classes = build_grid(Counter(pairs), min_support=1)
    by_signs = {c.signs: c for c in classes}
    assert ("SI", "SO") in by_signs
    assert by_signs[("SI", "SO")].pure
    assert ("JA", "JO") in by_signs
    assert by_signs[("JA", "JO")].pure
    assert ("TA", "TO") in by_signs
    assert by_signs[("TA", "TO")].pure
    assert len(classes) == 3


# --------------------------------------------------------------------------- #
# Grammar-match null (CHANGELOG "Null rate of the grammar match, and precision
# criteria"; TODO item 8, prerequisite 1). Reuses _GRID_WORDS: its ending
# channel has five alternations, all tied at support 1 (see the comment above
# test_alternation_bridging_pairs_on_grid_toy_set), of which three match a
# reference rule: (SI,JA)/(SI,JO) is rule 2 (adjective), (JA,)/(JO,) and
# (TA,)/(TO,) are both rule 1 (gender).
# --------------------------------------------------------------------------- #


def test_grammar_matched_count_real_top3_on_grid_toy_set():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    # All five alternations tie at support 1, so top-3-with-ties (A-053)
    # expands to all five; three of them match a reference rule.
    assert grammar_matched_count(channel.alternation_support, n=3) == 3


def test_grammar_matched_count_null_draw_is_bounded():
    rng = random.Random(0)
    for _ in range(20):
        drawn = n2_draw(_GRID_WORDS, stem_min=2, rng=rng, mirror=False)
        support = ending_channel(drawn, stem_min=2).alternation_support
        for n in GRAMMAR_MATCH_NS:
            matched = grammar_matched_count(support, n)
            assert 0 <= matched <= n


# --------------------------------------------------------------------------- #
# Strict grammar-match null (A-072): a strict top-n cut (deterministic
# tie-break, paradigms.ranked_alternations) applied identically to the real
# corpus and to every N2 draw, alongside the pre-existing ties-included
# variant above (A-053, A-069).
# --------------------------------------------------------------------------- #


def test_grammar_matched_count_strict_matched_count_is_bounded_by_n():
    rng = random.Random(0)
    for _ in range(20):
        drawn = n2_draw(_GRID_WORDS, stem_min=2, rng=rng, mirror=False)
        support = ending_channel(drawn, stem_min=2).alternation_support
        for n in GRAMMAR_MATCH_NS:
            matched = grammar_matched_count_strict(support, n)
            assert 0 <= matched <= n


def test_strict_and_ties_included_agree_when_support_has_no_ties():
    # Four alternations, all distinct support values: no tie at any rank, so the
    # ties-included top-n (A-053) and the strict top-n (paradigms.ranked_alternations)
    # select the same set at every n, and the two matched counts agree too.
    support = {
        (("A",), ("B",)): 4,
        (("C",), ("D",)): 3,
        (("E",), ("F",)): 2,
        (("G",), ("H",)): 1,
    }
    for n in (1, 2, 3, 4):
        ties_included = top_n_alternations_with_ties(support, n=n)
        strict = frozenset(pair for pair, _support in ranked_alternations(support, limit=n))
        assert ties_included == strict
        assert grammar_matched_count(support, n) == grammar_matched_count_strict(support, n)


def test_strict_and_ties_included_agree_on_anchor_words_top_1_no_tie():
    # _ANCHOR_WORDS' top alternation (SO/SI-JO, support 2) is the corpus
    # maximum with no other alternation tied at it, so top-1 has no tie.
    channel = ending_channel(_ANCHOR_WORDS, stem_min=2)
    ties_included = top_n_alternations_with_ties(channel.alternation_support, n=1)
    strict = frozenset(pair for pair, _support in ranked_alternations(channel.alternation_support, limit=1))
    assert ties_included == strict == {(("SI", "JO"), ("SO",))}


def test_grammar_matched_count_strict_top10_equals_top_10_matched_to_rule_on_linear_b():
    # Confirms the strict real top-10 matched count equals the pre-existing
    # top_10_matched_to_rule field: both are the same strict, lexicographically
    # tie-broken top-10 by support (paradigms.ranked_alternations) graded
    # against reference.is_grammar. perms is small since only the real value,
    # not the null distribution, is being checked here.
    report = build_report(corpus().documents, corpus="damos", perms=5, seed=0)
    d = report.as_dict()
    ending = d["ending_channel"]
    assert ending["grammar_match_null_strict"]["10"]["real_value"] == ending["top_10_matched_to_rule"]


def test_build_alternation_grid_report_smoke():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    report = build_alternation_grid_report(
        _GRID_WORDS, channel, stem_min=2, perms=5, seed=0, top_n=10
    )
    assert report.alternation_count == 5
    assert report.fraction.pair_count == 4
    assert report.fraction.fraction == 1.0
    assert report.null.draws == 5
    assert len(report.classes) == 3


# --------------------------------------------------------------------------- #
# Kober 0.4: context classes (context.py), context-restricted channel
# (paradigms.py), stratified N2 (nulls.py), and the criterion's chance-rate
# indicator (nulls.py). A-075 to A-090.
# --------------------------------------------------------------------------- #


def _tok(text: str, signs: tuple[str, ...], kind: TokenKind = TokenKind.WORD) -> Token:
    return Token(text=text, kind=kind, signs=signs, status=ReadingStatus.CERTAIN)


def test_word_type_context_class_on_hand_built_document():
    # Word (X1, X2) occurs three times: twice line-initial with a following WORD
    # token (class A: dominant, 2 occurrences) and once line-initial as the only
    # token on its line, so next kind is "none" (class B: 1 occurrence). Support
    # type "Tablet " normalises to "tablet" (A-079).
    tokens = [
        _tok("X1-X2", ("X1", "X2")),   # 0: line 0, idx 0 -> class A
        _tok("Y1-Y2", ("Y1", "Y2")),   # 1: line 0, idx 1 (last -> next "none")
        _tok("X1-X2", ("X1", "X2")),   # 2: line 1, idx 0 -> class A
        _tok("Z1-Z2", ("Z1", "Z2")),   # 3: line 1, idx 1 (last -> next "none")
        _tok("X1-X2", ("X1", "X2")),   # 4: line 2, idx 0, only token -> class B
    ]
    doc = Document(
        id="t1",
        script_id="damos",
        tokens=tokens,
        lines=[[0, 1], [2, 3], [4]],
        meta=DocumentMeta(support="Tablet "),
    )
    contexts = extract_word_contexts([doc])

    x_class = contexts.word_class[("X1", "X2")]
    assert x_class == ("tablet", True, "WORD")  # dominant: 2 of 3 occurrences
    assert contexts.census[("tablet", True, "WORD")] == 1  # one word type (X) has this class
    # Y and Z each occur once, both line-final with nothing after -> same class,
    # so the census counts both word types under it.
    assert contexts.word_class[("Y1", "Y2")] == ("tablet", False, "none")
    assert contexts.word_class[("Z1", "Z2")] == ("tablet", False, "none")
    assert contexts.census[("tablet", False, "none")] == 2
    assert sum(contexts.census.values()) == 3  # three word types total


def test_context_restricted_support_drops_stem_with_differing_word_classes():
    # Stem (X1, X2) has endings SO and SI-JO whose words fall in *different*
    # classes (A-076): the alternation must not count, and with only this one
    # candidate pair, (X1, X2) is not a restricted paradigm at all. Stem
    # (Y1, Y2) has endings TA/TO whose words share a class, so it does count.
    words = [
        ("X1", "X2", "SO"),
        ("X1", "X2", "SI", "JO"),
        ("Y1", "Y2", "TA"),
        ("Y1", "Y2", "TO"),
    ]
    word_class = {
        ("X1", "X2", "SO"): ("tablet", True, "WORD"),
        ("X1", "X2", "SI", "JO"): ("tablet", False, "none"),
        ("Y1", "Y2", "TA"): ("stirrup jar", True, "none"),
        ("Y1", "Y2", "TO"): ("stirrup jar", True, "none"),
    }
    channel = build_channel_context_restricted(words, word_class, stem_min=2, mirror=False)
    assert (("SI", "JO"), ("SO",)) not in channel.alternation_support
    assert ("X1", "X2") not in channel.anchors
    assert channel.alternation_support[(("TA",), ("TO",))] == 1
    assert ("Y1", "Y2") in channel.anchors


def test_ending_channel_context_restricted_matches_build_channel_context_restricted():
    word_class = {w: ("tablet", True, "WORD") for w in _GRID_WORDS}
    a = ending_channel_context_restricted(_GRID_WORDS, word_class, stem_min=2)
    b = build_channel_context_restricted(_GRID_WORDS, word_class, stem_min=2, mirror=False)
    assert a == b


# Two-word stratum (S1/S2, class "tablet"/True/"WORD") beside a singleton
# stratum (S3, class "stirrup jar"/False/"none"): the singleton has nothing to
# shuffle with (A-077) and the two strata must never trade endings.
_N2_CONTEXT_WORDS = [
    ("S1", "S1B", "E1"),
    ("S2", "S2B", "E2"),
    ("S3", "S3B", "E3"),
]
_N2_CONTEXT_CLASS = {
    ("S1", "S1B", "E1"): ("tablet", True, "WORD"),
    ("S2", "S2B", "E2"): ("tablet", True, "WORD"),
    ("S3", "S3B", "E3"): ("stirrup jar", False, "none"),
}


def test_n2_draw_stratified_preserves_each_stratum_multiset_of_endings():
    for seed in range(10):
        rng = random.Random(seed)
        drawn, drawn_class = n2_draw_stratified(
            _N2_CONTEXT_WORDS, _N2_CONTEXT_CLASS, stem_min=2, rng=rng, mirror=False
        )
        by_stem = {w[:2]: w[2:] for w in drawn}
        assert set(by_stem.keys()) == {("S1", "S1B"), ("S2", "S2B"), ("S3", "S3B")}
        # A-077: the singleton stratum passes through unshuffled.
        assert by_stem[("S3", "S3B")] == ("E3",)
        assert drawn_class[("S3", "S3B", "E3")] == ("stirrup jar", False, "none")
        # The two-word stratum's endings are a permutation of themselves only;
        # neither ending ever leaks to or from the singleton stratum.
        assert set(by_stem[("S1", "S1B")]) | set(by_stem[("S2", "S2B")]) == {"E1", "E2"}


def test_top_three_all_matched_returns_bool():
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    # All five alternations tie at support 1 (see the comment above
    # test_alternation_bridging_pairs_on_grid_toy_set); three match a rule, so
    # a strict top three (arbitrary among the tied five under the ranking's
    # own tie-break) need not be all three matched.
    result = top_three_all_matched(channel.alternation_support)
    assert isinstance(result, bool)


def test_top_three_all_matched_chance_rate_is_between_0_and_1():
    word_class = {w: ("tablet", True, "WORD") for w in _GRID_WORDS}
    ending_context = ending_channel_context_restricted(_GRID_WORDS, word_class, stem_min=2)
    result = run_n2_context(
        _GRID_WORDS, word_class, stem_min=2, draws=20, seed=0, real_ending=ending_context
    )
    assert 0.0 <= result.top_three_all_matched_chance_rate <= 1.0
    for n in GRAMMAR_MATCH_NS:
        nd = result.grammar_match_strict[n]
        assert 0 <= nd.real_value <= n


# --------------------------------------------------------------------------- #
# Kober 0.5: entry-role tie-break (paradigms.role_sharing_counts,
# ranked_alternations' role_sharing key, nulls.run_n2's word_roles
# parameter). A hand-built word set and a hand-built document, mirroring the
# style _GRID_WORDS and test_entry_roles.py already use.
# --------------------------------------------------------------------------- #

# Stem SX has endings QA/QB; stem SY has endings PA/PB. Both alternations tie
# at support 1, so the plain (role_sharing=None) ordering falls back to the
# lexicographic tie-break, which ranks PA/PB before QA/QB ("P" < "Q"). The
# hand-built document below puts SX's two forms in the same entry role
# (both single-word entries closed by logogram VIR, at raw entry indices 3
# and 4, both saturating to the capped index 3, A-092) and SY's two forms in
# different roles (different entry index and different closing logogram), so
# the role-tiebreak ordering promotes the QA/QB alternation ahead of PA/PB.
_ROLE_TIEBREAK_WORDS = [
    ("SX1", "SX2", "QA"),
    ("SX1", "SX2", "QB"),
    ("SY1", "SY2", "PA"),
    ("SY1", "SY2", "PB"),
]


def _role_tiebreak_document() -> Document:
    tokens = [
        _tok("SY1-SY2-PA", ("SY1", "SY2", "PA")),  # 0: entry 0, closed VIR
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),  # 1
        _tok("SY1-SY2-PB", ("SY1", "SY2", "PB")),  # 2: entry 1, closed OVIS
        _tok("OVIS", (), kind=TokenKind.LOGOGRAM),  # 3
        _tok("D1-D2", ("D1", "D2")),  # 4: entry 2 (filler), closed VIR
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),  # 5
        _tok("SX1-SX2-QA", ("SX1", "SX2", "QA")),  # 6: entry 3 (raw), closed VIR
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),  # 7
        _tok("SX1-SX2-QB", ("SX1", "SX2", "QB")),  # 8: entry 4 (raw, caps to 3), closed VIR
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),  # 9
    ]
    return Document(
        id="KN Fp 1",
        script_id="damos",
        tokens=tokens,
        lines=[[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        meta=DocumentMeta(support="tablet"),
    )


def test_role_sharing_counts_on_hand_built_document():
    doc = _role_tiebreak_document()
    roles = word_roles([doc])
    # SX's two forms both land at capped entry index 3, closed VIR, "first" ->
    # the identical role tuple, so they share a role.
    assert roles[("SX1", "SX2", "QA")] == roles[("SX1", "SX2", "QB")]
    # SY's two forms differ in entry index and closing logogram -> disjoint.
    assert not (roles[("SY1", "SY2", "PA")] & roles[("SY1", "SY2", "PB")])

    channel = ending_channel(_ROLE_TIEBREAK_WORDS, stem_min=2)
    counts = role_sharing_counts(channel, roles)
    assert counts.get((("QA",), ("QB",)), 0) == 1
    assert counts.get((("PA",), ("PB",)), 0) == 0


def test_ranked_alternations_role_tiebreak_reorders_equal_support_alternations():
    doc = _role_tiebreak_document()
    roles = word_roles([doc])
    channel = ending_channel(_ROLE_TIEBREAK_WORDS, stem_min=2)
    support = channel.alternation_support
    assert support[(("PA",), ("PB",))] == support[(("QA",), ("QB",))] == 1  # tied support

    # Flag off (role_sharing=None): the old, byte-identical ordering --
    # lexicographic tie-break alone, "P" before "Q".
    old_order = [pair for pair, _support in ranked_alternations(support)]
    assert old_order == [(("PA",), ("PB",)), (("QA",), ("QB",))]

    # Flag on: role-sharing count breaks the tie first, promoting QA/QB
    # (whose stem's two forms share a role) ahead of PA/PB (which do not).
    role_sharing = role_sharing_counts(channel, roles)
    new_order = [pair for pair, _support in ranked_alternations(support, role_sharing=role_sharing)]
    assert new_order == [(("QA",), ("QB",)), (("PA",), ("PB",))]
    assert new_order != old_order


def test_run_n2_role_tiebreak_chance_rate_and_matched_count_are_bounded():
    # word_roles=None (default): behaviour is exactly the pre-0.5 run_n2, no
    # role-tiebreak fields populated.
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    off = run_n2(_GRID_WORDS, stem_min=2, draws=10, seed=0, mirror=False, real_channel=channel)
    assert off.grammar_match_role_tiebreak is None
    assert off.top_three_all_matched_chance_rate_role_tiebreak is None

    # word_roles given: two of the grid words are given a shared, synthetic
    # role so the tie-break has something to bite on; the rest carry none.
    synthetic_roles = {
        ("X1", "X2", "SO"): frozenset({"r1"}),
        ("X1", "X2", "SI", "JO"): frozenset({"r1"}),
    }
    on = run_n2(
        _GRID_WORDS,
        stem_min=2,
        draws=20,
        seed=0,
        mirror=False,
        real_channel=channel,
        word_roles=synthetic_roles,
    )
    assert on.top_three_all_matched_chance_rate_role_tiebreak is not None
    assert 0.0 <= on.top_three_all_matched_chance_rate_role_tiebreak <= 1.0
    for n in GRAMMAR_MATCH_NS:
        nd = on.grammar_match_role_tiebreak[n]
        assert 0 <= nd.real_value <= n
        assert 0.0 <= nd.mean <= n


# --------------------------------------------------------------------------- #
# Kober 0.7: list-support tie-break (kober.lists.homogeneous_forms,
# paradigms.list_support_counts, ranked_alternations' list_support key,
# nulls.run_n2's listings parameter). A-116.
# --------------------------------------------------------------------------- #


def _list_tiebreak_documents() -> tuple[Document, Document]:
    """Two hand-built, eligible (>= 3 listed words) documents. Doc A's three
    listed words all end in QA, so QA is its modal sign and (SX1, SX2, QA)
    satisfies Assumption 7; doc B's all end in QB, so (SX1, SX2, QB) does
    too. (SY1, SY2, PA) and (SY1, SY2, PB) never appear as listed words in
    either document, so they satisfy nothing (``homogeneous_forms``' default
    empty set)."""
    tokens_a = [
        _tok("SX1-SX2-QA", ("SX1", "SX2", "QA")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
        _tok("W1-W2-QA", ("W1", "W2", "QA")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
        _tok("W3-W4-QA", ("W3", "W4", "QA")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
    ]
    doc_a = Document(
        id="KN Fp 10",
        script_id="damos",
        tokens=tokens_a,
        lines=[[0, 1], [2, 3], [4, 5]],
        meta=DocumentMeta(support="tablet"),
    )
    tokens_b = [
        _tok("SX1-SX2-QB", ("SX1", "SX2", "QB")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
        _tok("W5-W6-QB", ("W5", "W6", "QB")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
        _tok("W7-W8-QB", ("W7", "W8", "QB")),
        _tok("VIR", (), kind=TokenKind.LOGOGRAM),
    ]
    doc_b = Document(
        id="KN Fp 11",
        script_id="damos",
        tokens=tokens_b,
        lines=[[0, 1], [2, 3], [4, 5]],
        meta=DocumentMeta(support="tablet"),
    )
    return doc_a, doc_b


_LIST_TIEBREAK_WORDS = [
    ("SX1", "SX2", "QA"),
    ("SX1", "SX2", "QB"),
    ("SY1", "SY2", "PA"),
    ("SY1", "SY2", "PB"),
]


def test_list_support_counts_on_hand_built_documents():
    doc_a, doc_b = _list_tiebreak_documents()
    listings = extract_listed_words([doc_a, doc_b])
    homogeneous = homogeneous_forms_from_listings(listings)
    assert ("SX1", "SX2", "QA")[-1] in homogeneous[("SX1", "SX2", "QA")]
    assert ("SX1", "SX2", "QB")[-1] in homogeneous[("SX1", "SX2", "QB")]
    assert ("SY1", "SY2", "PA") not in homogeneous
    assert ("SY1", "SY2", "PB") not in homogeneous

    channel = ending_channel(_LIST_TIEBREAK_WORDS, stem_min=2)
    counts = list_support_counts(channel, homogeneous)
    assert counts.get((("QA",), ("QB",)), 0) == 1
    assert counts.get((("PA",), ("PB",)), 0) == 0


def test_ranked_alternations_list_tiebreak_reorders_equal_support_and_role_alternations():
    doc_a, doc_b = _list_tiebreak_documents()
    listings = extract_listed_words([doc_a, doc_b])
    homogeneous = homogeneous_forms_from_listings(listings)
    channel = ending_channel(_LIST_TIEBREAK_WORDS, stem_min=2)
    support = channel.alternation_support
    assert support[(("PA",), ("PB",))] == support[(("QA",), ("QB",))] == 1  # tied support

    list_support = list_support_counts(channel, homogeneous)
    assert list_support.get((("QA",), ("QB",)), 0) == 1
    assert list_support.get((("PA",), ("PB",)), 0) == 0

    # Equal role-sharing (both zero, given explicitly so the tie is not
    # decided by roles): with list_support omitted, the ordering is the 0.5
    # one (support, then role-sharing, then lexicographic) -- "flag off"
    # equals 0.5, "P" before "Q".
    tied_role_sharing = {(("PA",), ("PB",)): 0, (("QA",), ("QB",)): 0}
    old_order = [pair for pair, _support in ranked_alternations(support, role_sharing=tied_role_sharing)]
    assert old_order == [(("PA",), ("PB",)), (("QA",), ("QB",))]

    # list_support given: list-support count breaks the tie ahead of the
    # lexicographic fallback, promoting QA/QB (whose stem's two forms both
    # satisfy Assumption 7) ahead of PA/PB (which satisfy neither).
    new_order = [
        pair
        for pair, _support in ranked_alternations(
            support, role_sharing=tied_role_sharing, list_support=list_support
        )
    ]
    assert new_order == [(("QA",), ("QB",)), (("PA",), ("PB",))]
    assert new_order != old_order


def test_run_n2_list_tiebreak_chance_rate_and_matched_count_are_bounded():
    # listings=None (default): behaviour is exactly the pre-0.7 run_n2, no
    # list-tiebreak fields populated -- flag off.
    channel = ending_channel(_GRID_WORDS, stem_min=2)
    off = run_n2(_GRID_WORDS, stem_min=2, draws=10, seed=0, mirror=False, real_channel=channel)
    assert off.grammar_match_list_tiebreak_v1 is None
    assert off.grammar_match_list_tiebreak_v2 is None
    assert off.top_three_all_matched_chance_rate_list_tiebreak_v1 is None
    assert off.top_three_all_matched_chance_rate_list_tiebreak_v2 is None

    # Hand-built listings (DocListing objects directly, no token parsing
    # needed): one eligible document (>= 3 listed words) whose modal final
    # sign is SO, so (X1, X2, SO) satisfies Assumption 7.
    listings = [
        DocListing(
            doc_id="d1",
            series_letter="X",
            listed=(("X1", "X2", "SO"), ("A", "B", "SO"), ("C", "D", "SO")),
        ),
    ]
    on = run_n2(_GRID_WORDS, stem_min=2, draws=20, seed=0, mirror=False, real_channel=channel, listings=listings)
    assert on.top_three_all_matched_chance_rate_list_tiebreak_v1 is not None
    assert on.top_three_all_matched_chance_rate_list_tiebreak_v2 is not None
    assert 0.0 <= on.top_three_all_matched_chance_rate_list_tiebreak_v1 <= 1.0
    assert 0.0 <= on.top_three_all_matched_chance_rate_list_tiebreak_v2 <= 1.0
    for n in GRAMMAR_MATCH_NS:
        nd1 = on.grammar_match_list_tiebreak_v1[n]
        nd2 = on.grammar_match_list_tiebreak_v2[n]
        assert 0 <= nd1.real_value <= n
        assert 0 <= nd2.real_value <= n
        assert 0.0 <= nd1.mean <= n
        assert 0.0 <= nd2.mean <= n


def test_build_list_tiebreak_report_smoke_on_linear_b():
    # End-to-end wiring smoke test, mirroring the 0.5 report smoke test:
    # build_report with word_roles and listings populates the list-tiebreak
    # null inside the same N2 pass (no extra draws), and
    # build_list_tiebreak_report assembles the block from it.
    docs = corpus().documents
    roles = word_roles(docs)
    listings = extract_listed_words(docs)
    report = build_report(docs, corpus="damos", perms=5, seed=0, word_roles=roles, listings=listings)
    lt = build_list_tiebreak_report(report, roles, listings)
    assert len(lt.top_10) == 10
    assert lt.top_3 == lt.top_10[:3]
    assert 0 <= lt.positions_changed_vs_0_5 <= 10
    assert 0.0 <= lt.top_three_all_matched_chance_rate_v1 <= 1.0
    assert 0.0 <= lt.top_three_all_matched_chance_rate_v2 <= 1.0
    for n in GRAMMAR_MATCH_NS:
        nd1 = lt.grammar_match_null_list_tiebreak_v1[n]
        nd2 = lt.grammar_match_null_list_tiebreak_v2[n]
        assert 0 <= nd1.real_value <= n
        assert 0 <= nd2.real_value <= n


def test_build_role_tiebreak_report_smoke_on_linear_b():
    # End-to-end wiring smoke test: build_report with word_roles populates
    # the role-tiebreak null inside the same N2 pass (no extra draws), and
    # build_role_tiebreak_report assembles the block from it. perms is small
    # since only the shape and bounds are being checked here.
    docs = corpus().documents
    roles = word_roles(docs)
    report = build_report(docs, corpus="damos", perms=5, seed=0, word_roles=roles)
    rt = build_role_tiebreak_report(report, roles)
    assert len(rt.top_10) == 10
    assert rt.top_3 == rt.top_10[:3]
    assert 0 <= rt.positions_changed_vs_0_3 <= 10
    assert 0.0 <= rt.top_three_all_matched_chance_rate <= 1.0
    for n in GRAMMAR_MATCH_NS:
        nd = rt.grammar_match_null_role_tiebreak[n]
        assert 0 <= nd.real_value <= n


# --------------------------------------------------------------------------- #
# Kober 0.9: medial channel (medial.py), N3 null (nulls.py), homophone merge
# (words.py). CHANGELOG "0.9".
# --------------------------------------------------------------------------- #

# Two pairs of same-length words identical except at one interior position
# (A-B-C / A-X-C differ only at index 1; Q-B-C-D / Q-B-Z-D differ only at
# index 2), one unpaired length-3 word (M-N-P, shares no masked key with
# anything), and one length-3 pair differing at *two* positions (R-S-T /
# R-V-W), which must contribute no medial pair at all.
_MEDIAL_WORDS = [
    ("A", "B", "C"),
    ("A", "X", "C"),
    ("Q", "B", "C", "D"),
    ("Q", "B", "Z", "D"),
    ("M", "N", "P"),
    ("R", "S", "T"),
    ("R", "V", "W"),
]


def test_medial_pairs_hand_built_set():
    pairs = medial_pairs(_MEDIAL_WORDS)
    assert pairs == {("B", "X"): 1, ("C", "Z"): 1}


def test_medial_pairs_two_position_difference_is_not_a_pair():
    # R-S-T / R-V-W differ at index 1 (the only interior position for a
    # length-3 word) *and* at index 2 (the last position, a flanking sign
    # that must stay identical). The masked key at index 1, (R, T) vs
    # (R, W), does not match, so no pair is found -- not by special-casing,
    # but because the pair fails the "identical except one interior
    # position" definition at every interior position there is.
    pairs = medial_pairs(_MEDIAL_WORDS)
    assert ("S", "V") not in pairs
    assert ("T", "W") not in pairs


def test_medial_pairs_ignores_words_shorter_than_three_signs():
    assert medial_pairs([("A", "B"), ("A", "C")]) == {}


def test_medial_pairs_only_compares_same_length_words():
    assert medial_pairs([("A", "B", "C"), ("A", "B", "C", "D")]) == {}


def test_medial_pairs_support_counts_word_pairs_not_distinct_alternations():
    # Three words sharing a masked key (X1, ?, X3) with pairwise distinct
    # middle signs contribute three word pairs across three alternations,
    # not one alternation at support 3.
    words = [("X1", "P", "X3"), ("X1", "Q", "X3"), ("X1", "R", "X3")]
    pairs = medial_pairs(words)
    assert pairs == {("P", "Q"): 1, ("P", "R"): 1, ("Q", "R"): 1}


def test_ranked_medial_pairs_orders_by_support_then_lexicographic():
    support = {("B", "X"): 2, ("A", "Z"): 2, ("C", "D"): 1}
    assert ranked_medial_pairs(support) == [(("A", "Z"), 2), (("B", "X"), 2), (("C", "D"), 1)]


def test_ranked_medial_pairs_respects_limit():
    support = {("A", "B"): 3, ("C", "D"): 2, ("E", "F"): 1}
    assert ranked_medial_pairs(support, limit=2) == [(("A", "B"), 3), (("C", "D"), 2)]


def test_build_medial_report_smoke_on_toy_words():
    report = build_medial_report(_MEDIAL_WORDS, perms=20, seed=0)
    assert report.pair_count == 2
    assert report.max_support == 1
    assert len(report.top_20) == 2
    assert report.pair_count_null.draws == 20
    assert report.max_support_null.draws == 20
    assert report.consonant_fraction_null.draws == 20
    assert 0.0 <= report.consonant_fraction.fraction <= 1.0


# N3: shuffles only interior-position columns, holding each word's own first
# and last sign ("flanking signs") fixed. Flanking signs are unique per word
# below, so the drawn set's flanking pairs can be checked exactly against the
# originals regardless of how the interior columns were permuted.
_N3_WORDS = [
    ("F1", "M1", "L1"),
    ("F2", "M2", "L2"),
    ("F3", "M3", "L3"),
    ("G1", "H1", "I1", "L4"),
    ("G2", "H2", "I2", "L5"),
]


def test_n3_preserves_length_distribution():
    rng = random.Random(0)
    drawn = n3_draw(_N3_WORDS, rng)
    assert Counter(len(w) for w in drawn) == Counter(len(w) for w in _N3_WORDS)


def test_n3_holds_flanking_signs_fixed_per_word():
    rng = random.Random(3)
    drawn = n3_draw(_N3_WORDS, rng)
    original_flanks = Counter((w[0], w[-1]) for w in _N3_WORDS)
    drawn_flanks = Counter((w[0], w[-1]) for w in drawn)
    assert drawn_flanks == original_flanks


def test_n3_preserves_interior_positional_sign_frequency():
    rng = random.Random(0)
    drawn = n3_draw(_N3_WORDS, rng)
    length3 = [w for w in _N3_WORDS if len(w) == 3]
    drawn_length3 = [w for w in drawn if len(w) == 3]
    assert len(drawn_length3) == len(length3)
    assert Counter(w[1] for w in drawn_length3) == Counter(w[1] for w in length3)


def test_n3_is_deterministic_under_a_seed():
    a = n3_draw(_N3_WORDS, random.Random(5))
    b = n3_draw(_N3_WORDS, random.Random(5))
    assert a == b


def test_n3_length_below_3_has_no_interior_position_and_passes_through():
    words = [("A", "B")]  # n - 1 == 1: range(1, 1) is empty, nothing to shuffle
    rng = random.Random(0)
    drawn = n3_draw(words, rng)
    assert drawn == frozenset(words)


# Homophone merge (words.py, A-144): a2/RA2/etc. collapse to their plain
# form at extraction, before the two-or-more-sign filter and before every
# downstream statistic.
def test_homophone_merge_map_matches_the_design_page():
    assert HOMOPHONE_MERGE_MAP == {
        "A2": "A",
        "AI2": "AI",
        "PA2": "PA",
        "PU2": "PU",
        "RA2": "RA",
        "RA3": "RA",
        "RO2": "RO",
        "TA2": "TA",
    }


def test_merge_homophones_collapses_hand_built_duplicate_word_types():
    tokens = [
        _tok("KA-RA2-NA", ("KA", "RA2", "NA")),
        _tok("KA-RA-NA", ("KA", "RA", "NA")),
        _tok("PA2-PU2", ("PA2", "PU2")),
    ]
    doc = Document(id="t1", script_id="damos", tokens=tokens, lines=[[0, 1, 2]], meta=DocumentMeta())

    unmerged = extract_word_types([doc])
    assert {("KA", "RA2", "NA"), ("KA", "RA", "NA"), ("PA2", "PU2")} <= unmerged.words
    assert len(unmerged.words) == 3

    merged = extract_word_types([doc], merge_homophones=True)
    assert ("KA", "RA", "NA") in merged.words
    assert ("KA", "RA2", "NA") not in merged.words
    assert ("PA", "PU") in merged.words
    assert len(merged.words) == 2  # the two RA2/RA spellings of KA-RA-NA collapse to one


def test_merge_homophones_leaves_unlisted_signs_unchanged():
    tokens = [_tok("A3-RA4", ("A3", "RA4"))]  # not in HOMOPHONE_MERGE_MAP
    doc = Document(id="t1", script_id="damos", tokens=tokens, lines=[[0]], meta=DocumentMeta())
    merged = extract_word_types([doc], merge_homophones=True)
    assert ("A3", "RA4") in merged.words


def test_merge_homophones_does_not_affect_labels_changed_count():
    tokens = [_tok("KA-RA2-NA", ("KA", "RA2", "NA"))]
    doc = Document(id="t1", script_id="damos", tokens=tokens, lines=[[0]], meta=DocumentMeta())
    unmerged = extract_word_types([doc])
    merged = extract_word_types([doc], merge_homophones=True)
    assert merged.labels_changed == unmerged.labels_changed
    assert merged.labels_seen == unmerged.labels_seen


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{failures} failure(s)")
    sys.exit(1 if failures else 0)
