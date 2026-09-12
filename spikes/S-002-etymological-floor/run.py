#!/usr/bin/env python3
"""S-002: does more Linear B separate Greek from the wrong real languages?

See BRIEF.md. The etymological line is closed (F-008, F-013): on the full Linear
B corpus, Greek's lead over the best wrong real language (Finnish or Sumerian,
Greek map) is about one sample standard error. This spike asks whether that gap
would open up given more corpus, by running protocol 1.0 (unchanged) on Linear B
subsamples smaller and larger than the full corpus, at four target sizes in word
types: 988, 1,875, 2,750 and the full corpus (labelled 3,768 in this repo's usual
Kober-scale convention, see below for why the label and the number this script
actually reaches disagree).

Subsampling is the "tablet model" (CHANGELOG "Floor sweep on Linear B", A-063,
`scripts/kober_floor_sweep.py`): a prefix of one seeded permutation of document
ids from `kober.words.subsample_document_ids` (imported read-only), with the
prefix length K found by bisection so the resulting **protocol 1.0 word pool**
(`word_pool` in `scripts/controlled_comparison.py`: WORD, CERTAIN, 2 to 4 signs,
covered by both the Greek and Semitic consonant maps) lands within 2% of the
target word-type count. Twenty subsample seeds (0-19) per size; the full corpus
runs once, unsubsampled.

Protocol 1.0 itself is untouched: `word_sample`, `statistic`, `run_one` and the
map builders are imported from `controlled_comparison.py`, not reimplemented.
100 permutations, protocol seed 0 (word sample and null permutations both), same
as every other protocol 1.0 run in this repo -- the subsample seed only chooses
which documents are in the tablet-model subset, not anything inside the frozen
instrument. Greek map only, three real lexicons (no synthetic twins: the brief
asks about separation from wrong real languages, which F-008's synthetic-twin
control does not speak to): Greek archaic (`LOADERS["greek_archaic"]`), Finnish
(`unrelated_controls.load_control("fi")`) and Sumerian (`LOADERS["sumerian_epsd2"]`),
the two wrong real-language controls F-013 already established for this map.
`synthetic_like` is imported for parity with the frozen instrument's public
surface but not called here.

**The pool ceiling.** Protocol 1.0's own word pool on the *full, unsubsampled*
Linear B corpus is 2,548 word types, not 3,768. The two numbers measure
different things: 3,768 is `kober.words.extract_word_types`' count (any word of
2+ signs, no map-coverage filter, the number this repo's other size-matching
work uses throughout, e.g. F-022, claims.md C-3c/C-4a). 2,548 is protocol 1.0's
own pool after its stricter filter (2 to 4 signs, and covered by *both* the
Greek and Semitic consonant maps at once). A document subsample can only ever
have a pool less than or equal to the full corpus's own pool, so a target above
2,548 is unreachable by construction, at every subsample seed, regardless of
which documents are chosen. That makes the 2,750 target and the "full corpus"
target (labelled 3,768) collapse to the identical run: both bisect (or default)
to every document in the corpus, and `word_sample` on the same corpus with the
same protocol seed then draws the identical 400 words. This script detects that
collapse (`documents_k` returned by bisection equals the full document count)
and computes the full-corpus run once, reusing it rather than repeating an
identical hour of permutation work twenty times over. Recorded, not hidden: see
`reused_full_corpus_result` in every cached run and RESULT.md's reading.

Usage, chunked by size (each size finishes in well under a minute in practice,
despite the ~1 min/run estimate in the task -- see the wall-clock note in
RESULT.md):

    .venv/bin/python spikes/S-002-etymological-floor/run.py --sizes 988
    .venv/bin/python spikes/S-002-etymological-floor/run.py --sizes 1875
    .venv/bin/python spikes/S-002-etymological-floor/run.py --sizes 2750
    .venv/bin/python spikes/S-002-etymological-floor/run.py --sizes 3768
    .venv/bin/python spikes/S-002-etymological-floor/run.py --summary-only

Per-run results are cached to `cache/` (aggregate numbers only: no words, no
corpus text) keyed by (size, seed), so a rerun of a chunk already on disk is a
no-op and an interrupted sweep resumes where it left off. `cache/` is not
committed; `results.json` is the aggregate this script writes from it.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
ROOT = SPIKE_DIR.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

from controlled_comparison import (  # noqa: E402
    run_one,
    statistic,  # unused directly (run_one wraps it); imported for parity, per BRIEF.md
    synthetic_like,  # unused: real lexicons only, per BRIEF.md
    word_pool,
    word_sample,
)
from hypotheses.lexicons import LOADERS, greek_archaic  # noqa: E402
from hypotheses.phonologies import build_map  # noqa: E402
from kober.words import subsample_document_ids  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402
from unrelated_controls import load_control  # noqa: E402

_ = statistic, synthetic_like  # silence unused-import warnings; see docstring

SIZES = [988, 1875, 2750, 3768]
FULL_LABEL = 3768  # brief's label for "the full corpus", not a pool count -- see docstring
SUBSAMPLE_SEEDS = list(range(20))
PROTOCOL_SEED = 0  # word_sample and null-permutation seed, protocol 1.0's own default
PERMS = 100
N_WORDS = 400
TOLERANCE = 0.02  # A-063's tolerance, reused here
LEAD_BAR = 2.0  # BRIEF.md's "two standard errors", read as two z units (RESULT.md states this)

CACHE_DIR = SPIKE_DIR / "cache"
RESULTS_PATH = SPIKE_DIR / "results.json"

LEXICON_LABELS = {
    "greek_archaic": "Greek, archaic",
    "finnish": "Finnish",
    "sumerian": "Sumerian (ePSD2)",
}
WRONG_LEXICONS = ("finnish", "sumerian")


# --------------------------------------------------------------------------- #
# Setup: corpus, maps, lexicons -- built once, reused across every size/seed.
# --------------------------------------------------------------------------- #


def build_maps(corpus) -> tuple[ConsonantMap, ConsonantMap]:
    inv = corpus.sign_inventory
    upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})  # noqa: E731
    gmap = upper(build_map(inv, "greek_syllabic"))
    smap = upper(build_map(inv, "semitic_consonantal"))
    return gmap, smap


def load_lexicons() -> dict:
    return {
        "greek_archaic": greek_archaic(),
        "finnish": load_control("fi"),
        "sumerian": LOADERS["sumerian_epsd2"](),
    }


# --------------------------------------------------------------------------- #
# Tablet-model bisection on document count K (A-063 pattern, adapted from
# scripts/kober_floor_sweep.py's bisect_k for the protocol 1.0 word_pool metric
# rather than kober.words.extract_word_types).
# --------------------------------------------------------------------------- #


def _pool_count_for_k(corpus, doc_ids_sorted, k, seed, maps) -> int:
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    subset = corpus.subset(chosen)
    return len(word_pool(subset, maps))


def bisect_k(corpus, doc_ids_sorted, target, seed, maps, tol=TOLERANCE):
    """Return (k, resulting_pool_count, relative_error, within_tolerance)."""
    total = len(doc_ids_sorted)
    full_count = _pool_count_for_k(corpus, doc_ids_sorted, total, seed, maps)
    if full_count < target:
        # Target unreachable at this seed even using every document (docstring:
        # the pool ceiling is 2,548, so this fires for every seed at 2,750+).
        err = abs(full_count - target) / target
        return total, full_count, err, err <= tol

    lo, hi = 1, total
    while lo < hi:
        mid = (lo + hi) // 2
        c = _pool_count_for_k(corpus, doc_ids_sorted, mid, seed, maps)
        if c >= target:
            hi = mid
        else:
            lo = mid + 1
    k_hi = lo
    c_hi = _pool_count_for_k(corpus, doc_ids_sorted, k_hi, seed, maps)
    candidates = [(k_hi, c_hi)]
    if k_hi > 1:
        k_lo = k_hi - 1
        c_lo = _pool_count_for_k(corpus, doc_ids_sorted, k_lo, seed, maps)
        candidates.append((k_lo, c_lo))
    best_k, best_c = min(candidates, key=lambda kc: abs(kc[1] - target) / target)
    err = abs(best_c - target) / target
    return best_k, best_c, err, err <= tol


# --------------------------------------------------------------------------- #
# Scoring: protocol 1.0, unchanged, three real lexicons under the Greek map.
# --------------------------------------------------------------------------- #


def score_words(gmap, words, lexicons) -> dict:
    freq = collections.Counter(s for w in words for s in w)
    rows = {}
    for name, lex in lexicons.items():
        r = run_one(f"{LEXICON_LABELS[name]} (real)", gmap, lex, words, freq, PERMS, PROTOCOL_SEED)
        rows[name] = {
            "z": r["z"],
            "real": r["real"],
            "null_mean": r["null_mean"],
            "gap": r["real"] - r["null_mean"],
            "p": r["p"],
            "se_z": r["se_z"],
        }
    return {"n_words_sampled": len(words), "rows": rows}


def full_corpus_result(corpus, gmap, smap, lexicons) -> dict:
    cache_path = CACHE_DIR / "full-corpus.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    pool_count = len(word_pool(corpus, [gmap, smap]))
    words = word_sample(corpus, [gmap, smap], N_WORDS, PROTOCOL_SEED)
    result = score_words(gmap, words, lexicons)
    result["documents_k"] = len(list(corpus.documents))
    result["pool_count"] = pool_count
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, indent=2))
    return result


def run_size_seed(corpus, doc_ids_sorted, gmap, smap, lexicons, size, seed) -> dict:
    cache_path = CACHE_DIR / f"size{size}-seed{seed}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    total = len(doc_ids_sorted)
    k, pool_count, err, within_tol = bisect_k(corpus, doc_ids_sorted, size, seed, [gmap, smap])

    if k == total and not within_tol:
        # Unreachable at every seed once k hits the full document count (the
        # pool ceiling, docstring): the tablet-model subsample IS the full
        # corpus, and word_sample on the same corpus at the same protocol seed
        # draws the identical 400 words, so reuse rather than recompute.
        full = full_corpus_result(corpus, gmap, smap, lexicons)
        result = dict(full)
        result["reused_full_corpus_result"] = True
    else:
        chosen = subsample_document_ids(doc_ids_sorted, k, seed)
        subset = corpus.subset(chosen)
        words = word_sample(subset, [gmap, smap], N_WORDS, PROTOCOL_SEED)
        result = score_words(gmap, words, lexicons)
        result["documents_k"] = k
        result["pool_count"] = pool_count
        result["reused_full_corpus_result"] = False

    result["target_size"] = size
    result["subsample_seed"] = seed
    result["tolerance"] = TOLERANCE
    result["within_tolerance"] = within_tol
    result["relative_error"] = err

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(result, indent=2))
    return result


def run_full(corpus, gmap, smap, lexicons) -> dict:
    full = full_corpus_result(corpus, gmap, smap, lexicons)
    result = dict(full)
    result["target_size"] = FULL_LABEL
    result["subsample_seed"] = None
    result["tolerance"] = None
    result["within_tolerance"] = None
    result["relative_error"] = None
    result["reused_full_corpus_result"] = False  # this IS the canonical full-corpus run
    return result


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


def _lead(run: dict, lex: str) -> float:
    z = run["rows"][lex]["z"]
    best_wrong = max(run["rows"][w]["z"] for w in WRONG_LEXICONS)
    return z - best_wrong


def _gap_lead(run: dict, lex: str) -> float:
    gap = run["rows"][lex]["gap"]
    best_wrong = max(run["rows"][w]["gap"] for w in WRONG_LEXICONS)
    return gap - best_wrong


def summarise_size(runs: list[dict]) -> dict:
    z = {name: [r["rows"][name]["z"] for r in runs] for name in LEXICON_LABELS}
    gap = {name: [r["rows"][name]["gap"] for r in runs] for name in LEXICON_LABELS}
    leads = [_lead(r, "greek_archaic") for r in runs]
    gap_leads = [_gap_lead(r, "greek_archaic") for r in runs]
    pool_counts = [r["pool_count"] for r in runs]
    return {
        "n_runs": len(runs),
        "z_median": {name: statistics.median(vals) for name, vals in z.items()},
        "z_range": {name: [min(vals), max(vals)] for name, vals in z.items()},
        "gap_median": {name: statistics.median(vals) for name, vals in gap.items()},
        "gap_range": {name: [min(vals), max(vals)] for name, vals in gap.items()},
        "lead_z_median": statistics.median(leads),
        "lead_z_range": [min(leads), max(leads)],
        "lead_gap_median": statistics.median(gap_leads),
        "lead_gap_range": [min(gap_leads), max(gap_leads)],
        "count_lead_ge_2": sum(1 for x in leads if x >= LEAD_BAR),
        "pool_count_median": statistics.median(pool_counts),
        "pool_count_range": [min(pool_counts), max(pool_counts)],
        "any_reused_full_corpus": any(r.get("reused_full_corpus_result") for r in runs),
        "any_outside_tolerance": any(
            r.get("within_tolerance") is False for r in runs
        ),
    }


def build_results(sizes: list[int]) -> dict:
    out = {
        "protocol": {
            "version": "1.0 (unchanged; imported from scripts/controlled_comparison.py)",
            "map": "greek_syllabic",
            "lexicons": LEXICON_LABELS,
            "n_words": N_WORDS,
            "perms": PERMS,
            "protocol_seed": PROTOCOL_SEED,
            "subsample_seeds": [min(SUBSAMPLE_SEEDS), max(SUBSAMPLE_SEEDS)],
            "tolerance": TOLERANCE,
            "lead_bar": LEAD_BAR,
            "lead_bar_note": "BRIEF.md's 'two standard errors', read as two z units",
            "pool_ceiling_note": (
                "protocol 1.0's own word pool on the full, unsubsampled Linear B "
                "corpus is 2,548 word types, not 3,768 (kober.words' word-type "
                "count, used elsewhere in this repo for size-matching). Targets "
                "at or above 2,548 are unreachable by subsampling and collapse to "
                "the full-corpus run; see run.py's docstring."
            ),
        },
        "sizes": {},
    }
    for size in sizes:
        cached = []
        if size == FULL_LABEL:
            path = CACHE_DIR / "full-corpus.json"
            if path.exists():
                d = json.loads(path.read_text())
                d = dict(d)
                d["target_size"] = FULL_LABEL
                d["subsample_seed"] = None
                cached = [d]
        else:
            for seed in SUBSAMPLE_SEEDS:
                path = CACHE_DIR / f"size{size}-seed{seed}.json"
                if path.exists():
                    cached.append(json.loads(path.read_text()))
        if not cached:
            continue
        out["sizes"][str(size)] = {
            "runs": [
                {
                    "subsample_seed": r["subsample_seed"],
                    "documents_k": r["documents_k"],
                    "pool_count": r["pool_count"],
                    "within_tolerance": r.get("within_tolerance"),
                    "relative_error": r.get("relative_error"),
                    "reused_full_corpus_result": r.get("reused_full_corpus_result", False),
                    "z": {name: r["rows"][name]["z"] for name in LEXICON_LABELS},
                    "gap": {name: r["rows"][name]["gap"] for name in LEXICON_LABELS},
                    "p": {name: r["rows"][name]["p"] for name in LEXICON_LABELS},
                }
                for r in cached
            ],
            "summary": summarise_size(cached),
        }
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def parse_sizes(s: str | None) -> list[int]:
    if not s:
        return list(SIZES)
    return [int(x) for x in s.split(",")]


def parse_seeds(s: str | None) -> list[int]:
    if not s:
        return list(SUBSAMPLE_SEEDS)
    if "-" in s and "," not in s:
        lo, hi = s.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in s.split(",")]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", type=str, default=None, help="comma-separated target sizes (default: all four)")
    ap.add_argument("--seeds", type=str, default=None, help="comma list or lo-hi range (default: 0-19; ignored for 3768)")
    ap.add_argument("--summary-only", action="store_true", help="rebuild results.json from cache/, run nothing new")
    args = ap.parse_args()

    if args.summary_only:
        results = build_results(SIZES)
        RESULTS_PATH.write_text(json.dumps(results, indent=2))
        print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")
        return

    sizes = parse_sizes(args.sizes)
    seeds = parse_seeds(args.seeds)

    corpus = aegean.load("damos")
    gmap, smap = build_maps(corpus)
    lexicons = load_lexicons()
    doc_ids_sorted = sorted(d.id for d in corpus.documents)

    for size in sizes:
        if size == FULL_LABEL:
            r = run_full(corpus, gmap, smap, lexicons)
            print(f"size={size} (full corpus) documents_k={r['documents_k']} pool={r['pool_count']} "
                  f"z(greek)={r['rows']['greek_archaic']['z']:+.2f} "
                  f"z(finnish)={r['rows']['finnish']['z']:+.2f} "
                  f"z(sumerian)={r['rows']['sumerian']['z']:+.2f}")
            continue
        for seed in seeds:
            r = run_size_seed(corpus, doc_ids_sorted, gmap, smap, lexicons, size, seed)
            tag = " [reused full-corpus]" if r.get("reused_full_corpus_result") else ""
            print(f"size={size} seed={seed} k={r['documents_k']} pool={r['pool_count']} "
                  f"(target err {r['relative_error']:.3f}){tag} "
                  f"z(greek)={r['rows']['greek_archaic']['z']:+.2f} "
                  f"z(finnish)={r['rows']['finnish']['z']:+.2f} "
                  f"z(sumerian)={r['rows']['sumerian']['z']:+.2f}")

    results = build_results(SIZES)
    RESULTS_PATH.write_text(json.dumps(results, indent=2))
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
