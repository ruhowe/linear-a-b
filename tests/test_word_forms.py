"""The one exception in LICENSE.md: word forms live only in the toponym test's files.

Run: ``.venv/bin/python -m pytest tests/test_word_forms.py -q``

LICENSE.md says the value-transfer test's files are the only data files holding word
forms, and counts what they hold. An outside review on 2026-09-12 found the first
version of that paragraph wrong twice (it missed the matched Linear A words and
undercounted the place names), and on a third read that a check by key name alone
would miss a form stored under a new key. These tests check every JSON file under
``results/`` and ``spikes/`` outside the exception files three ways:

- a key that holds word forms in the toponym files (``surface``, ``lexicon_word``,
  ``matched_pairs``, ``dropped``, or ``linear_a`` holding a list of labels);
- any string, as a value or a key, that is a hyphenated run of three or more sign
  labels (``PA-I-TO``, ``a-sa-sa-ra-me``). Kober's alternation labels are one or two
  signs, and length bands such as ``6-10`` are not labels, so neither matches;
- any list of three or more sign labels that is not in sorted order. Sign classes and
  consonant sets (grid classes such as U, WE, WO) are stored sorted; a word stored as a
  list keeps its reading order.

Prose is outside the check: Markdown write-ups quote published readings from the works
they discuss, under LICENSE.md's quotation line.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LICENSE = ROOT / "LICENSE.md"
WORD_KEYS = {"surface", "lexicon_word", "matched_pairs", "dropped"}
LABEL = r"(?:\*?\d{2,3}|[A-Z]{1,3}[0-9₂₃]?|[a-z]{1,3}[0-9₂₃]?)"
SEQUENCE = re.compile(rf"^{LABEL}(?:-{LABEL}){{2,}}$")
ONE_LABEL = re.compile(rf"^{LABEL}$")


def data_files() -> list[Path]:
    return sorted([*ROOT.glob("results/**/*.json"), *ROOT.glob("spikes/**/*.json")])


def is_exception(path: Path) -> bool:
    return path.name.startswith("toponym_test")


def word_fields(obj, path: str = "") -> list[str]:
    """Places in a JSON document that hold, or look like, word forms."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}"
            if key in WORD_KEYS:
                found.append(here)
            if key == "linear_a" and isinstance(value, list) and all(isinstance(x, str) for x in value):
                found.append(here)
            if isinstance(key, str) and SEQUENCE.match(key):
                found.append(f"{here} (key)")
            found += word_fields(value, here)
    elif isinstance(obj, list):
        labels = [x for x in obj if isinstance(x, str)]
        if len(obj) >= 3 and len(labels) == len(obj) and all(ONE_LABEL.match(x) for x in labels) and labels != sorted(labels):
            found.append(f"{path} (unsorted label list {'-'.join(labels[:6])})")
        for i, item in enumerate(obj):
            found += word_fields(item, f"{path}[{i}]")
    elif isinstance(obj, str) and SEQUENCE.match(obj):
        found.append(f"{path} = {obj}")
    return found


def test_word_forms_only_in_the_exception_files() -> None:
    offenders = {}
    for f in data_files():
        if is_exception(f):
            continue
        try:
            fields = word_fields(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
        if fields:
            offenders[str(f.relative_to(ROOT))] = fields[:3]
    assert not offenders, f"word-shaped fields outside the LICENSE.md exception: {offenders}"


def test_the_check_sees_words_and_ignores_sign_sets() -> None:
    assert word_fields({"x": "PA-I-TO"}) and word_fields({"x": ["PA", "I", "TO"]})
    assert word_fields({"a-sa-sa-ra-me": 1}) and word_fields({"surface": "ko-no-so"})
    assert not word_fields({"class": ["U", "WE", "WO"], "consonants": ["K", "N", "T"]})
    assert not word_fields({"alternation": "JA-JO", "band": "6-10", "ending": "-ta-o"})


def exception_counts() -> tuple[int, int, int, int]:
    first = json.loads((ROOT / "results" / "toponym_test-gorila-seed0.json").read_text(encoding="utf-8"))
    lex = first["lexicons"]
    knossos = len(lex["knossos_toponyms"]["entries"]) + len(lex["knossos_toponyms"].get("dropped", []))
    pylos = len(lex["pylos_toponyms"]["entries"]) + len(lex["pylos_toponyms"].get("dropped", []))
    names = len(lex["knossos_personal_names"]["entries"])
    sequences = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "matched_pairs":
                    sequences.update(tuple(m["linear_a"]) for m in v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for f in data_files():
        if is_exception(f):
            walk(json.loads(f.read_text(encoding="utf-8")))
    return knossos, pylos, names, len(sequences)


def test_licence_counts_match_the_files() -> None:
    knossos, pylos, names, sequences = exception_counts()
    text = re.sub(r"\s+", " ", LICENSE.read_text(encoding="utf-8"))
    for phrase in (
        f"{knossos + pylos} place-name readings",
        f"{knossos} at Knossos and {pylos} at Pylos",
        f"{names} frequent Knossos personal names",
        f"{sequences} Linear A sign sequences",
    ):
        assert phrase in text, f"LICENSE.md should say '{phrase}' (counted from the toponym files)"


if __name__ == "__main__":
    test_the_check_sees_words_and_ignores_sign_sets()
    test_word_forms_only_in_the_exception_files()
    test_licence_counts_match_the_files()
    print("ok")
