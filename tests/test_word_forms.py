"""The one exception in LICENSE.md: word forms live only in the toponym test's files.

Run: ``.venv/bin/python -m pytest tests/test_word_forms.py -q``

LICENSE.md says the value-transfer test's files are the only data files holding word
forms, and counts what they hold. An outside review on 2026-09-12 found the first
version of that paragraph wrong twice (it missed the matched Linear A words and
undercounted the place names). These tests make both statements checkable: no other
results or spike JSON carries a word-shaped field, and the counts in LICENSE.md are the
counts in the files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LICENSE = ROOT / "LICENSE.md"
WORD_KEYS = {"surface", "lexicon_word", "matched_pairs", "dropped"}


def data_files() -> list[Path]:
    return sorted([*ROOT.glob("results/**/*.json"), *ROOT.glob("spikes/**/*.json")])


def is_exception(path: Path) -> bool:
    return path.name.startswith("toponym_test")


def word_fields(obj, path: str = "") -> list[str]:
    """Keys that hold word forms: the toponym lexicon and match fields, and any
    ``linear_a`` key whose value is a sequence of sign labels."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}"
            if key in WORD_KEYS:
                found.append(here)
            if key == "linear_a" and isinstance(value, list) and all(isinstance(x, str) for x in value):
                found.append(here)
            found += word_fields(value, here)
    elif isinstance(obj, list):
        for item in obj:
            found += word_fields(item, path + "[]")
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
    test_word_forms_only_in_the_exception_files()
    test_licence_counts_match_the_files()
    print("ok")
