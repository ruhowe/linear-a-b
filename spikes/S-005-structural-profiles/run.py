#!/usr/bin/env python3
"""S-005: structural profiles, Linear A against syllabically written corpora
(spikes/S-005-structural-profiles/BRIEF.md). Reads the private respelled
corpora ``build_corpora.py`` wrote under
``~/.cache/linear-a-b/reference/s005/`` (outside the repo), builds twenty
988-word-type subsamples of each plus the full set, profiles every one with
``src/kober`` functions used read-only exactly as ``scripts/kober_run.py`` /
``kober.report.build_report`` call them, and reports Linear A's distance from
each reference in units of that reference's own twenty-subsample spread --
pooled only within the order-driven and inventory-driven statistic groups
(F-044's rule), never across them.

Nine statistics per profile, five order-driven and four inventory-driven
(brief's own split):

- order-driven: paradigm-count ratio (real / N1 p99), max-alternation-support
  ratio (real / N2 p99), ending entropy (Shannon entropy, bits, of the
  word-type set's own last-sign distribution), prefix-channel paradigm ratio
  (real / N1 p99, prefix mirror), medial-channel pair-count ratio (real / N1
  p99, ``kober.medial``).
- inventory-driven: ending inventory size (distinct last signs), sign
  inventory size, sign hapax share, Heaps beta -- copied from S-010's own
  definitions (``spikes/S-010-script-type/run.py``), adapted from a token
  *stream* (S-010's unit) to a word-*type* set (this instrument's unit,
  matching ``kober.words``): the sign stream fed to the inventory/Heaps/hapax
  functions is every sign in the 988 word types, in one fixed
  (lexicographically sorted) order, applied identically to every corpus so no
  corpus gets an order advantage from having a real reading order.

The medial channel's consonant-sharing check and ``kober.grid`` are never run
here: both consult ``kober.values.consonant_of``, genuine Ventris values, and
none of these corpora's sign labels are real Linear B signs (see
RESPELLING.md). Only ``medial.pair_count`` and its N1 null are used.

Output: ``results.json`` (aggregate only) and ``RESULT.md``.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPIKE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from kober.medial import build_medial_report  # noqa: E402
from kober.nulls import run_n1, run_n2  # noqa: E402
from kober.paradigms import ending_channel, prefix_channel  # noqa: E402
from kober.words import extract_word_types, subsample_document_ids  # noqa: E402

REFERENCE_DIR = Path.home() / ".cache" / "linear-a-b" / "reference"
S005_DIR = REFERENCE_DIR / "s005"
KOBER_SWEEP_DIR = ROOT / "results" / "kober-sweep"

STEM_MIN = 2
PERMS = 200
SEED = 0
TARGET_TYPES = 988
N_SUBSAMPLES = 20

Word = tuple[str, ...]

ORDER_DRIVEN = [
    "paradigm_ratio",
    "max_support_ratio",
    "ending_entropy",
    "prefix_ratio",
    "medial_ratio",
]
INVENTORY_DRIVEN = [
    "ending_inventory_size",
    "sign_inventory_size",
    "hapax_share",
    "heaps_beta",
]
ALL_STATS = ORDER_DRIVEN + INVENTORY_DRIVEN


# --------------------------------------------------------------------------- #
# Statistics copied from S-010's own definitions (spikes/S-010-script-type/run.py),
# adapted to run over a word-*type* set's own sign stream rather than a token
# stream -- see module docstring.
# --------------------------------------------------------------------------- #


def _inventory_and_heaps(sign_stream: list[str]) -> dict:
    n = len(sign_stream)
    if n < 20:
        return {"inventory_size": len(set(sign_stream)), "heaps_beta": None}
    checkpoint_ns = sorted(set(int(x) for x in np.geomspace(max(10, n // 40), n, num=30)))
    seen: set[str] = set()
    cps_n: list[int] = []
    cps_v: list[int] = []
    ci = 0
    for i, s in enumerate(sign_stream, start=1):
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
    beta, _log_k = np.polyfit(logn, logv, 1)
    return {"inventory_size": len(seen), "heaps_beta": float(beta)}


def _hapax_share(sign_stream: list[str]) -> float | None:
    counts = Counter(sign_stream)
    inv = len(counts)
    if not inv:
        return None
    n_hapax = sum(1 for c in counts.values() if c == 1)
    return n_hapax / inv


def _shannon_entropy_bits(items: list[str]) -> float | None:
    if not items:
        return None
    c = Counter(items)
    n = sum(c.values())
    h = 0.0
    for v in c.values():
        p = v / n
        h -= p * math.log2(p)
    return h


def _safe_ratio(real: float, p99: float) -> float | None:
    if p99 > 0:
        return real / p99
    if real > 0:
        return None  # undefined: null never produced a positive value to compare against
    return 1.0  # both zero: no signal either way


# --------------------------------------------------------------------------- #
# The profile itself
# --------------------------------------------------------------------------- #


def compute_profile(words: frozenset[Word], seed: int = SEED, perms: int = PERMS, stem_min: int = STEM_MIN) -> dict:
    words = frozenset(words)
    ending = ending_channel(words, stem_min=stem_min)
    prefix = prefix_channel(words, stem_min=stem_min)
    n1 = run_n1(words, stem_min, perms, seed, ending, prefix)
    n2_ending = run_n2(words, stem_min, perms, seed, mirror=False, real_channel=ending)
    medial = build_medial_report(words, perms, seed)

    real_max_support = max(ending.alternation_support.values()) if ending.alternation_support else 0
    last_signs = [w[-1] for w in words if w]
    sign_stream = [s for w in sorted(words) for s in w]  # fixed order: every corpus alike

    heaps = _inventory_and_heaps(sign_stream)
    scalars = {
        "paradigm_ratio": _safe_ratio(ending.paradigm_count_total, n1.ending_paradigm_count.p99),
        "max_support_ratio": _safe_ratio(real_max_support, n2_ending.max_support.p99),
        "ending_entropy": _shannon_entropy_bits(last_signs),
        "prefix_ratio": _safe_ratio(prefix.paradigm_count_total, n1.prefix_paradigm_count.p99),
        "medial_ratio": _safe_ratio(medial.pair_count, medial.pair_count_null.p99),
        "ending_inventory_size": float(len(set(last_signs))),
        "sign_inventory_size": float(heaps["inventory_size"]),
        "hapax_share": _hapax_share(sign_stream),
        "heaps_beta": heaps["heaps_beta"],
    }
    diagnostics = {
        "n_word_types": len(words),
        "paradigm_count": ending.paradigm_count_total,
        "paradigm_count_n1_p99": n1.ending_paradigm_count.p99,
        "max_support": real_max_support,
        "max_support_n2_p99": n2_ending.max_support.p99,
        "prefix_paradigm_count": prefix.paradigm_count_total,
        "prefix_paradigm_count_n1_p99": n1.prefix_paradigm_count.p99,
        "medial_pair_count": medial.pair_count,
        "medial_pair_count_n1_p99": medial.pair_count_null.p99,
    }
    return {"scalars": scalars, "diagnostics": diagnostics}


# --------------------------------------------------------------------------- #
# Loading and subsampling each corpus
# --------------------------------------------------------------------------- #


def load_s005(name: str) -> dict:
    return json.loads((S005_DIR / f"{name}.json").read_text(encoding="utf-8"))


def chunk_subsample(token_stream: list[Word], target: int, seed: int) -> frozenset[Word]:
    """Greek only: a random contiguous span of the ordered token stream,
    walked until ``target`` distinct types have been seen, wrapping at the
    stream's end (mirrors S-010's ``contiguous_chunk_subsample``, but keyed
    to a distinct-type target rather than a sign-count budget, since this
    instrument's unit is the word type, not the sign token)."""
    n = len(token_stream)
    rng = random.Random(seed)
    start = rng.randrange(n)
    seen: set[Word] = set()
    i = start
    guard = 0
    max_guard = 4 * n + 100
    while len(seen) < target and guard < max_guard:
        seen.add(token_stream[i % n])
        i += 1
        guard += 1
    return frozenset(seen)


def random_subset(pool: list[Word], target: int, seed: int) -> frozenset[Word]:
    rng = random.Random(seed)
    pool_sorted = sorted(pool)
    k = min(target, len(pool_sorted))
    return frozenset(rng.sample(pool_sorted, k))


def build_reference_subsamples(name: str, payload: dict) -> tuple[list[frozenset[Word]], frozenset[Word], dict]:
    """Returns (twenty subsamples, full set, meta) for one s005 reference."""
    if payload.get("ordered"):
        stream = [tuple(w) for w in payload["token_stream"]]
        full = frozenset(stream)
        subs = [chunk_subsample(stream, TARGET_TYPES, seed) for seed in range(N_SUBSAMPLES)]
        meta = {"model": "chunk", "n_full_types": len(full), "target": TARGET_TYPES}
        return subs, full, meta

    pool = [tuple(w) for w in payload["types"]]
    full = frozenset(pool)
    n_pool = len(pool)
    if n_pool >= TARGET_TYPES:
        subs = [random_subset(pool, TARGET_TYPES, seed) for seed in range(N_SUBSAMPLES)]
        meta = {"model": "random_subset", "n_full_types": n_pool, "target": TARGET_TYPES}
        return subs, full, meta

    # Under-target reference (Etruscan): reduced-size bootstrap, flagged.
    reduced = max(2, int(0.8 * n_pool))
    subs = [random_subset(pool, reduced, seed) for seed in range(N_SUBSAMPLES)]
    meta = {
        "model": "random_subset_reduced",
        "n_full_types": n_pool,
        "target": TARGET_TYPES,
        "reduced_target": reduced,
        "caveat": (
            f"Pool has only {n_pool} usable types, short of the {TARGET_TYPES} target. "
            f"Subsamples here are 20 draws of {reduced} (80% of the pool), not {TARGET_TYPES}; "
            "not directly comparable in scale to every other reference's spread."
        ),
    }
    return subs, full, meta


def linear_b_tablet_subsamples() -> tuple[list[frozenset[Word]], dict]:
    """Reuses the exact document-count K per seed that
    ``scripts/kober_floor_sweep.py`` found for 988-word-type tablet-model
    subsamples (``results/kober-sweep/kober-sweep-tablet-size988-seed*.json``),
    so this spike's Linear B reference is the *same* twenty word-type sets
    F-022 already measured, not a fresh draw."""
    import aegean

    corpus = aegean.load("damos")
    doc_ids_sorted = sorted(d.id for d in corpus.documents)
    subs = []
    ks = []
    for seed in range(N_SUBSAMPLES):
        f = KOBER_SWEEP_DIR / f"kober-sweep-tablet-size988-seed{seed}.json"
        d = json.loads(f.read_text(encoding="utf-8"))
        k = d["sweep"]["documents_k"]
        ks.append(k)
        chosen = subsample_document_ids(doc_ids_sorted, k, seed)
        subset_docs = corpus.subset(chosen).documents
        words = extract_word_types(subset_docs).words
        subs.append(words)
    meta = {"model": "tablet (reused from results/kober-sweep)", "documents_k": ks}
    return subs, meta


# --------------------------------------------------------------------------- #
# Aggregation and distance
# --------------------------------------------------------------------------- #


def aggregate(profiles: list[dict]) -> dict:
    agg = {}
    for stat in ALL_STATS:
        values = [p["scalars"][stat] for p in profiles if p["scalars"][stat] is not None]
        if len(values) < 2:
            agg[stat] = {"mean": (values[0] if values else None), "sd": None, "n": len(values)}
            continue
        agg[stat] = {"mean": statistics.mean(values), "sd": statistics.pstdev(values), "n": len(values)}
    return agg


def per_statistic_z(subject_scalars: dict, ref_agg: dict) -> dict:
    out = {}
    for stat in ALL_STATS:
        subj = subject_scalars.get(stat)
        ref = ref_agg.get(stat, {})
        mean, sd = ref.get("mean"), ref.get("sd")
        if subj is None or mean is None or sd is None or sd == 0:
            out[stat] = None
            continue
        out[stat] = (subj - mean) / sd
    return out


def pooled_rms(z: dict, group: list[str]) -> tuple[float | None, int]:
    vals = [z[s] for s in group if z.get(s) is not None]
    if not vals:
        return None, 0
    return math.sqrt(sum(v * v for v in vals) / len(vals)), len(vals)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

SYNTHETIC_REFS = ["greek", "hittite", "akkadian", "sumerian", "ugaritic", "etruscan"]


def build_reference_result(name: str) -> dict:
    payload = load_s005(name)
    subs, full, sub_meta = build_reference_subsamples(name, payload)
    profiles = [compute_profile(s) for s in subs]
    full_profile = compute_profile(full) if len(full) else None
    agg = aggregate(profiles)
    self_z = [pooled_rms(per_statistic_z(p["scalars"], agg), ALL_STATS)[0] for p in profiles]
    self_z = [v for v in self_z if v is not None]
    return {
        "name": name,
        "meta": {k: v for k, v in payload.items() if k not in ("types", "token_stream")},
        "subsample_meta": sub_meta,
        "aggregate": agg,
        "full_profile": full_profile,
        "n_subsample_profiles": len(profiles),
        "self_noise_floor_rms_z": {
            "mean": statistics.mean(self_z) if self_z else None,
            "max": max(self_z) if self_z else None,
        },
    }


def build_linear_b_result() -> dict:
    subs, sub_meta = linear_b_tablet_subsamples()
    profiles = [compute_profile(s) for s in subs]
    agg = aggregate(profiles)
    self_z = [pooled_rms(per_statistic_z(p["scalars"], agg), ALL_STATS)[0] for p in profiles]
    self_z = [v for v in self_z if v is not None]
    return {
        "name": "linear_b",
        "meta": {"source": "DAMOS via aegean.load('damos')", "role": "the known case: real Linear B"},
        "subsample_meta": sub_meta,
        "aggregate": agg,
        "full_profile": None,
        "n_subsample_profiles": len(profiles),
        "self_noise_floor_rms_z": {
            "mean": statistics.mean(self_z) if self_z else None,
            "max": max(self_z) if self_z else None,
        },
    }


def build_subjects() -> dict:
    import aegean

    gorila = extract_word_types(aegean.load("lineara").documents).words
    sigla = extract_word_types(aegean.load("sigla").documents).words
    return {
        "linear_a_gorila": {"n_word_types": len(gorila), "profile": compute_profile(gorila)},
        "linear_a_sigla": {"n_word_types": len(sigla), "profile": compute_profile(sigla)},
    }


def main() -> None:
    t0 = time.time()
    references: dict[str, dict] = {}
    print("Linear B (tablet-model, reused F-022 subsamples)...", file=sys.stderr)
    references["linear_b"] = build_linear_b_result()
    for name in SYNTHETIC_REFS:
        print(f"{name}...", file=sys.stderr)
        references[name] = build_reference_result(name)

    print("Linear A (GORILA, SigLA)...", file=sys.stderr)
    subjects = build_subjects()

    distances: dict[str, dict] = {}
    for subj_name, subj in subjects.items():
        distances[subj_name] = {}
        for ref_name, ref in references.items():
            z = per_statistic_z(subj["profile"]["scalars"], ref["aggregate"])
            order_rms, order_n = pooled_rms(z, ORDER_DRIVEN)
            inv_rms, inv_n = pooled_rms(z, INVENTORY_DRIVEN)
            distances[subj_name][ref_name] = {
                "per_statistic_z": z,
                "order_driven_pooled_rms_z": order_rms,
                "order_driven_n": order_n,
                "inventory_driven_pooled_rms_z": inv_rms,
                "inventory_driven_n": inv_n,
            }

    result = {
        "spike": "S-005",
        "protocol": {
            "stem_min": STEM_MIN,
            "perms": PERMS,
            "seed": SEED,
            "target_types": TARGET_TYPES,
            "n_subsamples": N_SUBSAMPLES,
            "order_driven_stats": ORDER_DRIVEN,
            "inventory_driven_stats": INVENTORY_DRIVEN,
        },
        "references": references,
        "subjects": subjects,
        "distances": distances,
    }
    (SPIKE_DIR / "results.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {SPIKE_DIR / 'results.json'} in {time.time() - t0:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
