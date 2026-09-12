"""Grouped train/test splits. Nothing here may let one tablet reach both sides.

``corpus-sources.md`` states the binding invariant: *"Any train/test split must be
grouped by document, and probably by scribal hand and findspot. Consequence of a random
token-level split: leakage across joins of the same tablet and a meaningless accuracy
figure."* pyaegean supplies no helper for this — ``aegean/greek/heldout.py`` is
Greek-treebank-specific — so it is built here on document ids.

**Why document-grouped k-fold is the headline and hand-grouping is not.** Metadata on
the D family is extremely concentrated (measured, and re-asserted by the tests):

============  ==========  ===============================================
Field         Coverage    Concentration
============  ==========  ===============================================
``scribe``    943/1,016   hand 117 alone writes 684 (67%)
``findspot``  470/1,016   ``KN, J1`` alone is 397 (85% of those filled)
============  ==========  ===============================================

Holding out hand 117 therefore removes two thirds of the corpus, and holding out
everything else leaves a test set that is two thirds one scribe. Neither is a usable
headline. Both are reported as sensitivity analyses with those figures printed
alongside, so a reader can see why they are secondary rather than being told.

**Joins are already handled.** DĀMOS gives a rejoined tablet a single document id
(``KN Da 1079 + 7192 (117)``), so grouping by document id cannot split a join.
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence as Seq

__all__ = ["Fold", "document_folds", "leave_one_hand_out", "findspot_split", "coverage"]


@dataclass(frozen=True, slots=True)
class Fold:
    """One train/test division, addressed by document id."""

    index: int
    train_docs: frozenset[str]
    test_docs: frozenset[str]
    label: str = ""

    def __post_init__(self) -> None:
        overlap = self.train_docs & self.test_docs
        if overlap:
            raise ValueError(f"fold {self.index} leaks {len(overlap)} document(s)")

    def split(self, items: Iterable):
        """Partition any objects carrying ``doc_id`` into (train, test)."""
        train, test = [], []
        for item in items:
            if item.doc_id in self.test_docs:
                test.append(item)
            elif item.doc_id in self.train_docs:
                train.append(item)
        return train, test


def _stable_key(doc_id: str, seed: int) -> str:
    """Deterministic, order-independent hash so folds reproduce across runs and machines.

    ``hash()`` is salted per process in Python, so it must not be used here.
    """
    return hashlib.sha256(f"{seed}:{doc_id}".encode()).hexdigest()


def document_folds(doc_ids: Iterable[str], *, k: int = 5, seed: int = 0) -> list[Fold]:
    """Document-grouped k-fold. Every document appears in exactly one test fold.

    k=5 rather than a single held-out split because ~3,000 items spread over ~1,000
    documents is too little for one fold's accuracy to be stable.
    """
    unique = sorted(set(doc_ids))
    if k < 2:
        raise ValueError("k must be at least 2")
    if len(unique) < k:
        raise ValueError(f"{len(unique)} documents cannot make {k} folds")

    ordered = sorted(unique, key=lambda d: _stable_key(d, seed))
    buckets: list[list[str]] = [[] for _ in range(k)]
    for i, doc in enumerate(ordered):
        buckets[i % k].append(doc)

    folds = []
    for i, test in enumerate(buckets):
        test_set = frozenset(test)
        folds.append(
            Fold(
                index=i,
                train_docs=frozenset(unique) - test_set,
                test_docs=test_set,
                label=f"document-grouped {k}-fold, fold {i + 1}/{k}, seed {seed}",
            )
        )
    return folds


def leave_one_hand_out(
    doc_scribes: dict[str, str | None], *, min_docs: int = 10, exclude: Seq[str] = ("117",)
) -> list[Fold]:
    """Sensitivity only: hold out one scribal hand at a time.

    ``exclude`` drops hands too large to hold out — by default hand 117, which writes
    67% of the D family, so holding it out would train on a third of the corpus and
    test on two thirds. Documents with no recorded hand always train.
    """
    normalised = {
        doc: (hand.rstrip("?").strip() if hand else None)
        for doc, hand in doc_scribes.items()
    }
    counts = Counter(h for h in normalised.values() if h)
    folds = []
    for i, (hand, n) in enumerate(sorted(counts.items(), key=lambda kv: -kv[1])):
        if hand in exclude or n < min_docs:
            continue
        test = frozenset(d for d, h in normalised.items() if h == hand)
        folds.append(
            Fold(
                index=i,
                train_docs=frozenset(normalised) - test,
                test_docs=test,
                label=f"leave-one-hand-out: hand {hand} ({n} documents)",
            )
        )
    return folds


def findspot_split(doc_findspots: dict[str, str | None], *, holdout: str) -> Fold:
    """Sensitivity only: hold out one findspot. Documents with none always train."""
    test = frozenset(d for d, f in doc_findspots.items() if f == holdout)
    if not test:
        raise ValueError(f"no documents at findspot {holdout!r}")
    return Fold(
        index=0,
        train_docs=frozenset(doc_findspots) - test,
        test_docs=test,
        label=f"findspot holdout: {holdout} ({len(test)} documents)",
    )


def coverage(values: Iterable[str | None]) -> dict[str, object]:
    """Coverage and concentration of a metadata field — the numbers that decide viability."""
    seq = list(values)
    filled = [v for v in seq if v]
    counts = Counter(filled)
    top, top_n = (counts.most_common(1)[0] if counts else (None, 0))
    return {
        "total": len(seq),
        "filled": len(filled),
        "distinct": len(counts),
        "top_value": top,
        "top_count": top_n,
        "top_share_of_filled": (top_n / len(filled)) if filled else 0.0,
        "top_share_of_total": (top_n / len(seq)) if seq else 0.0,
    }


def group_documents(items: Iterable) -> dict[str, list]:
    """Bucket items carrying ``doc_id`` by document."""
    grouped: dict[str, list] = defaultdict(list)
    for item in items:
        grouped[item.doc_id].append(item)
    return dict(grouped)
