#!/usr/bin/env python3
"""Query the bibliography without reading the whole thing.

    .venv/bin/python scripts/bib.py --stats
    .venv/bin/python scripts/bib.py --script A --domain computational
    .venv/bin/python scripts/bib.py --standing untested --full
    .venv/bin/python scripts/bib.py --verified P --access paywalled   # the re-verify queue
    .venv/bin/python scripts/bib.py --tested-by semitic-null-test
    .venv/bin/python scripts/bib.py --grep entropy

Exists because the catalogue is data. An agent asking "what is published on Linear A
computationally, and how much of it did we actually verify" should get eight lines, not
a 260-line file. Filters combine with AND.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

WORKS = Path(__file__).resolve().parents[1] / "docs" / "works"

VERIFIED_MEANING = {
    "Y": "primary source fetched",
    "P": "secondary only, restated or from a review",
    "S": "search snippet only",
    "N": "not checked",
}


def load(path: Path = WORKS) -> list[dict]:
    """Read the frontmatter of every work page.

    The pages are the source of truth rather than a single catalogue file, because a
    page can be linked, reviewed and corrected on its own. The frontmatter keeps them
    queryable.
    """
    try:
        import yaml
    except ModuleNotFoundError:
        sys.exit("PyYAML not installed. Run: .venv/bin/pip install pyyaml")
    if not path.is_dir():
        sys.exit(f"No work pages at {path}. Run scripts/split_bibliography.py first.")

    works = []
    for page in sorted(path.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        _, _, rest = text.partition("---\n")
        front, _, body = rest.partition("\n---")
        try:
            record = yaml.safe_load(front) or {}
        except yaml.YAMLError as exc:
            print(f"skipping {page.name}: {exc}", file=sys.stderr)
            continue
        record["page"] = str(page.relative_to(path.parents[1]))
        record["claim"] = _first_section(body, "What it claims")
        record["notes"] = _first_section(body, "Our assessment")
        works.append(record)
    return works


def _first_section(body: str, heading: str) -> str:
    """The first paragraph under a named heading, for one-line display."""
    marker = f"## {heading}"
    if marker not in body:
        return ""
    after = body.split(marker, 1)[1]
    for para in after.split("\n\n"):
        cleaned = para.strip()
        if cleaned and not cleaned.startswith("#"):
            return " ".join(cleaned.split())
    return ""


def _has(record: dict, field: str, value: str) -> bool:
    got = record.get(field)
    if got is None:
        return False
    if isinstance(got, list):
        return any(value.lower() == str(g).lower() for g in got)
    return value.lower() == str(got).lower()


def filter_works(works: list[dict], args) -> list[dict]:
    out = works
    if args.script:
        out = [w for w in out if _has(w, "scripts", args.script)]
    if args.domain:
        out = [w for w in out if _has(w, "domains", args.domain)]
    if args.standing:
        out = [w for w in out if _has(w, "standing", args.standing)]
    if args.verified:
        out = [w for w in out if _has(w, "verified", args.verified)]
    if args.access:
        out = [w for w in out if _has(w, "access", args.access)]
    if args.tested_by:
        out = [w for w in out if _has(w, "tested_by", args.tested_by)]
    if args.year_from:
        out = [w for w in out if isinstance(w.get("year"), int) and w["year"] >= args.year_from]
    if args.grep:
        needle = args.grep.lower()
        out = [w for w in out if needle in str(w).lower()]
    return out


def show(works: list[dict], *, full: bool) -> None:
    for w in works:
        authors = ", ".join(w.get("authors", [])) or "?"
        scripts = "/".join(w.get("scripts", []))
        flag = w.get("verified", "?")
        print(f"\n[{w['key']}] {authors} {w.get('year','')} — {w.get('title','')}")
        print(f"    {w.get('venue','')} · {scripts} · {w.get('standing','')} · verified {flag} · {w.get('access','')}")
        print(f"    {w.get('claim','')}")
        if full:
            if w.get("notes"):
                print(f"    NOTE: {' '.join(str(w['notes']).split())}")
            if w.get("tested_by"):
                print(f"    tested by: {', '.join(w['tested_by'])}")
            print(f"    ref: {w.get('ref','—')}")
    print(f"\n{len(works)} work(s).")


def stats(works: list[dict]) -> None:
    def tally(field: str) -> Counter:
        c: Counter = Counter()
        for w in works:
            got = w.get(field)
            if isinstance(got, list):
                c.update(got)
            elif got is not None:
                c[got] += 1
        return c

    print(f"{len(works)} works catalogued.\n")
    for field in ("scripts", "domains", "standing", "verified", "access"):
        rows = tally(field).most_common()
        print(f"{field}:")
        for name, n in rows:
            extra = f"  ({VERIFIED_MEANING[name]})" if field == "verified" and name in VERIFIED_MEANING else ""
            print(f"    {str(name):<18} {n:>3}{extra}")
        print()

    unverified = [w for w in works if w.get("verified") in ("P", "S", "N")]
    print(f"Re-verify before print: {len(unverified)} of {len(works)} rest on secondary "
          f"or snippet evidence.")
    tested = [w for w in works if w.get("tested_by")]
    print(f"Put under test by this repo: {len(tested)} "
          f"({', '.join(w['key'] for w in tested)})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--script", help="A, B, CH, CM, Cypriot, Greek, other")
    p.add_argument("--domain", help="computational, philology, palaeography, imaging, edition, methodology, survey, decipherment-claim, resource")
    p.add_argument("--standing", help="accepted, contested, untested, fringe, superseded, n/a")
    p.add_argument("--verified", help="Y, P, S, N")
    p.add_argument("--access", help="open, paywalled, blocked, offline, print-only")
    p.add_argument("--tested-by", dest="tested_by", help="an instance file, e.g. semitic-null-test")
    p.add_argument("--year-from", dest="year_from", type=int)
    p.add_argument("--grep", help="free-text search across every field")
    p.add_argument("--full", action="store_true", help="include notes and refs")
    p.add_argument("--stats", action="store_true", help="summarise the whole catalogue")
    args = p.parse_args()

    works = load()
    if args.stats:
        stats(filter_works(works, args))
        return
    show(filter_works(works, args), full=args.full)


if __name__ == "__main__":
    main()
