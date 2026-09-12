"""Tests for spikes/S-007-model-as-kober/score.py, on a tiny synthetic
corpus (S-007's BRIEF.md; no real corpus data, per the licensing invariants
in docs/ai_context/corpus-sources.md).

Run: ``.venv/bin/python -m pytest tests/test_s007_score.py -q``
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "spikes" / "S-007-model-as-kober"))

import score  # noqa: E402

# A tiny synthetic corpus: two stems (A-B, C-D) each carrying the endings X
# and Y, so the alternation (X, Y) has support 2; a third stem (E-F) with
# only one ending contributes no paradigm. Also a stray word (Q-R) with no
# shared stem, and a real Mycenaean-shaped pair (TO/TA on stem WA-NA) so a
# --reference-version 1 run has something to match.
CORPUS_WORDS = [
    ("A", "B", "X"),
    ("A", "B", "Y"),
    ("C", "D", "X"),
    ("C", "D", "Y"),
    ("E", "F", "X"),
    ("Q", "R"),
    ("WA", "NA", "TO"),
    ("WA", "NA", "TA"),
]


def _write_corpus(tmp_path: Path) -> Path:
    path = tmp_path / "corpus.txt"
    path.write_text("\n".join("-".join(w) for w in sorted(CORPUS_WORDS)) + "\n")
    return path


def test_load_corpus_round_trips(tmp_path):
    path = _write_corpus(tmp_path)
    words = score.load_corpus(path)
    assert words == frozenset(CORPUS_WORDS)


def test_validate_proposal_valid():
    corpus_words = frozenset(CORPUS_WORDS)
    proposal = {
        "stem": ["A", "B"],
        "endings": [["X"], ["Y"]],
        "words": [["A", "B", "X"], ["A", "B", "Y"]],
    }
    valid, reasons, stem, endings = score.validate_proposal(proposal, corpus_words)
    assert valid, reasons
    assert stem == ("A", "B")
    assert endings == [("X",), ("Y",)]


def test_validate_proposal_word_not_in_corpus():
    corpus_words = frozenset(CORPUS_WORDS)
    proposal = {
        "stem": ["A", "B"],
        "endings": [["X"], ["Z"]],
        "words": [["A", "B", "X"], ["A", "B", "Z"]],
    }
    valid, reasons, _stem, _endings = score.validate_proposal(proposal, corpus_words)
    assert not valid
    assert any("not found in corpus" in r for r in reasons)


def test_validate_proposal_stem_plus_ending_mismatch():
    corpus_words = frozenset(CORPUS_WORDS)
    proposal = {
        "stem": ["A", "B"],
        "endings": [["X"], ["Y"]],
        # second word doesn't actually equal stem + ending
        "words": [["A", "B", "X"], ["C", "D", "Y"]],
    }
    valid, reasons, _stem, _endings = score.validate_proposal(proposal, corpus_words)
    assert not valid
    assert any("!=" in r for r in reasons)


def test_validate_proposal_fewer_than_two_distinct_endings():
    corpus_words = frozenset(CORPUS_WORDS)
    proposal = {
        "stem": ["A", "B"],
        "endings": [["X"], ["X"]],
        "words": [["A", "B", "X"], ["A", "B", "X"]],
    }
    valid, reasons, _stem, endings = score.validate_proposal(proposal, corpus_words)
    assert not valid
    assert endings == [("X",)]
    assert any("fewer than two distinct endings" in r for r in reasons)


def test_validate_proposal_malformed():
    corpus_words = frozenset(CORPUS_WORDS)
    valid, reasons, stem, endings = score.validate_proposal({"stem": ["A"]}, corpus_words)
    assert not valid
    assert stem is None
    assert endings == []
    assert reasons


def test_build_report_scores_valid_proposal_support_correctly():
    corpus_words = frozenset(CORPUS_WORDS)
    proposals = [
        {
            "stem": ["A", "B"],
            "endings": [["X"], ["Y"]],
            "words": [["A", "B", "X"], ["A", "B", "Y"]],
        }
    ]
    report = score.build_report(
        corpus_words, proposals, stem_min=2, draws=10, seed=0, top_n=5, reference_version=None
    )
    assert report["corpus_word_type_count"] == len(CORPUS_WORDS)
    entry = report["proposals"][0]
    assert entry["valid"]
    # (X, Y) is carried by stems A-B and C-D -> support 2.
    assert entry["support"] == 2
    assert len(entry["alternations"]) == 1
    assert entry["alternations"][0]["support"] == 2
    assert "grammar_rule" not in entry["alternations"][0]


def test_build_report_invalid_proposal_has_no_support():
    corpus_words = frozenset(CORPUS_WORDS)
    proposals = [
        {
            "stem": ["A", "B"],
            "endings": [["X"], ["Z"]],
            "words": [["A", "B", "X"], ["A", "B", "Z"]],
        }
    ]
    report = score.build_report(
        corpus_words, proposals, stem_min=2, draws=10, seed=0, top_n=5, reference_version=None
    )
    entry = report["proposals"][0]
    assert not entry["valid"]
    assert entry["support"] is None
    assert entry["above"] is False


def test_build_report_reference_version_grades_grammar():
    corpus_words = frozenset(CORPUS_WORDS)
    proposals = [
        {
            "stem": ["WA", "NA"],
            "endings": [["TO"], ["TA"]],
            "words": [["WA", "NA", "TO"], ["WA", "NA", "TA"]],
        }
    ]
    report = score.build_report(
        corpus_words, proposals, stem_min=2, draws=10, seed=0, top_n=5, reference_version=1
    )
    entry = report["proposals"][0]
    assert entry["valid"]
    # TO/TA is rule 1 (gender: same consonant T, vowels O/A).
    assert entry["alternations"][0]["grammar_rule"] == "gender"


def test_instrument_top_n_matches_real_channel():
    corpus_words = frozenset(CORPUS_WORDS)
    report = score.build_report(corpus_words, [], stem_min=2, draws=10, seed=0, top_n=5, reference_version=None)
    top = report["instrument_top_n"]
    assert top, "expected at least one alternation in the instrument's own top-n"
    # (X, Y) at support 2 should be the best-supported alternation.
    best = top[0]
    assert best["support"] == 2
    assert {tuple(best["e1"]), tuple(best["e2"])} == {("X",), ("Y",)}


def test_score_py_cli_end_to_end(tmp_path):
    corpus_path = _write_corpus(tmp_path)
    proposals_path = tmp_path / "proposals.json"
    proposals_path.write_text(
        json.dumps(
            [
                {
                    "stem": ["A", "B"],
                    "endings": [["X"], ["Y"]],
                    "words": [["A", "B", "X"], ["A", "B", "Y"]],
                },
                {"stem": ["Q"], "endings": [["R"], ["S"]], "words": [["Q", "R"], ["Q", "S"]]},
            ]
        )
    )
    out_path = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "spikes" / "S-007-model-as-kober" / "score.py"),
            "--corpus",
            str(corpus_path),
            "--proposals",
            str(proposals_path),
            "--draws",
            "10",
            "--seed",
            "0",
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report["summary"]["n_proposals"] == 2
    assert report["summary"]["n_valid"] == 1
    assert report["summary"]["n_invalid"] == 1
    assert out_path.exists()
    assert json.loads(out_path.read_text()) == report
