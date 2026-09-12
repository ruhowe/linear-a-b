#!/usr/bin/env python3
"""S-014: Barber's digram boundary test, within Linear A and Linear B words.

    .venv/bin/python spikes/S-014-boundaries/run.py

See BRIEF.md for the question and the two readings. Per spikes/README.md rule 4,
this script imports from ``src/`` (read-only) and edits nothing there.

**The test (Barber 1974, ch. IX; docs/works/barber1974.md).** Over every eligible
WORD token (``kind WORD``, ``status CERTAIN``, normalised via
``kober.words._normalise_label``, no length filter beyond that -- a one-sign token
contributes to the sign-marginal count but no digram), count each sign's own
frequency and each ordered adjacent-sign digram's frequency *within* words. The
expected count of digram (a, b) under independence is
``total_digrams * P(a) * P(b)``; a digram observed at least six times below its
expectation (``expected / observed >= 6``, or ``inf`` when observed is 0) is a
predicted boundary, Barber's own criterion, calibrated on her Linear B comparison
corpus. Factors 4 and 8 are reported alongside for sensitivity. Every corpus and
every subsample recomputes this table from its own text -- there is no
transferring Linear B's specific flagged pairs onto Linear A; what carries over is
only the choice of factor, which Barber calibrated on Linear B.

**Rate.** For each threshold, the predicted-boundary rate per 1,000 in-word sign
pairs is ``1000 * sum(digram_count[p] for p in predicted_set) / total_digrams`` --
equivalent to checking every digram occurrence in position order and counting
matches, since summing a pair's aggregate count is the same as counting its
occurrences one by one.

**Matched size.** Linear A (GORILA)'s own in-word digram count is the target;
twenty tablet-model subsamples of Linear B (``kober.words.subsample_document_ids``,
seeds 0-19, bisected on document count exactly as
``scripts/kober_floor_sweep.py`` bisects on word-type count, A-063's monotonicity
argument carrying over unchanged since digram count is also non-decreasing in a
fixed permutation's prefix) give Linear B's matched-size range for comparison.
SigLA is reported at its own native size, not separately matched, since GORILA is
the canonical Linear A edition (docs/ai_context/corpus-sources.md) and the brief
asks for one range.

**Reverse check.** At every point on a line where one eligible word ends and the
next eligible word begins (``doc.line_tokens``, skipping non-word tokens between
them), the flanking pair (word's last sign, next word's first sign) is one actual
boundary instance. The fraction of these that fall in the corpus's own predicted
set is the reverse check -- GORILA and, as a baseline, the Linear B full corpus;
SigLA carries no line structure (docs/ai_context/corpus-sources.md) and is
excluded, per the brief.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

from aegean.core.model import Document, ReadingStatus, TokenKind  # noqa: E402

from kober.words import _normalise_label, subsample_document_ids  # noqa: E402

FACTORS = (4, 6, 8)
PRIMARY_FACTOR = 6
TABLET_SEEDS = list(range(20))
TOLERANCE = 0.02  # matches scripts/kober_floor_sweep.py's A-063 convention


# --------------------------------------------------------------------------- #
# Sign and digram counting
# --------------------------------------------------------------------------- #


def eligible_word_labels(doc: Document) -> list[tuple[str, ...]]:
    """Every eligible WORD token's normalised sign-label tuple, in document order."""
    out: list[tuple[str, ...]] = []
    for tok in doc.tokens:
        if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
            continue
        labels = tuple(_normalise_label(label)[0] for label in tok.signs)
        if labels:
            out.append(labels)
    return out


def collect_signs_and_digrams(documents) -> tuple[Counter, Counter, int, int]:
    """(sign_counts, digram_counts, total_signs, total_digrams) over every
    eligible word in ``documents``."""
    sign_counts: Counter = Counter()
    digram_counts: Counter = Counter()
    total_signs = 0
    total_digrams = 0
    for doc in documents:
        for word in eligible_word_labels(doc):
            for s in word:
                sign_counts[s] += 1
                total_signs += 1
            for i in range(len(word) - 1):
                digram_counts[(word[i], word[i + 1])] += 1
                total_digrams += 1
    return sign_counts, digram_counts, total_signs, total_digrams


def digram_factors(sign_counts: Counter, digram_counts: Counter, total_signs: int, total_digrams: int) -> dict:
    """expected/observed factor for every ordered pair of signs that occur at
    all in the corpus (Barber's independence test)."""
    signs = list(sign_counts)
    factors: dict[tuple[str, str], float] = {}
    for a in signs:
        pa = sign_counts[a] / total_signs
        for b in signs:
            pb = sign_counts[b] / total_signs
            expected = total_digrams * pa * pb
            observed = digram_counts.get((a, b), 0)
            factors[(a, b)] = (expected / observed) if observed > 0 else math.inf
    return factors


def predicted_boundary_sets(factors: dict) -> dict[int, set]:
    return {f: {pair for pair, val in factors.items() if val >= f} for f in FACTORS}


def boundary_rate_per_1000(digram_counts: Counter, total_digrams: int, predicted: set) -> float:
    if total_digrams == 0:
        return 0.0
    matched = sum(digram_counts.get(pair, 0) for pair in predicted)
    return 1000.0 * matched / total_digrams


def full_table(documents) -> dict:
    sign_counts, digram_counts, total_signs, total_digrams = collect_signs_and_digrams(documents)
    factors = digram_factors(sign_counts, digram_counts, total_signs, total_digrams)
    predicted = predicted_boundary_sets(factors)
    rates = {f: boundary_rate_per_1000(digram_counts, total_digrams, predicted[f]) for f in FACTORS}
    return {
        "n_signs_seen": len(sign_counts),
        "total_signs": total_signs,
        "total_digrams": total_digrams,
        "n_ordered_pairs_considered": len(factors),
        "predicted_boundary_pairs_count": {f: len(predicted[f]) for f in FACTORS},
        "predicted_boundary_rate_per_1000": rates,
        "_digram_counts": digram_counts,
        "_predicted": predicted,
    }


# --------------------------------------------------------------------------- #
# Reverse check: actual word-to-word boundaries on the same line
# --------------------------------------------------------------------------- #


def boundary_crossing_pairs(documents) -> Counter:
    counts: Counter = Counter()
    for doc in documents:
        for line in doc.line_tokens:
            prev_last: str | None = None
            for tok in line:
                if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                    continue
                labels = tuple(_normalise_label(label)[0] for label in tok.signs)
                if not labels:
                    continue
                if prev_last is not None:
                    counts[(prev_last, labels[0])] += 1
                prev_last = labels[-1]
    return counts


def reverse_check(documents, predicted: dict[int, set]) -> dict:
    crossings = boundary_crossing_pairs(documents)
    total = sum(crossings.values())
    fractions = {}
    for f in FACTORS:
        matched = sum(crossings.get(pair, 0) for pair in predicted[f])
        fractions[f] = (matched / total) if total else 0.0
    return {"total_actual_boundary_instances": total, "fraction_predicted_boundary": fractions}


# --------------------------------------------------------------------------- #
# Tablet-model subsampling, bisected on total in-word digram count
# --------------------------------------------------------------------------- #


def _digram_count_for_k(corpus, doc_ids_sorted: list[str], k: int, seed: int) -> int:
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    subset_docs = corpus.subset(chosen).documents
    _sc, _dc, _ts, total_digrams = collect_signs_and_digrams(subset_docs)
    return total_digrams


def bisect_k(corpus, doc_ids_sorted: list[str], target: int, seed: int, tol: float = TOLERANCE):
    """Return (k, resulting_digram_count, relative_error, within_tolerance),
    same structure and tie-break as scripts/kober_floor_sweep.py's bisect_k,
    with digram count in place of word-type count (both non-decreasing in a
    fixed permutation's prefix, A-063's argument carrying over unchanged)."""
    total_docs = len(doc_ids_sorted)
    full_count = _digram_count_for_k(corpus, doc_ids_sorted, total_docs, seed)
    if full_count < target:
        err = abs(full_count - target) / target
        return total_docs, full_count, err, err <= tol

    lo, hi = 1, total_docs
    while lo < hi:
        mid = (lo + hi) // 2
        c = _digram_count_for_k(corpus, doc_ids_sorted, mid, seed)
        if c >= target:
            hi = mid
        else:
            lo = mid + 1
    k_hi = lo
    c_hi = _digram_count_for_k(corpus, doc_ids_sorted, k_hi, seed)
    candidates = [(k_hi, c_hi)]
    if k_hi > 1:
        k_lo = k_hi - 1
        c_lo = _digram_count_for_k(corpus, doc_ids_sorted, k_lo, seed)
        candidates.append((k_lo, c_lo))
    best_k, best_c = min(candidates, key=lambda kc: abs(kc[1] - target) / target)
    err = abs(best_c - target) / target
    return best_k, best_c, err, err <= tol


def run_subsample(corpus, doc_ids_sorted: list[str], target: int, seed: int) -> dict:
    k, count, err, within_tol = bisect_k(corpus, doc_ids_sorted, target, seed)
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    documents = corpus.subset(chosen).documents
    table = full_table(documents)
    return {
        "seed": seed,
        "documents_k": k,
        "total_digrams": table["total_digrams"],
        "target": target,
        "relative_error": err,
        "within_tolerance": within_tol,
        "predicted_boundary_rate_per_1000": table["predicted_boundary_rate_per_1000"],
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def _public(table: dict) -> dict:
    return {k: v for k, v in table.items() if not k.startswith("_")}


def main() -> dict:
    damos_corpus = aegean.load("damos")
    lineara_corpus = aegean.load("lineara")
    sigla_corpus = aegean.load("sigla")

    damos_docs = damos_corpus.documents
    lineara_docs = lineara_corpus.documents
    sigla_docs = sigla_corpus.documents

    damos_table = full_table(damos_docs)
    lineara_table = full_table(lineara_docs)
    sigla_table = full_table(sigla_docs)

    target = lineara_table["total_digrams"]

    doc_ids_sorted = sorted(d.id for d in damos_docs)
    subsamples = [run_subsample(damos_corpus, doc_ids_sorted, target, seed) for seed in TABLET_SEEDS]
    rates_by_factor = {
        f: [s["predicted_boundary_rate_per_1000"][f] for s in subsamples] for f in FACTORS
    }

    damos_reverse = reverse_check(damos_docs, damos_table["_predicted"])
    lineara_reverse = reverse_check(lineara_docs, lineara_table["_predicted"])

    def within_range(value: float, values: list[float]) -> dict:
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "value": value,
            "above_max": value > max(values),
            "below_min": value < min(values),
        }

    payload = {
        "question": (
            "Do Barber's digram boundary tests predict more within-word boundaries "
            "in Linear A than in Linear B at matched size, and do real word "
            "boundaries fall where the test predicts?"
        ),
        "protocol": {
            "factors_reported": list(FACTORS),
            "primary_factor": PRIMARY_FACTOR,
            "tablet_model_seeds": TABLET_SEEDS,
            "tolerance": TOLERANCE,
            "matched_size_target_total_digrams": target,
            "matched_size_source": "lineara (GORILA) full corpus, own in-word digram count",
        },
        "damos_full": _public(damos_table),
        "lineara_full": _public(lineara_table),
        "sigla_full": _public(sigla_table),
        "damos_tablet_model_subsamples_at_lineara_size": subsamples,
        "damos_matched_size_range_per_1000": {
            f: within_range(lineara_table["predicted_boundary_rate_per_1000"][f], rates_by_factor[f])
            for f in FACTORS
        },
        "reverse_check": {
            "damos_full_baseline": damos_reverse,
            "lineara_gorila": lineara_reverse,
            "sigla": "excluded: no line structure",
        },
    }

    out_dir = Path(__file__).resolve().parent
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return payload


if __name__ == "__main__":
    data = main()
    print("target total_digrams (lineara):", data["protocol"]["matched_size_target_total_digrams"])
    print("damos full rate/1000:", data["damos_full"]["predicted_boundary_rate_per_1000"])
    print("lineara full rate/1000:", data["lineara_full"]["predicted_boundary_rate_per_1000"])
    print("sigla full rate/1000:", data["sigla_full"]["predicted_boundary_rate_per_1000"])
    print("damos matched-size range (per_1000) vs lineara:", data["damos_matched_size_range_per_1000"])
    print("reverse check:", data["reverse_check"]["damos_full_baseline"], data["reverse_check"]["lineara_gorila"])
