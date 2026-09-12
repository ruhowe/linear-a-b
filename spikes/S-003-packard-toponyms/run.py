#!/usr/bin/env python3
"""S-003: Packard's Knossos toponym test, modernised, with a 200-draw frequency-banded null.

    .venv/bin/python spikes/S-003-packard-toponyms/run.py

See BRIEF.md for the question, the two readings, and why this sits outside the main
line. Per spikes/README.md rule 4, this script imports from ``src/`` and edits nothing
there.

**The lexicons.** Two Linear B word lists of the same size, both drawn from Knossos
tablets: a toponym lexicon (the well-known Knossos place-name set quoted in Ventris and
Chadwick 1973, cross-checked against Packard 1974's own Table 11, p.92, "Linear B Words
in Linear A") and a personal-name control (the most frequent non-toponym WORD types on
the Da-Dv sheep series, where the first word of a line is normally a shepherd's name).
Both lists are verified against ``aegean.load("damos")`` word types before use; an
unattested candidate is dropped and counted. Because the actual sign-tuples are corpus
derivatives, the lists themselves are written only to
``~/.cache/linear-a-b/reference/s003-knossos-lexicons.json``, never into this repo
(corpus-sources.md Invariants). This script recomputes both lexicons from the loaded
corpus every run rather than trusting that cache file, so a clean clone reproduces the
same lists deterministically.

**The match test.** Packard's own definition (Table 14, p.98): a "3=" match is two
Linear A/B sign-groups whose first two signs are identical labels and whose third sign
shares a consonant; a "4=" match is four signs identical, or three identical plus a
shared consonant on the fourth. "Identical labels" is a fixed, corpus-given fact about
which sign shapes the two scripts share under the transliteration convention: it does
not change between the real assignment and a null draw. What *does* change is which
Greek consonant each Linear A sign is taken to write, which only enters the test at the
one differing position (the third sign for "3=", the fourth for "4=" in its non-exact
form) via ``hypotheses.phonologies.build_map`` / ``SERIES_TO_GREEK``. A Linear B sign's
consonant is always read off its own known value; only the Linear A side is subject to
the null. Digit-suffixed signs (``RA2``) and undeciphered signs (``*301``) carry no
phonetic value in the loaded inventory and so can never satisfy the "shares a consonant"
clause on either side, matching how ``build_map`` already excludes them elsewhere in
this repo.

**The null.** ``hypotheses.run.frequency_matched_permute``, the null F-004 found
necessary: sign values are rotated within both a breadth class and a corpus-frequency
band (4 bands), so a common Linear A sign cannot trade its consonant options with a rare
one. 200 draws, seeded, against Packard's nine.

**Editions.** GORILA (``aegean.load("lineara")``) and SigLA (``aegean.load("sigla")``)
are scored separately, per BRIEF.md. SigLA's corpus carries no ``sign_inventory``
(measured 2026-09-12), so the same Greek consonant map, built from GORILA's inventory, is
applied to both editions' word lists, since the sign-to-value convention is
edition-independent. Only which words are attested differs. Each edition gets its own sign-frequency profile
for the null, computed from that edition's own 3+-sign CERTAIN WORD types.
"""

from __future__ import annotations

import json
import random
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from hypotheses.phonologies import SERIES_TO_GREEK, build_map  # noqa: E402
from hypotheses.run import frequency_matched_permute  # noqa: E402
from linearb_restore.normalise import normalise_text  # noqa: E402
from semitic_null.phonology import consonant_series  # noqa: E402

N_PERMUTATIONS = 200
SEED = 0
REFERENCE_DIR = Path.home() / ".cache" / "linear-a-b" / "reference"
REFERENCE_FILE = REFERENCE_DIR / "s003-knossos-lexicons.json"

# Candidate Knossos toponyms: the well-known set from Ventris and Chadwick 1973
# (*Documents in Mycenaean Greek*, 2nd ed.; place-names discussed pp. 139-150 and
# 183-194, indexed under "place-names" p.649), cross-checked against Packard 1974
# Table 11 p.92 ("Linear B Words in Linear A"), which tags pa-i-to, ku-do-ni-ja and
# su-ki-ri-ta explicitly "(place)". a-pu-do-si is a transaction term ("delivery"), not
# a toponym, and is excluded from the candidate list.
KNOSSOS_TOPONYM_CANDIDATES = [
    "ko-no-so", "a-mi-ni-so", "pa-i-to", "tu-ri-so", "ku-ta-to", "ru-ki-to",
    "se-to-i-ja", "da-*22-to", "qa-ra", "su-ri-mo", "ra-su-to", "ti-ri-to",
    "e-ko-so", "da-wo", "u-ta-no", "ku-do-ni-ja", "a-pa-ta-wa", "wa-to",
    "su-ki-ri-ta", "ri-jo-no", "di-ka-ta", "e-ra", "ra-to", "ra-ja", "tu-ni-ja",
    "pa-na-so", "qa-mo", "*56-ko-we", "si-ja-du-we", "ku-ta-i-to", "da-ta-ra-mo",
    "do-ti-ja", "pu-na-so",
]
PACKARD_TABLE11_PLACE_TAGGED = {"pa-i-to", "ku-do-ni-ja", "su-ki-ri-ta"}

# Packard 1974 Table 11 p.92 also tags da-mi-ni-jo "(place)", in a table whose column
# layout the PDF text extraction scrambles. It is not in the candidate list above (not
# part of the well-known V&C set used here) but it does surface as a high-frequency
# D-series word type, so it is excluded by name from the personal-name control rather
# than left ambiguous.
MANUAL_CONTROL_EXCLUDE = {("DA", "MI", "NI", "JO")}

D_SERIES_RE = re.compile(r"\bD[a-v]\s*\d")


def normalize_label(label: str) -> str:
    """Canonical sign-label form: strip Leiden marks, fold subscript to ASCII digit,
    upper-case. GORILA/SigLA tokens carry subscript digits (``RA₂``); DAMOS and its own
    sign inventory use ASCII digits (``ra2``/``RA2``); both editions otherwise agree.
    Reuses ``linearb_restore.normalise.normalise_text`` rather than re-deriving the
    subscript table.
    """
    text, _had_underdot, _had_span = normalise_text(label)
    return text.upper()


def is_clean_sign(sign: str) -> bool:
    """Whether a sign label carries no bracket, query mark, underdot or span-bracket
    damage mark, the same checks ``scripts/controlled_comparison.py`` applies before
    trusting a nominally-CERTAIN token (A-004)."""
    if any(ch in sign for ch in "[]?"):
        return False
    _text, had_underdot, had_span = normalise_text(sign)
    return not had_underdot and not had_span


def damos_word_types(corpus) -> set[tuple[str, ...]]:
    """Every distinct (WORD, CERTAIN) sign-label tuple, normalised."""
    types: set[tuple[str, ...]] = set()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is TokenKind.WORD and tok.status is ReadingStatus.CERTAIN:
                types.add(tuple(normalize_label(s) for s in tok.signs))
    return types


def build_toponym_lexicon(word_types: set[tuple[str, ...]]):
    """Verify each candidate toponym against the loaded DAMOS word types.

    Returns ``(attested, dropped)``: attested is a list of
    ``(surface_form, sign_tuple, sources)``; dropped is the list of candidate surface
    forms with no matching WORD/CERTAIN token anywhere in DAMOS.
    """
    attested = []
    dropped = []
    for surface in KNOSSOS_TOPONYM_CANDIDATES:
        signs = tuple(normalize_label(s) for s in surface.split("-"))
        if signs in word_types:
            sources = ["Ventris & Chadwick 1973 (Knossos place-name set)"]
            if surface in PACKARD_TABLE11_PLACE_TAGGED:
                sources.append("Packard 1974 Table 11 p.92, tagged \"(place)\"")
            attested.append((surface, signs, sources))
        else:
            dropped.append(surface)
    return attested, dropped


def exact_prefix_of_any(word: tuple[str, ...], others: list[tuple[str, ...]]) -> bool:
    return any(len(word) > len(o) and word[: len(o)] == o for o in others)


def build_personal_name_control(corpus, toponym_words: list[tuple[str, ...]], n: int):
    """The ``n`` most frequent non-toponym WORD types on the Knossos Da-Dv sheep series.

    Those tablets record shepherd name (+ sometimes a toponym in an oblique case) +
    OVIS + a number, so the dominant non-toponym vocabulary there is personal names.
    Toponyms themselves are frequent in this same series (the flock's location), so
    they and their exact-prefix derivatives (e.g. a locative built on ``*56-ko-we``) are
    excluded first; ties broken alphabetically for a reproducible ranking.
    """
    d_docs = [
        d for d in corpus.documents
        if d.meta and d.meta.site == "Knossos" and D_SERIES_RE.search(d.id or "")
    ]
    counts: Counter[tuple[str, ...]] = Counter()
    for d in d_docs:
        for tok in d.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            if not all(is_clean_sign(s) for s in tok.signs):
                continue
            counts[tuple(normalize_label(s) for s in tok.signs)] += 1

    toponym_set = set(toponym_words)
    candidates = [
        (w, c) for w, c in counts.items()
        if w not in toponym_set
        and w not in MANUAL_CONTROL_EXCLUDE
        and not exact_prefix_of_any(w, toponym_words)
    ]
    candidates.sort(key=lambda wc: (-wc[1], wc[0]))
    return candidates[:n], len(d_docs)


def linear_a_word_types(corpus, min_len: int = 3) -> list[tuple[str, ...]]:
    """Distinct (WORD, CERTAIN) sign-label tuples of at least ``min_len`` signs."""
    types: set[tuple[str, ...]] = set()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if (
                tok.kind is TokenKind.WORD
                and tok.status is ReadingStatus.CERTAIN
                and len(tok.signs) >= min_len
            ):
                types.add(tuple(normalize_label(s) for s in tok.signs))
    return sorted(types)


def b_consonant_set(label: str) -> frozenset[str] | None:
    """A Linear B sign's own Greek consonant set (never permuted)."""
    series = consonant_series(label.lower())
    if series is None:
        return None
    return SERIES_TO_GREEK.get(series)


def count_matches(la_words, lexicon_words, cmap) -> tuple[int, int]:
    """Packard's "3=" and "4=" counts, total qualifying (Linear A, Linear B) pairs.

    ``cmap`` supplies the Linear A side's consonant set per sign under one value
    assignment (real, or one null draw); the Linear B side always reads its own known
    value via :func:`b_consonant_set`.
    """
    c3 = c4 = 0
    lex3 = [w for w in lexicon_words if len(w) >= 3]
    lex4 = [w for w in lexicon_words if len(w) >= 4]
    b_cache: dict[str, frozenset[str] | None] = {}

    def b_set(label: str):
        if label not in b_cache:
            b_cache[label] = b_consonant_set(label)
        return b_cache[label]

    for w in la_words:
        wl = len(w)
        if wl >= 3:
            for t in lex3:
                if w[0] == t[0] and w[1] == t[1]:
                    a_opts = cmap.get(w[2])
                    b_opts = b_set(t[2])
                    if a_opts and b_opts and (a_opts & b_opts):
                        c3 += 1
        if wl >= 4:
            for t in lex4:
                if w[0] == t[0] and w[1] == t[1] and w[2] == t[2] and w[3] == t[3]:
                    c4 += 1
                elif w[0] == t[0] and w[1] == t[1] and w[2] == t[2]:
                    a_opts = cmap.get(w[3])
                    b_opts = b_set(t[3])
                    if a_opts and b_opts and (a_opts & b_opts):
                        c4 += 1
    return c3, c4


def percentile(values: list[float], pct: int) -> float:
    return statistics.quantiles(values, n=100, method="inclusive")[pct - 1]


def real_percentile_rank(real: int, nulls: list[int]) -> float:
    n = len(nulls)
    less = sum(1 for x in nulls if x < real)
    equal = sum(1 for x in nulls if x == real)
    return 100.0 * (less + 0.5 * equal) / n


def score_edition(edition_name: str, la_words: list[tuple[str, ...]], gmap,
                   lexicons: dict[str, list[tuple[str, ...]]], seed: int,
                   n_permutations: int) -> dict:
    sign_freq = Counter(s for w in la_words for s in w)
    rows = []
    for lex_name, lex_words in lexicons.items():
        real3, real4 = count_matches(la_words, lex_words, gmap)
        rng = random.Random(seed)
        null3: list[int] = []
        null4: list[int] = []
        for _ in range(n_permutations):
            pmap = frequency_matched_permute(gmap, rng, sign_freq)
            c3, c4 = count_matches(la_words, lex_words, pmap)
            null3.append(c3)
            null4.append(c4)
        for match_class, real, nulls in (("3=", real3, null3), ("4=", real4, null4)):
            rows.append({
                "edition": edition_name,
                "lexicon": lex_name,
                "match_class": match_class,
                "real": real,
                "null_mean": statistics.fmean(nulls),
                "null_sd": statistics.pstdev(nulls),
                "null_p95": percentile(nulls, 95),
                "null_p99": percentile(nulls, 99),
                "real_percentile": real_percentile_rank(real, nulls),
                "n_permutations": n_permutations,
            })
    return {
        "edition": edition_name,
        "n_word_types_3plus": len(la_words),
        "sign_freq_bands": 4,
        "rows": rows,
    }


def main() -> dict:
    damos = aegean.load("damos")
    gorila = aegean.load("lineara")
    sigla = aegean.load("sigla")

    word_types = damos_word_types(damos)
    attested, dropped = build_toponym_lexicon(word_types)
    toponym_words = [signs for _surface, signs, _sources in attested]

    control_pairs, n_d_docs = build_personal_name_control(damos, toponym_words, len(toponym_words))
    control_words = [w for w, _count in control_pairs]

    # Record the lexicons and their sources outside the repo (corpus-derived).
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCE_FILE.write_text(json.dumps({
        "generated_by": "spikes/S-003-packard-toponyms/run.py",
        "toponym_candidates": len(KNOSSOS_TOPONYM_CANDIDATES),
        "toponym_attested": len(attested),
        "toponym_dropped": dropped,
        "toponyms": [
            {"surface": surface, "signs": list(signs), "sources": sources}
            for surface, signs, sources in attested
        ],
        "personal_name_control_source": (
            f"Top {len(control_words)} non-toponym WORD/CERTAIN types by frequency on "
            f"the {n_d_docs} Knossos Da-Dv sheep-series documents"
        ),
        "personal_names_control": [
            {"signs": list(w), "frequency": c} for w, c in control_pairs
        ],
    }, indent=2))

    gmap = build_map(gorila.sign_inventory, "greek_syllabic")
    lexicons = {"toponyms": toponym_words, "personal_names_control": control_words}

    editions = []
    for name, corpus in (("gorila", gorila), ("sigla", sigla)):
        la_words = linear_a_word_types(corpus, min_len=3)
        editions.append(score_edition(name, la_words, gmap, lexicons, SEED, N_PERMUTATIONS))

    payload = {
        "question": "Does Packard's Knossos toponym match count survive a 200-draw "
                     "frequency-banded null, on GORILA and on SigLA?",
        "protocol": {
            "n_permutations": N_PERMUTATIONS,
            "seed": SEED,
            "null": "frequency_matched_permute, 4 bands (hypotheses.run)",
            "phonology": "greek_syllabic (hypotheses.phonologies), built from the "
                         "GORILA sign inventory and reused for SigLA (SigLA carries no "
                         "sign_inventory)",
            "match_definition": (
                "3= : first two sign labels identical, third sign shares a Greek "
                "consonant. 4= : four sign labels identical, or first three identical "
                "and the fourth shares a consonant. Identical-label positions are fixed "
                "by the corpus and do not vary under the null; only the Linear A side's "
                "consonant set at the differing position does."
            ),
            "toponym_lexicon_size": len(toponym_words),
            "toponym_candidates": len(KNOSSOS_TOPONYM_CANDIDATES),
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
        print(f"\n== {ed['edition']}  n_word_types(3+)={ed['n_word_types_3plus']}")
        for r in ed["rows"]:
            print(
                f"{r['lexicon']:<24} {r['match_class']:<3} real={r['real']:>3} "
                f"null_mean={r['null_mean']:>6.2f} sd={r['null_sd']:>5.2f} "
                f"p95={r['null_p95']:>5.1f} p99={r['null_p99']:>5.1f} "
                f"real_pct={r['real_percentile']:>5.1f}"
            )
