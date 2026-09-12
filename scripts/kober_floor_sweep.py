#!/usr/bin/env python3
"""Floor sweep on Linear B (CHANGELOG "Kober method" -> "Floor sweep on Linear B"):
at what corpus size does Kober stage 1's criterion become readable on Greek text.

Kober 0.3 stage 1, unmodified. Two subsampling models at each of seven target
sizes (1,250, 1,500, 1,750, 2,000, 2,500, 3,000, 3,500 word types), twenty
subsample seeds (0-19) each, null seed 0, 200 draws per null, stage 1 only (no
grid flags):

    type model    --subsample N directly (word-type subsample, as F-019).
    tablet model  --subsample-docs K, K found per seed by bisection so the
                   resulting type count lands within 2% of N (A-063); the
                   document subsample is a prefix of one seeded permutation of
                   document ids (``kober.words.subsample_document_ids``), so the
                   type count is non-decreasing in K and bisection is valid.

Writes one results JSON per run under results/kober-sweep/ (aggregate numbers
only, same fields as kober_run.py's output plus a "sweep" block) and merges a
summary, results/kober-sweep-summary.json, across every run currently on disk
for each (size, model) -- so separate invocations covering different --sizes or
--model chunks merge into the same file rather than overwriting each other.

Examples, each finishing well inside a 10-minute timeout:

    .venv/bin/python scripts/kober_floor_sweep.py --sizes 1250,1500,1750,2000 --model type
    .venv/bin/python scripts/kober_floor_sweep.py --sizes 2500,3000,3500 --model type
    .venv/bin/python scripts/kober_floor_sweep.py --sizes 1250,1500 --model tablet
    ...
    .venv/bin/python scripts/kober_floor_sweep.py --bisect
        # round 3: for each model, the two adjacent coarse sizes where the
        # all-three pass count crosses 16 of 20 (from below 16 to at least 16,
        # scanning ascending, first crossing only), run their midpoint at 20
        # subsamples, and add it to the summary. Requires the coarse pass
        # (all seven sizes, both models) already on disk.

    .venv/bin/python scripts/kober_floor_sweep.py --summary-only
        # rebuild the summary from whatever run files already exist, no new runs.

CHANGELOG "Floor sweep under Kober 0.9.1, merged identities and reference list
v3" (2026-09-12) reruns this design under Kober 0.9.1, homophones merged and
graded against reference list v3, tablet model only:

    .venv/bin/python scripts/kober_floor_sweep.py --sizes 500 --model tablet \\
        --merge-homophones --reference-version 3 --results-dir results/kober-sweep-09

``--results-dir`` defaults to ``results/kober-sweep`` (this file's original
behaviour, unchanged); passing ``results/kober-sweep-09`` also switches the
summary step to (a) read the 988-word-type and full-corpus cells from
``results/kober-09-merged/`` instead of the 0.3 files, and (b) additionally
score the strict-top-three-all-grammar criterion (b) from the 2026-09-12
entry, both under reference list v3, alongside the unmodified criterion (a)
(part three regraded at v3 -- see ``criterion_a_parts_v3``'s docstring for why
the stored ``top_10_matched_to_rule`` field cannot be reused for this). The
summary is then also written as a companion ``.md`` file and gains a
``floors`` block (the entry's own rule: smallest swept size with at least 16
of 20 passing, per criterion). Neither addition touches the default
``results/kober-sweep`` path's summary shape or content.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

from kober.report import build_report  # noqa: E402
from kober.words import extract_word_types, subsample_document_ids  # noqa: E402

# Reused, not reimplemented (task instruction): the strict top-n slice and the
# grammar-match predicates already built for the 0.8 reference-list-v3 table
# (docs/ai_context/kober-method.md "Version 0.8"; A-072's strict tie-break).
from kober_reference_v3_table import _all_match, _count_matched, _strict_top_n  # noqa: E402

SIZES = [1250, 1500, 1750, 2000, 2500, 3000, 3500]
SIZES_09 = [500, 750, 1250, 1500, 1750]  # CHANGELOG "Floor sweep under Kober 0.9.1"
SUBSAMPLE_SEEDS = list(range(20))
NULL_SEED = 0
PERMS = 200
STEM_MIN = 2
TOLERANCE = 0.02  # A-063
PASS_BAR = 16  # of 20, CHANGELOG "Floor sweep on Linear B"
REFERENCE_VERSION_09 = 3  # the version the 0.9.1 sweep's own criteria (a) part 3 and (b) grade under

RESULTS_DIR = ROOT / "results" / "kober-sweep"
SUMMARY_PATH = ROOT / "results" / "kober-sweep-summary.json"

# The two ends already known (F-019 and the full-corpus run), read from existing
# results files rather than rerun. Used when --results-dir is the default.
KNOWN_988_FILES = [
    ROOT / "results" / f"kober-damos-seed0-sub988-s{s}.json" for s in range(10)
]
KNOWN_FULL_FILE = ROOT / "results" / "kober-damos-seed0.json"

# Kober 0.9.1 merged/v3 988 and full-corpus cells (CHANGELOG "Floor sweep under
# Kober 0.9.1"): twenty tablet-model subsamples and the merged full-corpus run,
# already on disk, read rather than rerun. Used when --results-dir names the
# 0.9.1 sweep's own results directory (kober-sweep-09).
MERGED_09_DIR = ROOT / "results" / "kober-09-merged"
KOBER_09_RESULTS_DIR_NAME = "kober-sweep-09"


# --------------------------------------------------------------------------- #
# Criterion (docs/ai_context/kober-method.md, stage 1)
# --------------------------------------------------------------------------- #


def criterion_parts(d: dict) -> tuple[bool, bool, bool]:
    ec = d["ending_channel"]
    part1 = ec["paradigm_count_total"] > ec["n1_paradigm_count"]["p99"]
    n2max = ec["n2_alternation_support"]["max_support"]
    part2 = n2max["real_value"] > n2max["p99"]
    part3 = ec["top_10_matched_to_rule"] >= 7
    return part1, part2, part3


def criterion_a_parts_v3(d: dict) -> tuple[bool, bool, bool]:
    """Criterion (a) from CHANGELOG "Floor sweep under Kober 0.9.1": parts one
    and two exactly as ``criterion_parts``, part three regraded at reference
    version 3.

    ``ending_channel.top_10_matched_to_rule`` (``src/kober/report.py``,
    ``_channel_dict``) is *not* usable here: it sums ``alternations[:10]``'s
    own ``rule`` field, and that field is built by ``_alternation_entries``
    calling ``is_grammar(e1, e2)`` with no ``version`` argument -- always
    version 1, regardless of what ``--reference-version`` the run used
    (``build_report``'s own docstring: "ending/prefix ... are built before
    this parameter is used at all ... stay bit-identical to a
    reference_version=1 run"). So part three is recomputed here from the top
    ten's own ``e1``/``e2`` pairs at version 3, reusing
    ``kober_reference_v3_table.py``'s ``_strict_top_n``/``_count_matched``
    (the same strict, deterministic top-n cut ``top_10_matched_to_rule``
    itself uses, A-072) rather than the stored field.
    """
    ec = d["ending_channel"]
    part1 = ec["paradigm_count_total"] > ec["n1_paradigm_count"]["p99"]
    n2max = ec["n2_alternation_support"]["max_support"]
    part2 = n2max["real_value"] > n2max["p99"]
    top10 = _strict_top_n(ec, 10)
    part3 = _count_matched(top10, version=REFERENCE_VERSION_09) >= 7
    return part1, part2, part3


def criterion_b_pass_v3(d: dict) -> bool:
    """Criterion (b) from CHANGELOG "Floor sweep under Kober 0.9.1": the
    strict top three all grammar under the reference version used (v3 here) --
    ``top_n_alternations_with_ties``'s strict variant (A-072), via the same
    ``_strict_top_n``/``_all_match`` helpers ``kober_reference_v3_table.py``
    uses for its own strict-top-three-all-grammar count."""
    top3 = _strict_top_n(d["ending_channel"], 3)
    return _all_match(top3, version=REFERENCE_VERSION_09)


# --------------------------------------------------------------------------- #
# Type model
# --------------------------------------------------------------------------- #


def run_type_model(
    documents,
    size: int,
    seed: int,
    merge_homophones: bool = False,
    reference_version: int = 1,
) -> dict:
    report = build_report(
        documents,
        corpus="damos",
        stem_min=STEM_MIN,
        perms=PERMS,
        seed=NULL_SEED,
        subsample_n=size,
        subsample_seed=seed,
        merge_homophones=merge_homophones,
        reference_version=reference_version,
    )
    d = report.as_dict()
    d["sweep"] = {"model": "type", "target_size": size, "subsample_seed": seed}
    return d


# --------------------------------------------------------------------------- #
# Tablet model: bisection on document count K, then stage 1 at that K.
#
# A-063: subsample_document_ids returns a prefix of one seeded permutation, so
# the resulting type count is non-decreasing in K at a fixed seed and a binary
# search for the smallest K with type_count(K) >= target is valid. When no K's
# type count falls within `tol` of the target (the count is a step function of
# K and can jump past it), the K adjacent to the search boundary whose type
# count is relatively closest to the target is used, and whether it actually
# met tolerance is recorded rather than assumed.
# --------------------------------------------------------------------------- #


def _type_count_for_k(
    corpus, doc_ids_sorted: list[str], k: int, seed: int, merge_homophones: bool = False
) -> int:
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    subset = corpus.subset(chosen)
    return len(extract_word_types(subset.documents, merge_homophones=merge_homophones).words)


def bisect_k(
    corpus,
    doc_ids_sorted: list[str],
    target: int,
    seed: int,
    tol: float = TOLERANCE,
    merge_homophones: bool = False,
) -> tuple[int, int, float, bool]:
    """Return (k, resulting_type_count, relative_error, within_tolerance)."""
    total = len(doc_ids_sorted)
    full_count = _type_count_for_k(corpus, doc_ids_sorted, total, seed, merge_homophones)
    if full_count < target:
        # A-063: target unreachable at this seed even using every document.
        err = abs(full_count - target) / target
        return total, full_count, err, err <= tol

    lo, hi = 1, total
    while lo < hi:
        mid = (lo + hi) // 2
        c = _type_count_for_k(corpus, doc_ids_sorted, mid, seed, merge_homophones)
        if c >= target:
            hi = mid
        else:
            lo = mid + 1
    k_hi = lo
    c_hi = _type_count_for_k(corpus, doc_ids_sorted, k_hi, seed, merge_homophones)
    candidates = [(k_hi, c_hi)]
    if k_hi > 1:
        k_lo = k_hi - 1
        c_lo = _type_count_for_k(corpus, doc_ids_sorted, k_lo, seed, merge_homophones)
        candidates.append((k_lo, c_lo))
    # A-063: ties broken toward the smaller K (candidates listed k_hi first).
    best_k, best_c = min(candidates, key=lambda kc: abs(kc[1] - target) / target)
    err = abs(best_c - target) / target
    return best_k, best_c, err, err <= tol


def run_tablet_model(
    corpus,
    doc_ids_sorted: list[str],
    size: int,
    seed: int,
    merge_homophones: bool = False,
    reference_version: int = 1,
) -> dict:
    k, count, err, within_tol = bisect_k(
        corpus, doc_ids_sorted, size, seed, merge_homophones=merge_homophones
    )
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    documents = corpus.subset(chosen).documents
    report = build_report(
        documents,
        corpus="damos",
        stem_min=STEM_MIN,
        perms=PERMS,
        seed=NULL_SEED,
        merge_homophones=merge_homophones,
        reference_version=reference_version,
    )
    d = report.as_dict()
    d["sweep"] = {
        "model": "tablet",
        "target_size": size,
        "subsample_seed": seed,
        "documents_k": k,
        "tolerance": TOLERANCE,
        "within_tolerance": within_tol,
        "relative_error": err,
    }
    return d


# --------------------------------------------------------------------------- #
# Per-run I/O
# --------------------------------------------------------------------------- #


def _run_path(results_dir: Path, model: str, size: int, seed: int) -> Path:
    return results_dir / f"kober-sweep-{model}-size{size}-seed{seed}.json"


def write_run(d: dict, results_dir: Path, model: str, size: int, seed: int) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    path = _run_path(results_dir, model, size, seed)
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return path


def sweep(
    sizes: list[int],
    models: list[str],
    results_dir: Path = RESULTS_DIR,
    merge_homophones: bool = False,
    reference_version: int = 1,
) -> None:
    corpus = aegean.load("damos")
    doc_ids_sorted = sorted(d.id for d in corpus.documents)
    for size in sizes:
        for model in models:
            for seed in SUBSAMPLE_SEEDS:
                t0 = time.time()
                if model == "type":
                    d = run_type_model(
                        corpus.documents, size, seed, merge_homophones, reference_version
                    )
                else:
                    d = run_tablet_model(
                        corpus, doc_ids_sorted, size, seed, merge_homophones, reference_version
                    )
                elapsed = time.time() - t0
                d["sweep"]["wall_time_s"] = round(elapsed, 2)
                path = write_run(d, results_dir, model, size, seed)
                print(f"{model} size={size} seed={seed} -> {path.name} ({elapsed:.1f}s)")


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #


def _is_09(results_dir: Path) -> bool:
    return results_dir.name == KOBER_09_RESULTS_DIR_NAME


def _summarise_group(dicts: list[dict]) -> dict:
    """0.3 criterion, unchanged (CHANGELOG "Floor sweep on Linear B")."""
    p1 = p2 = p3 = all3 = 0
    top10s: list[int] = []
    counts: list[int] = []
    for d in dicts:
        a, b, c = criterion_parts(d)
        p1 += a
        p2 += b
        p3 += c
        all3 += a and b and c
        top10s.append(d["ending_channel"]["top_10_matched_to_rule"])
        counts.append(d["word_types"]["count"])
    return {
        "n": len(dicts),
        "part1_paradigm_count_above_n1_p99": p1,
        "part2_max_support_above_n2_p99": p2,
        "part3_top10_matched_ge_7": p3,
        "all_three": all3,
        "type_count_median": statistics.median(counts) if counts else None,
        "type_count_range": [min(counts), max(counts)] if counts else None,
        "top_10_matched_median": statistics.median(top10s) if top10s else None,
        "top_10_matched_range": [min(top10s), max(top10s)] if top10s else None,
    }


def _summarise_group_v3(dicts: list[dict]) -> dict:
    """CHANGELOG "Floor sweep under Kober 0.9.1": both criteria, per size --
    (a) the sweep's three parts, part three regraded at reference version 3
    (``criterion_a_parts_v3``); (b) strict top three all grammar under v3
    (``criterion_b_pass_v3``). Also the median/range of type count, of the
    strict top-ten matched count at v3, and of the strict top-three matched
    count at v3."""
    p1 = p2 = p3 = all3_a = b_pass = 0
    top10_matched_v3: list[int] = []
    top3_matched_v3: list[int] = []
    counts: list[int] = []
    for d in dicts:
        a, b, c = criterion_a_parts_v3(d)
        p1 += a
        p2 += b
        p3 += c
        all3_a += a and b and c
        ec = d["ending_channel"]
        top10_matched_v3.append(_count_matched(_strict_top_n(ec, 10), version=REFERENCE_VERSION_09))
        top3_matched_v3.append(_count_matched(_strict_top_n(ec, 3), version=REFERENCE_VERSION_09))
        b_pass += criterion_b_pass_v3(d)
        counts.append(d["word_types"]["count"])
    n = len(dicts)
    return {
        "n": n,
        "criterion_a": {
            "part1_paradigm_count_above_n1_p99": p1,
            "part2_max_support_above_n2_p99": p2,
            "part3_top10_matched_ge_7_v3": p3,
            "all_three": all3_a,
        },
        "criterion_b_strict_top3_all_grammar_v3": {"pass": b_pass, "of": n},
        "type_count_median": statistics.median(counts) if counts else None,
        "type_count_range": [min(counts), max(counts)] if counts else None,
        "top_10_matched_v3_median": statistics.median(top10_matched_v3) if top10_matched_v3 else None,
        "top_10_matched_v3_range": [min(top10_matched_v3), max(top10_matched_v3)]
        if top10_matched_v3
        else None,
        "strict_top3_matched_v3_median": statistics.median(top3_matched_v3) if top3_matched_v3 else None,
        "strict_top3_matched_v3_range": [min(top3_matched_v3), max(top3_matched_v3)]
        if top3_matched_v3
        else None,
    }


def _load_group(results_dir: Path, model: str, size: int) -> list[dict]:
    out = []
    for seed in SUBSAMPLE_SEEDS:
        path = _run_path(results_dir, model, size, seed)
        if path.exists():
            out.append(json.loads(path.read_text()))
    return out


def _known_988(results_dir: Path) -> dict | None:
    if _is_09(results_dir):
        files = sorted(MERGED_09_DIR.glob("kober-damos-seed0-docs*-s*.json"))
        if not files:
            return None
        dicts = [json.loads(p.read_text()) for p in files]
        summary = _summarise_group_v3(dicts)
        summary["source"] = (
            f"Kober 0.9.1 merged/v3 tablet-model 988 cells "
            f"(existing {MERGED_09_DIR.relative_to(ROOT)}/kober-damos-seed0-docs*-s*.json, seeds 0-19)"
        )
        return summary
    dicts = [json.loads(p.read_text()) for p in KNOWN_988_FILES if p.exists()]
    if not dicts:
        return None
    summary = _summarise_group(dicts)
    summary["source"] = "F-019 size-matched control (existing results/kober-damos-seed0-sub988-s*.json, seeds 0-9)"
    return summary


def _known_full(results_dir: Path) -> dict | None:
    if _is_09(results_dir):
        path = MERGED_09_DIR / "kober-damos-seed0.json"
        if not path.exists():
            return None
        d = json.loads(path.read_text())
        summary = _summarise_group_v3([d])
        summary["source"] = (
            f"Kober 0.9.1 merged full-corpus run (existing {MERGED_09_DIR.relative_to(ROOT)}/kober-damos-seed0.json)"
        )
        return summary
    if not KNOWN_FULL_FILE.exists():
        return None
    d = json.loads(KNOWN_FULL_FILE.read_text())
    summary = _summarise_group([d])
    summary["source"] = "full corpus (existing results/kober-damos-seed0.json)"
    return summary


def _find_floor(sizes_block: dict, pass_count_fn) -> dict:
    """CHANGELOG "Floor sweep under Kober 0.9.1"'s own rule: the floor is the
    smallest swept size at which at least ``PASS_BAR`` of twenty pass.
    ``pass_count_fn(group) -> int`` reads the pass count for one criterion
    from a (tablet or known) group dict. Scans every recorded size ascending,
    "known" cells (988, 3768) included, so a known cell of n=1 (the full
    corpus) is scanned too but can never reach the bar by construction --
    consistent with the entry's readings, which treat F-040's single-size
    eighteen-of-twenty as a different (988-only) result, not a floor."""
    ordered = sorted(sizes_block.keys(), key=int)
    for size_str in ordered:
        entry = sizes_block[size_str]
        group = entry.get("tablet") or entry.get("known")
        if group is None:
            continue
        if pass_count_fn(group) >= PASS_BAR:
            return {"size": int(size_str), "reached": True}
    return {"size": None, "reached": False, "note": f"no swept size reached {PASS_BAR}/20"}


def build_summary(
    results_dir: Path = RESULTS_DIR,
    extra: dict | None = None,
    sizes: list[int] | None = None,
) -> dict:
    is_09 = _is_09(results_dir)
    scan_sizes = sizes if sizes is not None else (SIZES_09 if is_09 else SIZES)
    summary: dict = {
        "protocol": (
            "Kober 0.9.1 stage 1, homophones merged, reference list v3, floor sweep on "
            "Linear B (CHANGELOG 'Floor sweep under Kober 0.9.1, merged identities and "
            "reference list v3')"
            if is_09
            else "Kober 0.3 stage 1, floor sweep on Linear B (CHANGELOG 'Floor sweep on Linear B')"
        ),
        "perms": PERMS,
        "null_seed": NULL_SEED,
        "subsample_seeds": [min(SUBSAMPLE_SEEDS), max(SUBSAMPLE_SEEDS)],
        "pass_bar": PASS_BAR,
        "tolerance": TOLERANCE,
        "sizes": {},
    }
    if is_09:
        summary["reference_version"] = REFERENCE_VERSION_09
        summary["merge_homophones"] = True
    known_988 = _known_988(results_dir)
    if known_988 is not None:
        summary["sizes"]["988"] = {"known": known_988}
    models = ("tablet",) if is_09 else ("type", "tablet")
    for size in scan_sizes:
        entry: dict = {}
        for model in models:
            dicts = _load_group(results_dir, model, size)
            if dicts:
                entry[model] = _summarise_group_v3(dicts) if is_09 else _summarise_group(dicts)
        if entry:
            summary["sizes"][str(size)] = entry
    known_full = _known_full(results_dir)
    if known_full is not None:
        summary["sizes"]["3768"] = {"known": known_full}
    if extra:
        summary["bisection"] = extra
    elif not is_09:
        # Preserve a bisection section from an earlier invocation of this script
        # when this call did not recompute it (e.g. a plain coarse-sweep chunk).
        # Bisection is a 0.3-only round (the 0.9.1 entry runs no bisection).
        if SUMMARY_PATH.exists():
            try:
                prev = json.loads(SUMMARY_PATH.read_text())
                if "bisection" in prev:
                    summary["bisection"] = prev["bisection"]
            except (OSError, json.JSONDecodeError):
                pass
    if is_09:
        summary["floors"] = {
            "criterion_a_all_three": _find_floor(
                summary["sizes"], lambda g: g["criterion_a"]["all_three"]
            ),
            "criterion_b_strict_top3_all_grammar_v3": _find_floor(
                summary["sizes"], lambda g: g["criterion_b_strict_top3_all_grammar_v3"]["pass"]
            ),
        }
    return summary


def _summary_paths(results_dir: Path) -> tuple[Path, Path | None]:
    """Default results dir: unchanged, JSON only, at the original fixed path.
    Any other results dir (the 0.9.1 sweep's own): JSON and a companion
    markdown file, both named after the results dir itself, under results/."""
    if results_dir == RESULTS_DIR:
        return SUMMARY_PATH, None
    name = results_dir.name
    return ROOT / "results" / f"{name}-summary.json", ROOT / "results" / f"{name}-summary.md"


def _fmt_pass(pass_count: int, of: int) -> str:
    return f"{pass_count}/{of}"


def render_summary_markdown(summary: dict, results_dir: Path) -> str:
    lines = [
        f"# {results_dir.name}: floor sweep summary",
        "",
        summary["protocol"] + ".",
        "",
        f"perms={summary['perms']}, null_seed={summary['null_seed']}, "
        f"subsample_seeds={summary['subsample_seeds'][0]}-{summary['subsample_seeds'][1]}, "
        f"pass_bar={summary['pass_bar']}/20.",
        "",
    ]
    is_09 = "floors" in summary
    if is_09:
        lines += [
            "## Per size",
            "",
            "| size | n | (a) part1 | (a) part2 | (a) part3 (v3) | (a) all three | "
            "(b) strict top-3 all grammar (v3) |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for size_str in sorted(summary["sizes"].keys(), key=int):
            entry = summary["sizes"][size_str]
            group = entry.get("tablet") or entry.get("known")
            if group is None:
                continue
            a = group["criterion_a"]
            b = group["criterion_b_strict_top3_all_grammar_v3"]
            n = group["n"]
            lines.append(
                f"| {size_str} | {n} | "
                f"{_fmt_pass(a['part1_paradigm_count_above_n1_p99'], n)} | "
                f"{_fmt_pass(a['part2_max_support_above_n2_p99'], n)} | "
                f"{_fmt_pass(a['part3_top10_matched_ge_7_v3'], n)} | "
                f"{_fmt_pass(a['all_three'], n)} | "
                f"{_fmt_pass(b['pass'], b['of'])} |"
            )
        lines += [
            "",
            "## Floors (CHANGELOG 'Floor sweep under Kober 0.9.1': smallest swept size "
            f"with at least {summary['pass_bar']}/20 passing)",
            "",
            "| criterion | floor |",
            "|---|---|",
        ]
        for key, label in (
            ("criterion_a_all_three", "(a) all three parts"),
            ("criterion_b_strict_top3_all_grammar_v3", "(b) strict top three all grammar (v3)"),
        ):
            f = summary["floors"][key]
            value = f["size"] if f["reached"] else "not reached at or below the largest swept size"
            lines.append(f"| {label} | {value} |")
        lines.append("")
    else:
        lines += [
            "## Per size (type / tablet model)",
            "",
            "| size | model | n | part1 | part2 | part3 | all three |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
        for size_str in sorted(summary["sizes"].keys(), key=int):
            entry = summary["sizes"][size_str]
            for model in ("known", "type", "tablet"):
                group = entry.get(model)
                if group is None:
                    continue
                n = group["n"]
                lines.append(
                    f"| {size_str} | {model} | {n} | "
                    f"{_fmt_pass(group['part1_paradigm_count_above_n1_p99'], n)} | "
                    f"{_fmt_pass(group['part2_max_support_above_n2_p99'], n)} | "
                    f"{_fmt_pass(group['part3_top10_matched_ge_7'], n)} | "
                    f"{_fmt_pass(group['all_three'], n)} |"
                )
        lines.append("")
    return "\n".join(lines)


def write_summary(
    results_dir: Path = RESULTS_DIR,
    extra: dict | None = None,
    sizes: list[int] | None = None,
) -> Path:
    summary = build_summary(results_dir, extra, sizes)
    json_path, md_path = _summary_paths(results_dir)
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    if md_path is not None:
        md_path.write_text(render_summary_markdown(summary, results_dir))
    return json_path


# --------------------------------------------------------------------------- #
# Round 3: bisection on size, per model (0.3 only; the 0.9.1 entry runs none)
# --------------------------------------------------------------------------- #


def find_crossing(size_all3: list[tuple[int, int]]) -> tuple[int, int] | None:
    """First adjacent pair (ascending) where the all-three count goes from
    below PASS_BAR to at least PASS_BAR. ``size_all3`` is (size, all_three) pairs
    already sorted ascending by size."""
    for (s0, c0), (s1, c1) in zip(size_all3, size_all3[1:]):
        if c0 < PASS_BAR <= c1:
            return s0, s1
    return None


def run_bisection_round(models: list[str], results_dir: Path = RESULTS_DIR) -> dict:
    corpus = aegean.load("damos")
    doc_ids_sorted = sorted(d.id for d in corpus.documents)
    coarse_sizes = list(SIZES)  # snapshot: the fixed seven, before any midpoint is appended
    result: dict = {}
    for model in models:
        size_all3 = []
        for size in coarse_sizes:
            dicts = _load_group(results_dir, model, size)
            if len(dicts) != 20:
                print(
                    f"skipping bisection for {model}: size {size} has "
                    f"{len(dicts)}/20 runs, need the full coarse pass first",
                    file=sys.stderr,
                )
                result[model] = {"error": f"coarse pass incomplete at size {size}"}
                break
            all3 = _summarise_group(dicts)["all_three"]
            size_all3.append((size, all3))
        else:
            crossing = find_crossing(size_all3)
            if crossing is None:
                result[model] = {
                    "reached_pass_bar_below_3768": False,
                    "coarse_all_three_by_size": dict(size_all3),
                    "note": (
                        f"all-three pass count never reached {PASS_BAR} of 20 "
                        "at a swept size below 3,768; no bisection run"
                    ),
                }
                continue
            lo, hi = crossing
            midpoint = round((lo + hi) / 2)
            print(f"{model}: crossing {lo} -> {hi}, running midpoint {midpoint}")
            for seed in SUBSAMPLE_SEEDS:
                t0 = time.time()
                if model == "type":
                    d = run_type_model(corpus.documents, midpoint, seed)
                else:
                    d = run_tablet_model(corpus, doc_ids_sorted, midpoint, seed)
                elapsed = time.time() - t0
                d["sweep"]["wall_time_s"] = round(elapsed, 2)
                path = write_run(d, results_dir, model, midpoint, seed)
                print(f"{model} size={midpoint} seed={seed} -> {path.name} ({elapsed:.1f}s)")
            midpoint_dicts = _load_group(results_dir, model, midpoint)
            result[model] = {
                "crossing": [lo, hi],
                "midpoint": midpoint,
                "coarse_all_three_by_size": dict(size_all3),
                "midpoint_summary": _summarise_group(midpoint_dicts),
            }
            if midpoint not in SIZES:
                # so the midpoint also appears as its own row in "sizes"
                SIZES.append(midpoint)
                SIZES.sort()
    return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="comma-separated target sizes to run the coarse pass for (default: all seven "
        "0.3 sizes, or the five 0.9.1 sizes when --results-dir names that sweep's directory)",
    )
    ap.add_argument(
        "--model",
        choices=["type", "tablet", "both"],
        default="both",
        help="which subsampling model to run (default: both)",
    )
    ap.add_argument(
        "--bisect",
        action="store_true",
        help="round 3: find the crossing of the 16-of-20 bar between adjacent coarse "
        "sizes and run the midpoint, per model (requires the coarse pass already on disk); "
        "0.3 only, CHANGELOG 'Floor sweep on Linear B'",
    )
    ap.add_argument(
        "--summary-only",
        action="store_true",
        help="rebuild the results summary from existing run files; run no new sweep",
    )
    ap.add_argument(
        "--merge-homophones",
        action="store_true",
        help="Kober 0.9's identity sensitivity, forwarded to kober.report.build_report "
        "(CHANGELOG '0.9'); default off reproduces every pre-0.9.1 sweep run exactly",
    )
    ap.add_argument(
        "--reference-version",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="reference-list version forwarded to kober.report.build_report (Kober 0.6/0.8, "
        "CHANGELOG '0.6'/'0.8'); grades the grammar-match null blocks in each run's own JSON "
        "only. Default 1 reproduces every pre-0.9.1 sweep run exactly",
    )
    ap.add_argument(
        "--results-dir",
        type=str,
        default=str(RESULTS_DIR.relative_to(ROOT)),
        help="write per-run JSON under this directory instead of results/kober-sweep/ "
        "(default), and read/write the summary accordingly. Passing results/kober-sweep-09 "
        "(CHANGELOG 'Floor sweep under Kober 0.9.1') also switches the summary step to read "
        "the 988 and full-corpus cells from results/kober-09-merged/ and to score criterion "
        "(b) alongside criterion (a); any other custom directory behaves like the default "
        "except for its own file location",
    )
    args = ap.parse_args()

    results_dir = (ROOT / args.results_dir).resolve() if not Path(args.results_dir).is_absolute() else Path(args.results_dir)
    models = ["type", "tablet"] if args.model == "both" else [args.model]

    if args.summary_only:
        path = write_summary(results_dir)
        print(f"Wrote {path}")
        return

    if args.bisect:
        extra = run_bisection_round(models, results_dir)
        path = write_summary(results_dir, extra)
        print(f"Wrote {path}")
        return

    default_sizes = SIZES_09 if _is_09(results_dir) else SIZES
    sizes = [int(s) for s in args.sizes.split(",")] if args.sizes else list(default_sizes)
    t0 = time.time()
    sweep(sizes, models, results_dir, args.merge_homophones, args.reference_version)
    # Always rebuild the summary from every run currently on disk for this
    # results_dir's own default size list, not just the sizes this invocation
    # just computed, so separate per-size invocations merge into one summary
    # (the same "merges ... across every run currently on disk" property the
    # 0.3 sweep already has).
    path = write_summary(results_dir)
    print(f"Wrote {path}")
    print(f"Wall time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
