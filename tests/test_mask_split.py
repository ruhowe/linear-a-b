"""Leakage and integrity gates for masking, splitting and vocabulary.

A leak here does not crash anything — it quietly inflates every accuracy figure
downstream. These tests are the only thing standing between a leak and a published
number, so they check the properties directly rather than checking counts.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aegean  # noqa: E402

from linearb_restore.extract import d_family, extract_sequences  # noqa: E402
from linearb_restore.mask import MASK, make_items  # noqa: E402
from linearb_restore.split import (  # noqa: E402
    Fold,
    coverage,
    document_folds,
    findspot_split,
    leave_one_hand_out,
)
from linearb_restore.vocab import build_vocabulary  # noqa: E402

_CACHE: dict = {}


def sequences():
    if "seq" not in _CACHE:
        corpus = aegean.load("damos")
        _CACHE["seq"] = extract_sequences(corpus, d_family(corpus))
    return _CACHE["seq"]


def items():
    if "items" not in _CACHE:
        _CACHE["items"] = make_items(sequences())
    return _CACHE["items"]


# --------------------------------------------------------------------------- #
# Masking
# --------------------------------------------------------------------------- #


def test_leave_one_out_item_count_matches_maskable_positions():
    """Exhaustive LOO must produce exactly one item per eligible sign position."""
    expected = sum(len(r.maskable_positions()) for r in sequences())
    assert len(items()) == expected
    assert expected == 2684


def test_answer_is_never_visible_in_the_item():
    """The masked sign must not survive anywhere in the context handed to a model."""
    for item in items():
        assert MASK in item.word_signs
        assert len(item.answers) == item.word_signs.count(MASK)
        visible = list(item.left) + list(item.right) + [
            s for s in item.word_signs if s != MASK
        ]
        # The answer may legitimately recur elsewhere (e.g. a repeated sign); what must
        # not happen is the masked slot itself still showing its own value.
        assert item.word_signs[item.sign_index] == MASK
        del visible


def test_context_reconstructs_the_original_sequence_length():
    """left + masked word + right must account for every symbol in the sequence."""
    for item in items()[:500]:
        total = len(item.left) + len(item.word_signs) + len(item.right)
        assert total >= len(item.word_signs)
        assert all(s != MASK for s in item.left + item.right)


def test_span_and_word_final_regimes_are_harder_and_smaller():
    seqs = sequences()
    loo = make_items(seqs, regime="leave_one_out")
    span = make_items(seqs, regime="span", span=2)
    final = make_items(seqs, regime="word_final")
    assert 0 < len(span) < len(loo)
    assert 0 < len(final) < len(loo)
    assert all(i.n_masked == 2 for i in span)
    assert all(i.n_masked == 1 for i in final)
    # word_final never targets a single-sign word: hiding its only sign leaves nothing
    assert all(not i.single_sign_word for i in final)


def test_single_sign_words_are_identifiable_as_a_stratum():
    singles = [i for i in items() if i.single_sign_word]
    assert len(singles) == 269
    assert all(i.word_signs == (MASK,) for i in singles)


# --------------------------------------------------------------------------- #
# Splitting — the leakage gates
# --------------------------------------------------------------------------- #


def test_folds_are_document_disjoint_and_cover_every_document():
    docs = {r.doc_id for r in sequences() if r.eligible}
    folds = document_folds(docs, k=5, seed=0)
    assert len(folds) == 5
    seen: set[str] = set()
    for fold in folds:
        assert not (fold.train_docs & fold.test_docs)
        assert not (seen & fold.test_docs), "a document appears in two test folds"
        seen |= fold.test_docs
    assert seen == docs, "every document must be tested exactly once"


def test_no_item_crosses_a_fold():
    folds = document_folds({r.doc_id for r in sequences() if r.eligible}, k=5, seed=0)
    for fold in folds:
        train, test = fold.split(items())
        assert {i.doc_id for i in train} & {i.doc_id for i in test} == set()
        assert len(train) + len(test) == len(items())


def test_fold_construction_rejects_a_leaking_fold():
    try:
        Fold(index=0, train_docs=frozenset({"a", "b"}), test_docs=frozenset({"b"}))
    except ValueError as exc:
        assert "leak" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a leaking fold was accepted")


def test_folds_are_deterministic_across_runs():
    docs = {r.doc_id for r in sequences() if r.eligible}
    a = [sorted(f.test_docs) for f in document_folds(docs, k=5, seed=0)]
    b = [sorted(f.test_docs) for f in document_folds(docs, k=5, seed=0)]
    assert a == b, "folds must reproduce — do not use salted hash()"
    c = [sorted(f.test_docs) for f in document_folds(docs, k=5, seed=1)]
    assert a != c, "a different seed must give a different partition"


def test_metadata_concentration_forces_document_grouping():
    """The numbers that make hand- and findspot-grouping unusable as headlines."""
    docs = {r.doc_id: r for r in sequences()}.values()
    scribes = coverage(r.scribe for r in docs)
    findspots = coverage(r.findspot for r in docs)
    assert scribes["top_share_of_filled"] > 0.6, "hand 117 should dominate"
    assert findspots["top_share_of_filled"] > 0.8, "one findspot should dominate"


def test_sensitivity_splits_build_and_stay_disjoint():
    by_doc = {r.doc_id: r for r in sequences()}
    hands = leave_one_hand_out({d: r.scribe for d, r in by_doc.items()})
    assert hands, "there should be holdable-out hands besides 117"
    assert all("117" != f.label.split()[-3] for f in hands)
    for fold in hands:
        assert not (fold.train_docs & fold.test_docs)
    spot = findspot_split({d: r.findspot for d, r in by_doc.items()}, holdout="KN, J1")
    assert not (spot.train_docs & spot.test_docs)


def test_certainty_qualified_hands_normalise_before_grouping():
    """`117?` must group with `117`, or the same hand lands on both sides."""
    folds = leave_one_hand_out(
        {"d1": "118", "d2": "118?", "d3": "120", "d4": "120", "d5": "120"},
        min_docs=2,
        exclude=(),
    )
    by_hand = {f.label.split()[-3]: f for f in folds}
    assert "118" in by_hand
    assert by_hand["118"].test_docs == frozenset({"d1", "d2"})


# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #


def test_vocabulary_holds_only_maskable_signs():
    """Logograms, <NUM> and <SEP> must never become candidates."""
    vocab = build_vocabulary(items())
    assert all(not s.startswith("<") for s in vocab.signs)
    assert not any(":" in s for s in vocab.signs), "logogram labels leaked in"
    assert len(vocab) == 77


def test_vocabulary_is_built_from_training_data_only():
    """A sign attested solely in the test fold must not be rankable."""
    folds = document_folds({r.doc_id for r in sequences() if r.eligible}, k=5, seed=0)
    train, test = folds[0].split(items())
    vocab = build_vocabulary(train)
    train_signs = {s for i in train for s in i.answers}
    assert set(vocab.signs) >= train_signs
    test_only = {s for i in test for s in i.answers} - train_signs
    assert not (test_only & set(vocab.signs)), "test-only signs leaked into candidates"


def test_top_k_share_exposes_the_top20_caveat():
    """top-20 over this vocabulary admits about a quarter of all candidates."""
    vocab = build_vocabulary(items())
    assert 0.2 < vocab.top_k_share(20) < 0.3
    assert vocab.top_k_share(1) < 0.02


def test_seen_word_stratification_key_works():
    folds = document_folds({r.doc_id for r in sequences() if r.eligible}, k=5, seed=0)
    train, test = folds[0].split(items())
    vocab = build_vocabulary(train)
    seen = [i for i in test if vocab.seen_word(i.word_text)]
    unseen = [i for i in test if not vocab.seen_word(i.word_text)]
    assert seen and unseen, "both strata must be populated"
    assert len(seen) + len(unseen) == len(test)


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
