"""Tests for scripts/kober_floor_sweep.py's CHANGELOG "Floor sweep under Kober
0.9.1" additions: the new CLI options thread through without changing the
script's default behaviour, and the new summary-step criteria are computed
correctly.

Run: ``.venv/bin/python -m pytest tests/test_kober_floor_sweep.py -q``
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import kober_floor_sweep as kfs  # noqa: E402

MERGED_09_DIR = ROOT / "results" / "kober-09-merged"
DEFAULT_SUMMARY = ROOT / "results" / "kober-sweep-summary.json"


def _synthetic_ending_channel(top10_labels_and_rules: list[tuple[str, str, str | None]]) -> dict:
    """A minimal ``ending_channel`` dict: n1/n2 real values fixed comfortably
    above their p99 (parts one and two both pass), and ``top_20_alternations``
    built from ``(e1, e2, v1_rule)`` triples of single-sign endings, exactly
    the shape ``report.py``'s ``_alternation_entries`` produces."""
    alternations = []
    for e1, e2, v1_rule in top10_labels_and_rules:
        alternations.append(
            {
                "e1": [e1],
                "e2": [e2],
                "e1_label": e1,
                "e2_label": e2,
                "support": 10,
                "rule": v1_rule,
            }
        )
    return {
        "paradigm_count_total": 100,
        "n1_paradigm_count": {"p99": 10},
        "n2_alternation_support": {"max_support": {"real_value": 50, "p99": 5}},
        "top_20_alternations": alternations,
        "top_10_matched_to_rule": sum(1 for a in alternations[:10] if a["rule"] is not None),
    }


class TestCriterionAPartsV3:
    def test_part_three_recomputed_at_v3_not_read_from_stored_field(self):
        """TA/TE is grammar only under reference version 3 (rule_v1=None,
        rule_v3='consonant_stem_case': results/kober-reference-v3-table.json's
        own full_corpus_top_50_gained_rule_under_v3_over_v1 list, rank 15).
        Seven such pairs give a stored ``top_10_matched_to_rule`` of 0 (every
        v1 ``rule`` is None) but a v3-recomputed count of 7 -- part three must
        follow the recomputation, not the stored field."""
        pairs = [("TA", "TE", None)] * 7 + [("X1", "Y1", None), ("X2", "Y2", None), ("X3", "Y3", None)]
        ec = _synthetic_ending_channel(pairs)
        d = {"ending_channel": ec}
        assert ec["top_10_matched_to_rule"] == 0  # the stored, v1-graded field
        part1, part2, part3 = kfs.criterion_a_parts_v3(d)
        assert (part1, part2) == (True, True)
        assert part3 is True  # 7 of 10 matched at v3, even though the stored field says 0

    def test_part_three_false_when_fewer_than_seven_match_at_v3(self):
        pairs = [("TA", "TE", None)] * 6 + [(f"X{i}", f"Y{i}", None) for i in range(4)]
        ec = _synthetic_ending_channel(pairs)
        _, _, part3 = kfs.criterion_a_parts_v3({"ending_channel": ec})
        assert part3 is False


class TestCriterionBPassV3:
    def test_strict_top_three_all_grammar_at_v3(self):
        pairs = [("TA", "TE", None), ("WA", "WE", None), ("JA", "JO", "gender")]
        ec = _synthetic_ending_channel(pairs)
        assert kfs.criterion_b_pass_v3({"ending_channel": ec}) is True

    def test_strict_top_three_fails_if_any_of_first_three_is_not_grammar(self):
        pairs = [("TA", "TE", None), ("ZZ", "QQ", None), ("JA", "JO", "gender")]
        ec = _synthetic_ending_channel(pairs)
        assert kfs.criterion_b_pass_v3({"ending_channel": ec}) is False


class TestDefaultBehaviourUnchanged:
    def test_default_results_dir_summary_reproduces_committed_file(self):
        """The 2026-09-11 sweep's summary must be reproducible by the
        unchanged default path (task instruction; CHANGELOG 'Floor sweep
        under Kober 0.9.1': 'default behaviour unchanged')."""
        if not DEFAULT_SUMMARY.exists():
            pytest.skip("results/kober-sweep-summary.json not present in this checkout")
        committed = json.loads(DEFAULT_SUMMARY.read_text())
        rebuilt = kfs.build_summary(kfs.RESULTS_DIR)
        assert rebuilt == committed

    def test_default_results_dir_argument_resolves_to_original_constant(self):
        assert (ROOT / "results/kober-sweep").resolve() == kfs.RESULTS_DIR

    def test_summary_paths_default_is_json_only_at_original_path(self):
        json_path, md_path = kfs._summary_paths(kfs.RESULTS_DIR)
        assert json_path == kfs.SUMMARY_PATH
        assert md_path is None

    def test_summary_paths_custom_dir_gets_json_and_markdown(self):
        custom = ROOT / "results" / "kober-sweep-09"
        json_path, md_path = kfs._summary_paths(custom)
        assert json_path == ROOT / "results" / "kober-sweep-09-summary.json"
        assert md_path == ROOT / "results" / "kober-sweep-09-summary.md"


class TestKnownCellsSwitchOnResultsDir:
    def test_is_09_detected_by_results_dir_name(self):
        assert kfs._is_09(ROOT / "results" / "kober-sweep-09") is True
        assert kfs._is_09(ROOT / "results" / "kober-sweep") is False
        assert kfs._is_09(ROOT / "results" / "kober-sweep-other") is False

    def test_known_988_reads_merged_v3_tablet_files_for_09(self):
        if not MERGED_09_DIR.exists():
            pytest.skip("results/kober-09-merged/ not present in this checkout")
        known = kfs._known_988(ROOT / "results" / "kober-sweep-09")
        assert known is not None
        assert known["n"] == 20
        files = sorted(MERGED_09_DIR.glob("kober-damos-seed0-docs*-s*.json"))
        assert known["n"] == len(files)

    def test_known_988_criterion_b_pin_matches_f040(self):
        """F-040 (docs/ai_context/kober-method.md, Version 0.9): the homophone
        merge carried Greek at 988 word types to eighteen of twenty on the
        strict top-three criterion. Regression pin against silent drift in
        criterion_b_pass_v3 or the strict-top-n reuse."""
        if not MERGED_09_DIR.exists():
            pytest.skip("results/kober-09-merged/ not present in this checkout")
        known = kfs._known_988(ROOT / "results" / "kober-sweep-09")
        assert known["criterion_b_strict_top3_all_grammar_v3"] == {"pass": 18, "of": 20}

    def test_known_full_reads_merged_seed0_for_09(self):
        path = MERGED_09_DIR / "kober-damos-seed0.json"
        if not path.exists():
            pytest.skip("results/kober-09-merged/kober-damos-seed0.json not present")
        known = kfs._known_full(ROOT / "results" / "kober-sweep-09")
        assert known is not None
        assert known["n"] == 1


class TestFindFloor:
    def test_floor_is_smallest_passing_size(self):
        sizes_block = {
            "500": {"tablet": {"criterion_a": {"all_three": 5}}},
            "750": {"tablet": {"criterion_a": {"all_three": 16}}},
            "1250": {"tablet": {"criterion_a": {"all_three": 20}}},
        }
        floor = kfs._find_floor(sizes_block, lambda g: g["criterion_a"]["all_three"])
        assert floor == {"size": 750, "reached": True}

    def test_floor_not_reached_reports_none(self):
        sizes_block = {"500": {"tablet": {"criterion_a": {"all_three": 1}}}}
        floor = kfs._find_floor(sizes_block, lambda g: g["criterion_a"]["all_three"])
        assert floor["reached"] is False
        assert floor["size"] is None

    def test_a_single_run_known_cell_of_n_one_cannot_reach_the_bar(self):
        # A "known" full-corpus cell has n=1: the raw pass count (0 or 1) can
        # never reach PASS_BAR=16, so it never registers as a floor by itself.
        sizes_block = {"3768": {"known": {"criterion_a": {"all_three": 1}}}}
        floor = kfs._find_floor(sizes_block, lambda g: g["criterion_a"]["all_three"])
        assert floor["reached"] is False


def test_cli_accepts_new_options_without_running_a_sweep():
    """--merge-homophones, --reference-version and --results-dir parse and
    take the summary-only short-circuit without touching any real results
    directory (a nonexistent custom dir just yields an empty summary)."""
    custom_name = "kober-sweep-TESTONLY-cli-smoke"
    json_path = ROOT / "results" / f"{custom_name}-summary.json"
    md_path = ROOT / "results" / f"{custom_name}-summary.md"
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "kober_floor_sweep.py"),
                "--summary-only",
                "--merge-homophones",
                "--reference-version",
                "3",
                "--results-dir",
                f"results/{custom_name}",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr
        # Any results-dir other than the exact default gets a JSON + markdown
        # pair named after it (_summary_paths); only a dir literally named
        # "kober-sweep-09" also gets the reference_version/merge_homophones/
        # floors block (_is_09), so this custom name does not -- confirming
        # the new flags parsed and ran the summary-only path without error is
        # the point of this test, not that they changed the summary shape.
        assert json_path.exists()
        assert md_path.exists()
        summary = json.loads(json_path.read_text())
        assert "reference_version" not in summary
    finally:
        json_path.unlink(missing_ok=True)
        md_path.unlink(missing_ok=True)
