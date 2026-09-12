"""Score every runnable hypothesis against its own null, and weight by scenario.

    .venv/bin/python -c "import sys;sys.path.insert(0,'src');from hypotheses.run import main;main()"

Each hypothesis gets the identical Linear A word list, the identical permutation
procedure and the identical hit criterion. What differs is its lexicon and its
sign-to-phoneme map, which is the hypothesis. Scoring each against its own permuted null
rather than against a shared one is deliberate: lexicon density varies by more than an
order of magnitude between languages, so raw match rates are not comparable, while
distance from one's own null is.
"""

from __future__ import annotations

import itertools
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from semitic_null.lexicon import Lexicon  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402

from .harness import (  # noqa: E402
    HypothesisResult,
    format_table,
    load_registry,
    load_scenarios,
    posterior_ordering,
)
from .lexicons import load_for  # noqa: E402
from .phonologies import build_map  # noqa: E402

__all__ = ["main", "score", "stratified_permute"]

CAP = 20000  # refuse a word whose candidate expansion exceeds this


def skeletons(signs: Sequence[str], cmap: ConsonantMap) -> set[str] | None:
    """Every phoneme skeleton this sign sequence could write under one hypothesis.

    Generic across hypotheses, unlike the Semitic-specific version in
    ``semitic_null.experiment``. Two rules carry the differences between languages:

    A sign mapping to an **empty** phoneme set contributes nothing. That is how Greek
    treats a vowel sign, and it is a real prediction rather than a failure.

    A sign that *may* be silent contributes an empty option alongside its phonemes. That
    is how Semitic treats a vowel sign, which may write a laryngeal or nothing at all,
    and the tested reading relies on it.
    """
    options: list[tuple[str, ...]] = []
    for sign in signs:
        allowed = cmap.get(sign)
        if allowed is None:
            return None
        if not allowed:
            options.append(("",))
            continue
        opts = tuple(sorted(allowed))
        # A broad laryngeal set is optional; a narrow consonant set is obligatory.
        if len(opts) >= 4 and "ʾ" in allowed:
            opts = opts + ("",)
        options.append(opts)

    total = 1
    for opt in options:
        total *= len(opt)
        if total > CAP:
            return None
    return {"".join(combo) for combo in itertools.product(*options)}


def score(
    words: Sequence[Sequence[str]],
    cmap: ConsonantMap,
    lex: Lexicon,
    *,
    min_len: int = 2,
    max_len: int = 4,
) -> tuple[float, float]:
    """``(hit rate, mean candidates per word)``. A hit is any candidate being attested."""
    hits: list[int] = []
    breadth: list[int] = []
    for signs in words:
        expanded = skeletons(signs, cmap)
        if expanded is None:
            continue
        usable = {s for s in expanded if min_len <= len(s) <= max_len}
        if not usable:
            continue
        breadth.append(len(usable))
        hits.append(int(any(lex.attested(s) for s in usable)))
    if not hits:
        return 0.0, 0.0
    return statistics.fmean(hits), statistics.fmean(breadth)


def stratified_permute(cmap: ConsonantMap, rng: random.Random) -> ConsonantMap:
    """Permute phoneme sets only among signs holding the same number of options.

    Holds each sign's breadth fixed so the null reaches the same number of candidate
    words as the real map. Without this the test rewards combinatorial reach and returns
    a false positive, documented in ``semitic-null-test.md``.

    **Not sufficient on its own.** It does not preserve which signs are *common*, so a
    frequent sign can trade its phoneme with a rare one. Use
    :func:`frequency_matched_permute` when comparing across hypotheses.
    """
    by_size: dict[int, list[str]] = {}
    for label, options in cmap.mapping.items():
        by_size.setdefault(len(options), []).append(label)
    out: dict[str, frozenset[str]] = {}
    for _, labels in by_size.items():
        labels = sorted(labels)
        values = [cmap.mapping[k] for k in labels]
        rng.shuffle(values)
        out.update(dict(zip(labels, values)))
    return ConsonantMap(out)


def frequency_matched_permute(
    cmap: ConsonantMap,
    rng: random.Random,
    sign_freq: dict[str, int],
    *,
    n_bands: int = 4,
) -> ConsonantMap:
    """Permute within both a breadth class and a corpus-frequency band.

    The third-generation null, and the first that survives a control.

    A breadth-matched permutation still lets a *frequent* sign swap phonemes with a
    *rare* one. That matters more than it sounds, because Linear A's conventional values
    are Linear B values, and Linear B values are Greek. The phoneme frequencies implied
    by the signs therefore align with Greek phoneme frequencies by construction
    (measured correlation +0.69, against +0.15 for Hebrew). Any permutation that breaks
    the frequency alignment hands the real map an advantage that has nothing to do with
    whether the hypothesis is true.

    Banding by corpus frequency preserves that alignment, so what remains under test is
    only which particular phoneme each sign writes. This is Packard's 1974 design read
    strictly: he reassigned values *within frequency bands* for exactly this reason, and
    the detail was easy to miss.
    """
    ranked = sorted(cmap.mapping, key=lambda s: (-sign_freq.get(s, 0), s))
    band_of = {sign: (i * n_bands) // max(1, len(ranked)) for i, sign in enumerate(ranked)}

    groups: dict[tuple[int, int], list[str]] = {}
    for label, options in cmap.mapping.items():
        groups.setdefault((len(options), band_of.get(label, 0)), []).append(label)

    out: dict[str, frozenset[str]] = {}
    for _, labels in groups.items():
        labels = sorted(labels)
        values = [cmap.mapping[k] for k in labels]
        rng.shuffle(values)
        out.update(dict(zip(labels, values)))
    return ConsonantMap(out)


def linear_a_words(corpus, cmap: ConsonantMap) -> list[tuple[str, ...]]:
    """Distinct multi-sign securely-read word types the map covers."""
    seen = set()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if (
                tok.kind is TokenKind.WORD
                and tok.status is ReadingStatus.CERTAIN
                and len(tok.signs) >= 2
                and cmap.covered(tok.signs)
            ):
                seen.add(tuple(tok.signs))
    return sorted(seen)


def main(out_dir: str | Path = "results", *, n_permutations: int = 999, seed: int = 0) -> dict:
    import aegean

    corpus = aegean.load("lineara")
    inventory = corpus.sign_inventory
    registry = load_registry()
    scenarios = load_scenarios()

    phonology_for = {
        "semitic_hebrew": "semitic_consonantal",
        "greek_mycenaean": "greek_syllabic",
    }

    results: list[HypothesisResult] = []
    blocked: list[dict] = []
    word_counts: dict[str, int] = {}

    for hyp in registry:
        if not hyp.runnable or hyp.key not in phonology_for:
            blocked.append(
                {"key": hyp.key, "label": hyp.label, "status": hyp.status,
                 "blocker": hyp.blocker or "no lexicon loader wired"}
            )
            continue

        lex = load_for(hyp.lexicon_loader)
        cmap = build_map(inventory, phonology_for[hyp.key])
        words = linear_a_words(corpus, cmap)
        word_counts[hyp.key] = len(words)

        real_rate, breadth = score(words, cmap, lex)
        sign_freq = Counter(s for w in words for s in w)

        by_null: dict[str, dict] = {}
        for null_name, permute in (
            ("breadth_matched", lambda m, r: stratified_permute(m, r)),
            ("frequency_matched", lambda m, r: frequency_matched_permute(m, r, sign_freq)),
        ):
            rng = random.Random(seed)
            nulls = [score(words, permute(cmap, rng), lex)[0] for _ in range(n_permutations)]
            mean = statistics.fmean(nulls)
            sd = statistics.pstdev(nulls)
            at_least = sum(1 for r in nulls if r >= real_rate)
            by_null[null_name] = {
                "null_mean": mean,
                "null_sd": sd,
                "excess": real_rate - mean,
                "z": (real_rate - mean) / sd if sd else 0.0,
                "p_value": (at_least + 1) / (n_permutations + 1),
            }

        strongest = by_null["frequency_matched"]
        result = HypothesisResult(
            key=hyp.key,
            label=hyp.label,
            n_words=len(words),
            real_rate=real_rate,
            null_mean=strongest["null_mean"],
            null_sd=strongest["null_sd"],
            p_value=strongest["p_value"],
            mean_candidates=breadth,
            note=hyp.notes,
        )
        result.by_null = by_null  # type: ignore[attr-defined]
        results.append(result)

    payload = {
        "question": "Does any candidate language match Linear A better than a permuted control?",
        "protocol": {
            "null": "frequency_matched is the headline; breadth_matched retained for comparison",
            "calibration": "Greek is a known-false control. Its score under the strongest null is the artifact benchmark any hypothesis must beat.",
            "permutations": n_permutations,
            "seed": seed,
            "hit": "any candidate skeleton attested in that hypothesis's lexicon",
            "note": "Each hypothesis is scored against its own null; raw rates are not comparable across lexicons.",
        },
        "results": [r.row() | {"label": r.label, "mean_candidates": r.mean_candidates,
                               "by_null": getattr(r, "by_null", {})} for r in results],
        "blocked": blocked,
        "scenarios": {
            sc.key: {
                "label": sc.label,
                "source": sc.source,
                "ordering": [
                    {"hypothesis": k, "prior": p, "posterior": s}
                    for k, p, s in posterior_ordering(results, sc)
                ],
            }
            for sc in scenarios
        },
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hypotheses.json").write_text(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":  # pragma: no cover
    data = main()
    print(format_table([
        HypothesisResult(
            key=r["hypothesis"], label=r["label"], n_words=r["n"],
            real_rate=r["real"], null_mean=r["null"], null_sd=0.0, p_value=r["p"],
        ) for r in data["results"]
    ]))
