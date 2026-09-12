#!/usr/bin/env python3
"""Check and display how this repo's claims relate to earlier work.

    .venv/bin/python scripts/prior_art.py              # check every Ledger row's awareness against git
    .venv/bin/python scripts/prior_art.py --suggest    # print the awareness git supports, row by row
    .venv/bin/python scripts/prior_art.py --write-view # regenerate the grouped view in claims.md

Awareness is the one Ledger column that must not rest on memory, because "we reached
this independently" is the claim a reader will doubt. It is read from git:

- first seen: the first commit anywhere in the repo whose diff mentions the work, by its
  catalogue key or by first-author surname followed by the year on the same line.
- finding commit: the commit that added the earliest FINDINGS entry the atom cites.
- design files: the FINDINGS entry, CHANGELOG.md, ASSUMPTIONS.md and the method's HENGE
  file(s), as they stood at the finding commit.

independent = first seen after the finding commit. known = first seen at or before it.
built on = known, and mentioned in a design file at the finding commit. The check fails
only on a claim the history contradicts; it never upgrades "known" to "built on" by itself.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "docs" / "ai_context" / "claims.md"
WORKS = ROOT / "docs" / "works"
START, END = "<!-- view:start -->", "<!-- view:end -->"

HENGE_FOR = {
    "kober": ["docs/ai_context/kober-method.md"],
    "etymological": ["docs/ai_context/hypothesis-harness.md", "docs/ai_context/semitic-null-test.md"],
    "restoration": ["docs/ai_context/linearb-restoration.md"],
}
GROUPS = [
    ("built on", "Built on: we knew the work and used it in the design or reading of the finding"),
    ("known", "Known, not used: in our survey before the finding, not drawn on by it"),
    ("independent", "Reached independently: first mentioned in the repo after the finding"),
]

sys.path.insert(0, str(ROOT / "scripts"))
from findings import FINDINGS, parse  # noqa: E402


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _rows(text: str, heading: str) -> list[list[str]]:
    start = text.index(f"## {heading}\n")
    nxt = text.find("\n## ", start + 1)
    out = []
    for line in text[start: nxt if nxt != -1 else len(text)].splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out[1:]


def ledger(text: str | None = None) -> list[dict]:
    text = text if text is not None else CLAIMS.read_text(encoding="utf-8")
    cols = ["atom", "work", "grade", "relation", "awareness", "evidence", "V"]
    return [dict(zip(cols, r)) for r in _rows(text, "Ledger")]


def atom_findings(text: str | None = None) -> dict[str, list[str]]:
    """Map each atom (C-1a ...) to the F-ids cited in its bullet."""
    text = text if text is not None else CLAIMS.read_text(encoding="utf-8")
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"^- \*\*(C-\d+[a-z])\.\*\*(.*?)(?=^- |\n### |\n## |\Z)", text, re.M | re.S):
        out[m.group(1)] = re.findall(r"F-\d{3}", m.group(2))
    return out


def work_key(cell: str) -> str:
    return re.sub(r"[\[\]]", "", cell).split("(")[0].strip()


def search_regex(key: str) -> str:
    """Catalogue key; first-author surname then the year within one line (table rows
    included); and any ``aliases:`` listed in the work page's frontmatter, for works the
    repo names without a year ("Kober") or by an identifier ("48600107")."""
    page = WORKS / f"{key}.md"
    year = re.search(r"(\d{4})", key)
    lead = re.match(r"[a-z]+", key)
    surname = lead.group(0).capitalize() if lead else key
    aliases: list[str] = []
    if page.exists():
        front = page.read_text(encoding="utf-8").split("\n---", 1)[0]
        a = re.search(r"^authors:\s*\[?\s*([^,\]\n]+)", front, re.M)
        y = re.search(r"^year:\s*(\d{4})", front, re.M)
        al = re.search(r"^aliases:\s*\[([^\]]*)\]", front, re.M)
        if a:
            surname = a.group(1).strip().strip("'\"").split(",")[0].split()[-1]
        if y:
            year = y
        if al:
            aliases = [s.strip().strip("'\"") for s in al.group(1).split(",") if s.strip()]
    pat = re.escape(key)
    if year:
        pat += f"|{re.escape(surname)}.{{0,60}}{year.group(1)}"
    for alias in aliases:
        pat += f"|{re.escape(alias)}"
    return pat


@lru_cache(maxsize=None)
def first_seen(pattern: str) -> str | None:
    out = git("log", "--reverse", "-E", f"-G{pattern}", "--format=%H", "--", ".").split()
    return out[0] if out else None


@lru_cache(maxsize=None)
def finding_commit(fid: str) -> str | None:
    out = git("log", "--reverse", "-S", f"## {fid} ·", "--format=%H", "--", "FINDINGS.md").split()
    return out[0] if out else None


def is_ancestor(a: str, b: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=ROOT).returncode == 0


def in_design(pattern: str, fid: str, commit: str) -> bool:
    entries = {e.id: e for e in parse(git("show", f"{commit}:FINDINGS.md"))}
    method = entries[fid].method if fid in entries else "other"
    texts = [entries[fid].body if fid in entries else ""]
    for path in ["CHANGELOG.md", "ASSUMPTIONS.md", *HENGE_FOR.get(method, [])]:
        try:
            texts.append(git("show", f"{commit}:{path}"))
        except subprocess.CalledProcessError:
            pass
    rx = re.compile(pattern)
    return any(rx.search(t) for t in texts)


def supported(row: dict, atoms: dict[str, list[str]]) -> tuple[str, str]:
    """(awareness git supports, reason)."""
    key = work_key(row["work"])
    fids = atoms.get(row["atom"], [])
    commits = [c for c in (finding_commit(f) for f in fids) if c]
    if not commits:
        return "?", f"{row['atom']} cites no finding with a commit"
    pairs = sorted(zip(commits, fids), key=lambda cf: int(git("log", "-1", "--format=%ct", cf[0]).strip()))
    fc, fid = pairs[0]
    pat = search_regex(key)
    seen = first_seen(pat)
    if seen is None or not is_ancestor(seen, fc):
        return "independent", f"first seen {seen[:7] if seen else 'never'}, after {fid} ({fc[:7]})"
    if in_design(pat, fid, fc):
        return "built on", f"cited in design files at {fid} ({fc[:7]})"
    return "known", f"first seen {seen[:7]}, before {fid} ({fc[:7]}), not in its design files"


def check(rows: list[dict], atoms: dict[str, list[str]]) -> list[str]:
    errors = []
    for r in rows:
        got, why = supported(r, atoms)
        claimed = r["awareness"]
        if claimed == "independent" and got != "independent":
            errors.append(f"{r['atom']} {r['work']}: marked independent, but {why}")
        if claimed in ("known", "built on") and got == "independent":
            errors.append(f"{r['atom']} {r['work']}: marked {claimed}, but {why}")
        if claimed == "built on" and got == "known":
            errors.append(f"{r['atom']} {r['work']}: marked built on, but {why}")
    return errors


def view(rows: list[dict]) -> str:
    parts = []
    for aw, title in GROUPS:
        sel = sorted((r for r in rows if r["awareness"] == aw), key=lambda r: (r["atom"], r["work"]))
        parts.append(f"**{title}.** {len(sel)} rows.\n")
        if sel:
            parts.append("| atom | work | their grade | ours |\n|---|---|---|---|")
            parts += [f"| {r['atom']} | {r['work']} | {r['grade']} | {r['relation']} |" for r in sel]
        parts.append("")
    return "\n".join(parts).rstrip()


def write_view(text: str, rows: list[dict]) -> str:
    block = f"{START}\n{view(rows)}\n{END}"
    return text[: text.index(START)] + block + text[text.index(END) + len(END):]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suggest", action="store_true")
    ap.add_argument("--write-view", action="store_true")
    args = ap.parse_args()
    text = CLAIMS.read_text(encoding="utf-8")
    rows, atoms = ledger(text), atom_findings(text)
    if args.suggest:
        for r in rows:
            got, why = supported(r, atoms)
            flag = "" if got == r["awareness"] else "  <-- differs"
            print(f"{r['atom']:6} {work_key(r['work']):28} marked {r['awareness']:12} git {got:12} {why}{flag}")
        return
    if args.write_view:
        CLAIMS.write_text(write_view(text, rows), encoding="utf-8")
        print(f"view written: {len(rows)} rows")
        return
    errors = check(rows, atoms)
    print("\n".join(errors) if errors else f"ok: {len(rows)} rows consistent with git")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
