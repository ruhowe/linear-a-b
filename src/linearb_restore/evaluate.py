"""Scoring, with the two things that make a number on this corpus mean anything.

**Every figure carries its floor.** Top-k on a 77-sign inventory is not intuitive: k=20
admits 26% of all candidates, so frequency alone scores highly. A top-k number quoted
without the prior's score on the same axis invites the reader to over-read it.

**Every figure is stratified by whether the word type was seen in training.** On the D
tablets a handful of place names recur across dozens of documents. An aggregate score is
therefore mostly a measurement of how well a model recalls a gazetteer. Splitting
seen from unseen separates memorisation from generalisation, and the gap between them
is the actual finding. Neither published paper this project compares against appears to
report it.

Confidence intervals and paired tests come from pyaegean's own pure-stdlib helpers
(``analysis.stats.bootstrap_ci_seq``, ``analysis.significance``), which take plain lists
of per-item scores.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Iterable, Sequence as Seq

from aegean.analysis.significance import mcnemar, paired_bootstrap
from aegean.analysis.stats import bootstrap_ci_seq

from .mask import MaskedItem
from .rankers import Ranker
from .split import Fold
from .vocab import Vocabulary, build_vocabulary

__all__ = ["Score", "Result", "evaluate_fold", "cross_validate", "compare"]

TOP_K = (1, 5, 20)


@dataclass
class Score:
    """Top-k accuracy for one stratum, with bootstrap intervals."""

    label: str
    n: int
    hits: dict[int, list[int]] = field(default_factory=dict)

    def accuracy(self, k: int) -> float:
        vals = self.hits.get(k, [])
        return statistics.fmean(vals) if vals else 0.0

    def interval(self, k: int, *, n_resamples: int = 999, seed: int = 0) -> tuple[float, float]:
        vals = self.hits.get(k, [])
        if len(vals) < 2:
            return (0.0, 0.0)
        ci = bootstrap_ci_seq(vals, statistics.fmean, n_resamples=n_resamples, seed=seed)
        return (ci.low, ci.high)

    def row(self) -> dict:
        out = {"stratum": self.label, "n": self.n}
        for k in TOP_K:
            low, high = self.interval(k)
            out[f"top{k}"] = self.accuracy(k)
            out[f"top{k}_ci"] = (low, high)
        return out


@dataclass
class Result:
    """One ranker's scores, overall and by stratum."""

    ranker: str
    overall: Score
    seen: Score
    unseen: Score
    single_sign: Score
    per_item_hits: dict[int, list[int]] = field(default_factory=dict)
    candidate_set_size: int = 0

    def top_k_share(self, k: int) -> float:
        return min(k, self.candidate_set_size) / self.candidate_set_size if self.candidate_set_size else 0.0


def _score_items(
    ranker: Ranker, items: Seq[MaskedItem], vocab: Vocabulary
) -> tuple[dict[str, Score], dict[int, list[int]]]:
    strata = {
        "overall": Score("all items", 0),
        "seen": Score("word type seen in training", 0),
        "unseen": Score("word type unseen in training", 0),
        "single": Score("single-sign words (no within-word context)", 0),
    }
    for score in strata.values():
        score.hits = {k: [] for k in TOP_K}
    flat: dict[int, list[int]] = {k: [] for k in TOP_K}

    for item in items:
        # Only single-sign-answer items are scored; span items are evaluated separately.
        if item.n_masked != 1:
            continue
        ranked = ranker.rank(item)
        answer = item.answers[0]
        try:
            position = ranked.index(answer)
        except ValueError:
            position = len(ranked) + 1

        buckets = [strata["overall"]]
        buckets.append(strata["seen"] if vocab.seen_word(item.word_text) else strata["unseen"])
        if item.single_sign_word:
            buckets.append(strata["single"])

        for k in TOP_K:
            hit = int(position < k)
            flat[k].append(hit)
            for bucket in buckets:
                bucket.hits[k].append(hit)
        for bucket in buckets:
            bucket.n += 1

    return strata, flat


def evaluate_fold(
    ranker: Ranker, fold: Fold, items: Seq[MaskedItem]
) -> tuple[dict[str, Score], dict[int, list[int]], Vocabulary]:
    train, test = fold.split(items)
    vocab = build_vocabulary(train)
    ranker.fit(train, vocab)
    strata, flat = _score_items(ranker, test, vocab)
    return strata, flat, vocab


def cross_validate(
    ranker_factory, folds: Seq[Fold], items: Seq[MaskedItem]
) -> Result:
    """Pool per-item results across folds.

    Pooling rather than averaging fold means: every item is tested exactly once, so the
    pooled list is a clean per-item sample for the bootstrap, and folds of unequal size
    do not need weighting.
    """
    merged = {
        key: Score(label, 0)
        for key, label in (
            ("overall", "all items"),
            ("seen", "word type seen in training"),
            ("unseen", "word type unseen in training"),
            ("single", "single-sign words (no within-word context)"),
        )
    }
    for score in merged.values():
        score.hits = {k: [] for k in TOP_K}
    pooled: dict[int, list[int]] = {k: [] for k in TOP_K}
    vocab_sizes: list[int] = []
    name = ""

    for fold in folds:
        ranker = ranker_factory()
        name = ranker.name
        strata, flat, vocab = evaluate_fold(ranker, fold, items)
        vocab_sizes.append(len(vocab))
        for key, score in strata.items():
            merged[key].n += score.n
            for k in TOP_K:
                merged[key].hits[k].extend(score.hits[k])
        for k in TOP_K:
            pooled[k].extend(flat[k])

    return Result(
        ranker=name,
        overall=merged["overall"],
        seen=merged["seen"],
        unseen=merged["unseen"],
        single_sign=merged["single"],
        per_item_hits=pooled,
        candidate_set_size=round(statistics.fmean(vocab_sizes)) if vocab_sizes else 0,
    )


def compare(a: Result, b: Result, k: int = 1) -> dict:
    """Paired significance between two rankers on identical, identically-ordered items.

    Only valid when both were run over the same folds in the same order — which
    ``cross_validate`` guarantees, since fold membership is deterministic.
    """
    hits_a, hits_b = a.per_item_hits[k], b.per_item_hits[k]
    if len(hits_a) != len(hits_b):
        raise ValueError("rankers were scored on different item sets")
    mc = mcnemar([bool(x) for x in hits_a], [bool(x) for x in hits_b])
    pb = paired_bootstrap(hits_a, hits_b, seed=0)
    return {
        "k": k,
        "a": a.ranker,
        "b": b.ranker,
        "mcnemar_p": mc.p_value,
        "mcnemar_method": mc.method,
        "discordant": (mc.b, mc.c),
        "mean_difference": pb.mean_difference,
        "ci": (pb.low, pb.high),
    }
