#!/usr/bin/env python3
"""S-008: Kober's Assumption 3 as a statistic (BRIEF.md).

Splits word types into "listed" (attested at least once followed, skipping
separators, by a logogram or numeral -- the "listed word" definition
``kober.lists.extract_listed_words`` already uses for F-030, which is the
codebase's own operationalisation of the list position kober1946's
Assumption 3 names) and "not listed" (everything else), on Linear B (DAMOS),
then Linear A under both editions (GORILA, SigLA). For each set: type count,
hapax share, ending inventory (last sign, last two signs), ending entropy,
and the paradigm ratio (stems with two or more endings, against the N1 null,
stem_min and draws as stage 1 uses -- 200 draws, seed 0 and seed 1 as a
check). Linear B only: a part-of-speech proxy from the reference alternation
rules (verb, participle, infinitive) applied to endings that appear in a
real attested alternation within each set. Then the transfer test: Linear
B's twenty tablet-model subsamples at 988 word types give the sampling noise
on each listed-minus-not-listed difference, against which Linear A's own
differences (both editions, already close to that scale) are read.

Imports only from src/kober and aegean; edits nothing under src/. Writes
results.json (aggregate only -- ending labels with counts, no word lists, no
corpus text) beside this file.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
ROOT = SPIKE_DIR.parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from kober.lists import extract_listed_words  # noqa: E402
from kober.nulls import run_n1  # noqa: E402
from kober.paradigms import ChannelResult, Word, ending_channel, prefix_channel  # noqa: E402
from kober.reference import decompose, is_grammar  # noqa: E402
from kober.words import _normalise_label, extract_word_types, subsample_document_ids  # noqa: E402

STEM_MIN = 2
DRAWS = 200
SEEDS = (0, 1)
TABLET_SUBSAMPLE_TARGET = 988
TABLET_SUBSAMPLE_SEEDS = list(range(20))
TABLET_TOLERANCE = 0.02  # A-063, as scripts/kober_floor_sweep.py uses

POS_PROXY_RULES = frozenset({"verb", "participle", "infinitive"})
POS_PROXY_REFERENCE_VERSION = 3  # only version with the infinitive rule (19)

OUT_PATH = SPIKE_DIR / "results.json"


# --------------------------------------------------------------------------- #
# Corpus-wide word-type frequency (for hapax share) and the listed/not-listed
# split (kober.lists.extract_listed_words is F-030's own "listed word": a
# CERTAIN WORD token of >= 2 normalised signs, followed on its line, skipping
# separators, by a logogram or numeral).
# --------------------------------------------------------------------------- #


def word_token_counts(documents) -> Counter:
    """Corpus-wide token frequency per eligible word type -- same eligibility
    (CERTAIN WORD, normalised, >= 2 signs) as ``kober.words.extract_word_types``,
    counting occurrences instead of just membership."""
    counts: Counter = Counter()
    for doc in documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            labels = []
            for label in tok.signs:
                norm, _changed = _normalise_label(label)
                labels.append(norm)
            if len(labels) >= 2:
                counts[tuple(labels)] += 1
    return counts


def split_listed(documents, word_types: frozenset) -> tuple[frozenset, frozenset]:
    listings = extract_listed_words(documents)
    listed = frozenset({w for dl in listings for w in dl.listed} & word_types)
    not_listed = frozenset(word_types - listed)
    return listed, not_listed


# --------------------------------------------------------------------------- #
# Per-set descriptive statistics
# --------------------------------------------------------------------------- #


def shannon_entropy_bits(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    ent = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        ent -= p * math.log2(p)
    return ent


def set_stats(word_type_set: frozenset, freq: Counter) -> dict:
    n = len(word_type_set)
    hapax = sum(1 for w in word_type_set if freq.get(w, 0) == 1)
    last1 = Counter(w[-1] for w in word_type_set)
    last2 = Counter(w[-2:] for w in word_type_set)
    inv1, inv2 = len(last1), len(last2)
    ent1 = shannon_entropy_bits(list(last1.values()))
    ent2 = shannon_entropy_bits(list(last2.values()))
    return {
        "n_types": n,
        "hapax_count": hapax,
        "hapax_share": (hapax / n) if n else 0.0,
        "ending_inventory_last1": inv1,
        "ending_inventory_last2": inv2,
        "ending_diversity_last1": (inv1 / n) if n else 0.0,
        "ending_diversity_last2": (inv2 / n) if n else 0.0,
        "entropy_last1_bits": ent1,
        "entropy_last2_bits": ent2,
        "entropy_last1_normalized": (ent1 / math.log2(inv1)) if inv1 > 1 else None,
        "entropy_last2_normalized": (ent2 / math.log2(inv2)) if inv2 > 1 else None,
        "last1_label_counts": dict(sorted(last1.items(), key=lambda kv: (-kv[1], kv[0]))),
        "last2_label_counts": {
            f"{a}-{b}": c for (a, b), c in sorted(last2.items(), key=lambda kv: (-kv[1], kv[0]))
        },
    }


def paradigm_stats(word_type_set: frozenset, stem_min: int = STEM_MIN, draws: int = DRAWS, seeds=SEEDS):
    """Real paradigm count (stems with >= 2 endings) against the N1 null, at
    each seed. Returns (stats dict, real ending ChannelResult) -- the channel
    is returned so its alternation_support can be reused by the pos-proxy
    without rebuilding it."""
    words_list = sorted(word_type_set)
    real_end = ending_channel(words_list, stem_min)
    real_pre = prefix_channel(words_list, stem_min)
    out = {"paradigm_count_total": real_end.paradigm_count_total, "n1": {}}
    for seed in seeds:
        res = run_n1(words_list, stem_min, draws, seed, real_end, real_pre)
        nd = res.ending_paradigm_count
        ratio = (nd.real_value / nd.mean) if nd.mean > 0 else None
        out["n1"][seed] = {
            "draws": nd.draws,
            "null_mean": nd.mean,
            "null_sd": nd.sd,
            "null_p99": nd.p99,
            "real_value": nd.real_value,
            "real_percentile": nd.real_percentile,
            "ratio_to_null_mean": ratio,
        }
    return out, real_end


# --------------------------------------------------------------------------- #
# Linear B part-of-speech proxy: an ending counts as "verb/participle/
# infinitive only" when every attested alternation it appears in (within
# this same word-type set's real ending channel) is matched by reference.py's
# verb, participle or infinitive rule and never by any of the noun/adjective
# rules -- reusing is_grammar and the already-built alternation_support
# rather than a new single-ending heuristic. Weak by construction: an ending
# with no attested alternation at all is left unclassified (not counted
# either way), and an ending is graded on whichever rule reference.py's
# fixed, first-match order assigns its pairs, not on a real part of speech.
# --------------------------------------------------------------------------- #


def classify_endings_by_rule(alternation_support, version: int = POS_PROXY_REFERENCE_VERSION) -> dict[Word, set]:
    labels: dict[Word, set] = defaultdict(set)
    for e1, e2 in alternation_support:
        rule = is_grammar(e1, e2, version=version)
        if rule is not None:
            labels[e1].add(rule)
            labels[e2].add(rule)
    return labels


def pos_proxy_stats(word_type_set: frozenset, real_channel: ChannelResult) -> dict:
    labels = classify_endings_by_rule(real_channel.alternation_support)
    n = len(word_type_set)
    not_noun_only = 0
    classified = 0
    for w in word_type_set:
        candidates = {w[-1:], w[-2:]}
        matched: set = set()
        for cand in candidates:
            matched |= labels.get(cand, set())
        if not matched:
            continue
        classified += 1
        if matched <= POS_PROXY_RULES:
            not_noun_only += 1
    return {
        "n_types": n,
        "classified_count": classified,
        "not_noun_only_count": not_noun_only,
        "not_noun_only_share_of_all": (not_noun_only / n) if n else 0.0,
        "not_noun_only_share_of_classified": (not_noun_only / classified) if classified else None,
        "reference_version": POS_PROXY_REFERENCE_VERSION,
        "rules_counted_as_not_noun": sorted(POS_PROXY_RULES),
    }


# --------------------------------------------------------------------------- #
# Assembling one corpus/edition
# --------------------------------------------------------------------------- #

SIGNATURE_METRICS = (
    "hapax_share",
    "ending_diversity_last1",
    "ending_diversity_last2",
    "entropy_last1_bits",
    "entropy_last2_bits",
    "entropy_last1_normalized",
    "entropy_last2_normalized",
    "paradigm_ratio_seed0",
)


def _paradigm_ratio_seed0(pstats: dict):
    return pstats["n1"][0]["ratio_to_null_mean"]


def compute_differences(listed_stats: dict, not_listed_stats: dict) -> dict:
    diffs = {}
    for metric in SIGNATURE_METRICS:
        lv = listed_stats.get(metric)
        nv = not_listed_stats.get(metric)
        diffs[metric] = (lv - nv) if (lv is not None and nv is not None) else None
    return diffs


def analyze_documents(documents, include_pos_proxy: bool = False) -> dict:
    wt = extract_word_types(documents)
    word_types = wt.words
    listed, not_listed = split_listed(documents, word_types)
    freq = word_token_counts(documents)

    sets = {}
    channels = {}
    for name, s in (("listed", listed), ("not_listed", not_listed)):
        stats = set_stats(s, freq)
        pstats, real_end = paradigm_stats(s)
        stats["paradigm"] = pstats
        stats["paradigm_ratio_seed0"] = _paradigm_ratio_seed0(pstats)
        stats["paradigm_ratio_seed1"] = pstats["n1"][1]["ratio_to_null_mean"] if 1 in pstats["n1"] else None
        sets[name] = stats
        channels[name] = real_end

    if include_pos_proxy:
        for name, s in (("listed", listed), ("not_listed", not_listed)):
            sets[name]["pos_proxy"] = pos_proxy_stats(s, channels[name])

    return {
        "total_types": len(word_types),
        "sets": sets,
        "differences": compute_differences(sets["listed"], sets["not_listed"]),
    }


# --------------------------------------------------------------------------- #
# Linear B tablet-model subsampling at 988 word types (kober-method.md's
# floor-sweep methodology, scripts/kober_floor_sweep.py's bisect_k, reused
# here at the fixed target 988 -- Linear A's own scale -- across seeds 0-19)
# --------------------------------------------------------------------------- #


def _type_count_for_k(corpus, doc_ids_sorted: list[str], k: int, seed: int) -> int:
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    subset = corpus.subset(chosen)
    return len(extract_word_types(subset.documents).words)


def bisect_k(corpus, doc_ids_sorted: list[str], target: int, seed: int, tol: float = TABLET_TOLERANCE):
    total = len(doc_ids_sorted)
    full_count = _type_count_for_k(corpus, doc_ids_sorted, total, seed)
    if full_count < target:
        err = abs(full_count - target) / target
        return total, full_count, err, err <= tol
    lo, hi = 1, total
    while lo < hi:
        mid = (lo + hi) // 2
        c = _type_count_for_k(corpus, doc_ids_sorted, mid, seed)
        if c >= target:
            hi = mid
        else:
            lo = mid + 1
    k_hi = lo
    c_hi = _type_count_for_k(corpus, doc_ids_sorted, k_hi, seed)
    candidates = [(k_hi, c_hi)]
    if k_hi > 1:
        k_lo = k_hi - 1
        c_lo = _type_count_for_k(corpus, doc_ids_sorted, k_lo, seed)
        candidates.append((k_lo, c_lo))
    best_k, best_c = min(candidates, key=lambda kc: abs(kc[1] - target) / target)
    err = abs(best_c - target) / target
    return best_k, best_c, err, err <= tol


def linear_b_tablet_noise(corpus) -> dict:
    doc_ids_sorted = sorted(d.id for d in corpus.documents)
    per_seed = []
    for seed in TABLET_SUBSAMPLE_SEEDS:
        t0 = time.time()
        k, count, err, within_tol = bisect_k(corpus, doc_ids_sorted, TABLET_SUBSAMPLE_TARGET, seed)
        chosen = subsample_document_ids(doc_ids_sorted, k, seed)
        documents = corpus.subset(chosen).documents
        analysis = analyze_documents(documents, include_pos_proxy=False)
        per_seed.append(
            {
                "seed": seed,
                "documents_k": k,
                "type_count": count,
                "relative_error": err,
                "within_tolerance": within_tol,
                "differences": analysis["differences"],
            }
        )
        print(f"  tablet subsample seed={seed} k_docs={k} types={count} ({time.time() - t0:.1f}s)", flush=True)

    noise = {}
    for metric in SIGNATURE_METRICS:
        values = [row["differences"][metric] for row in per_seed if row["differences"][metric] is not None]
        noise[metric] = {
            "n": len(values),
            "mean": statistics.mean(values) if values else None,
            "sd": statistics.pstdev(values) if len(values) > 1 else None,
            "min": min(values) if values else None,
            "max": max(values) if values else None,
        }
    return {
        "target_size": TABLET_SUBSAMPLE_TARGET,
        "tolerance": TABLET_TOLERANCE,
        "seeds": TABLET_SUBSAMPLE_SEEDS,
        "per_seed": per_seed,
        "noise": noise,
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> None:
    t_start = time.time()
    results: dict = {
        "spike": "S-008",
        "stem_min": STEM_MIN,
        "draws": DRAWS,
        "seeds": list(SEEDS),
        "listed_definition": (
            "kober.lists.extract_listed_words: a CERTAIN WORD token of >= 2 "
            "normalised signs, followed on its line (skipping separators) by "
            "a logogram or numeral token. A word type is 'listed' if any of "
            "its occurrences meets this, matching F-030's own operationalisation."
        ),
        "corpora": {},
    }

    print("Loading damos ...", flush=True)
    damos = aegean.load("damos")
    print(f"  {len(damos.documents)} documents", flush=True)
    t0 = time.time()
    results["corpora"]["linear_b_damos"] = analyze_documents(damos.documents, include_pos_proxy=True)
    print(f"  full-corpus analysis: {time.time() - t0:.1f}s", flush=True)

    print("Linear B tablet-model subsamples at 988 (seeds 0-19) ...", flush=True)
    t0 = time.time()
    results["linear_b_tablet_noise_988"] = linear_b_tablet_noise(damos)
    print(f"  subsample sweep: {time.time() - t0:.1f}s", flush=True)

    print("Loading lineara (GORILA) ...", flush=True)
    lineara = aegean.load("lineara")
    print(f"  {len(lineara.documents)} documents", flush=True)
    t0 = time.time()
    results["corpora"]["linear_a_gorila"] = analyze_documents(lineara.documents, include_pos_proxy=False)
    print(f"  full-corpus analysis: {time.time() - t0:.1f}s", flush=True)

    print("Loading sigla ...", flush=True)
    sigla = aegean.load("sigla")
    print(f"  {len(sigla.documents)} documents", flush=True)
    t0 = time.time()
    results["corpora"]["linear_a_sigla"] = analyze_documents(sigla.documents, include_pos_proxy=False)
    print(f"  full-corpus analysis: {time.time() - t0:.1f}s", flush=True)

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT_PATH} (total {time.time() - t_start:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
