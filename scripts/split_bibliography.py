#!/usr/bin/env python3
"""Convert bibliography.yaml into one markdown page per work.

    .venv/bin/python scripts/split_bibliography.py

A single YAML catalogue is queryable but hard to discuss. GitHub review comments attach
to lines in a diff, and an Issue can only link to a file or a line range, so a hundred
works in one file all share one comment thread. One file per work gives each source its
own page, its own permalink, its own review thread, and its own edit history.

The frontmatter keeps everything machine-readable, so `bib.py` still answers the same
questions. The body is for prose a YAML field cannot hold: what the work argues, what we
checked and how, and where the source material is.

Run once. After that the pages are the source of truth and this script is history.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "ai_context" / "bibliography.yaml"
OUT = ROOT / "docs" / "works"

FIELD_ORDER = [
    "key", "authors", "year", "title", "venue", "ref",
    "scripts", "domains", "standing", "verified", "verified_on",
    "access", "tested_by", "bibliography",
]


def yaml_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    if isinstance(value, str) and (":" in value or value.startswith(("*", "&", "["))):
        return '"' + value.replace('"', "'") + '"'
    return str(value)


def page(rec: dict) -> str:
    lines = ["---"]
    for field in FIELD_ORDER:
        if field in rec and rec[field] not in (None, [], ""):
            lines.append(f"{field}: {yaml_value(rec[field])}")
    lines.append("---")
    lines.append("")

    authors = ", ".join(rec.get("authors", [])) or "Unknown"
    lines.append(f"# {authors} ({rec.get('year', 'n.d.')}), *{rec.get('title', rec['key'])}*")
    lines.append("")
    lines.append(f"{rec.get('venue', 'Venue unrecorded')}.")
    lines.append("")

    lines.append("## What it claims")
    lines.append("")
    lines.append(rec.get("claim", "Not yet summarised.") or "Not yet summarised.")
    lines.append("")

    if rec.get("claim_shape"):
        lines.append(" ".join(str(rec["claim_shape"]).split()))
        lines.append("")

    lines.append("## Where to find it")
    lines.append("")
    ref = rec.get("ref")
    if ref and ref != "n/a":
        if str(ref).startswith("10."):
            lines.append(f"- DOI [{ref}](https://doi.org/{ref})")
        elif str(ref).startswith("arXiv:"):
            ident = str(ref).split(":", 1)[1]
            lines.append(f"- [{ref}](https://arxiv.org/abs/{ident})")
        elif "/" in str(ref):
            url = ref if str(ref).startswith("http") else f"https://{ref}"
            lines.append(f"- [{ref}]({url})")
        else:
            lines.append(f"- Reference: {ref}")
    else:
        lines.append("- No stable identifier recorded. Add one if you find it.")
    lines.append(f"- Access: **{rec.get('access', 'unknown')}**")
    lines.append("")

    lines.append("## Our assessment")
    lines.append("")
    verified = rec.get("verified", "N")
    meaning = {
        "Y": "We fetched and read the primary source.",
        "P": "We have only seen this restated elsewhere, in a review, index record or later paper. Re-verify before citing it in print.",
        "S": "We have only seen a search snippet. Treat every number in this record as unconfirmed.",
        "N": "Not checked.",
    }.get(verified, "Not checked.")
    lines.append(f"Verification **{verified}**. {meaning}")
    lines.append("")
    if rec.get("notes"):
        lines.append(" ".join(str(rec["notes"]).split()))
        lines.append("")
    if rec.get("tested_by"):
        tested = ", ".join(f"[{t}](../ai_context/{t}.md)" for t in rec["tested_by"])
        lines.append(f"Put under test here in {tested}.")
        lines.append("")

    lines.append("## Discussion")
    lines.append("")
    lines.append(
        "Corrections and disagreement are welcome. Open a pull request against this "
        "file, or email ru@stornaway.io naming the file. If you are the author of this work and "
        "we have misrepresented it, say so and we will fix it."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    try:
        import yaml
    except ModuleNotFoundError:
        sys.exit("PyYAML not installed: .venv/bin/pip install pyyaml")
    if not SRC.exists():
        sys.exit(f"No bibliography at {SRC}")

    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    works = data.get("works", [])
    OUT.mkdir(parents=True, exist_ok=True)

    written = 0
    for rec in works:
        path = OUT / f"{rec['key']}.md"
        if path.exists():
            print(f"skip (exists): {path.name}")
            continue
        path.write_text(page(rec), encoding="utf-8")
        written += 1
    print(f"\nWrote {written} page(s) to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
