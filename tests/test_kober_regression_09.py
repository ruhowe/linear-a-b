"""Regression pins for Kober 0.9: the medial-channel real values and the
homophone-merged word-type counts, on Linear B and Linear A.

Reruns extraction plus the medial channel with the current code and asserts
that every real-valued (non-null) statistic equals the committed results
files under ``results/kober-09/`` and ``results/kober-09-merged/``. Null
draws are not compared (cross-process RNG-ordering noise, A-062, the same
reason ``tests/test_kober_regression.py`` excludes them): the real medial
values (pair count, max support, the top-20 pairs, the consonant-sharing
fraction) are deterministic and must not move; the 0.1 pins in
``test_kober_regression.py`` are untouched by this file.

If this fails after a code change, either the medial channel or the
homophone merge changed (CHANGELOG needs a new version and the affected
findings a rerun and a dated note), or it is a bug.

Run: ``.venv/bin/python -m pytest tests/test_kober_regression_09.py -q``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PINS_UNMERGED = {
    "damos": ROOT / "results" / "kober-09" / "kober-damos-seed0.json",
    "lineara": ROOT / "results" / "kober-09" / "kober-lineara-seed0.json",
}
PINS_MERGED = {
    "damos": ROOT / "results" / "kober-09-merged" / "kober-damos-seed0.json",
    "lineara": ROOT / "results" / "kober-09-merged" / "kober-lineara-seed0.json",
}


def _medial_real_fields(report: dict) -> dict:
    m = report["medial"]
    return {
        "word_types": report["word_types"]["count"],
        "merge_homophones": report["merge_homophones"],
        "pair_count": m["pair_count"],
        "max_support": m["max_support"],
        "top_20_pairs": [
            (e["s1"], e["s2"], e["support"], e["shares_consonant"]) for e in m["top_20_pairs"]
        ],
        "consonant_sharing_fraction": m["consonant_sharing_fraction"],
        "consonant_sharing_chance_fraction": m["consonant_sharing_chance_fraction"],
        "consonant_sharing_scored_count": m["consonant_sharing_scored_count"],
        "consonant_sharing_excluded_count": m["consonant_sharing_excluded_count"],
    }


def _rerun(corpus: str, merge_homophones: bool) -> dict:
    import aegean
    from kober.report import build_medial_report, build_report

    c = aegean.load(corpus)
    report = build_report(
        c.documents, corpus=corpus, stem_min=2, perms=5, seed=0, merge_homophones=merge_homophones
    )
    medial = build_medial_report(report.word_types.words, perms=5, seed=0)
    d = report.as_dict()
    d["medial"] = medial.as_dict()
    return d


@pytest.mark.parametrize("corpus", ["damos", "lineara"])
def test_09_medial_real_values_match_committed_results_unmerged(corpus: str) -> None:
    pinned = _medial_real_fields(json.loads(PINS_UNMERGED[corpus].read_text()))
    current = _medial_real_fields(_rerun(corpus, merge_homophones=False))
    assert current == pinned, f"{corpus} (unmerged): 0.9 medial real values moved; see module docstring"


@pytest.mark.parametrize("corpus", ["damos", "lineara"])
def test_09_medial_real_values_match_committed_results_merged(corpus: str) -> None:
    pinned = _medial_real_fields(json.loads(PINS_MERGED[corpus].read_text()))
    current = _medial_real_fields(_rerun(corpus, merge_homophones=True))
    assert current == pinned, f"{corpus} (merged): 0.9 medial real values moved; see module docstring"


@pytest.mark.parametrize("corpus", ["damos", "lineara"])
def test_09_merge_homophones_reduces_or_holds_type_count(corpus: str) -> None:
    """The merge only ever collapses spellings together, never splits one."""
    unmerged_count = json.loads(PINS_UNMERGED[corpus].read_text())["word_types"]["count"]
    merged_count = json.loads(PINS_MERGED[corpus].read_text())["word_types"]["count"]
    assert merged_count <= unmerged_count
