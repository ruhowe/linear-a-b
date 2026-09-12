"""Tests for Value transfer 1.0 (CHANGELOG "Value transfer (A-001): the toponym test",
entry 1.0). See scripts/toponym_test.py for the protocol.

Run: ``.venv/bin/python -m pytest tests/test_toponym_test.py -q``.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

import toponym_test as tt  # noqa: E402


def test_lexicon_sizes():
    """The four lexicons come out at the sizes the protocol expects: 32 Knossos
    toponyms (33 candidates, di-ka-ta unattested), 32 Knossos personal names (matched
    to the toponym count), a Pylos toponym control built from 21 candidates with two
    (a-pu2, e-ra-to) unattested in that exact nominative form, and a reversed-toponym
    control of the same size as (a)."""
    damos = aegean.load("damos")
    lexicons, provenance = tt.build_lexicons(damos)

    assert len(tt.KNOSSOS_TOPONYM_CANDIDATES) == 33
    assert provenance["knossos_toponyms"]["dropped"] == ["di-ka-ta"]
    assert len(lexicons["knossos_toponyms"]) == 32

    assert len(lexicons["knossos_personal_names"]) == 32

    assert len(tt.PYLOS_TOPONYM_CANDIDATES) == 21
    assert set(provenance["pylos_toponyms"]["dropped"]) == {"a-pu2", "e-ra-to"}
    assert len(lexicons["pylos_toponyms"]) == 19

    assert len(lexicons["knossos_toponyms_reversed"]) == len(lexicons["knossos_toponyms"])
    for reversed_word, original in zip(
        lexicons["knossos_toponyms_reversed"], lexicons["knossos_toponyms"]
    ):
        assert reversed_word == tuple(reversed(original))


def test_match_appears_under_identity_and_disappears_under_permutation():
    """A hand-built assignment: PA-I-TO (Linear A) should 3=-match a lexicon word
    PA-I-TO under the identity assignment (every position literally equal), and the
    match must disappear under a permutation that sends PA's value elsewhere."""
    la_words = [("PA", "I", "TO")]
    lexicon_words = [("PA", "I", "TO")]
    ranked_labels = ["PA", "I", "TO", "KO", "NO", "SO"]

    id_map = tt.identity_map(ranked_labels)
    c3, c4, pairs3, pairs4 = tt.count_matches(la_words, lexicon_words, id_map, collect_pairs=True)
    assert c3 == 1
    assert pairs3 == [(("PA", "I", "TO"), ("PA", "I", "TO"))]

    # A permutation that moves PA's value to KO breaks the first-position identity
    # the 3= test requires, so the match must vanish.
    broken_map = dict(id_map)
    broken_map["PA"] = "KO"
    broken_map["KO"] = "PA"
    c3_broken, c4_broken, _, _ = tt.count_matches(la_words, lexicon_words, broken_map)
    assert c3_broken == 0
    assert c4_broken == 0


def test_null_preserves_band_label_multiset():
    """permuted_map draws one independent permutation per band: within each band, the
    multiset of values assigned is identical to the multiset of labels in that band
    (a bijection restricted to the band), for every one of several seeded draws."""
    bands = [["A", "B", "C", "D"], ["E", "F", "G"]]
    for seed in range(10):
        rng = random.Random(seed)
        pmap = tt.permuted_map(bands, rng)
        for band in bands:
            assert sorted(pmap[label] for label in band) == sorted(band)
        # Every key maps to a value, and no value is shared across bands.
        assert set(pmap.keys()) == {label for band in bands for label in band}
        assert set(pmap.values()) == {label for band in bands for label in band}


def test_chunk_fixed_and_chunk_n_cover_the_ranked_list_exactly():
    ranked = [str(i) for i in range(23)]
    fixed = tt.chunk_fixed(ranked, 10)
    assert [len(b) for b in fixed] == [10, 10, 3]
    assert [x for band in fixed for x in band] == ranked

    four = tt.chunk_n(ranked, 4)
    assert sum(len(b) for b in four) == len(ranked)
    assert [x for band in four for x in band] == ranked
    # Near-equal: no band differs from another by more than one.
    sizes = [len(b) for b in four]
    assert max(sizes) - min(sizes) <= 1
