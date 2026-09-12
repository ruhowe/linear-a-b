"""README catalogue counts: the scope paragraph must match the work pages' flags.

Run: ``.venv/bin/python -m pytest tests/test_readme_counts.py -q``

The README states how many works are catalogued, how many are verified from a primary
text (flags Y and V), from a pointer (P) and from a search snippet (S), and how many
concern each script. An outside review found those figures stale on 2026-09-12; this
test keeps them tied to the pages.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKS = ROOT / "docs" / "works"
README = ROOT / "README.md"

SENTENCE = re.compile(
    r"(\d+) works, of which (\d+) are verified from a primary text \(flags Y\s+and V\), "
    r"(\d+) are recorded from a reliable pointer but unread \(P\), and (\d+) rest on a "
    r"search\s+snippet \(S\); (\d+) concern Linear A and (\d+) Linear B",
    re.S,
)


def page_counts() -> tuple[int, Counter, Counter]:
    flags: Counter = Counter()
    scripts: Counter = Counter()
    pages = sorted(WORKS.glob("*.md"))
    for page in pages:
        front = page.read_text(encoding="utf-8").split("\n---", 1)[0]
        v = re.search(r"^verified:\s*(\w+)", front, re.M)
        flags[v.group(1) if v else "?"] += 1
        s = re.search(r"^scripts:\s*\[([^\]]*)\]", front, re.M)
        for name in (x.strip() for x in (s.group(1).split(",") if s else [])):
            scripts[name] += 1
    return len(pages), flags, scripts


def test_readme_scope_counts_match_pages() -> None:
    m = SENTENCE.search(README.read_text(encoding="utf-8"))
    assert m, "README scope sentence not found; update the test's pattern with the sentence"
    total, primary, pointer, snippet, a, b = map(int, m.groups())
    n, flags, scripts = page_counts()
    assert total == n, f"README says {total} works, docs/works has {n}"
    assert primary == flags["Y"] + flags["V"], f"README primary {primary}, pages Y+V {flags['Y'] + flags['V']}"
    assert pointer == flags["P"], f"README pointer {pointer}, pages P {flags['P']}"
    assert snippet == flags["S"], f"README snippet {snippet}, pages S {flags['S']}"
    assert set(flags) <= {"Y", "V", "P", "S"}, f"unexpected flags: {dict(flags)}"
    assert a == scripts["A"], f"README Linear A {a}, pages {scripts['A']}"
    assert b == scripts["B"], f"README Linear B {b}, pages {scripts['B']}"


if __name__ == "__main__":
    test_readme_scope_counts_match_pages()
    print("ok")
