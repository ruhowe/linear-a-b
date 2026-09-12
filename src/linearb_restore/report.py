"""Produce the results tables. Aggregate figures only — safe to commit and to publish.

Writes markdown and JSON side by side: markdown for the HENGE doc and for reading,
JSON so a later run can be diffed against this one without re-reading prose.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict
from pathlib import Path
from typing import Sequence as Seq

from .evaluate import TOP_K, Result, compare, cross_validate
from .extract import corpus_summary, d_family, extract_sequences
from .mask import make_items
from .split import Fold, coverage, document_folds
from . import rankers as R

__all__ = ["run", "markdown_table"]


def markdown_table(results: Seq[Result]) -> str:
    lines = [
        "| Ranker | Stratum | n | top-1 | top-5 | top-20 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for res in results:
        for score in (res.overall, res.seen, res.unseen, res.single_sign):
            if score.n == 0:
                continue
            cells = []
            for k in TOP_K:
                low, high = score.interval(k)
                cells.append(f"{score.accuracy(k):.1%} ({low:.1%}–{high:.1%})")
            lines.append(
                f"| {res.ranker} | {score.label} | {score.n} | " + " | ".join(cells) + " |"
            )
    return "\n".join(lines)


def run(out_dir: Path | str = "results", *, k: int = 5, seed: int = 0) -> dict:
    import aegean

    corpus = aegean.load("damos")
    docs = d_family(corpus)
    sequences = extract_sequences(corpus, docs)
    items = make_items(sequences)
    summary = corpus_summary(sequences)
    folds = document_folds({s.doc_id for s in sequences if s.eligible}, k=k, seed=seed)

    results = [
        cross_validate(factory, folds, items)
        for factory in (R.PriorRanker, R.BigramRanker, R.LexiconRanker, R.BackoffRanker)
    ]
    by_name = {r.ranker: r for r in results}

    comparisons = [
        compare(by_name["bigram"], by_name["prior"], k=1),
        compare(by_name["lexicon"], by_name["bigram"], k=1),
        compare(by_name["backoff"], by_name["lexicon"], k=1),
    ]

    # Sensitivity: the prototype's protocol (no single-sign promotion), 5-fold and
    # across single 80/20 splits, to quantify how unstable a one-split estimate is.
    proto_seqs = extract_sequences(corpus, docs, include_single_sign_words=False)
    proto_items = make_items(proto_seqs)
    proto_docs = sorted({s.doc_id for s in proto_seqs if s.eligible})
    proto_folds = document_folds(proto_docs, k=k, seed=seed)
    proto_cv = cross_validate(R.BigramRanker, proto_folds, proto_items)
    single_split = []
    for s in range(8):
        test = document_folds(proto_docs, k=k, seed=s)[0].test_docs
        fold = Fold(0, frozenset(proto_docs) - test, test, f"80/20 seed {s}")
        r = cross_validate(R.BigramRanker, [fold], proto_items)
        single_split.append({"seed": s, "n": r.overall.n, **{f"top{kk}": r.overall.accuracy(kk) for kk in TOP_K}})

    payload = {
        "corpus": {
            "provenance": str(getattr(corpus, "provenance", "")),
            **{key: val for key, val in zip(
                [r[0] for r in summary.as_rows()], [r[1] for r in summary.as_rows()]
            )},
            "by_subseries": summary.by_subseries,
        },
        "protocol": {
            "unit": "physical line",
            "masking": "exhaustive leave-one-sign-out",
            "split": f"document-grouped {k}-fold, seed {seed}",
            "items": len(items),
            "candidate_set_size": results[0].candidate_set_size,
            "top20_share_of_candidates": results[0].top_k_share(20),
        },
        "metadata_concentration": {
            "scribe": coverage(r.scribe for r in {s.doc_id: s for s in sequences}.values()),
            "findspot": coverage(r.findspot for r in {s.doc_id: s for s in sequences}.values()),
        },
        "results": [
            {
                "ranker": res.ranker,
                "strata": {
                    name: score.row()
                    for name, score in (
                        ("overall", res.overall),
                        ("seen", res.seen),
                        ("unseen", res.unseen),
                        ("single_sign", res.single_sign),
                    )
                    if score.n
                },
            }
            for res in results
        ],
        "comparisons": comparisons,
        "single_split_instability": {
            "protocol": "prototype protocol (single-sign words excluded), single 80/20 split",
            "five_fold_pooled": {f"top{kk}": proto_cv.overall.accuracy(kk) for kk in TOP_K},
            "splits": single_split,
            "top1_range": [
                min(s["top1"] for s in single_split),
                max(s["top1"] for s in single_split),
            ],
        },
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "linearb_restoration.json").write_text(json.dumps(payload, indent=2))
    (out / "linearb_restoration.md").write_text(markdown_table(results) + "\n")
    return payload


if __name__ == "__main__":
    import sys

    data = run(sys.argv[1] if len(sys.argv) > 1 else "results")
    print(json.dumps(data["protocol"], indent=2))
    print(json.dumps(data["single_split_instability"]["top1_range"], indent=2))
