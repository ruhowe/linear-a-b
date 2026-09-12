"""Tests for --extra-word-types (CHANGELOG "Supplement sensitivity (F-047)"),
added to scripts/toponym_test.py and scripts/kober_run.py.

Covers the two pure helpers each script exposes: parsing the private JSONL, and
appending its tuples to a word-type set before any statistic runs. Does not
invoke either script's ``main()``, since that runs the real 400/200-draw
protocol against the loaded corpora; the byte-identical-without-the-option
check for each script's actual output is done separately (regenerate an
existing small results file and diff, not a pytest assertion).

Run: ``.venv/bin/python -m pytest tests/test_extra_word_types.py -q``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import kober_run as kr  # noqa: E402
import toponym_test as tt  # noqa: E402
from kober.words import WordTypes  # noqa: E402

EXTRA_JSONL = """# source: test fixture, not a real corpus derivation
["I", "DA", "DA"]
["DI", "NA", "U"]
"""


def _write_extra_file(tmp_path: Path) -> Path:
    path = tmp_path / "extra-word-types.jsonl"
    path.write_text(EXTRA_JSONL)
    return path


# --------------------------------------------------------------------------
# toponym_test.py
# --------------------------------------------------------------------------


def test_toponym_load_extra_word_types_skips_comment_and_upper_cases(tmp_path):
    path = _write_extra_file(tmp_path)
    loaded = tt.load_extra_word_types(path)
    assert loaded == [("I", "DA", "DA"), ("DI", "NA", "U")]


def test_toponym_load_extra_word_types_upper_cases_lowercase_input(tmp_path):
    path = tmp_path / "lower.jsonl"
    path.write_text('# source: test\n["tu", "pi", "ta"]\n')
    assert tt.load_extra_word_types(path) == [("TU", "PI", "TA")]


def test_toponym_merge_extra_word_types_appends_to_gorila_only():
    per_edition_words = {
        "gorila": [("A", "B", "C")],
        "sigla": [("X", "Y", "Z")],
    }
    extra = [("I", "DA", "DA"), ("DI", "NA", "U")]
    merged = tt.merge_extra_word_types(per_edition_words, extra, edition="gorila")

    assert set(merged["gorila"]) == {("A", "B", "C"), ("I", "DA", "DA"), ("DI", "NA", "U")}
    assert merged["sigla"] == [("X", "Y", "Z")]
    # Original input is untouched (merge returns a new dict/list).
    assert per_edition_words["gorila"] == [("A", "B", "C")]


def test_toponym_merge_extra_word_types_absent_option_unchanged():
    per_edition_words = {
        "gorila": [("A", "B", "C")],
        "sigla": [("X", "Y", "Z")],
    }
    merged = tt.merge_extra_word_types(per_edition_words, [], edition="gorila")
    assert merged == per_edition_words


def test_toponym_merge_extra_word_types_dedupes_against_existing():
    per_edition_words = {"gorila": [("I", "DA", "DA")]}
    extra = [("I", "DA", "DA"), ("DI", "NA", "U")]
    merged = tt.merge_extra_word_types(per_edition_words, extra, edition="gorila")
    assert sorted(merged["gorila"]) == [("DI", "NA", "U"), ("I", "DA", "DA")]


# --------------------------------------------------------------------------
# kober_run.py
# --------------------------------------------------------------------------


def test_kober_load_extra_word_types_skips_comment_and_upper_cases(tmp_path):
    path = _write_extra_file(tmp_path)
    loaded = kr.load_extra_word_types(path)
    assert loaded == [("I", "DA", "DA"), ("DI", "NA", "U")]


def test_kober_extract_word_types_with_extra_appends_two_tuple_file(tmp_path):
    path = _write_extra_file(tmp_path)
    extra = kr.load_extra_word_types(path)

    base = WordTypes(words=frozenset({("A", "B")}), labels_changed=3, labels_seen=40)

    def fake_base_extract_word_types(documents, merge_homophones: bool = False):
        return base

    wrapped = kr.extract_word_types_with_extra(fake_base_extract_word_types, extra)
    result = wrapped(documents=[])

    assert result.words == frozenset({("A", "B"), ("I", "DA", "DA"), ("DI", "NA", "U")})
    # labels_changed/labels_seen describe the real corpus's own signary, not
    # this addition, and are carried through unchanged.
    assert result.labels_changed == base.labels_changed
    assert result.labels_seen == base.labels_seen


def test_kober_extract_word_types_with_extra_absent_option_unchanged():
    base = WordTypes(words=frozenset({("A", "B")}), labels_changed=3, labels_seen=40)

    def fake_base_extract_word_types(documents, merge_homophones: bool = False):
        return base

    wrapped = kr.extract_word_types_with_extra(fake_base_extract_word_types, [])
    result = wrapped(documents=[])

    # No extra types: the wrapper returns the base call's own result, unchanged.
    assert result is base
