#!/usr/bin/env python3
"""Rescore every existing Kober results file under the reference lists revised
by Kober 0.6 and Kober 0.8, without rerunning anything (CHANGELOG "0.6", "0.8",
A-037).

Stage 1's own statistics (paradigm count, alternation support, each top-20
alternation's stored "rule" field, both nulls) are untouched: they are read,
never recomputed. Only new ``reference_v2`` and ``reference_v3`` blocks are
added, each computed from data already in the file:

- for the ``ending_channel`` and ``prefix_channel`` blocks, the top-20
  alternations' own ``e1``/``e2`` are regraded under
  ``kober.reference.is_grammar(e1, e2, version=2)`` (which also tries rule 11,
  ethnic derivation) and, separately, ``version=3`` (which also tries rules 12
  to 22, CHANGELOG "0.8"); ``matched_strict`` reports how many of the strict
  top 3, 5 and 10 (the same order the file's own ``top_20_alternations`` is
  already in -- support descending, then the ending pair in sorted
  lexicographic order, ``paradigms.ranked_alternations``) match a rule under
  that version;
- wherever the file already carries a strict grammar-match *null* block
  (``ending_channel.grammar_match_null_strict``, ``context.
  grammar_match_null_strict_stratified``, or ``role_tiebreak.
  grammar_match_null_role_tiebreak``), that null cannot be rescored from the
  stored summary statistics alone -- grading a null draw under the new rule
  needs the draw's own support mapping, which is not what gets written to
  disk -- so the corresponding ``reference_v2``/``reference_v3`` subsection
  records ``"null": "not rescorable from stored summaries; rerun required"``
  and nothing else. Kober 0.6's and 0.8's own nulls are rerun separately
  (``scripts/kober_run.py --reference-version 2`` into
  ``results/kober-grammar-null-v2/``, ``--reference-version 3`` into
  ``results/kober-grammar-null-v3/``).

A file without an ``ending_channel`` key (an aggregate table, a summary, or a
diagnostic with its own unrelated shape) is left alone.

Idempotent: each block is always recomputed from the file's own stage-1 data
(never from a ``reference_v2``/``reference_v3`` block already present), so
running this twice writes the same bytes both times. Running this script adds
or refreshes ``reference_v3`` without disturbing an existing ``reference_v2``
block (both are computed independently from the same stage-1 data and written
as separate top-level keys).

    .venv/bin/python scripts/kober_rescore_reference.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from kober.reference import is_grammar  # noqa: E402

RESULTS_DIR = ROOT / "results"

# The directories and top-level glob named in the task: every Kober per-run
# results file lives in one of these.
_SCAN_DIRS = ("kober-sweep", "kober-grammar-null", "kober-context", "kober-role-tiebreak")

_STRICT_NS = (3, 5, 10)

_NOT_RESCORABLE = "not rescorable from stored summaries; rerun required"

# Excluded outright, not merely skipped after reading: a concurrent read-only
# diagnostic (scripts/kober_list_homogeneity.py) owns this file while this
# script runs, and the task instructions are not to touch its script or its
# results, reads included.
_EXCLUDE_NAMES = {"kober-list-homogeneity-damos.json"}


def _iter_candidate_files() -> list[Path]:
    files = sorted(RESULTS_DIR.glob("kober-*.json"))
    for sub in _SCAN_DIRS:
        d = RESULTS_DIR / sub
        if d.is_dir():
            files.extend(sorted(d.glob("*.json")))
    return [f for f in files if f.name not in _EXCLUDE_NAMES]


def _rescore_channel(channel: dict, version: int) -> dict:
    """``reference_v{version}`` subsection for one channel (ending or prefix):
    each top-20 alternation's rule under ``version``, and the strict
    top-3/5/10 matched counts under it. ``channel["top_20_alternations"]`` is
    already in strict rank order (report.py's ``ranked_alternations``), so a
    strict top-n is simply its first n entries -- the same reading
    ``kober_precision_table.py``'s ``_strict_top_n_matched`` and the file's
    own ``top_10_matched_to_rule`` use.
    """
    top_20 = channel.get("top_20_alternations", [])
    rescored = []
    for a in top_20:
        e1, e2 = tuple(a["e1"]), tuple(a["e2"])
        rescored.append(
            {
                "e1_label": a["e1_label"],
                "e2_label": a["e2_label"],
                "support": a["support"],
                f"rule_v{version}": is_grammar(e1, e2, version=version),
            }
        )
    matched_strict = {
        str(n): sum(1 for a in rescored[:n] if a[f"rule_v{version}"] is not None) for n in _STRICT_NS
    }
    out = {f"top_20_v{version}": rescored, "matched_strict": matched_strict}
    if "grammar_match_null_strict" in channel:
        out["null"] = _NOT_RESCORABLE
    return out


def _rescore_at_version(report: dict, version: int, changelog_version: str) -> dict | None:
    """The ``reference_v{version}`` block for ``report``, or None if it is not
    a per-run Kober results file (no ``ending_channel``)."""
    if "ending_channel" not in report:
        return None
    block: dict = {"reference_version": version, "version": changelog_version}
    block["ending_channel"] = _rescore_channel(report["ending_channel"], version)
    if "prefix_channel" in report:
        block["prefix_channel"] = _rescore_channel(report["prefix_channel"], version)
    if "context" in report and "grammar_match_null_strict_stratified" in report["context"]:
        block["context"] = {"null": _NOT_RESCORABLE}
    if "role_tiebreak" in report and "grammar_match_null_role_tiebreak" in report["role_tiebreak"]:
        block["role_tiebreak"] = {"null": _NOT_RESCORABLE}
    return block


def rescore(report: dict) -> dict | None:
    """The ``reference_v2`` block for ``report`` (Kober 0.6), or None if it is
    not a per-run Kober results file (no ``ending_channel``). Kept for the
    pre-existing v2-only entry point; ``main`` also computes ``reference_v3``
    (Kober 0.8) the same way, via ``_rescore_at_version``."""
    return _rescore_at_version(report, 2, "0.6")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    args = ap.parse_args()

    files = _iter_candidate_files()
    rescored = 0
    skipped = 0
    unchanged = 0
    for path in files:
        report = json.loads(path.read_text())
        block_v2 = _rescore_at_version(report, 2, "0.6")
        block_v3 = _rescore_at_version(report, 3, "0.8")
        if block_v2 is None:
            skipped += 1
            continue
        changed_here = False
        if report.get("reference_v2") != block_v2:
            report["reference_v2"] = block_v2
            changed_here = True
        if report.get("reference_v3") != block_v3:
            report["reference_v3"] = block_v3
            changed_here = True
        if not changed_here:
            unchanged += 1
            continue
        rescored += 1
        if not args.dry_run:
            path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    verb = "would rescore" if args.dry_run else "rescored"
    print(
        f"{verb} {rescored} file(s); {unchanged} already up to date; "
        f"{skipped} skipped (no ending_channel) of {len(files)} scanned"
    )


if __name__ == "__main__":
    main()
