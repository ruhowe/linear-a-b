#!/usr/bin/env python3
"""S-011: one language in Linear A, or two, with Linear B's own genre and site
spread as the control.

    .venv/bin/python spikes/S-011-one-language-or-two/run.py

See BRIEF.md for the question, the two readings and why this sits outside the main
line. Per spikes/README.md rule 4, this script imports from ``src/`` (read-only)
and edits nothing there.

**Subsets.** Linear A (``aegean.load("lineara")``): (a) tablets (``support_type_of``
== "tablet") against every other support type pooled, plus the stone-vessel group
alone as a secondary comparison against tablets if it clears 100 word tokens; (b)
Hagia Triada (document id starts "HT") against everything else. Linear B
(``aegean.load("damos")``): (c) Knossos against Pylos (``meta.site``); (d) Knossos's
livestock series (``aegean.analysis.hands.series_of`` starting "D") against its
personnel series (starting "A"). (c) and (d) are the "same language, different
genre and site" control the brief asks for.

**Unit.** Word *tokens* for every distribution (sign unigram, first sign, last
sign, word length): CERTAIN WORD tokens, normalised as ``kober.words`` does, two or
more signs, one entry per occurrence -- unlike ``kober.words.extract_word_types``,
which dedupes to types, this keeps repeats because a frequency profile needs the
corpus's own multiplicities. The stage 1 paradigm ratio (``kober.paradigms.build_channel``
ending-channel paradigm count over its ``kober.nulls.n1_draw`` mean, 100 draws) runs
on the *type* set (``frozenset`` of the token list), per A-038 and per every other
Kober statistic in this repo.

**Distances.** Jensen-Shannon divergence (log base 2, so each is in [0, 1]) between
the two subsets' unigram / first-sign / last-sign / length-count distributions;
absolute difference of paradigm ratios for the fifth.

**Noise floor and size control**, both seeded 0-19 per split from an independent
stream (``_seed``, offsets below) so a run is reproducible and no two procedures
share draws. Size control: the larger subset is subsampled (individual tokens,
without replacement) down to the smaller subset's token count, 20 times, and every
distance recomputed against the smaller subset's own (fixed) profile -- this is a
median and range, not a single number, because which tokens are dropped varies by
seed. Noise floor: the two subsets pooled token-for-token, shuffled and cut into two
equal halves (odd token dropped), 20 times, distances recomputed between the
halves -- this is what splitting one population into two random parts of about
these sizes produces with no real difference at all. Report per split and per
distance: the real (full-size) distance, the noise floor's median and 95th
percentile, whether the real distance exceeds that 95th percentile, and the real
distance in units of it -- the quantity the brief's final comparison uses.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.analysis import hands  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from kober.context import support_type_of  # noqa: E402
from kober.nulls import _percentile, n1_draw  # noqa: E402
from kober.paradigms import build_channel  # noqa: E402
from kober.words import _normalise_label  # noqa: E402

STEM_MIN = 2
N_DRAWS = 100
N_SUBSAMPLES = 20
DISTANCE_KEYS = ["sign_js", "first_sign_js", "last_sign_js", "length_js", "paradigm_ratio_diff"]

SPIKE_DIR = Path(__file__).resolve().parent

Word = tuple[str, ...]


# --------------------------------------------------------------------------- #
# Extraction (token level, not type level -- see module docstring)
# --------------------------------------------------------------------------- #


def extract_word_tokens(documents) -> list[Word]:
    """Every eligible CERTAIN WORD token's normalised sign tuple, one entry per
    occurrence. Same eligibility as ``kober.words.extract_word_types``: kind
    WORD, status CERTAIN, normalised label, two or more signs -- just not
    deduped to a set, since the distributions below need the corpus's own
    token multiplicities."""
    out: list[Word] = []
    for doc in documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            labels = [_normalise_label(label)[0] for label in tok.signs]
            if len(labels) >= 2:
                out.append(tuple(labels))
    return out


# --------------------------------------------------------------------------- #
# Per-subset profile
# --------------------------------------------------------------------------- #


class SubsetStats:
    __slots__ = (
        "token_count",
        "type_count",
        "unigram",
        "first",
        "last",
        "length",
        "paradigm_count",
        "null_mean",
        "null_sd",
        "paradigm_ratio",
    )

    def __init__(self, tokens: Sequence[Word], draws: int, seed: int, stem_min: int = STEM_MIN) -> None:
        unigram: Counter = Counter()
        first: Counter = Counter()
        last: Counter = Counter()
        length: Counter = Counter()
        for w in tokens:
            length[len(w)] += 1
            first[w[0]] += 1
            last[w[-1]] += 1
            unigram.update(w)
        self.token_count = len(tokens)
        self.unigram, self.first, self.last, self.length = unigram, first, last, length

        # A-057: a set/frozenset's iteration order depends on the process hash
        # seed, not the RNG seed, and n1_draw's own internal sort is per length
        # group only -- the *order the groups are visited in* still follows
        # this list's order, which changes which length group draws first from
        # the shared rng stream. Sorting here is what makes (seed) reproducible
        # across processes, the same fix kober.words/_group_by_length apply.
        word_types = sorted(set(tokens))
        self.type_count = len(word_types)
        real_count = build_channel(word_types, stem_min=stem_min, mirror=False).paradigm_count_total
        rng = random.Random(seed)
        null_counts = [
            build_channel(n1_draw(word_types, rng), stem_min=stem_min, mirror=False).paradigm_count_total
            for _ in range(draws)
        ]
        self.paradigm_count = real_count
        self.null_mean = statistics.mean(null_counts) if null_counts else 0.0
        self.null_sd = statistics.pstdev(null_counts) if len(null_counts) > 1 else 0.0
        self.paradigm_ratio = (real_count / self.null_mean) if self.null_mean else float("nan")

    def as_dict(self) -> dict:
        return {
            "token_count": self.token_count,
            "type_count": self.type_count,
            "paradigm_count": self.paradigm_count,
            "n1_null_mean": round(self.null_mean, 2),
            "n1_null_sd": round(self.null_sd, 2),
            "paradigm_ratio": self.paradigm_ratio,
        }


def _js(c1: Counter, c2: Counter) -> float:
    """Jensen-Shannon divergence, log base 2, bounded in [0, 1]. NaN if either
    side has zero mass (an empty subset)."""
    n1, n2 = sum(c1.values()), sum(c2.values())
    if n1 == 0 or n2 == 0:
        return float("nan")
    keys = set(c1) | set(c2)
    p = {k: c1.get(k, 0) / n1 for k in keys}
    q = {k: c2.get(k, 0) / n2 for k in keys}
    m = {k: 0.5 * (p[k] + q[k]) for k in keys}

    def kl(a: dict, b: dict) -> float:
        return sum(a[k] * math.log2(a[k] / b[k]) for k in keys if a[k] > 0)

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def distances(a: SubsetStats, b: SubsetStats) -> dict[str, float]:
    return {
        "sign_js": _js(a.unigram, b.unigram),
        "first_sign_js": _js(a.first, b.first),
        "last_sign_js": _js(a.last, b.last),
        "length_js": _js(a.length, b.length),
        "paradigm_ratio_diff": abs(a.paradigm_ratio - b.paradigm_ratio),
    }


# --------------------------------------------------------------------------- #
# Split analysis: real distance, size-matched control, random-halves noise floor
# --------------------------------------------------------------------------- #


def _seed(seed_base: int, stream: str, i: int = 0) -> int:
    """Deterministic, independent seed per (split, stream, draw index) -- the
    same "own stream per usage" pattern ``kober.nulls._sub_seed`` uses, so no
    two procedures in this script ever share a random stream."""
    streams = {"a": 0, "b": 1, "sizematch_tokens": 2, "sizematch_null": 3, "halves_split": 4, "halves_null_x": 5, "halves_null_y": 6}
    return seed_base * 100_000 + streams[stream] * 1000 + i


def analyse_split(label: str, name_a: str, tokens_a: list[Word], name_b: str, tokens_b: list[Word], seed_base: int) -> dict:
    stats_a = SubsetStats(tokens_a, N_DRAWS, seed=_seed(seed_base, "a"))
    stats_b = SubsetStats(tokens_b, N_DRAWS, seed=_seed(seed_base, "b"))
    real = distances(stats_a, stats_b)

    if len(tokens_a) >= len(tokens_b):
        bigger, smaller, smaller_stats = tokens_a, tokens_b, stats_b
    else:
        bigger, smaller, smaller_stats = tokens_b, tokens_a, stats_a

    size_matched: dict[str, list[float]] = {k: [] for k in DISTANCE_KEYS}
    for i in range(N_SUBSAMPLES):
        sample = random.Random(_seed(seed_base, "sizematch_tokens", i)).sample(bigger, len(smaller))
        sample_stats = SubsetStats(sample, N_DRAWS, seed=_seed(seed_base, "sizematch_null", i))
        d = distances(sample_stats, smaller_stats)
        for k in DISTANCE_KEYS:
            size_matched[k].append(d[k])

    pooled = list(tokens_a) + list(tokens_b)
    noise: dict[str, list[float]] = {k: [] for k in DISTANCE_KEYS}
    for i in range(N_SUBSAMPLES):
        idx = list(range(len(pooled)))
        random.Random(_seed(seed_base, "halves_split", i)).shuffle(idx)
        half = len(idx) // 2
        half_x = [pooled[j] for j in idx[:half]]
        half_y = [pooled[j] for j in idx[half : half * 2]]
        stats_x = SubsetStats(half_x, N_DRAWS, seed=_seed(seed_base, "halves_null_x", i))
        stats_y = SubsetStats(half_y, N_DRAWS, seed=_seed(seed_base, "halves_null_y", i))
        d = distances(stats_x, stats_y)
        for k in DISTANCE_KEYS:
            noise[k].append(d[k])

    noise_p95 = {k: _percentile(sorted(noise[k]), 95) for k in DISTANCE_KEYS}
    noise_median = {k: statistics.median(noise[k]) for k in DISTANCE_KEYS}

    def ratio(k: str) -> float:
        p95 = noise_p95[k]
        if not p95 or math.isnan(p95):
            return float("nan")
        return real[k] / p95

    return {
        "label": label,
        "a": {"name": name_a, **stats_a.as_dict()},
        "b": {"name": name_b, **stats_b.as_dict()},
        "real_distance": real,
        "size_matched_median": {k: statistics.median(size_matched[k]) for k in DISTANCE_KEYS},
        "size_matched_range": {k: [min(size_matched[k]), max(size_matched[k])] for k in DISTANCE_KEYS},
        "noise_floor_median": noise_median,
        "noise_floor_p95": noise_p95,
        "exceeds_p95": {k: bool(real[k] > noise_p95[k]) for k in DISTANCE_KEYS},
        "ratio_to_p95": {k: ratio(k) for k in DISTANCE_KEYS},
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> None:
    la = aegean.load("lineara")
    lb = aegean.load("damos")

    tablets = [d for d in la.documents if support_type_of(d) == "tablet"]
    nontablets = [d for d in la.documents if support_type_of(d) != "tablet"]
    stonevessel = [d for d in la.documents if support_type_of(d) == "stone vessel"]
    ht = [d for d in la.documents if d.id.startswith("HT")]
    nonht = [d for d in la.documents if not d.id.startswith("HT")]

    kn = [d for d in lb.documents if (d.meta.site or "").strip() == "Knossos"]
    py = [d for d in lb.documents if (d.meta.site or "").strip() == "Pylos"]
    kn_livestock = [d for d in kn if (hands.series_of(d) or "").startswith("D")]
    kn_personnel = [d for d in kn if (hands.series_of(d) or "").startswith("A")]

    wt = extract_word_tokens

    splits = {
        "a_tablets_vs_other": analyse_split(
            "Linear A: tablets vs every other support type pooled",
            "tablets", wt(tablets), "non-tablets", wt(nontablets), seed_base=1,
        ),
        "b_ht_vs_other": analyse_split(
            "Linear A: Hagia Triada vs everything else",
            "HT", wt(ht), "non-HT", wt(nonht), seed_base=2,
        ),
        "c_knossos_vs_pylos": analyse_split(
            "Linear B: Knossos vs Pylos",
            "Knossos", wt(kn), "Pylos", wt(py), seed_base=3,
        ),
        "d_livestock_vs_personnel": analyse_split(
            "Linear B: Knossos D-series (livestock) vs A-series (personnel)",
            "D-series", wt(kn_livestock), "A-series", wt(kn_personnel), seed_base=4,
        ),
    }

    stone_tokens = wt(stonevessel)
    stone_vessel_extra = None
    if len(stone_tokens) >= 100:
        stone_vessel_extra = analyse_split(
            "Linear A: tablets vs stone vessels alone",
            "tablets", wt(tablets), "stone vessels", stone_tokens, seed_base=5,
        )

    out = {
        "protocol": "S-011, stage 1 paradigm ratio + JS distance profiles, 100 N1 draws, "
        "20 seeded size-matched subsamples, 20 seeded random-halves noise draws",
        "stem_min": STEM_MIN,
        "n_draws": N_DRAWS,
        "n_subsamples": N_SUBSAMPLES,
        "splits": splits,
        "stone_vessel_extra": stone_vessel_extra,
    }

    (SPIKE_DIR / "results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, allow_nan=True) + "\n")
    write_result_md(out)
    print(f"Wrote {SPIKE_DIR / 'results.json'} and {SPIKE_DIR / 'RESULT.md'}")


# --------------------------------------------------------------------------- #
# RESULT.md
# --------------------------------------------------------------------------- #


def _fmt(x: float, nd: int = 3) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    return f"{x:.{nd}f}"


DISTANCE_LABELS = {
    "sign_js": "sign unigram JS",
    "first_sign_js": "first-sign JS",
    "last_sign_js": "last-sign JS",
    "length_js": "word-length JS",
    "paradigm_ratio_diff": "paradigm ratio abs diff",
}


def _split_section(key: str, s: dict) -> str:
    a, b = s["a"], s["b"]
    lines = [f"## {s['label']}", ""]
    lines.append(
        f"`{a['name']}`: {a['token_count']} word tokens, {a['type_count']} types, "
        f"paradigm ratio {_fmt(a['paradigm_ratio'])} (count {a['paradigm_count']}, "
        f"N1 mean {a['n1_null_mean']}). `{b['name']}`: {b['token_count']} word tokens, "
        f"{b['type_count']} types, paradigm ratio {_fmt(b['paradigm_ratio'])} "
        f"(count {b['paradigm_count']}, N1 mean {b['n1_null_mean']})."
    )
    lines.append("")
    lines.append(
        "| distance | real | size-matched median [range] | noise floor median | "
        "noise floor p95 | real > p95 | real / p95 |"
    )
    lines.append("|---|---:|---:|---:|---:|:---:|---:|")
    for k in DISTANCE_KEYS:
        sm_lo, sm_hi = s["size_matched_range"][k]
        lines.append(
            f"| {DISTANCE_LABELS[k]} | {_fmt(s['real_distance'][k])} | "
            f"{_fmt(s['size_matched_median'][k])} [{_fmt(sm_lo)}, {_fmt(sm_hi)}] | "
            f"{_fmt(s['noise_floor_median'][k])} | {_fmt(s['noise_floor_p95'][k])} | "
            f"{'yes' if s['exceeds_p95'][k] else 'no'} | {_fmt(s['ratio_to_p95'][k])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _headline_table(splits: dict) -> str:
    order = ["a_tablets_vs_other", "b_ht_vs_other", "c_knossos_vs_pylos", "d_livestock_vs_personnel"]
    lines = ["| split | " + " | ".join(DISTANCE_LABELS[k] for k in DISTANCE_KEYS) + " |"]
    lines.append("|---|" + "---:|" * len(DISTANCE_KEYS))
    for key in order:
        s = splits[key]
        row = [s["label"]] + [_fmt(s["ratio_to_p95"][k]) for k in DISTANCE_KEYS]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _reading_paragraph(splits: dict) -> str:
    a_ratios = [splits["a_tablets_vs_other"]["ratio_to_p95"][k] for k in DISTANCE_KEYS]
    b_ratios = [splits["b_ht_vs_other"]["ratio_to_p95"][k] for k in DISTANCE_KEYS]
    c_ratios = [splits["c_knossos_vs_pylos"]["ratio_to_p95"][k] for k in DISTANCE_KEYS]
    d_ratios = [splits["d_livestock_vs_personnel"]["ratio_to_p95"][k] for k in DISTANCE_KEYS]

    def clean(xs: list[float]) -> list[float]:
        return [x for x in xs if not (isinstance(x, float) and math.isnan(x))]

    la_max = max(clean(a_ratios + b_ratios), default=float("nan"))
    lb_max = max(clean(c_ratios + d_ratios), default=float("nan"))

    a_exceeds = any(splits["a_tablets_vs_other"]["exceeds_p95"].values())
    b_exceeds = any(splits["b_ht_vs_other"]["exceeds_p95"].values())

    if (not math.isnan(la_max)) and (not math.isnan(lb_max)) and la_max > lb_max and (a_exceeds or b_exceeds):
        verdict = (
            f"**Interesting** applies. At least one Linear A distance (tablets against "
            f"the rest, or Hagia Triada against the rest) sits at {_fmt(la_max, 2)} times "
            f"its own random-halves 95th percentile, above Linear B's largest genre-or-site "
            f"ratio of {_fmt(lb_max, 2)} for the same kind of distance, and clears its own "
            f"noise floor. Linear A's archive-against-religious split is more separated "
            f"than one language produces across genre and site in Linear B, by more than "
            f"the subsample noise accounts for."
        )
    else:
        verdict = (
            f"**Nothing** applies. Linear A's largest tablets-versus-rest or "
            f"HT-versus-rest ratio to its own noise floor is {_fmt(la_max, 2)}, against "
            f"Linear B's largest genre-or-site ratio of {_fmt(lb_max, 2)}. Linear A's split "
            f"sits inside the spread one language produces across genre and site in Linear "
            f"B, once each distance is read in units of its own random-halves noise."
        )
    return verdict


def write_result_md(out: dict) -> None:
    splits = out["splits"]
    parts = [
        "# S-011 result: one language in Linear A, or two?",
        "",
        f"Ran {__import__('datetime').date.today().isoformat()}. Code: `run.py`. Raw numbers: "
        f"`results.json`. `stem_min` {out['stem_min']}, {out['n_draws']} N1 draws per paradigm "
        f"ratio, {out['n_subsamples']} seeded draws each for the size-matched control and the "
        "random-halves noise floor. Distances are Jensen-Shannon divergence (log base 2, "
        "bounded in [0, 1]) on word tokens, plus the absolute difference of stage 1 paradigm "
        "ratios on word types.",
        "",
        _split_section("a", splits["a_tablets_vs_other"]),
        _split_section("b", splits["b_ht_vs_other"]),
        _split_section("c", splits["c_knossos_vs_pylos"]),
        _split_section("d", splits["d_livestock_vs_personnel"]),
    ]

    if out["stone_vessel_extra"] is not None:
        parts.append(_split_section("stone", out["stone_vessel_extra"]))
        parts.append(
            "Stone vessels alone clear the 100-word-token threshold the brief sets for "
            "reporting this group on its own; the tablets-vs-non-tablets split above already "
            "pools them into \"non-tablets\"."
        )
        parts.append("")

    parts.append("## Headline: each split's real distance in units of its own noise floor")
    parts.append("")
    parts.append(_headline_table(splits))
    parts.append("")
    parts.append("## Reading against the brief")
    parts.append("")
    parts.append(_reading_paragraph(splits))
    parts.append("")
    parts.append(
        "This must not be read as evidence for any particular language in either Linear A "
        "set, per the brief. Nothing here is a finding (spikes/README.md rule 1)."
    )
    (SPIKE_DIR / "RESULT.md").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    main()
