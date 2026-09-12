#!/usr/bin/env python3
"""S-010: what kind of script is Linear A? (spikes/S-010-script-type/BRIEF.md)

Computes, for Linear A (GORILA and SigLA, the subject) and six typological
references built by ``fetch.py`` (Linear B, Ugaritic, Sumerian, Akkadian,
Egyptian, Chinese, Greek), the statistics the brief asks for: inventory size and
Heaps exponent, sign hapax share, word length in signs, the Zipf slope over the
top 50 signs, positional entropy (first/medial/last), conditional bigram entropy
within words (maximum likelihood and add-half smoothed), and a Kober-grid
signature — then the distance of Linear A from each reference, in standardised
units of that reference's own 20-subsample spread.

**Target size.** The brief says "Linear A's token count of about 6,400 signs".
corpus-sources.md's own measured figures show DAMOS/GORILA/SigLA "tokens" counts
(CLAUDE.md's "6,406") are word-level Token objects, not sign occurrences — GORILA's
actual CERTAIN-WORD sign-token count (as fetch.py builds it) is 4,011, SigLA's is
3,379. Rather than resolve which of these the brief meant, TARGET_SIGNS below is
fixed at the round number both CLAUDE.md and the brief already use as shorthand for
"Linear A's scale" project-wide (6,400); every reference is subsampled to that many
sign tokens. Linear A itself (both editions) is used at full size, unsampled — it
is the subject, not one of the six references being subsampled down to it.

**Subsampling.** Linear B: the tablet model (CHANGELOG "Floor sweep on Linear B",
scripts/kober_floor_sweep.py) — documents in a seeded random order, accumulated
until the running sign count reaches the target (slight overshoot allowed and
recorded, not corrected by bisection: the brief's "about 6,400" already accepts
approximation). The other six references: contiguous chunks — the corpus's own
documents concatenated into one word stream in file order, a random start point
drawn per seed, words taken in order (wrapping around the stream's end when the
corpus is smaller than 20 non-overlapping windows' worth, which is true for five
of the six: only Sumerian, Egyptian and Greek exceed 128,000 signs). 20 subsample
seeds (0-19) per reference, matching the brief.

**Kober-grid signature.** Not src/kober/grid.py, which is specific to Linear B's
stem/ending paradigm model and consults known Linear-B consonant values — neither
applies to an unknown script or a foreign one with no assumed values. Implemented
here directly from the brief's own description: over a subsample's distinct word
*types*, group by (length, all-positions-but-one), which finds exactly the pairs
of words identical except at one position, without an O(n^2) scan; every such
pair contributes an (undirected, weighted) edge between the two differing signs.
Classes are the edge graph's connected components (union-find, as the existing
Kober grid module also uses for its classes); the reported "modularity" is
Newman's Q for that same partition. The shuffled control independently permutes
each position's column of signs within each word-length class (preserving each
position's own marginal sign frequency, destroying cross-position co-occurrence),
20 draws, mirroring the profile subsampling count.

Output: ``results.json`` (aggregate numbers only — no sign-label lists, no word
lists, no corpus text, per spikes/README.md rule 6) and ``RESULT.md``.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPIKE_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = Path.home() / ".cache" / "linear-a-b" / "reference" / "script-types"

TARGET_SIGNS = 6400
N_SUBSAMPLES = 20
N_GRID_NULL_DRAWS = 20
ZIPF_TOP_N = 50

REFERENCE_CORPORA = [
    "linear_b",
    "ugaritic",
    "sumerian",
    "akkadian",
    "egyptian",
    "chinese",
    "greek",
]
SUBJECT_CORPORA = ["linear_a_gorila", "linear_a_sigla"]

DISTANCE_STATS = [
    "heaps_beta",
    "hapax_share",
    "word_length_mean",
    "zipf_slope",
    "positional_entropy_first",
    "positional_entropy_medial",
    "positional_entropy_last",
    "bigram_entropy_ml",
    "bigram_entropy_add_half",
    "grid_modularity",
]

Word = tuple[str, ...]


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #


def load_corpus(name: str) -> tuple[list[list[Word]], dict]:
    path = REFERENCE_DIR / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    documents = [[tuple(word) for word in doc] for doc in data["documents"]]
    return documents, data


def flatten(documents: list[list[Word]]) -> list[Word]:
    return [w for doc in documents for w in doc]


# --------------------------------------------------------------------------- #
# Subsampling
# --------------------------------------------------------------------------- #


def tablet_model_subsample(documents: list[list[Word]], target_signs: int, seed: int) -> list[Word]:
    """Documents in a seeded random order, accumulated to >= target_signs signs."""
    rng = random.Random(seed)
    order = list(range(len(documents)))
    rng.shuffle(order)
    words: list[Word] = []
    total = 0
    for i in order:
        doc_words = documents[i]
        words.extend(doc_words)
        total += sum(len(w) for w in doc_words)
        if total >= target_signs:
            break
    return words


def contiguous_chunk_subsample(documents: list[list[Word]], target_signs: int, seed: int) -> list[Word]:
    """A random contiguous span of the corpus's own word stream, wrapping if needed."""
    stream = flatten(documents)
    n = len(stream)
    rng = random.Random(seed)
    start = rng.randrange(n)
    words: list[Word] = []
    total = 0
    i = start
    guard = 0
    max_guard = 4 * n + 100
    while total < target_signs and guard < max_guard:
        w = stream[i % n]
        words.append(w)
        total += len(w)
        i += 1
        guard += 1
    return words


# --------------------------------------------------------------------------- #
# Statistics
# --------------------------------------------------------------------------- #


def inventory_and_heaps(words: list[Word]) -> dict:
    stream = [s for w in words for s in w]
    n = len(stream)
    if n < 20:
        return {"inventory_size": len(set(stream)), "n_signs": n, "heaps_beta": None, "heaps_k": None}
    checkpoint_ns = sorted(set(int(x) for x in np.geomspace(max(10, n // 40), n, num=30)))
    seen: set[str] = set()
    cps_n: list[int] = []
    cps_v: list[int] = []
    ci = 0
    for i, s in enumerate(stream, start=1):
        seen.add(s)
        while ci < len(checkpoint_ns) and checkpoint_ns[ci] <= i:
            cps_n.append(i)
            cps_v.append(len(seen))
            ci += 1
    if not cps_n or cps_n[-1] != n:
        cps_n.append(n)
        cps_v.append(len(seen))
    logn = np.log(np.array(cps_n, dtype=float))
    logv = np.log(np.array(cps_v, dtype=float))
    beta, log_k = np.polyfit(logn, logv, 1)
    return {
        "inventory_size": len(seen),
        "n_signs": n,
        "heaps_beta": float(beta),
        "heaps_k": float(math.exp(log_k)),
    }


def hapax_share(words: list[Word]) -> dict:
    stream = [s for w in words for s in w]
    counts = Counter(stream)
    n_hapax = sum(1 for c in counts.values() if c == 1)
    inv = len(counts)
    return {
        "inventory_size": inv,
        "hapax_count": n_hapax,
        "hapax_share": (n_hapax / inv) if inv else None,
    }


def word_length_stats(words: list[Word]) -> dict:
    lengths = [len(w) for w in words]
    if not lengths:
        return {"mean": None, "stdev": None, "median": None, "min": None, "max": None, "histogram": {}}
    return {
        "mean": statistics.mean(lengths),
        "stdev": statistics.pstdev(lengths) if len(lengths) > 1 else 0.0,
        "median": statistics.median(lengths),
        "min": min(lengths),
        "max": max(lengths),
        "histogram": dict(sorted(Counter(lengths).items())),
    }


def zipf_slope(words: list[Word], top_n: int = ZIPF_TOP_N) -> dict:
    stream = [s for w in words for s in w]
    counts = Counter(stream)
    ranked = sorted(counts.values(), reverse=True)[:top_n]
    if len(ranked) < 5:
        return {"slope": None, "intercept": None, "n_ranks": len(ranked)}
    ranks = np.arange(1, len(ranked) + 1, dtype=float)
    logr = np.log(ranks)
    logf = np.log(np.array(ranked, dtype=float))
    slope, intercept = np.polyfit(logr, logf, 1)
    return {"slope": float(slope), "intercept": float(intercept), "n_ranks": len(ranked)}


def _entropy_bits(counter: Counter) -> float | None:
    total = sum(counter.values())
    if total == 0:
        return None
    h = 0.0
    for c in counter.values():
        p = c / total
        h -= p * math.log2(p)
    return h


def positional_entropy(words: list[Word]) -> dict:
    first: Counter = Counter()
    last: Counter = Counter()
    medial: Counter = Counter()
    for w in words:
        if len(w) >= 1:
            first[w[0]] += 1
            last[w[-1]] += 1
        if len(w) >= 3:
            for s in w[1:-1]:
                medial[s] += 1
    return {
        "first": {"entropy_bits": _entropy_bits(first), "n": sum(first.values()), "distinct": len(first)},
        "last": {"entropy_bits": _entropy_bits(last), "n": sum(last.values()), "distinct": len(last)},
        "medial": {"entropy_bits": _entropy_bits(medial), "n": sum(medial.values()), "distinct": len(medial)},
    }


def bigram_conditional_entropy(words: list[Word]) -> dict:
    """Conditional entropy H(next sign | previous sign), within words only.

    ``ml_bits``: maximum likelihood (no smoothing), summed over observed
    contexts, weighted by each context's own empirical probability.
    ``add_half_bits``: Krichevsky-Trofimov add-1/2 smoothing over the full sign
    vocabulary V seen in this subsample's bigrams (as a context or as a
    following sign) — every context's distribution over all V possible next
    signs gets +0.5 pseudo-count, denominator n_context + 0.5*V, including the
    V - (signs actually observed after this context) unobserved signs at
    probability 0.5 / (n_context + 0.5*V) each.
    """
    pair_counts: dict[str, Counter] = defaultdict(Counter)
    context_counts: Counter = Counter()
    for w in words:
        for i in range(len(w) - 1):
            a, b = w[i], w[i + 1]
            pair_counts[a][b] += 1
            context_counts[a] += 1
    total_pairs = sum(context_counts.values())
    if total_pairs == 0:
        return {"ml_bits": None, "add_half_bits": None, "n_bigrams": 0, "vocab_size": 0}

    vocab: set[str] = set()
    for a, ctr in pair_counts.items():
        vocab.add(a)
        vocab.update(ctr.keys())
    V = len(vocab)

    h_ml = 0.0
    h_half = 0.0
    for a, ctr in pair_counts.items():
        n_a = context_counts[a]
        p_a = n_a / total_pairs
        h_a_ml = 0.0
        for _b, n_ab in ctr.items():
            p = n_ab / n_a
            h_a_ml -= p * math.log2(p)
        h_ml += p_a * h_a_ml

        denom = n_a + 0.5 * V
        h_a_half = 0.0
        for _b, n_ab in ctr.items():
            p = (n_ab + 0.5) / denom
            h_a_half -= p * math.log2(p)
        n_unobserved = V - len(ctr)
        if n_unobserved > 0:
            p0 = 0.5 / denom
            h_a_half -= n_unobserved * p0 * math.log2(p0)
        h_half += p_a * h_a_half

    return {"ml_bits": h_ml, "add_half_bits": h_half, "n_bigrams": total_pairs, "vocab_size": V}


# --------------------------------------------------------------------------- #
# Kober-grid signature
# --------------------------------------------------------------------------- #


def _grid_edges(word_types: set[Word]) -> Counter:
    """Weighted edges between signs that differ at an otherwise-identical position.

    Groups words by (length, positions-other-than-i), which is exactly the set
    of words identical to each other except possibly at position i; every
    pair within such a group differs at i (else they would be the same tuple,
    impossible in a set) and contributes one unit of edge weight between their
    two signs at that position.
    """
    by_length: dict[int, list[Word]] = defaultdict(list)
    for w in word_types:
        by_length[len(w)].append(w)

    edges: Counter = Counter()
    for length, words in by_length.items():
        if length < 2:
            continue
        buckets: dict[tuple, list[Word]] = defaultdict(list)
        for w in words:
            for i in range(length):
                key = (i, w[:i], w[i + 1 :])
                buckets[key].append(w)
        for (i, _pre, _post), group in buckets.items():
            if len(group) < 2:
                continue
            n = len(group)
            for a in range(n):
                for b in range(a + 1, n):
                    sa, sb = group[a][i], group[b][i]
                    if sa == sb:
                        continue
                    edges[tuple(sorted((sa, sb)))] += 1
    return edges


def _classes_and_modularity(edges: Counter) -> dict:
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    nodes: set[str] = set()
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
        union(a, b)

    if not nodes:
        return {"n_classes": 0, "n_nodes": 0, "n_edges_distinct": 0, "edge_weight_total": 0, "modularity": None, "class_sizes": []}

    groups: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        groups[find(node)].add(node)
    class_sizes = sorted((len(g) for g in groups.values()), reverse=True)

    m = sum(edges.values())
    degree: Counter = Counter()
    for (a, b), w in edges.items():
        degree[a] += w
        degree[b] += w
    comm_of = {node: find(node) for node in nodes}
    in_weight = sum(w for (a, b), w in edges.items() if comm_of[a] == comm_of[b])
    two_m = 2 * m
    comm_degree: Counter = Counter()
    for node in nodes:
        comm_degree[comm_of[node]] += degree[node]
    term1 = in_weight / m if m else 0.0
    term2 = sum((d / two_m) ** 2 for d in comm_degree.values()) if two_m else 0.0
    q = term1 - term2

    return {
        "n_classes": len(groups),
        "n_nodes": len(nodes),
        "n_edges_distinct": len(edges),
        "edge_weight_total": m,
        "modularity": float(q),
        "class_sizes": class_sizes,
    }


def _shuffled_word_types(word_types: set[Word], rng: random.Random) -> set[Word]:
    by_length: dict[int, list[Word]] = defaultdict(list)
    for w in word_types:
        by_length[len(w)].append(w)
    shuffled: set[Word] = set()
    for length, words in by_length.items():
        if length == 0:
            continue
        columns = [list(col) for col in zip(*words)]
        for col in columns:
            rng.shuffle(col)
        for idx in range(len(words)):
            shuffled.add(tuple(columns[pos][idx] for pos in range(length)))
    return shuffled


def grid_signature(word_types: set[Word], seed: int, n_draws: int = N_GRID_NULL_DRAWS) -> dict:
    real_edges = _grid_edges(word_types)
    real = _classes_and_modularity(real_edges)

    rng = random.Random(seed)
    null_modularity: list[float] = []
    null_n_classes: list[int] = []
    for _ in range(n_draws):
        shuffled = _shuffled_word_types(word_types, rng)
        shuffled_result = _classes_and_modularity(_grid_edges(shuffled))
        if shuffled_result["modularity"] is not None:
            null_modularity.append(shuffled_result["modularity"])
        null_n_classes.append(shuffled_result["n_classes"])

    def _summ(real_val, null_vals):
        if not null_vals:
            return {"mean": None, "sd": None, "real_percentile": None}
        mean = statistics.mean(null_vals)
        sd = statistics.pstdev(null_vals) if len(null_vals) > 1 else 0.0
        pct = None
        if real_val is not None:
            pct = 100.0 * sum(1 for v in null_vals if v <= real_val) / len(null_vals)
        return {"mean": mean, "sd": sd, "real_percentile": pct}

    out = dict(real)
    out["null_modularity"] = _summ(real["modularity"], null_modularity)
    out["null_n_classes"] = _summ(float(real["n_classes"]), [float(v) for v in null_n_classes])
    out["n_word_types"] = len(word_types)
    return out


# --------------------------------------------------------------------------- #
# Per-subsample profile
# --------------------------------------------------------------------------- #


def compute_profile(words: list[Word], grid_seed: int) -> dict:
    word_types = set(words)
    heaps = inventory_and_heaps(words)
    hapax = hapax_share(words)
    wl = word_length_stats(words)
    zipf = zipf_slope(words)
    pos = positional_entropy(words)
    bigram = bigram_conditional_entropy(words)
    grid = grid_signature(word_types, seed=grid_seed)
    return {
        "n_word_tokens": len(words),
        "n_sign_tokens": sum(len(w) for w in words),
        "n_word_types": len(word_types),
        "heaps": heaps,
        "hapax": hapax,
        "word_length": wl,
        "zipf": zipf,
        "positional_entropy": pos,
        "bigram_entropy": bigram,
        "grid": grid,
        # flat scalar view used by the distance computation
        "scalars": {
            "heaps_beta": heaps["heaps_beta"],
            "hapax_share": hapax["hapax_share"],
            "word_length_mean": wl["mean"],
            "zipf_slope": zipf["slope"],
            "positional_entropy_first": pos["first"]["entropy_bits"],
            "positional_entropy_medial": pos["medial"]["entropy_bits"],
            "positional_entropy_last": pos["last"]["entropy_bits"],
            "bigram_entropy_ml": bigram["ml_bits"],
            "bigram_entropy_add_half": bigram["add_half_bits"],
            "grid_modularity": grid["modularity"],
        },
    }


# --------------------------------------------------------------------------- #
# Aggregation and distance
# --------------------------------------------------------------------------- #


def aggregate_scalars(profiles: list[dict]) -> dict:
    """Mean and (population) sd of each DISTANCE_STATS scalar, across subsamples."""
    agg = {}
    for stat in DISTANCE_STATS:
        values = [p["scalars"][stat] for p in profiles if p["scalars"][stat] is not None]
        if len(values) < 2:
            agg[stat] = {"mean": (values[0] if values else None), "sd": None, "n": len(values)}
            continue
        agg[stat] = {"mean": statistics.mean(values), "sd": statistics.pstdev(values), "n": len(values)}
    return agg


def standardised_distance(subject_scalars: dict, ref_agg: dict) -> dict:
    """Per-statistic z-score of the subject against a reference's subsample spread,
    plus a pooled RMS distance over every statistic with a usable (non-zero) sd."""
    per_stat = {}
    z_values = []
    for stat in DISTANCE_STATS:
        subj_val = subject_scalars.get(stat)
        ref = ref_agg.get(stat, {})
        mean, sd = ref.get("mean"), ref.get("sd")
        if subj_val is None or mean is None or sd is None or sd == 0:
            per_stat[stat] = None
            continue
        z = (subj_val - mean) / sd
        per_stat[stat] = z
        z_values.append(z)
    pooled = math.sqrt(sum(z * z for z in z_values) / len(z_values)) if z_values else None
    return {"per_statistic_z": per_stat, "pooled_rms_z": pooled, "n_statistics_used": len(z_values)}


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def build_reference(name: str) -> dict:
    documents, meta = load_corpus(name)
    profiles = []
    for seed in range(N_SUBSAMPLES):
        if name == "linear_b":
            words = tablet_model_subsample(documents, TARGET_SIGNS, seed)
            model = "tablet"
        else:
            words = contiguous_chunk_subsample(documents, TARGET_SIGNS, seed)
            model = "contiguous_chunk"
        profile = compute_profile(words, grid_seed=hash((name, seed)) & 0xFFFFFFFF)
        profile["subsample_seed"] = seed
        profile["subsample_model"] = model
        profiles.append(profile)
    agg = aggregate_scalars(profiles)
    # Linear B's own noise floor: each subsample's distance from the aggregate
    # built from all 20 (including itself) — the brief's "noise floor" use of
    # Linear B against its own subsamples.
    self_distances = [
        standardised_distance(p["scalars"], agg)["pooled_rms_z"] for p in profiles
    ]
    self_distances = [d for d in self_distances if d is not None]
    return {
        "corpus": name,
        "role": meta.get("role"),
        "n_documents": meta.get("n_documents"),
        "n_word_tokens_full_corpus": meta.get("n_word_tokens"),
        "n_sign_tokens_full_corpus": meta.get("n_sign_tokens"),
        "target_signs": TARGET_SIGNS,
        "n_subsamples": N_SUBSAMPLES,
        "subsample_model": profiles[0]["subsample_model"] if profiles else None,
        "profiles": profiles,
        "aggregate": agg,
        "self_noise_floor": {
            "pooled_rms_z_mean": statistics.mean(self_distances) if self_distances else None,
            "pooled_rms_z_max": max(self_distances) if self_distances else None,
            "n": len(self_distances),
        },
    }


def build_subject(name: str) -> dict:
    documents, meta = load_corpus(name)
    words = flatten(documents)
    profile = compute_profile(words, grid_seed=hash((name, "full")) & 0xFFFFFFFF)
    return {
        "corpus": name,
        "role": meta.get("role"),
        "n_documents": meta.get("n_documents"),
        "profile": profile,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only-references", type=str, default=None, help="comma-separated subset (debug)")
    args = ap.parse_args()

    t0 = time.time()
    ref_names = args.only_references.split(",") if args.only_references else REFERENCE_CORPORA

    references = {}
    for name in ref_names:
        t1 = time.time()
        references[name] = build_reference(name)
        print(f"{name}: {N_SUBSAMPLES} subsamples in {time.time()-t1:.1f}s", file=sys.stderr)

    subjects = {}
    for name in SUBJECT_CORPORA:
        subjects[name] = build_subject(name)
        print(f"{name}: full-corpus profile built", file=sys.stderr)

    distances = {}
    for subj_name, subj in subjects.items():
        distances[subj_name] = {}
        for ref_name, ref in references.items():
            distances[subj_name][ref_name] = standardised_distance(subj["profile"]["scalars"], ref["aggregate"])

    result = {
        "spike": "S-010",
        "target_signs": TARGET_SIGNS,
        "n_subsamples": N_SUBSAMPLES,
        "n_grid_null_draws": N_GRID_NULL_DRAWS,
        "distance_statistics": DISTANCE_STATS,
        "references": references,
        "subjects": subjects,
        "distances": distances,
    }
    (SPIKE_DIR / "results.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {SPIKE_DIR / 'results.json'}", file=sys.stderr)
    print(f"Total wall time: {time.time()-t0:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
