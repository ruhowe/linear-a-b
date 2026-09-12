"""Claims register gates: every claim rests on current findings; every graded work is catalogued.

Run: ``.venv/bin/python -m pytest tests/test_claims.py -q``
(or ``.venv/bin/python tests/test_claims.py``).

The register is ``docs/ai_context/claims.md``. A claim whose finding is superseded or
withdrawn must be rewritten in the same commit, and this test is what notices.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from findings import FINDINGS, parse  # noqa: E402

CLAIMS = ROOT / "docs" / "ai_context" / "claims.md"
WORKS = ROOT / "docs" / "works"
GRADES = {"Shown", "Precursor", "Shown elsewhere", "Stated", "Contradicted", "Not found"}


def _section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}\n")
    nxt = text.find("\n## ", start + 1)
    return text[start: nxt if nxt != -1 else len(text)]


def _rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows[1:]  # drop the header row


def register() -> dict[str, list[str]]:
    rows = _rows(_section(CLAIMS.read_text(encoding="utf-8"), "Register"))
    return {r[0]: re.findall(r"F-\d{3}", r[3]) for r in rows if re.fullmatch(r"C-\d+", r[0])}


def ledger() -> list[list[str]]:
    return _rows(_section(CLAIMS.read_text(encoding="utf-8"), "Ledger"))


def test_every_claim_rests_on_a_current_finding() -> None:
    status = {e.id: e.status for e in parse(FINDINGS.read_text(encoding="utf-8"))}
    claims = register()
    assert claims, "no claims parsed from the Register table"
    for cid, fids in claims.items():
        assert fids, f"{cid} cites no finding"
        for fid in fids:
            assert fid in status, f"{cid} cites {fid}, which is not in FINDINGS.md"
            assert status[fid].startswith("current"), f"{cid} rests on {fid}, status {status[fid]!r}"


def test_every_claim_has_a_section_with_atoms() -> None:
    text = CLAIMS.read_text(encoding="utf-8")
    for cid in register():
        assert re.search(rf"^### {cid} · ", text, re.M), f"no section for {cid}"
        assert re.search(rf"\*\*{cid}a\.\*\*", text), f"{cid} has no atom {cid}a"


def test_ledger_rows_are_graded_and_catalogued() -> None:
    claims = register()
    for row in ledger():
        atom, work, grade = row[0], row[1], row[2]
        assert re.fullmatch(r"C-\d+[a-z]", atom) and atom[:-1] in claims, f"bad atom {atom!r}"
        assert grade.strip("*") in GRADES, f"{atom} {work}: grade {grade!r} not in the scale"
        key = re.sub(r"[\[\]]", "", work).split("(")[0].strip()
        assert (WORKS / f"{key}.md").exists(), f"{atom}: no docs/works/{key}.md for ledger work {work!r}"


def test_ledger_awareness_matches_git() -> None:
    import prior_art

    text = CLAIMS.read_text(encoding="utf-8")
    rows = prior_art.ledger(text)
    for r in rows:
        assert r["awareness"] in {"built on", "known", "independent"}, f"{r['atom']} {r['work']}: {r['awareness']!r}"
    errors = prior_art.check(rows, prior_art.atom_findings(text))
    assert not errors, "\n".join(errors)


def test_every_atom_has_a_status_row() -> None:
    text = CLAIMS.read_text(encoding="utf-8")
    atoms = set(re.findall(r"^- \*\*(C-\d+[a-z])\.\*\*", text, re.M))
    status = {r[0] for r in _rows(_section(text, "Atom status"))}
    assert atoms == status, f"atoms without status: {sorted(atoms - status)}; status without atom: {sorted(status - atoms)}"


def test_plain_english_summary_covers_every_atom() -> None:
    """docs/guides/what-we-found.md is the people-facing version; it must not drift."""
    text = CLAIMS.read_text(encoding="utf-8")
    atoms = set(re.findall(r"^- \*\*(C-\d+[a-z])\.\*\*", text, re.M))
    guide = (ROOT / "docs" / "guides" / "what-we-found.md").read_text(encoding="utf-8")
    cited = set(re.findall(r"C-\d+[a-z]", " ".join(re.findall(r"<!--(.*?)-->", guide, re.S))))
    assert atoms <= cited, f"atoms missing from what-we-found.md: {sorted(atoms - cited)}"


if __name__ == "__main__":
    test_plain_english_summary_covers_every_atom()
    test_every_claim_rests_on_a_current_finding()
    test_every_claim_has_a_section_with_atoms()
    test_ledger_rows_are_graded_and_catalogued()
    test_ledger_awareness_matches_git()
    test_every_atom_has_a_status_row()
    print("ok")
