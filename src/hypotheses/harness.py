"""Run one test across every runnable hypothesis, and weight the outcome by scenario.

The unit of work is ``(test, hypothesis)``. A **test** is a callable that scores a word
list under a sign→phoneme-set map and returns a hit rate. A **hypothesis** supplies the
lexicon and the map. The harness takes the cross-product, scores each hypothesis against
its *own* permuted null, and reports them side by side.

Three properties this buys, which a single-hypothesis script cannot:

1. **Comparability.** "Semitic scores 72%" is uninterpretable alone. "Semitic 72% vs its
   null 70%, Greek 41% vs its null 40%" is a result. Raghavendra 2026 requires preferring
   one language *over matched alternatives*; this is that requirement, implemented.
2. **Fairness.** Every claim goes through the identical pipeline, including the
   mainstream position and a known-false control. No claimant is singled out.
3. **Extensibility.** A new hypothesis is a registry record plus a lexicon loader.
   Nothing here changes.

Each hypothesis is scored against its own null rather than a shared one, because
lexicon size and phonological permissiveness differ enormously between them. Comparing
raw hit rates across hypotheses would measure lexicon size; comparing each to its own
null measures fit.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol, Sequence

__all__ = [
    "Hypothesis",
    "Scenario",
    "HypothesisResult",
    "load_registry",
    "load_scenarios",
    "run_across_hypotheses",
    "posterior_ordering",
]

_HERE = Path(__file__).resolve().parent


class PhonemeMap(Protocol):
    """Whatever a hypothesis uses to map sign labels to candidate phoneme sets."""

    mapping: dict[str, frozenset[str]]

    def get(self, sign: str) -> frozenset[str] | None: ...
    def covered(self, signs) -> bool: ...


@dataclass(frozen=True, slots=True)
class Hypothesis:
    key: str
    label: str
    family: str
    status: str
    standing: str
    proponents: tuple[str, ...] = ()
    notes: str = ""
    lexicon_loader: str | None = None
    blocker: str | None = None

    @property
    def runnable(self) -> bool:
        return self.status == "runnable" or (
            self.status == "control" and self.lexicon_loader not in (None, "none")
        )


@dataclass(frozen=True, slots=True)
class Scenario:
    key: str
    label: str
    weights: dict[str, float]
    source: str = ""

    def normalised(self) -> dict[str, float]:
        total = sum(self.weights.values()) or 1.0
        return {k: v / total for k, v in self.weights.items()}


@dataclass
class HypothesisResult:
    """One hypothesis scored against its own permuted null."""

    key: str
    label: str
    n_words: int
    real_rate: float
    null_mean: float
    null_sd: float
    p_value: float
    mean_candidates: float = 0.0
    note: str = ""

    @property
    def z(self) -> float:
        return (self.real_rate - self.null_mean) / self.null_sd if self.null_sd else 0.0

    @property
    def excess(self) -> float:
        """How far above its own null, in points. The comparable quantity."""
        return self.real_rate - self.null_mean

    def row(self) -> dict:
        return {
            "hypothesis": self.key,
            "n": self.n_words,
            "real": self.real_rate,
            "null": self.null_mean,
            "excess": self.excess,
            "z": self.z,
            "p": self.p_value,
        }


def _read_yaml(path: Path) -> dict:
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit("PyYAML not installed: .venv/bin/pip install pyyaml") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_registry(path: Path | None = None) -> list[Hypothesis]:
    data = _read_yaml(path or _HERE / "registry.yaml")
    out = []
    for rec in data.get("hypotheses", []):
        lex = rec.get("lexicon") or {}
        out.append(
            Hypothesis(
                key=rec["key"],
                label=rec.get("label", rec["key"]),
                family=rec.get("family", ""),
                status=rec.get("status", "blocked"),
                standing=rec.get("standing", ""),
                proponents=tuple(rec.get("proponents", ())),
                notes=" ".join(str(rec.get("notes", "")).split()),
                lexicon_loader=lex.get("loader"),
                blocker=" ".join(str(lex.get("blocker", "")).split()) or None,
            )
        )
    return out


def load_scenarios(path: Path | None = None) -> list[Scenario]:
    data = _read_yaml(path or _HERE / "scenarios.yaml")
    return [
        Scenario(
            key=rec["key"],
            label=rec.get("label", rec["key"]),
            weights=dict(rec.get("weights", {})),
            source=" ".join(str(rec.get("source", "")).split()),
        )
        for rec in data.get("scenarios", [])
    ]


def run_across_hypotheses(
    words: Sequence[Sequence[str]],
    builders: dict[str, Callable[[], tuple[PhonemeMap, object]]],
    scorer: Callable[[Sequence[Sequence[str]], PhonemeMap, object], tuple[float, float]],
    permuter: Callable[[PhonemeMap, random.Random], PhonemeMap],
    *,
    registry: Sequence[Hypothesis] | None = None,
    n_permutations: int = 999,
    seed: int = 0,
) -> list[HypothesisResult]:
    """Score every hypothesis with a builder against its own null.

    ``builders`` maps a hypothesis key to a zero-arg callable returning
    ``(phoneme_map, lexicon)``. ``scorer`` returns ``(hit_rate, mean_candidates)``.
    A hypothesis in the registry with no builder is skipped and reported as blocked by
    the caller — silence about an untestable hypothesis would misrepresent the survey.
    """
    registry = list(registry or load_registry())
    results: list[HypothesisResult] = []

    for hyp in registry:
        build = builders.get(hyp.key)
        if build is None:
            continue
        pmap, lex = build()
        real_rate, breadth = scorer(words, pmap, lex)
        rng = random.Random(seed)
        null_rates = [
            scorer(words, permuter(pmap, rng), lex)[0] for _ in range(n_permutations)
        ]
        mean = statistics.fmean(null_rates)
        sd = statistics.pstdev(null_rates)
        at_least = sum(1 for r in null_rates if r >= real_rate)
        results.append(
            HypothesisResult(
                key=hyp.key,
                label=hyp.label,
                n_words=len(words),
                real_rate=real_rate,
                null_mean=mean,
                null_sd=sd,
                p_value=(at_least + 1) / (n_permutations + 1),
                mean_candidates=breadth,
                note=hyp.notes,
            )
        )
    return results


def posterior_ordering(
    results: Sequence[HypothesisResult], scenario: Scenario, *, floor: float = 1e-6
) -> list[tuple[str, float, float]]:
    """Crude prior × evidence ordering under one scenario.

    Evidence is taken as ``1 - p``, a blunt monotone stand-in for a likelihood ratio.
    **This is a sensitivity device, not a calibrated posterior**, and must be reported as
    such. Its purpose is to show whether the evidence changes the ordering at all. When
    every hypothesis returns a null result, the posterior simply reproduces the prior —
    which is the honest outcome and should be stated in exactly those words.

    Returns ``(key, prior, score)`` sorted by score.
    """
    priors = scenario.normalised()
    rows = []
    for res in results:
        prior = priors.get(res.key, floor)
        evidence = max(1.0 - res.p_value, floor)
        rows.append((res.key, prior, prior * evidence))
    total = sum(score for _, _, score in rows) or 1.0
    rows = [(k, p, s / total) for k, p, s in rows]
    return sorted(rows, key=lambda r: -r[2])


def format_table(results: Sequence[HypothesisResult]) -> str:
    lines = [
        f"{'hypothesis':<20} {'n':>5} {'real':>7} {'null':>7} {'excess':>8} {'z':>6} {'p':>7}",
        "-" * 64,
    ]
    for r in sorted(results, key=lambda x: -x.excess):
        lines.append(
            f"{r.key:<20} {r.n_words:>5} {r.real_rate:>6.1%} {r.null_mean:>6.1%} "
            f"{r.excess:>+7.1%} {r.z:>+6.2f} {r.p_value:>7.3f}"
        )
    return "\n".join(lines)
