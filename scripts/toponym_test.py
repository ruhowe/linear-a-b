#!/usr/bin/env python3
"""Value transfer 1.0: Packard's Knossos toponym test, main line (CHANGELOG "Value
transfer (A-001): the toponym test", entry 1.0).

    .venv/bin/python scripts/toponym_test.py

Promotes spike S-003b (F-038, exploratory) to a frozen, pre-registered protocol, adding
a second wrong control S-003b lacked (Pylos toponyms) and a third (Knossos toponyms with
sign order reversed), two band structures, two null seeds and 400 draws each. Per
result-discipline.md, this file is the frozen protocol; FINDINGS.md and CHANGELOG.md are
not touched by this script or by hand as part of this change.

**Lexicons**, each verified against ``aegean.load("damos")`` word types (WORD/CERTAIN)
before use, so an unattested candidate is dropped and counted rather than assumed:

(a) Knossos toponyms. The 32-of-33 candidate set carried over unchanged from spike S-003
    (``spikes/S-003-packard-toponyms/run.py``, reused here rather than re-typed, since it
    is the object under test's answer key and must stay byte-identical): the well-known
    Ventris and Chadwick 1973 Knossos place-name set, cross-checked against Packard 1974
    Table 11 p.92. Verified here specifically against Knossos-site (``doc.meta.site ==
    "Knossos"``) WORD/CERTAIN types (A-136): stricter than S-003, which checked the whole
    DAMOS corpus without a site filter, but confirmed to drop the identical single
    candidate (``di-ka-ta``, only ``di-ka-ta-de``/``di-ka-ta-jo`` attested).

(b) Knossos personal names, a wrong control of the same script and site. The 32 most
    frequent non-toponym WORD/CERTAIN types on Knossos documents whose archival series
    (``aegean.analysis.hands.series_of``) starts with "D" (A-137): broader than S-003's
    control, which restricted to the Da-Dv sheep series specifically; here every D-series
    document (Da through Dv, Do, Dp, Dq, Dg, Dh, Dk, Dl, Dm, Dn, bare "D") counts, per the
    CHANGELOG 1.0 wording. Toponym-lexicon exact matches, their exact-signed prefixes
    (e.g. a locative built on a toponym), and ``da-mi-ni-jo`` (Packard Table 11 p.92 tags
    it "(place)", carried over from S-003's manual exclusion) are excluded before ranking.

(c) Pylos toponyms, a wrong control by geography: mainland places a Cretan Linear A
    archive should not name (A-134). The sixteen major Hither and Further Province towns
    (Ventris and Chadwick 1973 pp.141-143, tablets 75=Cn02, 250=Vn01, 257=Jn09), plus
    Pu-ro (Pylos itself, pp.140-141), Ro-u-so (replaces E-ra-to in the parallel Jn09
    list, p.141), A-pi-no-e-wi-jo (PY 184=Nn01 and the Mb series, pp.146, 323, named
    there as place names rather than adjectives), and two further Further-Province towns
    named in the same Ma sector-grouping discussion, E-sa-re-wi-ja and A-te-re-wi-ja
    (p.144; A-138 records the choice to include these two beyond the task's named list).
    Verified against Pylos-site WORD/CERTAIN types; two of the sixteen (A-pu2, E-ra-to)
    are dropped as unattested in that exact nominative form, both flagged with a query
    mark in Ventris and Chadwick's own table.

(d) Knossos toponyms, sign order reversed: lexicon (a) with each word's sign tuple
    reversed, same signs, same lengths, no meaning. Tests whether the match count is
    sensitive to word identity at all, or just to the multiset of signs and lengths.

**Corpora.** GORILA (``aegean.load("lineara")``) and SigLA (``aegean.load("sigla")``),
Linear A WORD/CERTAIN types of three or more signs, scored separately (own sign
frequency ranking, own bands).

**The value assignment and the match test.** Reused unchanged from spike S-003b
(``spikes/S-003b-packard-toponyms-full-null/run.py``), moved into this main-line script
per the task brief rather than re-derived: a value assignment is a bijection from every
Linear A sign label eligible for a value (occurs in a 3+-sign WORD/CERTAIN type of that
edition *and* is a Linear B sign label) to a label within its own frequency band. The
real assignment is identity, the transliteration convention under test. "3=": the
assignment's image of the Linear A word's first two signs equals the lexicon word's
first two signs (literal label identity), and the image of the third sign shares a Greek
consonant (``kober.values.consonant_of``) with the lexicon word's own third sign, read
off its own known Linear B value directly, never through the assignment. "4=": the first
three images equal the lexicon word's first three signs, and the fourth image either
equals its fourth sign outright or shares a consonant with it. Distinct (Linear A word,
lexicon word) pairs are counted; every position, not just the differing one, is subject
to the assignment, so a null draw has to earn every identical position by chance exactly
as the real (identity) assignment does (this is what S-003b corrected in S-003).

**The null.** One random permutation per frequency band, all bands drawn together
(Packard 1974 pp.73-74's own construction: signs ranked by whole-corpus token frequency,
split into contiguous groups of ten), 400 draws, seeds 0 and 1. A four-band split of the
same ranked list is scored alongside as a sensitivity. (``src/hypotheses/run.py``'s
``frequency_matched_permute`` documents the same banding convention for a different
statistic, breadth-matched consonant sets rather than a label bijection; it is not
imported here, since S-003b's simpler bijection-within-band null is what CHANGELOG's 1.0
entry specifies and what this script reuses.)

**Criterion** (frozen in CHANGELOG "Value transfer 1.0"): the toponym lexicon's 3= real
count exceeds its null's 99th percentile in every (edition, banding, seed) cell; no
wrong-control lexicon's real count exceeds its own null's 99th percentile anywhere, in
either match class.

**Output.** ``results/toponym_test-{edition}-seed{S}.json`` per edition and seed:
aggregate numbers (real, null mean/sd/p95/p99, real percentile) for every lexicon, class
and banding, plus the real-assignment matched pairs as sign labels and the set of sign
labels the matches involve (A-139 defines this as the union of the signs at the matched
positions, both sides, over every matched pair in either class). Toponym surface forms
are published readings, not corpus text (corpus-sources.md Invariants). A markdown
summary, ``results/toponym_test.md``, with every table and the criterion evaluated cell
by cell.

**--extra-word-types PATH, --results-dir DIR, --edition {gorila,sigla,both}**
(CHANGELOG "Supplement sensitivity (F-047)"). ``--extra-word-types`` reads a private
JSONL of extra Linear A sign-label tuples and appends them to the GORILA word-type set
(``merge_extra_word_types``) before any statistic runs; omitted, output is byte-identical
to before the option existed. ``--results-dir`` and ``--edition`` exist so the
sensitivity run can write GORILA-only results to a scratch directory without touching
``results/toponym_test-*.json`` or ``results/toponym_test.md``; their defaults
(``results``, ``both``) reproduce every existing invocation exactly.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402
from aegean.analysis.hands import series_of  # noqa: E402

from kober.values import consonant_of  # noqa: E402
from linearb_restore.normalise import normalise_text  # noqa: E402

PROTOCOL_VERSION = "1.0"
N_PERMUTATIONS = 400
SEEDS = [0, 1]
BAND_SIZE = 10
N_SENSITIVITY_BANDS = 4

# --------------------------------------------------------------------------
# Lexicon (a): Knossos toponyms. Candidate list and Packard tagging carried
# over unchanged from spikes/S-003-packard-toponyms/run.py.
# --------------------------------------------------------------------------

KNOSSOS_TOPONYM_CANDIDATES = [
    "ko-no-so", "a-mi-ni-so", "pa-i-to", "tu-ri-so", "ku-ta-to", "ru-ki-to",
    "se-to-i-ja", "da-*22-to", "qa-ra", "su-ri-mo", "ra-su-to", "ti-ri-to",
    "e-ko-so", "da-wo", "u-ta-no", "ku-do-ni-ja", "a-pa-ta-wa", "wa-to",
    "su-ki-ri-ta", "ri-jo-no", "di-ka-ta", "e-ra", "ra-to", "ra-ja", "tu-ni-ja",
    "pa-na-so", "qa-mo", "*56-ko-we", "si-ja-du-we", "ku-ta-i-to", "da-ta-ra-mo",
    "do-ti-ja", "pu-na-so",
]
_KNOSSOS_BASE_SOURCE = "Ventris and Chadwick 1973, pp.139-150, 183-194 (Knossos place-name discussion)"
PACKARD_TABLE11_PLACE_TAGGED = {"pa-i-to", "ku-do-ni-ja", "su-ki-ri-ta"}


def knossos_toponym_sources(surface: str) -> list[str]:
    sources = [_KNOSSOS_BASE_SOURCE]
    if surface in PACKARD_TABLE11_PLACE_TAGGED:
        sources.append('Packard 1974 Table 11 p.92, tagged "(place)"')
    return sources


# --------------------------------------------------------------------------
# Lexicon (b): Knossos personal names, wrong control 1.
# --------------------------------------------------------------------------

MANUAL_CONTROL_EXCLUDE = {("DA", "MI", "NI", "JO")}
_PERSONAL_NAME_EXCLUDE_SOURCE = (
    'Packard 1974 Table 11 p.92 tags da-mi-ni-jo "(place)"; excluded by name rather '
    "than left ambiguous (carried over from S-003)."
)

# --------------------------------------------------------------------------
# Lexicon (c): Pylos toponyms, wrong control 2 (A-134, A-138).
# --------------------------------------------------------------------------

PYLOS_TOPONYM_SOURCES: dict[str, list[str]] = {
    # Nine Towns of the Hither Province.
    "pi-*82": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "me-ta-pa": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "pe-to-no": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "pa-ki-ja-ne": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "a-pu2": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01; given there as \"A-pu2?-\", their own query mark)"],
    "a-ke-re-wa": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "e-ra-to": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "ka-ra-do-ro": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    "ri-jo": ["Ventris and Chadwick 1973, pp.141-142 (Nine Towns, 75=Cn02, 250=Vn01)"],
    # Seven Towns of the Further Province (257=Jn09 continuation).
    "ti-mi-to-a-ke-e": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "ra-wa-ra-ta2": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "sa-ma-ra": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "a-si-ja-ti-ja": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "e-ra-te-re-wa-pi": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "za-ma-e-wi-ja": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    "e-re-i": ["Ventris and Chadwick 1973, pp.142-143 (Seven Towns, 257=Jn09)"],
    # Named individually in the task brief.
    "pu-ro": ["Ventris and Chadwick 1973, pp.140-141 (Pylos itself, the site name; 172=Kn02, the Ab tablets)"],
    "ro-u-so": ["Ventris and Chadwick 1973, p.141 (replaces e-ra-to in the parallel Jn09 list); p.416 (Additional Commentary, northern frontier)"],
    "a-pi-no-e-wi-jo": ["Ventris and Chadwick 1973, p.146 (PY 184=Nn01, \"seem to be place-names rather than adjectives\"); p.323 (Additional Commentary, Mb 1396)"],
    # Two further Further-Province towns named in the same Ma sector-grouping
    # discussion as the Seven Towns list (A-138: included beyond the task's
    # named sixteen plus three, since Ventris and Chadwick name them as towns
    # in the identical passage).
    "e-sa-re-wi-ja": ["Ventris and Chadwick 1973, p.144 (Further Province sector grouping); p.424 (associated with the Further Province, On 300)"],
    "a-te-re-wi-ja": ["Ventris and Chadwick 1973, p.144 (Further Province sector grouping); p.424 (\"associated with it on An 830\")"],
}
PYLOS_TOPONYM_CANDIDATES = list(PYLOS_TOPONYM_SOURCES)


# --------------------------------------------------------------------------
# Normalisation helpers (reused from S-003's run.py, not re-derived).
# --------------------------------------------------------------------------

def normalize_label(label: str) -> str:
    """Canonical sign-label form: strip Leiden marks, fold subscript digits, upper-case."""
    text, _had_underdot, _had_span = normalise_text(label)
    return text.upper()


def is_clean_sign(sign: str) -> bool:
    """No bracket, query mark, underdot or span-bracket damage mark (A-004)."""
    if any(ch in sign for ch in "[]?"):
        return False
    _text, had_underdot, had_span = normalise_text(sign)
    return not had_underdot and not had_span


def word_types_for_site(corpus, site: str) -> set[tuple[str, ...]]:
    """Every distinct (WORD, CERTAIN) sign-label tuple at documents of one site."""
    types: set[tuple[str, ...]] = set()
    for doc in corpus.documents:
        if not doc.meta or doc.meta.site != site:
            continue
        for tok in doc.tokens:
            if tok.kind is TokenKind.WORD and tok.status is ReadingStatus.CERTAIN:
                types.add(tuple(normalize_label(s) for s in tok.signs))
    return types


def build_toponym_lexicon(candidates: list[str], sources: dict, word_types: set[tuple[str, ...]]):
    """Verify each candidate against ``word_types``.

    Returns ``(attested, dropped)``: attested is a list of
    ``(surface_form, sign_tuple, sources)``; dropped is the list of candidate surface
    forms with no matching WORD/CERTAIN token at that site.
    """
    attested = []
    dropped = []
    for surface in candidates:
        signs = tuple(normalize_label(s) for s in surface.split("-"))
        if signs in word_types:
            attested.append((surface, signs, sources[surface]))
        else:
            dropped.append(surface)
    return attested, dropped


def exact_prefix_of_any(word: tuple[str, ...], others: list[tuple[str, ...]]) -> bool:
    return any(len(word) > len(o) and word[: len(o)] == o for o in others)


def build_personal_name_control(corpus, toponym_words: list[tuple[str, ...]], n: int):
    """The ``n`` most frequent non-toponym WORD/CERTAIN types on Knossos documents
    whose archival series starts with "D" (CHANGELOG 1.0; broader than S-003's
    Da-Dv-only control, A-137). Toponyms, their exact-signed prefixes, and the one
    Packard-tagged exclusion are removed before ranking; ties broken alphabetically."""
    d_docs = [
        d for d in corpus.documents
        if d.meta and d.meta.site == "Knossos" and (series_of(d) or "").startswith("D")
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


def sign_token_frequency(corpus) -> Counter:
    """Occurrences of each normalised sign label across every WORD/CERTAIN token,
    any length (Packard's whole-corpus ranking, not the 3+-sign subset)."""
    freq: Counter = Counter()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is TokenKind.WORD and tok.status is ReadingStatus.CERTAIN:
                for s in tok.signs:
                    freq[normalize_label(s)] += 1
    return freq


def build_sign_inventory(la_words_3plus: list[tuple[str, ...]], b_labels: set[str],
                          freq: Counter) -> list[str]:
    """Labels usable in a value assignment: occur in a 3+-sign Linear A word type and
    are also a Linear B sign label. Ranked by whole-corpus token frequency, descending,
    ties broken alphabetically."""
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
    """One independent random permutation per band; every band's label multiset (as
    keys, and as values) is unchanged, only the pairing is shuffled."""
    cmap: dict[str, str] = {}
    for band in bands:
        shuffled = list(band)
        rng.shuffle(shuffled)
        cmap.update(zip(band, shuffled))
    return cmap


def count_matches(la_words: list[tuple[str, ...]], lexicon_words: list[tuple[str, ...]],
                   cmap: dict[str, str], collect_pairs: bool = False):
    """Packard's "3=" and "4=" counts under one value assignment ``cmap``.

    The lexicon side is a real Linear B word: its own consonant is read directly off
    its label, never through ``cmap``. Every position of the Linear A side goes through
    ``cmap``. When ``collect_pairs`` is set, also returns the matched (Linear A word,
    lexicon word) pairs for each class (only meaningful for the real/identity
    assignment; null draws only need the counts).
    """
    c3 = c4 = 0
    pairs3: list = [] if collect_pairs else None
    pairs4: list = [] if collect_pairs else None
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
                        if collect_pairs:
                            pairs3.append((w, t))
        if wl >= 4:
            c3v = cons(a[3])
            for t in lex4:
                if a[0] == t[0] and a[1] == t[1] and a[2] == t[2]:
                    if a[3] == t[3]:
                        c4 += 1
                        if collect_pairs:
                            pairs4.append((w, t))
                    elif c3v is not None and cons(t[3]) == c3v:
                        c4 += 1
                        if collect_pairs:
                            pairs4.append((w, t))
    return c3, c4, pairs3, pairs4


def signs_involved(pairs: list[tuple], match_len: int) -> set[str]:
    """A-139: the set of sign labels (either side) appearing at a matched position,
    over every pair in one match class."""
    involved: set[str] = set()
    for la_word, lex_word in pairs:
        involved.update(la_word[:match_len])
        involved.update(lex_word[:match_len])
    return involved


def percentile(values: list[float], pct: int) -> float:
    return statistics.quantiles(values, n=100, method="inclusive")[pct - 1]


def real_percentile_rank(real: int, nulls: list[int]) -> float:
    n = len(nulls)
    less = sum(1 for x in nulls if x < real)
    equal = sum(1 for x in nulls if x == real)
    return 100.0 * (less + 0.5 * equal) / n


def score_band_structure(structure_name: str, bands: list[list[str]], ranked_labels: list[str],
                          la_words: list[tuple[str, ...]], lexicons: dict[str, list[tuple[str, ...]]],
                          seed: int, n_permutations: int) -> dict:
    id_map = identity_map(ranked_labels)

    rows = []
    for name, words in lexicons.items():
        real3, real4, pairs3, pairs4 = count_matches(la_words, words, id_map, collect_pairs=True)
        rng = random.Random(seed)
        null3: list[int] = []
        null4: list[int] = []
        for _ in range(n_permutations):
            pmap = permuted_map(bands, rng)
            c3, c4, _, _ = count_matches(la_words, words, pmap)
            null3.append(c3)
            null4.append(c4)
        for match_class, real, nulls, pairs, match_len in (
            ("3=", real3, null3, pairs3, 3),
            ("4=", real4, null4, pairs4, 4),
        ):
            rows.append({
                "lexicon": name,
                "match_class": match_class,
                "real": real,
                "null_mean": statistics.fmean(nulls),
                "null_sd": statistics.pstdev(nulls),
                "null_p95": percentile(nulls, 95),
                "null_p99": percentile(nulls, 99),
                "real_percentile": real_percentile_rank(real, nulls),
                "n_permutations": n_permutations,
                "matched_pairs": [
                    {"linear_a": list(la), "lexicon_word": list(lex)} for la, lex in pairs
                ],
                "sign_labels_involved": sorted(signs_involved(pairs, match_len)),
            })

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
    )
    four_bands = score_band_structure(
        "four_bands", bands_4, ranked, la_words, lexicons, seed, n_permutations,
    )

    return {
        "edition": edition_name,
        "n_word_types_3plus": len(la_words),
        "sign_inventory_size": len(ranked),
        "band_structures": {"groups_of_10": groups_of_10, "four_bands": four_bands},
    }


def load_extra_word_types(path: str | Path) -> list[tuple[str, ...]]:
    """CHANGELOG "Supplement sensitivity" (F-047): read a private JSONL of extra
    Linear A sign-label-tuple word types. One JSON list of labels per line; lines
    starting with ``#`` (the required source header) are ignored. Labels are
    upper-cased to match ``normalize_label``'s output, so a differently-cased
    source file still lines up with the corpus's own word-type tuples."""
    types: list[tuple[str, ...]] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        labels = json.loads(line)
        types.append(tuple(str(s).upper() for s in labels))
    return types


def merge_extra_word_types(
    per_edition_words: dict[str, list[tuple[str, ...]]],
    extra_word_types: list[tuple[str, ...]],
    edition: str = "gorila",
) -> dict[str, list[tuple[str, ...]]]:
    """CHANGELOG "Supplement sensitivity" (F-047): append ``extra_word_types``
    into ``per_edition_words[edition]`` only, before any statistic is computed
    from it (the CHANGELOG entry appends the four new types "to the GORILA
    word-type set"; other editions, ``sigla`` included, are returned unchanged).
    An empty ``extra_word_types`` (the option omitted) returns every edition's
    word list with the same values as given -- the byte-identical-output
    requirement is about the written JSON, which this preserves."""
    result = dict(per_edition_words)
    if extra_word_types and edition in result:
        result[edition] = sorted(set(result[edition]) | set(extra_word_types))
    return result


def build_lexicons(damos):
    """Build all four lexicons once (seed- and edition-independent). Returns
    ``(lexicons, provenance)`` where ``lexicons`` maps name -> list of sign tuples and
    ``provenance`` carries per-entry source notes and drop lists for the results file."""
    kn_word_types = word_types_for_site(damos, "Knossos")
    py_word_types = word_types_for_site(damos, "Pylos")

    kn_toponym_sources = {s: knossos_toponym_sources(s) for s in KNOSSOS_TOPONYM_CANDIDATES}
    kn_attested, kn_dropped = build_toponym_lexicon(
        KNOSSOS_TOPONYM_CANDIDATES, kn_toponym_sources, kn_word_types
    )
    knossos_toponym_words = [signs for _surface, signs, _sources in kn_attested]

    py_attested, py_dropped = build_toponym_lexicon(
        PYLOS_TOPONYM_CANDIDATES, PYLOS_TOPONYM_SOURCES, py_word_types
    )
    pylos_toponym_words = [signs for _surface, signs, _sources in py_attested]

    control_pairs, n_d_docs = build_personal_name_control(
        damos, knossos_toponym_words, len(knossos_toponym_words)
    )
    personal_name_words = [w for w, _count in control_pairs]

    reversed_words = [tuple(reversed(w)) for w in knossos_toponym_words]

    lexicons = {
        "knossos_toponyms": knossos_toponym_words,
        "knossos_personal_names": personal_name_words,
        "pylos_toponyms": pylos_toponym_words,
        "knossos_toponyms_reversed": reversed_words,
    }

    provenance = {
        "knossos_toponyms": {
            "size": len(knossos_toponym_words),
            "candidates": len(KNOSSOS_TOPONYM_CANDIDATES),
            "dropped": kn_dropped,
            "entries": [
                {"surface": s, "signs": list(sg), "sources": src} for s, sg, src in kn_attested
            ],
        },
        "knossos_personal_names": {
            "size": len(personal_name_words),
            "source": (
                f"Top {len(personal_name_words)} non-toponym WORD/CERTAIN types by "
                f"frequency on {n_d_docs} Knossos documents whose series_of starts "
                f'with "D"'
            ),
            "manual_exclusion": _PERSONAL_NAME_EXCLUDE_SOURCE,
            "entries": [{"signs": list(w), "frequency": c} for w, c in control_pairs],
        },
        "pylos_toponyms": {
            "size": len(pylos_toponym_words),
            "candidates": len(PYLOS_TOPONYM_CANDIDATES),
            "dropped": py_dropped,
            "entries": [
                {"surface": s, "signs": list(sg), "sources": src} for s, sg, src in py_attested
            ],
        },
        "knossos_toponyms_reversed": {
            "size": len(reversed_words),
            "source": "Lexicon (a), each word's sign tuple reversed. Same signs and lengths, no meaning.",
        },
    }
    return lexicons, provenance


def main(
    out_dir: str | Path = "results",
    extra_word_types_path: str | Path | None = None,
    editions: tuple[str, ...] = ("gorila", "sigla"),
) -> dict:
    out_path = ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)

    damos = aegean.load("damos")
    edition_loaders = {"gorila": "lineara", "sigla": "sigla"}
    corpora = {name: aegean.load(edition_loaders[name]) for name in editions}

    lexicons, provenance = build_lexicons(damos)
    b_labels = {s.label for s in damos.sign_inventory.signs}

    per_edition_words = {
        name: linear_a_word_types(corpus, min_len=3) for name, corpus in corpora.items()
    }
    per_edition_freq = {name: sign_token_frequency(corpus) for name, corpus in corpora.items()}

    extra_word_types: list[tuple[str, ...]] = []
    if extra_word_types_path is not None:
        extra_word_types = load_extra_word_types(extra_word_types_path)
        per_edition_words = merge_extra_word_types(per_edition_words, extra_word_types, edition="gorila")

    all_results: dict[tuple[str, int], dict] = {}
    for seed in SEEDS:
        for name in corpora:
            edition_result = score_edition(
                name, per_edition_words[name], b_labels, per_edition_freq[name],
                lexicons, seed, N_PERMUTATIONS,
            )
            payload = {
                "protocol_version": PROTOCOL_VERSION,
                "seed": seed,
                "n_permutations": N_PERMUTATIONS,
                "band_size": BAND_SIZE,
                "n_sensitivity_bands": N_SENSITIVITY_BANDS,
                "match_definition": (
                    "3= : the assignment's image of the Linear A word's first two "
                    "signs equals the lexicon word's first two signs, and the third "
                    "sign's image shares a Greek consonant (kober.values.consonant_of) "
                    "with the lexicon word's third sign. 4= : the first three images "
                    "equal the lexicon word's first three signs, and the fourth image "
                    "either equals its fourth sign or shares a consonant with it. The "
                    "lexicon side always reads its own known Linear B value directly, "
                    "never through the assignment."
                ),
                "null": (
                    "one random permutation per frequency band, all bands drawn "
                    "together, every word position read through the resulting "
                    "assignment (spike S-003b's construction, moved into the main line)"
                ),
                "lexicons": provenance,
                "edition": edition_result,
            }
            if extra_word_types_path is not None and name == "gorila":
                payload["extra_word_types_count"] = len(extra_word_types)
                payload["extra_word_types_file"] = Path(extra_word_types_path).name
            all_results[(name, seed)] = payload
            out_file = out_path / f"toponym_test-{name}-seed{seed}.json"
            out_file.write_text(json.dumps(payload, indent=2))

    write_markdown_summary(out_path / "toponym_test.md", all_results, provenance)
    return all_results


def _row_lookup(payload: dict, structure: str, lexicon: str, match_class: str) -> dict:
    for row in payload["edition"]["band_structures"][structure]["rows"]:
        if row["lexicon"] == lexicon and row["match_class"] == match_class:
            return row
    raise KeyError((structure, lexicon, match_class))


def write_markdown_summary(path: Path, all_results: dict[tuple[str, int], dict], provenance: dict) -> None:
    lexicon_labels = {
        "knossos_toponyms": "Knossos toponyms",
        "knossos_personal_names": "Knossos personal names (control)",
        "pylos_toponyms": "Pylos toponyms (control)",
        "knossos_toponyms_reversed": "Knossos toponyms, reversed (control)",
    }
    structures = ["groups_of_10", "four_bands"]
    structure_labels = {"groups_of_10": "groups of ten", "four_bands": "four bands"}
    editions = [e for e in ("gorila", "sigla") if any(k[0] == e for k in all_results)]

    lines = []
    lines.append("# Value transfer 1.0: the toponym test")
    lines.append("")
    lines.append(
        f"Protocol version {PROTOCOL_VERSION}. {N_PERMUTATIONS} draws per (edition, "
        f"banding, seed) cell, seeds {SEEDS}. Match test and value-assignment null "
        "reused from spike S-003b. Raw numbers: "
        "`results/toponym_test-{edition}-seed{seed}.json`. Full detail in "
        "CHANGELOG.md \"Value transfer (A-001): the toponym test\", entry 1.0."
    )
    lines.append("")

    lines.append("## Lexicons")
    lines.append("")
    kn = provenance["knossos_toponyms"]
    lines.append(
        f"(a) Knossos toponyms: {kn['size']} of {kn['candidates']} candidates attested "
        f"as WORD/CERTAIN types in DAMOS Knossos documents. Dropped: {', '.join(kn['dropped']) or 'none'}."
    )
    pn = provenance["knossos_personal_names"]
    lines.append(f"(b) Knossos personal names, control: {pn['source']}.")
    py = provenance["pylos_toponyms"]
    lines.append(
        f"(c) Pylos toponyms, control: {py['size']} of {py['candidates']} candidates "
        f"attested as WORD/CERTAIN types in DAMOS Pylos documents. "
        f"Dropped: {', '.join(py['dropped']) or 'none'}."
    )
    rv = provenance["knossos_toponyms_reversed"]
    lines.append(f"(d) Knossos toponyms reversed, control: {rv['source']}")
    lines.append("")

    lines.append("### Lexicon (a): Knossos toponyms, per entry")
    lines.append("")
    lines.append("| surface | sources |")
    lines.append("|---|---|")
    for e in kn["entries"]:
        lines.append(f"| {e['surface']} | {'; '.join(e['sources'])} |")
    lines.append("")

    lines.append("### Lexicon (c): Pylos toponyms, per entry")
    lines.append("")
    lines.append("| surface | sources |")
    lines.append("|---|---|")
    for e in py["entries"]:
        lines.append(f"| {e['surface']} | {'; '.join(e['sources'])} |")
    lines.append("")

    lines.append("## Match counts")
    lines.append("")
    for edition in editions:
        for structure in structures:
            lines.append(f"### {edition.upper()}, {structure_labels[structure]}")
            lines.append("")
            for seed in SEEDS:
                payload = all_results[(edition, seed)]
                lines.append(f"**Seed {seed}**")
                lines.append("")
                lines.append(
                    "| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile |"
                )
                lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
                for lex_name in lexicon_labels:
                    for match_class in ("3=", "4="):
                        row = _row_lookup(payload, structure, lex_name, match_class)
                        lines.append(
                            f"| {lexicon_labels[lex_name]} | {match_class} | {row['real']} | "
                            f"{row['null_mean']:.2f} | {row['null_sd']:.2f} | "
                            f"{row['null_p95']:.1f} | {row['null_p99']:.1f} | "
                            f"{row['real_percentile']:.1f} |"
                        )
                lines.append("")

    if ("gorila", 0) in all_results:
        lines.append("## Matched pairs (real assignment), lexicon (a) 3= and 4=, GORILA groups of ten, seed 0")
        lines.append("")
        ref = all_results[("gorila", 0)]
        for match_class in ("3=", "4="):
            row = _row_lookup(ref, "groups_of_10", "knossos_toponyms", match_class)
            lines.append(f"**{match_class}** ({row['real']} pairs)")
            lines.append("")
            if row["matched_pairs"]:
                lines.append("| Linear A word | Knossos toponym |")
                lines.append("|---|---|")
                for pair in row["matched_pairs"]:
                    lines.append(f"| {'-'.join(pair['linear_a'])} | {'-'.join(pair['lexicon_word'])} |")
            else:
                lines.append("(none)")
            lines.append("")
            lines.append(f"Sign labels involved: {', '.join(row['sign_labels_involved']) or 'none'}")
            lines.append("")

    lines.append("## Criterion")
    lines.append("")
    lines.append(
        "Frozen in CHANGELOG \"Value transfer 1.0\": the toponym lexicon's 3= real "
        "count exceeds its null's 99th percentile in every (edition, banding, seed) "
        "cell; no wrong-control lexicon's real count exceeds its own null's 99th "
        "percentile anywhere, in either match class."
    )
    lines.append("")
    lines.append("| edition | banding | seed | lexicon | class | real > null p99 |")
    lines.append("|---|---|---|---|---|---|")
    toponyms_pass = True
    controls_fail_cells = []
    for edition in editions:
        for structure in structures:
            for seed in SEEDS:
                payload = all_results[(edition, seed)]
                for lex_name in lexicon_labels:
                    for match_class in ("3=", "4="):
                        row = _row_lookup(payload, structure, lex_name, match_class)
                        exceeds = row["real"] > row["null_p99"]
                        if lex_name == "knossos_toponyms" and match_class == "3=":
                            if not exceeds:
                                toponyms_pass = False
                        elif lex_name != "knossos_toponyms":
                            if exceeds:
                                controls_fail_cells.append(
                                    (edition, structure, seed, lex_name, match_class)
                                )
                        lines.append(
                            f"| {edition} | {structure_labels[structure]} | {seed} | "
                            f"{lexicon_labels[lex_name]} | {match_class} | {exceeds} |"
                        )
    lines.append("")
    lines.append(f"Toponyms clear the 99th percentile in 3= everywhere: {toponyms_pass}.")
    if controls_fail_cells:
        lines.append("Wrong controls that also clear the 99th percentile somewhere:")
        for cell in controls_fail_cells:
            lines.append(f"- {cell[3]}, {cell[4]}, {cell[0]}, {structure_labels[cell[1]]}, seed {cell[2]}")
    else:
        lines.append("No wrong control clears the 99th percentile anywhere.")
    lines.append("")
    criterion_met = toponyms_pass and not controls_fail_cells
    lines.append(f"Criterion met: {criterion_met}.")
    lines.append("")

    path.write_text("\n".join(lines))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--extra-word-types",
        type=str,
        default=None,
        help="path to a private JSONL of extra Linear A sign-label-tuple word "
        "types (CHANGELOG 'Supplement sensitivity (F-047)'); appended to the "
        "GORILA word-type set before any statistic runs. Without this option, "
        "behaviour and output are byte-identical to before the option existed.",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="write results files under this directory instead of results/ "
        "(e.g. results/supplement-sensitivity/), so a sensitivity rerun does "
        "not overwrite the frozen results files (F-041's toponym_test-*.json, "
        "toponym_test.md)",
    )
    parser.add_argument(
        "--edition",
        choices=["gorila", "sigla", "both"],
        default="both",
        help="restrict the run to one Linear A edition (CHANGELOG 'Supplement "
        "sensitivity' runs GORILA only); default both, matching every "
        "existing invocation byte-identically",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    editions = ("gorila", "sigla") if args.edition == "both" else (args.edition,)
    results = main(
        out_dir=args.results_dir,
        extra_word_types_path=args.extra_word_types,
        editions=editions,
    )
    for (edition, seed), payload in results.items():
        print(f"== {edition} seed {seed} ==")
        for structure_name, structure in payload["edition"]["band_structures"].items():
            print(f"  -- {structure_name} band_sizes={structure['band_sizes']}")
            for r in structure["rows"]:
                print(
                    f"     {r['lexicon']:<28} {r['match_class']:<3} real={r['real']:>3} "
                    f"null_mean={r['null_mean']:>6.2f} sd={r['null_sd']:>5.2f} "
                    f"p95={r['null_p95']:>5.1f} p99={r['null_p99']:>5.1f} "
                    f"real_pct={r['real_percentile']:>5.1f}"
                )
