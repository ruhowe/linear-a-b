"""Regression pins for the Kober findings.

Reruns stage 1 of the Kober method on Linear B and Linear A with the current code and
asserts that every real-valued statistic equals the committed results file that FINDINGS
F-016 and F-019 quote. Null draws are not compared (they carry cross-process RNG-ordering
noise, A-062); the real values are deterministic and must not move.

If this test fails after a code change, one of two things is true: the change altered
the instrument, in which case CHANGELOG needs a new version and the affected findings a
rerun and a dated note; or the change is a bug. Either way the earlier finding is
reproducible from its tag: ``git checkout F-016``.

Run: ``.venv/bin/python -m pytest tests/test_kober_regression.py -q`` (about ten seconds).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

PINS = {
    "damos": ROOT / "results" / "kober-damos-seed0.json",
    "lineara": ROOT / "results" / "kober-lineara-seed0.json",
}


def _real_fields(report: dict) -> dict:
    """The deterministic part of a stage 1 results file."""
    out = {"word_types": report["word_types"]["count"]}
    for ch in ("ending_channel", "prefix_channel"):
        c = report[ch]
        out[ch] = {
            "paradigm_count_total": c["paradigm_count_total"],
            "paradigm_count_by_stem_length": {str(k): v for k, v in c["paradigm_count_by_stem_length"].items()},
            "top_10_matched_to_rule": c["top_10_matched_to_rule"],
            "top_20": [(a["e1_label"], a["e2_label"], a["support"], a.get("rule")) for a in c["top_20_alternations"]],
            "max_support_real": c["n2_alternation_support"]["max_support"]["real_value"],
            "tenth_support_real": c["n2_alternation_support"]["tenth_support"]["real_value"],
        }
    return out


def _rerun(corpus: str) -> dict:
    import aegean
    from kober.report import build_report

    c = aegean.load(corpus)
    report = build_report(c.documents, corpus=corpus, stem_min=2, perms=5, seed=0)
    return report.as_dict()


@pytest.mark.parametrize("corpus", ["damos", "lineara"])
def test_stage1_real_values_match_committed_results(corpus: str) -> None:
    pinned = _real_fields(json.loads(PINS[corpus].read_text()))
    current = _real_fields(_rerun(corpus))
    assert current == pinned, f"{corpus}: stage 1 real values moved; see module docstring"
