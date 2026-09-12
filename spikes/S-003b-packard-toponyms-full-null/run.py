#!/usr/bin/env python3
"""S-003b: Packard's Knossos toponym test with values permuted at every sign position.

    .venv/bin/python spikes/S-003b-packard-toponyms-full-null/run.py

See BRIEF.md for the question, the corrected null, and why S-003's own null (which fixed
the first two match positions as a corpus fact) was too weak to read. Per spikes/README.md
rule 4, this script imports from ``src/`` and edits nothing there.

**Lexicons.** Reused unchanged from S-003
(``spikes/S-003-packard-toponyms/run.py``, loaded here as a module, not copied): 32 of 33
candidate Knossos toponyms attested as WORD/CERTAIN types in DAMOS, and a 32-entry
personal-name control (the most frequent non-toponym WORD/CERTAIN types on the Knossos
Da-Dv sheep series). Both lists are cached outside the repo at
``~/.cache/linear-a-b/reference/s003-knossos-lexicons.json`` (corpus-derived,
corpus-sources.md Invariants); this script recomputes them from the loaded corpus rather
than trusting that cache.

**The value assignment (Packard's own construction, p. 73-74).** A Linear A sign
inventory is built as: every sign label that occurs in a GORILA (or SigLA) WORD/CERTAIN
word type of three or more signs *and* is also a Linear B sign label, so a value exists
to transfer at all (the two editions' overlaps with Linear B are entirely syllabic
signs, checked directly). Labels are ranked by Linear A token frequency: occurrences of
each label across every WORD/CERTAIN token in that edition, any length, not just the
3+-sign subset used to build the inventory, matching Packard's own practice of ranking
the whole sign inventory by frequency before working with any subset. Ranked labels are
split into contiguous bands of ten in descending frequency (Packard's own grouping); a
four-band split of the same ranked list is also scored as a sensitivity. A *value
assignment* is a bijection from each label to a label within its own band. The real
assignment is identity (the transliteration convention). A null draw is one independent
random permutation per band, all bands drawn together, 200 draws, seeded.

**The match test, read through an assignment.** For a Linear A word and a lexicon word
of the same or greater length, let ``a[i]`` be the assignment's image of the Linear A
word's i-th sign (``None`` if that sign carries no assigned value). "3=": ``a[0]`` and
``a[1]`` equal the lexicon word's first two signs (literal label identity, exactly as
Packard tabulated it) and ``a[2]``'s Greek consonant (``kober.values.consonant_of``)
equals the lexicon word's third sign's own consonant (read off its known Linear B
value directly, never through the assignment: the lexicon side is a real Linear B word).
"4=": ``a[0..2]`` equal the lexicon word's first three signs and either ``a[3]`` equals
its fourth sign outright, or ``a[3]``'s consonant matches it. Distinct (Linear A word,
lexicon word) pairs are counted. Unlike S-003, no position is exempted from the
assignment: under the real (identity) assignment this is exactly Packard's literal
"identical labels" test; under a null draw, every position must be earned by the luck of
that draw's permutation, including the first two.

**Packard's own nine-rotation scheme, reproduced for comparison only.** For k = 1 to 9,
each band of ten (only the groups-of-ten structure; Packard did not report a four-band
version) is cyclically rotated by k positions, so the value at one rank always lands on
a sign k ranks away, no sign keeping its own value (k mod band size = 0 only for a band
smaller than k, an edge case confined to the smallest, lowest-frequency band on each
edition; noted in RESULT.md). The mean count over these nine rotations is reported
alongside the 200-draw permutation null so Packard's own comparison scheme (his 3.0 for
Knossos-name 3-equal) sits next to the properly characterised one.

**Editions.** GORILA (``aegean.load("lineara")``) and SigLA (``aegean.load("sigla")``)
each get their own sign inventory, frequency ranking and bands, since only which words
and signs are attested differs between them; SigLA carries no ``sign_inventory`` of its
own (measured 2026-09-12, unchanged since S-003), which is irrelevant here since this
script never touches either edition's sign_inventory, only its word tokens.
"""

from __future__ import annotations

import importlib.util
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402
from kober.values import consonant_of  # noqa: E402

# Reuse S-003's lexicon construction (toponym + personal-name control) as a module,
# rather than re-deriving it: it is the object under test's answer key and must stay
# byte-identical between the two spikes. Loaded, not executed: S-003's run.py only runs
# its main() under ``if __name__ == "__main__"``.
_S003_PATH = ROOT / "spikes" / "S-003-packard-toponyms" / "run.py"
_spec = importlib.util.spec_from_file_location("s003_run", _S003_PATH)
s003_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s003_run)

N_PERMUTATIONS = 200
SEED = 0
BAND_SIZE = 10
N_SENSITIVITY_BANDS = 4


def sign_token_frequency(corpus) -> Counter:
    """Occurrences of each normalised sign label across every WORD/CERTAIN token,
    any length. This is the whole-corpus sign frequency Packard ranked, not the
    frequency restricted to the 3+-sign subset used to build the value inventory."""
    freq: Counter = Counter()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is TokenKind.WORD and tok.status is ReadingStatus.CERTAIN:
                for s in tok.signs:
                    freq[s003_run.normalize_label(s)] += 1
    return freq


def build_sign_inventory(la_words_3plus: list[tuple[str, ...]], b_labels: set[str],
                          freq: Counter) -> list[str]:
    """Labels usable in a value assignment: occur in a 3+-sign Linear A word type and
    are also a Linear B sign label. Ranked by whole-corpus token frequency, descending,
    ties broken alphabetically for a reproducible ranking."""
    labels_in_words = {s for w in la_words_3plus for s in w}
    eligible = labels_in_words & b_labels
    return sorted(eligible, key=lambda l: (-freq[l], l))


def chunk_fixed(seq: list[str], size: int) -> list[list[str]]:
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def chunk_n(seq: list[str], n: int) -> list[list[str]]:
    """n contiguous, near-equal bands; any remainder goes to the earliest bands."""
    length = len(seq)
    base, rem = divmod(length, n)
    bands = []
    idx = 0
    for i in range(n):
        take = base + (1 if i < rem else 0)
        bands.append(seq[idx:idx + take])
        idx += take
    return bands


def identity_map(ranked_labels: list[str]) -> dict[str, str]:
    return {label: label for label in ranked_labels}


def permuted_map(bands: list[list[str]], rng: random.Random) -> dict[str, str]:
    cmap: dict[str, str] = {}
    for band in bands:
        shuffled = list(band)
        rng.shuffle(shuffled)
        cmap.update(zip(band, shuffled))
    return cmap


def rotated_map(bands: list[list[str]], k: int) -> dict[str, str]:
    """Packard's construction: cyclic rotation by k within each band of ten."""
    cmap: dict[str, str] = {}
    for band in bands:
        m = len(band)
        if m == 0:
            continue
        eff_k = k % m
        rotated = band[eff_k:] + band[:eff_k]
        cmap.update(zip(band, rotated))
    return cmap


def count_matches(la_words: list[tuple[str, ...]], lexicon_words: list[tuple[str, ...]],
                   cmap: dict[str, str]) -> tuple[int, int]:
    """Packard's "3=" and "4=" counts under one value assignment ``cmap``. The lexicon
    side is a real Linear B word: its own consonant is read directly off its label, never
    through ``cmap``. Every position of the Linear A side goes through ``cmap``."""
    c3 = c4 = 0
    lex3 = [w for w in lexicon_words if len(w) >= 3]
    lex4 = [w for w in lexicon_words if len(w) >= 4]
    cons_cache: dict[str, str | None] = {}

    def cons(label: str | None) -> str | None:
        if label is None:
            return None
        if label not in cons_cache:
            cons_cache[label] = consonant_of(label)
        return cons_cache[label]

    for w in la_words:
        wl = len(w)
        a = [cmap.get(s) for s in w[:4]]
        if wl >= 3:
            c2 = cons(a[2])
            if c2 is not None:
                for t in lex3:
                    if a[0] == t[0] and a[1] == t[1] and cons(t[2]) == c2:
                        c3 += 1
        if wl >= 4:
            c3v = cons(a[3])
            for t in lex4:
                if a[0] == t[0] and a[1] == t[1] and a[2] == t[2]:
                    if a[3] == t[3]:
                        c4 += 1
                    elif c3v is not None and cons(t[3]) == c3v:
                        c4 += 1
    return c3, c4


def percentile(values: list[float], pct: int) -> float:
    return statistics.quantiles(values, n=100, method="inclusive")[pct - 1]


def real_percentile_rank(real: int, nulls: list[int]) -> float:
    n = len(nulls)
    less = sum(1 for x in nulls if x < real)
    equal = sum(1 for x in nulls if x == real)
    return 100.0 * (less + 0.5 * equal) / n


def score_band_structure(structure_name: str, bands: list[list[str]], ranked_labels: list[str],
                          la_words: list[tuple[str, ...]], lexicons: dict[str, list[tuple[str, ...]]],
                          seed: int, n_permutations: int,
                          packard_rotation: bool) -> dict:
    id_map = identity_map(ranked_labels)
    reals = {name: count_matches(la_words, words, id_map) for name, words in lexicons.items()}

    rng = random.Random(seed)
    nulls: dict[str, dict[str, list[int]]] = {
        name: {"3=": [], "4=": []} for name in lexicons
    }
    for _ in range(n_permutations):
        pmap = permuted_map(bands, rng)
        for name, words in lexicons.items():
            c3, c4 = count_matches(la_words, words, pmap)
            nulls[name]["3="].append(c3)
            nulls[name]["4="].append(c4)

    rotation_means: dict[str, dict[str, float]] = {}
    if packard_rotation:
        rot_counts = {name: {"3=": [], "4=": []} for name in lexicons}
        for k in range(1, 10):
            rmap = rotated_map(bands, k)
            for name, words in lexicons.items():
                c3, c4 = count_matches(la_words, words, rmap)
                rot_counts[name]["3="].append(c3)
                rot_counts[name]["4="].append(c4)
        for name in lexicons:
            rotation_means[name] = {
                cls: statistics.fmean(rot_counts[name][cls]) for cls in ("3=", "4=")
            }

    rows = []
    for name in lexicons:
        real3, real4 = reals[name]
        for match_class, real in (("3=", real3), ("4=", real4)):
            null_list = nulls[name][match_class]
            row = {
                "lexicon": name,
                "match_class": match_class,
                "real": real,
                "null_mean": statistics.fmean(null_list),
                "null_sd": statistics.pstdev(null_list),
                "null_p95": percentile(null_list, 95),
                "null_p99": percentile(null_list, 99),
                "real_percentile": real_percentile_rank(real, null_list),
                "n_permutations": n_permutations,
            }
            if packard_rotation:
                row["packard_nine_rotation_mean"] = rotation_means[name][match_class]
            rows.append(row)

    return {
        "structure": structure_name,
        "band_sizes": [len(b) for b in bands],
        "rows": rows,
    }


def score_edition(edition_name: str, la_words: list[tuple[str, ...]], b_labels: set[str],
                   freq: Counter, lexicons: dict[str, list[tuple[str, ...]]], seed: int,
                   n_permutations: int) -> dict:
    ranked = build_sign_inventory(la_words, b_labels, freq)

    bands_10 = chunk_fixed(ranked, BAND_SIZE)
    bands_4 = chunk_n(ranked, N_SENSITIVITY_BANDS)

    groups_of_10 = score_band_structure(
        "groups_of_10", bands_10, ranked, la_words, lexicons, seed, n_permutations,
        packard_rotation=True,
    )
    four_bands = score_band_structure(
        "four_bands", bands_4, ranked, la_words, lexicons, seed, n_permutations,
        packard_rotation=False,
    )

    return {
        "edition": edition_name,
        "n_word_types_3plus": len(la_words),
        "sign_inventory_size": len(ranked),
        "band_structures": {"groups_of_10": groups_of_10, "four_bands": four_bands},
    }


def main() -> dict:
    damos = aegean.load("damos")
    gorila = aegean.load("lineara")
    sigla = aegean.load("sigla")

    word_types = s003_run.damos_word_types(damos)
    attested, dropped = s003_run.build_toponym_lexicon(word_types)
    toponym_words = [signs for _surface, signs, _sources in attested]

    control_pairs, n_d_docs = s003_run.build_personal_name_control(
        damos, toponym_words, len(toponym_words)
    )
    control_words = [w for w, _count in control_pairs]

    lexicons = {"toponyms": toponym_words, "personal_names_control": control_words}
    b_labels = {s.label for s in damos.sign_inventory.signs}

    editions = []
    for name, corpus in (("gorila", gorila), ("sigla", sigla)):
        freq = sign_token_frequency(corpus)
        la_words = s003_run.linear_a_word_types(corpus, min_len=3)
        editions.append(
            score_edition(name, la_words, b_labels, freq, lexicons, SEED, N_PERMUTATIONS)
        )

    payload = {
        "question": "Does Packard's Knossos toponym match count survive a 200-draw "
                     "value-permutation null with every sign position subject to the "
                     "null, on GORILA and on SigLA?",
        "protocol": {
            "n_permutations": N_PERMUTATIONS,
            "seed": SEED,
            "null": "one random permutation per frequency band, all bands drawn "
                     "together, every word position read through the resulting "
                     "assignment (S-003b, correcting S-003's fixed-position null)",
            "band_structures": "groups of ten (Packard's own grouping), and four "
                                "bands as a sensitivity",
            "sign_ranking": "whole-corpus token frequency of each label across every "
                             "WORD/CERTAIN token of that edition, any length",
            "match_definition": (
                "3= : the assignment's image of the Linear A word's first two signs "
                "equals the lexicon word's first two signs, and the third sign's image "
                "shares a Greek consonant (kober.values.consonant_of) with the lexicon "
                "word's third sign. 4= : the first three images equal the lexicon "
                "word's first three signs, and the fourth image either equals its "
                "fourth sign or shares a consonant with it. The lexicon side always "
                "reads its own known Linear B value directly, never through the "
                "assignment."
            ),
            "toponym_lexicon_size": len(toponym_words),
            "toponym_candidates": len(s003_run.KNOSSOS_TOPONYM_CANDIDATES),
            "toponym_dropped": len(dropped),
            "personal_name_control_size": len(control_words),
        },
        "packard_1974_table14": {
            "note": "Table 14 p.98, Linear B values vs. mean of his 9 random "
                    "decipherments; reproduced here for comparison, not recomputed",
            "knossos_name_3_equal": {"linear_b_values": 13, "random_mean": 3.0},
            "knossos_name_4_equal": {"linear_b_values": 2, "random_mean": 0.0},
        },
        "editions": editions,
    }

    out_dir = Path(__file__).resolve().parent
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    data = main()
    print(json.dumps(data["protocol"], indent=2))
    for ed in data["editions"]:
        print(f"\n== {ed['edition']}  n_word_types(3+)={ed['n_word_types_3plus']} "
              f"sign_inventory={ed['sign_inventory_size']}")
        for structure_name, structure in ed["band_structures"].items():
            print(f"  -- {structure_name}  band_sizes={structure['band_sizes']}")
            for r in structure["rows"]:
                extra = ""
                if "packard_nine_rotation_mean" in r:
                    extra = f" packard9={r['packard_nine_rotation_mean']:>5.2f}"
                print(
                    f"     {r['lexicon']:<24} {r['match_class']:<3} real={r['real']:>3} "
                    f"null_mean={r['null_mean']:>6.2f} sd={r['null_sd']:>5.2f} "
                    f"p95={r['null_p95']:>5.1f} p99={r['null_p99']:>5.1f} "
                    f"real_pct={r['real_percentile']:>5.1f}{extra}"
                )
