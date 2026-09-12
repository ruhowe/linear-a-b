"""Lexicon loaders, one per hypothesis, behind a single interface.

A hypothesis needs a set of attested word-shapes to match Linear A against. Each loader
returns a ``semitic_null.lexicon.Lexicon``, which indexes consonantal skeletons by length
and can report how dense that space is.

**Every lexicon must be independent of the hypothesis it tests.** A dictionary assembled
to support a proposal cannot test it, which is the standing objection to the Uralic line
and the reason several registry entries are blocked rather than merely unimplemented.

Density differs enormously between languages and that is expected. Hebrew is
root-based, so 2,111 of 10,648 possible three-consonant skeletons are attested, about 20%.
Greek is not root-based and yields 662, well under 1%. Comparing raw match rates across
hypotheses would therefore measure lexicon shape rather than fit, which is why the harness
scores each hypothesis against its own permuted null instead.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from semitic_null.lexicon import Lexicon, load_lexicon  # noqa: E402

__all__ = [
    "LOADERS", "load_for", "strongs_hebrew", "greek_nt", "ugaritic_cuc", "akkadian_oracc",
    "hittite_kaikki", "sumerian_epsd2",
]

# Greek consonants to the same skeleton alphabet the Hebrew loader uses where the sounds
# correspond. Aspirates fold to their plain stop (θ→t, φ→p, χ→k) because the Aegean
# syllabary cannot write aspiration, so a reading could not distinguish them anyway.
GREEK_CONSONANTS: dict[str, str] = {
    "β": "b", "γ": "g", "δ": "d", "ζ": "z", "θ": "t", "κ": "k", "λ": "l",
    "μ": "m", "ν": "n", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "τ": "t",
    "φ": "p", "χ": "k",
}
# Double consonants expand, since the syllabary would write them as two signs.
GREEK_CLUSTERS: dict[str, str] = {"ξ": "ks", "ψ": "ps"}


def greek_skeleton(word: str) -> str:
    """Consonant skeleton of a Greek word, vowels and breathings discarded."""
    decomposed = unicodedata.normalize("NFD", word.lower())
    out: list[str] = []
    for char in decomposed:
        if char in GREEK_CLUSTERS:
            out.append(GREEK_CLUSTERS[char])
        elif char in GREEK_CONSONANTS:
            out.append(GREEK_CONSONANTS[char])
    return "".join(out)


def strongs_hebrew() -> Lexicon:
    """Strong's Hebrew, 8,674 entries. Public domain; JSON edition CC BY-SA."""
    return load_lexicon()


def greek_nt(*, min_len: int = 2, max_len: int = 5) -> Lexicon:
    """Koine Greek from the bundled Nestle 1904 New Testament, via pyaegean.

    25,187 word types. Chosen because it is bundled and offline, so the control runs
    without a fetch.

    Two limitations, both stated rather than hidden. Koine has lost the digamma, so a
    Linear A word containing the w-series can never match, which costs the Greek
    hypothesis a little. And Koine is roughly a thousand years later than Linear A, so
    this tests "looks like Greek" rather than "looks like Mycenaean Greek". Both make
    the control conservative, which is the right direction for a hypothesis we expect
    to fail.
    """
    import aegean

    corpus = aegean.load("nt")
    counts: Counter[str] = Counter()
    seen: set[str] = set()
    for doc in corpus.documents:
        for token in doc.tokens:
            text = (token.text or "").strip(".,·;:()[]’“”")
            if not text or not text[0].isalpha() or text in seen:
                continue
            seen.add(text)
            skeleton = greek_skeleton(text)
            if min_len <= len(skeleton) <= max_len:
                counts[skeleton] += 1

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=len(seen),
    )


# Archaic Greek, roughly 750 to 480 BC, which is as close to Mycenaean as a substantial
# readable corpus gets. Homer and Hesiod preserve formulaic vocabulary inherited from the
# Bronze Age, including place names in the Catalogue of Ships.
#
# The lyric poets are missing and their absence is a real gap: Perseus carries no Sappho,
# Alcaeus, Archilochus, Alcman or Anacreon under their own identifiers, because their
# fragments live in edited collections rather than as works. What remains is epic,
# didactic, hymnic, early philosophical and choral, which is a reasonable spread of
# register but light on everyday and personal vocabulary.
ARCHAIC_WORKS: dict[str, str] = {
    "tlg0012.tlg001": "Homer, Iliad",
    "tlg0012.tlg002": "Homer, Odyssey",
    "tlg0012.tlg003": "Homer, Epigrams",
    "tlg0020.tlg001": "Hesiod, Theogony",
    "tlg0020.tlg002": "Hesiod, Works and Days",
    "tlg0020.tlg003": "Hesiod, Shield",
    "tlg0233.tlg001": "Hipponax, fragment",
    "tlg1681.tlg001": "Solon",
    "tlg0626.tlg002": "Heraclitus, fragments",
    "tlg1562.tlg002": "Parmenides, fragments",
    "tlg1347.tlg004": "Epimenides, fragments",
    "tlg0579.tlg010": "Orphica, fragments",
    "tlg1304.tlg002": "Democritus, fragments",
    "tlg1596.tlg002": "Philolaus, fragments",
    "tlg0362.tlg001": "Carmina Delphis Inventa",
    "tlg0521.tlg008": "Epicharmus, fragments",
    "tlg2691.tlg002": "Musaeus Eleusinius, fragments",
    "tlg0033.tlg001": "Pindar, Olympian",
    "tlg0033.tlg002": "Pindar, Pythian",
    "tlg0033.tlg003": "Pindar, Nemean",
    "tlg0033.tlg004": "Pindar, Isthmian",
    "tlg0199.tlg001": "Bacchylides, Epinicians",
    "tlg0199.tlg002": "Bacchylides, Dithyrambs",
    **{f"tlg0013.tlg{i:03d}": f"Homeric Hymn {i}" for i in range(1, 34)},
}


def greek_archaic(*, min_len: int = 2, max_len: int = 5, cache: bool = True) -> Lexicon:
    """Archaic Greek: Homer, Hesiod, the Homeric Hymns, early philosophy and choral lyric.

    286,345 tokens and 53,026 word types over 56 works, against 137,745 and 25,187 for the
    Koine New Testament this replaced. Closer in date by roughly a thousand years, and a
    better test of the Greek hypothesis for that reason.

    Fetched from Perseus on first use, about 40 seconds, then cached as a skeleton list in
    ``~/.cache/linear-a-b/reference/``. The texts are CC BY-SA through pyaegean's
    commit-pinned Perseus mirror.
    """
    import json

    cache_path = Path.home() / ".cache" / "linear-a-b" / "reference" / "greek-archaic-skeletons.json"
    if cache and cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        counts = payload["counts"]
        n_entries = payload["n_entries"]
    else:
        import aegean
        from aegean import greek as greek_mod

        counts_c: Counter[str] = Counter()
        seen: set[str] = set()
        for work_id in ARCHAIC_WORKS:
            try:
                corpus = greek_mod.load_work(work_id)
            except Exception:
                continue  # a missing work weakens the lexicon, it does not invalidate it
            for doc in corpus.documents:
                for token in doc.tokens:
                    text = (token.text or "").strip(".,·;:()[]’“”—")
                    if not text or not text[0].isalpha() or text in seen:
                        continue
                    seen.add(text)
                    skeleton = greek_skeleton(text)
                    if min_len <= len(skeleton) <= max_len:
                        counts_c[skeleton] += 1
        counts = dict(counts_c)
        n_entries = len(seen)
        if cache:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps({"counts": counts, "n_entries": n_entries}), encoding="utf-8"
            )

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=counts,
        inventory=frozenset("".join(counts)),
        n_entries=n_entries,
    )


def greek_lsj(*, min_len: int = 2, max_len: int = 5) -> Lexicon:
    """Liddell-Scott-Jones headwords, via pyaegean's cached Perseus index.

    116,414 entries, 80,435 usable headwords, 19,891 distinct skeletons. Headwords rather
    than inflected forms, which puts it on the same footing as Strong's Hebrew (also a
    headword lexicon) and unlike the archaic running-text corpus. Coverage runs from
    Homer to the papyri, so it is broad and late; the two are different objects and both
    belong in the comparison. Perseus LSJ is CC BY-SA 4.0. Requires `greek.use_lsj()` to
    have built the index once (~270 MB download).
    """
    import gzip
    import json

    from aegean.data import cache_dir

    path = Path(cache_dir()) / "lsj-perseus-index.json.gz"
    if not path.exists():
        from aegean import greek as greek_mod

        greek_mod.use_lsj()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        index = json.load(fh)

    counts: Counter[str] = Counter()
    seen = 0
    for headword in index:
        if not any("Ͱ" <= c <= "Ͽ" or "ἀ" <= c <= "῿" for c in headword):
            continue
        skeleton = greek_skeleton(headword)
        if min_len <= len(skeleton) <= max_len:
            counts[skeleton] += 1
            seen += 1
    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)
    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=seen,
    )


# --- Ugaritic (Copenhagen Ugaritic Corpus) -------------------------------------------
#
# Source: DT-UCPH-cuc, v0.2.7 (Zenodo concept DOI 10.5281/zenodo.10695308), cached at
# ~/.cache/linear-a-b/reference/cuc/DT-UCPH-cuc-03a334e/lexicon_and_grammar/
# ugaritic_lexicon.txt. Zenodo's own badge says CC BY 4.0; the repo's own README states
# **CC BY-NC 4.0** ("License: CC BY-NC 4.0" badge, read 2026-09-11). The two disagree —
# recorded here as NC, the more restrictive of the two, per the corpus-sources.md
# invariant of treating disputed licensing conservatively.
#
# The file is a 4,996-entry DULAT-based lemma list, one headword per line, tab-separated:
# our-transliteration, DULAT lexeme, DULAT page, part of speech, gender, gloss, etymology.
# Column 1 (our-transliteration) is used here. Its own header comment gives the alphabet:
# a i u ʕ b d ḏ g ġ h ḫ ḥ k l m n p q r s ś š ṣ t ṯ ṭ w y z ẓ — the 30-sign Ugaritic
# abecedary. Ugaritic vowels are written only through three aleph glyphs (ʔa/ʔi/ʔu), so a
# bare a/i/u in this transliteration is never a free vowel: it always spells the aleph
# consonant, with a vowel quality the script happens to record alongside it. Root-pattern
# entries such as "/ʔ-b-d/" spell aleph with the literal ʔ glyph instead of a/i/u.
UGARITIC_CONSONANTS: dict[str, str] = {
    "a": "ʾ", "i": "ʾ", "u": "ʾ", "ʔ": "ʾ",  # three aleph-bearing signs + literal aleph
    "ʕ": "O", "ġ": "O",                       # ayin and ghayin both neutralise to ayin
    "ḥ": "H", "ḫ": "H",
    "ṭ": "T",
    "ẓ": "S", "ṣ": "S",
    "š": "C", "ś": "C", "ṯ": "C",
    "ḏ": "d",
    "b": "b", "g": "g", "d": "d", "h": "h", "w": "w", "z": "z", "y": "y",
    "k": "k", "l": "l", "m": "m", "n": "n", "s": "s", "p": "p", "q": "q",
    "r": "r", "t": "t",
}

UGARITIC_LEXICON_PATH = (
    Path.home() / ".cache" / "linear-a-b" / "reference" / "cuc" / "DT-UCPH-cuc-03a334e"
    / "lexicon_and_grammar" / "ugaritic_lexicon.txt"
)


def _ugaritic_skeleton(raw: str) -> str | None:
    """Consonant skeleton of one Copenhagen Ugaritic Corpus headword, or ``None`` to skip it.

    Skipped rather than guessed at, each documented and each small relative to the
    4,996-entry file:

    - **Damaged or reconstructed headwords** (containing ``[``, ``]``, ``*`` or ``?``):
      the visible letters are not the whole word, and a skeleton built from a partial or
      disputed reading is not a real attested form.
    - **Mid-word slash alternations** (167 of 4,996 entries, e.g. ``abḏ/šr``,
      ``aupš/ṯ(n)``): the source marks a disputed consonant or split without saying which
      reading is primary, and concatenating both sides would mint a form nobody attests.
    - **Colon-marked s/ś ambiguity** (16 entries, e.g. ``s:śdn``): ``s`` and ``ś`` fold to
      different skeleton symbols here (``s`` vs ``C``), so this one ambiguity cannot be
      resolved by folding through it.

    Kept: root-pattern entries such as ``/ʔ-b-d/``, where the enclosing slashes and
    internal hyphens are separators around a single reading, not an alternative.
    Roman-numeral homonym tags such as ``(II)`` disappear on their own, since I and V are
    not in the consonant map.
    """
    text = raw.strip()
    if not text:
        return None
    if any(marker in text for marker in "[]*?:"):
        return None
    is_root = text.startswith("/") and text.endswith("/") and text.count("/") == 2
    if "/" in text and not is_root:
        return None
    out = [UGARITIC_CONSONANTS[c] for c in text if c in UGARITIC_CONSONANTS]
    return "".join(out) if out else None


def ugaritic_cuc(*, min_len: int = 2, max_len: int = 5, path: str | Path | None = None) -> Lexicon:
    """Ugaritic headwords from the Copenhagen Ugaritic Corpus (DULAT-based lemma list).

    4,996 headwords in the source file; consonantal by construction, so no vowel-stripping
    step is needed the way Hebrew and Greek need one; the fold table above only collapses
    Ugaritic's finer sibilant and laryngeal distinctions onto the 22-symbol Hebrew-Semitic
    skeleton alphabet (`semitic_null.lexicon.HEBREW_CONSONANTS`) every Semitic-map lexicon
    in this repo shares. See `_ugaritic_skeleton` for what gets excluded and why.

    Licence: CC BY-NC 4.0 per the corpus repo's own README (see module-level note above).
    """
    src = Path(path) if path is not None else UGARITIC_LEXICON_PATH
    counts: Counter[str] = Counter()
    seen = 0
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        raw = cols[0].strip() if cols else ""
        if not raw:
            continue
        skel = _ugaritic_skeleton(raw)
        if skel is None:
            continue
        if min_len <= len(skel) <= max_len:
            counts[skel] += 1
            seen += 1

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=seen,
    )


# --- Akkadian (ORACC project glossaries) ----------------------------------------------
#
# Source: three ORACC project JSON exports, downloaded from
# http://oracc.museum.upenn.edu/json/<project>.zip into
# ~/.cache/linear-a-b/reference/oracc/<project>.zip — saao.zip (64 MB), rinap.zip (23 MB),
# ribo.zip (6.7 MB), all comfortably under the 200 MB skip threshold. Each zip carries
# <project>/gloss-akk.json, an Akkadian glossary of headword entries with a citation form
# (`cf`) and guide-word gloss (`gw`). ORACC's project-level `license` field for all three
# glossaries reads **"This data is released under the CC0 license"** (checked 2026-09-11
# from the JSON itself) — more permissive than the CC BY-SA 3.0 ORACC states as its
# general default, so CC0 is what is recorded and relied on here.
#
# `cf` is a normalised phonetic transcription (macrons for vowel length, š/ṣ/ṭ/ʾ for the
# consonants the Latin alphabet lacks), not a cuneiform transliteration — already exactly
# the "citation form" the task asks for. A handful of entries cite a Sumerogram instead of
# a phonetic Akkadian form (e.g. `AB2.GA`, `KAxKIB.U2`, `SUM.NINDA`) rather than a phonetic
# one; these are recognisable by a digit, subscript digit or `.` in `cf` (Sumerographic
# sign-name conventions) and are dropped rather than folded as if they were Akkadian
# phonemes. Capitalised entries without any digit/`.` (`Aššur`, `Anūtu`, `Addaru`) are kept
# — real Akkadian proper nouns, not logograms, capitalised only because they are names.
AKKADIAN_CONSONANTS: dict[str, str] = {
    "ʾ": "ʾ",
    # This dataset's `cf` field spells ḫ as plain ASCII "h" throughout (verified: the
    # diacritic ḫ character never appears in any of the three glossaries' `cf` values).
    # Akkadian has no plain /h/ phoneme, so every "h" here is ḫ; folded to "H" per the
    # ḫ→H rule, same target symbol Hebrew ḥ uses (the two merge in Akkadian historically).
    "h": "H", "ḫ": "H",
    "ṣ": "S",
    "ṭ": "T",
    "š": "C",
    "b": "b", "d": "d", "g": "g", "k": "k", "l": "l", "m": "m", "n": "n",
    "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "w": "w", "y": "y", "z": "z",
}

ORACC_DIR = Path.home() / ".cache" / "linear-a-b" / "reference" / "oracc"
ORACC_PROJECTS: tuple[str, ...] = ("saao", "rinap", "ribo")

_ORACC_LOGOGRAM_RE = re.compile(r"[0-9.₀-₉]")


def _akkadian_skeleton(cf: str) -> str | None:
    """Consonant skeleton of one ORACC citation form, or ``None`` for a Sumerogram entry.

    Deliberately **not** run through NFD decomposition, unlike the Hebrew and Ugaritic
    skeleton functions. Hebrew vowel points are separate combining characters already, so
    decomposing only strips them. Here the diacritics are load-bearing on precomposed
    Latin letters: š/ṣ/ṭ/ḫ NFD-decompose to a bare s/s/t/h plus a combining caron or dot-
    or-macron-below, which would silently collapse š and ṣ onto plain s (and ṭ onto plain
    t) instead of folding them to C/S/T as intended. Operating on the precomposed string
    keeps š, ṣ, ṭ, ḫ, ʾ intact as single lookup keys. Vowels still fall away correctly
    either way: ā/ē/ī/ū/â/ê/î/û are precomposed codepoints of their own, absent from
    `AKKADIAN_CONSONANTS`, so a plain membership test drops them without decomposing
    anything.
    """
    if not cf or _ORACC_LOGOGRAM_RE.search(cf):
        return None
    out = [AKKADIAN_CONSONANTS[c] for c in cf.lower() if c in AKKADIAN_CONSONANTS]
    return "".join(out) if out else None


def akkadian_oracc(
    *,
    min_len: int = 2,
    max_len: int = 5,
    projects: tuple[str, ...] = ORACC_PROJECTS,
    oracc_dir: str | Path | None = None,
) -> Lexicon:
    """Akkadian citation forms unioned across three ORACC project glossaries.

    Projects: SAAO (Neo-Assyrian/Neo-Babylonian royal and scholarly correspondence), RINAP
    (Neo-Assyrian royal inscriptions), RIBo (Babylonian royal inscriptions). Deduped on
    (citation form, guide word) across all three, so the same word attested in more than
    one project counts once, and two entries sharing a citation form but glossed
    differently (distinct senses) both count, matching the "distinct headword/lemma" rule
    every other loader in this module follows. Licence: CC0, see module-level note above.

    Period note (2026-09-11). saao, rinap and ribo are Neo-Assyrian and Babylonian royal
    inscriptions of the first millennium BC, not the Old Babylonian contemporary with Linear
    A. Citation forms are dictionary lemmas, so the lexical stock is largely shared across
    periods, but the register is royal and military. Treat this as first-millennium
    Akkadian, and do not describe it as contemporary with the Minoan palaces.
    """
    root = Path(oracc_dir) if oracc_dir is not None else ORACC_DIR
    seen_pairs: set[tuple[str, str]] = set()
    counts: Counter[str] = Counter()
    seen = 0
    for project in projects:
        with zipfile.ZipFile(root / f"{project}.zip") as zf:
            with zf.open(f"{project}/gloss-akk.json") as fh:
                data = json.load(fh)
        for entry in data.get("entries", []):
            cf = (entry.get("cf") or "").strip()
            gw = (entry.get("gw") or "").strip()
            if not cf:
                continue
            key = (cf, gw)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            skel = _akkadian_skeleton(cf)
            if skel is None:
                continue
            if min_len <= len(skel) <= max_len:
                counts[skel] += 1
                seen += 1

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=seen,
    )


# --- Hittite (kaikki.org Wiktionary extract) -------------------------------------------
#
# Source: https://kaikki.org/dictionary/Hittite/kaikki.org-dictionary-Hittite.jsonl,
# downloaded to ~/.cache/linear-a-b/reference/kaikki-hittite.jsonl. This is a Wiktionary
# extract (the kaikki.org project machine-parses Wiktionary dumps into JSONL), so
# coverage is whatever Wiktionary editors happened to add: 481 entries total, thin next
# to a real Hittite dictionary (HED, CHD run to tens of thousands of words), and Old,
# Middle and New Hittite forms are mixed together with no period tagging in this export.
# Licence: Wiktionary text is CC BY-SA 4.0 (kaikki.org states this is preserved from the
# Wiktionary source), same family as the Ugaritic and SigLA data already in this repo.
#
# Most entries carry a cuneiform "word" (Hittite is normally written in cuneiform, and
# most of this file's headwords are given that way). A minority — 67 of 481, measured
# 2026-09-11 — have a Latin-script "word" instead: overwhelmingly pos == "romanization"
# entries, whose gloss reads "Broad transcription of <cuneiform>", plus one stray pos ==
# "noun" entry ("šākuwan") that also happens to give a Latin headword. Latin-script is
# detected directly (no character in the Cuneiform or Cuneiform Numbers Unicode blocks,
# U+12000-U+1254F) rather than by trusting the pos field, so that stray case is not missed.
# All 67 are distinct; no deduplication was needed.
HITTITE_CONSONANTS: dict[str, str] = {
    "s": "s", "š": "s",  # š merges onto plain s; the two are not distinguished downstream
    "z": "z",
    "t": "t", "d": "d", "k": "k", "g": "g", "p": "p", "b": "b",
    "l": "l", "m": "m", "n": "n", "r": "r", "w": "w", "y": "y",
}
HITTITE_VOWELS = frozenset("aeiuāēīū")  # macron vowels included: stripped, then dropped
HITTITE_LARYNGEAL = "ḫ"

KAIKKI_HITTITE_PATH = Path.home() / ".cache" / "linear-a-b" / "reference" / "kaikki-hittite.jsonl"

_CUNEIFORM_RE = re.compile("[\U00012000-\U0001254f]")


def _hittite_is_latin(word: str) -> bool:
    """True if `word` has no character in the Cuneiform / Cuneiform Numbers blocks."""
    return bool(word) and not _CUNEIFORM_RE.search(word)


def _hittite_skeleton(raw: str) -> str | None:
    """Consonant skeleton of one Hittite Latin-script headword, or ``None`` to skip it.

    Mapped onto the Greek map's skeleton alphabet (`phonologies.SERIES_TO_GREEK`: b d g
    k l m n p r s t w z), which has no laryngeal or sibilant-emphatic slots, unlike the
    Semitic map's. Rules, applied in order:

    - Any uppercase letter (Sumerograms/Akkadograms spelled with Hittite phonetic
      complements, e.g. ``LUGAL``-ma-, and the one proper name in this list,
      ``Tarḫuntaš``) skips the whole headword.
    - Hyphens, ``=`` (clitic boundary), spaces, and any superscript character (the
      determinative convention in fuller transliterations, e.g. superscript ``d`` for a
      divine determinative) are removed before the letters are read. None of those
      appear in this particular headword list, but the rule is general rather than
      fitted to what happens to be present.
    - Macron vowels (ā ē ī ū) lose the macron and then, like plain a/e/i/u, are dropped:
      Hittite vowel quantity and quality are not something a Linear A/B sign can encode.
    - **ḫ is dropped outright, not folded to anything.** This is a known limitation, not
      an oversight: the Greek map's alphabet (b d g k l m n p r s t w z) has no laryngeal
      symbol at all, unlike the Semitic map's H. A Hittite word built partly out of ḫ
      therefore contributes a shorter, laryngeal-blind skeleton, which is conservative
      (it can only make Hittite words look more like other things, never less) but is
      real information loss and should be named as such wherever this lexicon is used.
    - š folds to s (the two are not distinguished in the output alphabet); z stays z;
      t d k g p b l m n r s w y pass through letter for letter.
    - Any other character (parentheses marking an optional/variant spelling, e.g.
      ``ašānz(a)``, is the one case in this list) skips the headword: guessing which
      variant is "the" word would mint a form nobody attests, the same reasoning
      `_ugaritic_skeleton` applies to slash alternations.
    """
    if not raw or any(c.isupper() for c in raw):
        return None
    text = raw.replace("-", "").replace("=", "").replace(" ", "")
    text = "".join(c for c in text if not ("⁰" <= c <= "₟" or c == "°"))
    out: list[str] = []
    for ch in text:
        if ch in HITTITE_VOWELS:
            continue
        if ch == HITTITE_LARYNGEAL:
            continue
        mapped = HITTITE_CONSONANTS.get(ch)
        if mapped is None:
            return None
        out.append(mapped)
    return "".join(out) if out else None


def hittite_kaikki(*, min_len: int = 2, max_len: int = 5, path: str | Path | None = None) -> Lexicon:
    """Hittite Latin-script headwords from the kaikki.org Wiktionary extract.

    481 entries in the source file; 67 carry a Latin-script (rather than cuneiform)
    headword, all distinct. Wiktionary-derived, so coverage is uneven and not a
    substitute for a real Hittite dictionary; Old, Middle and New Hittite forms are
    mixed with no period tagging available in this export. Licence: CC BY-SA (inherited
    from Wiktionary; see module-level note above). Runs only under the Greek map: see
    `_hittite_skeleton` for the folding rules, and note in particular that ḫ is dropped
    rather than mapped, because the Greek map's alphabet has no laryngeal symbol.
    """
    src = Path(path) if path is not None else KAIKKI_HITTITE_PATH
    counts: Counter[str] = Counter()
    seen_words: set[str] = set()
    seen = 0
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            word = (entry.get("word") or "").strip()
            if not word or not _hittite_is_latin(word) or word in seen_words:
                continue
            seen_words.add(word)
            skel = _hittite_skeleton(word)
            if skel is None:
                continue
            if min_len <= len(skel) <= max_len:
                counts[skel] += 1
                seen += 1

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=seen,
    )


# --- Sumerian (ORACC epsd2/literary glossary) ------------------------------------------
#
# Source: http://oracc.museum.upenn.edu/json/epsd2-literary.zip, downloaded to
# ~/.cache/linear-a-b/reference/oracc/epsd2-literary.zip (39.5 MB). It carries
# epsd2/literary/gloss-sux.json, the Old Babylonian literary-corpus Sumerian glossary
# (3,605 entries), so the epsd2.zip fallback mentioned in the brief (213 MB, the full
# epsd2 project) was not needed. The JSON's own `license` field reads **"This data is
# released under the CC0 license"** (checked 2026-09-11), same as the three Akkadian
# ORACC glossaries above.
#
# `cf` is the citation form and `gw` the guide word, same shape as the Akkadian entries.
# Every one of the 3,605 entries carries a non-empty `cf`, and (cf, gw) pairs are already
# unique in this file (measured: 3,605 entries, 3,605 distinct pairs), but the dedup is
# still applied for parity with `akkadian_oracc` and in case that stops holding on a
# future re-download.
#
# ORACC's own convention for Sumerian citation forms uses UPPERCASE sign names in place
# of a phonetic reading precisely where the reading is uncertain or the word is a
# multi-sign compound cited by its component signs (``AB×A``, ``ad.KID``, ``DAG.KISIM₅×AB₂``),
# plus ``.``, ``@``, ``×``, ``&`` and a literal space as compound/variant markup. All of
# that is logographic or notational rather than a phonetic Sumerian reading, so (per the
# uppercase/punctuation skip rule below) none of it is folded. Measured: 741 of the 3,605
# entries are skipped for exactly this reason, leaving 2,428 with a length-2-to-5 skeleton.
SUMERIAN_CONSONANTS: dict[str, str] = {
    "s": "s", "š": "s",  # š merges onto plain s, as for Hittite
    "z": "z",
    "t": "t", "d": "d", "k": "k", "g": "g", "p": "p", "b": "b",
    "l": "l", "m": "m", "n": "n", "r": "r", "w": "w",
}
SUMERIAN_VOWELS = frozenset("aeiu")
SUMERIAN_LARYNGEALS = frozenset("hḫ")  # ḫ, or plain ASCII h as this dataset spells it
SUMERIAN_DIGITS = frozenset("0123456789₀₁₂₃₄₅₆₇₈₉")  # index numbers, subscript or plain

EPSD2_LITERARY_ZIP = (
    Path.home() / ".cache" / "linear-a-b" / "reference" / "oracc" / "epsd2-literary.zip"
)
EPSD2_GLOSS_SUX_MEMBER = "epsd2/literary/gloss-sux.json"


def _sumerian_skeleton(raw: str) -> str | None:
    """Consonant skeleton of one Sumerian citation form, or ``None`` to skip it.

    Folds onto the same Greek-map alphabet as `_hittite_skeleton` (b d g k l m n p r s
    t w z), by the same reasoning: no laryngeal or sibilant-emphatic slot exists in it.

    - Any uppercase letter, or any of ``. @ × & %`` or a literal space (ORACC's own
      compound/uncertain-reading markup, see the module note above), skips the headword
      rather than guessing which component is "the" reading.
    - Index digits, plain or subscript (``du₃``, ``gu4``), are dropped: they number
      homophonous citation forms and carry no consonant of their own.
    - a e i u are dropped, matching every other vowel-stripping loader in this module.
    - ŋ (also spelled ĝ or g̃ in some transliteration systems, normalised to ŋ first)
      folds to g, since the Greek map's alphabet has no separate velar nasal slot.
    - **ḫ, or plain ASCII h as this particular dataset spells it, is dropped outright**,
      the same known limitation `_hittite_skeleton` documents: the Greek map's alphabet
      has no laryngeal symbol to fold it onto.
    - š folds to s; z stays z; y is dropped (a glide, not in the target alphabet); b d g
      k l m n p r s t w pass through letter for letter.
    - ʾ (the glottal-stop/aleph mark some transliterations use for vowel hiatus, e.g.
      ``aʾa``) is not in any rule given for this loader and is therefore treated as a
      character outside the defined set: it skips the headword rather than being folded
      or silently dropped. 129 of the 3,605 entries carry it. This is a narrower reading
      than `_hittite_skeleton`'s ḫ-drop and is flagged here because the two could
      reasonably be treated the same way; this loader does not, so the count is lower
      than dropping ʾ would give.
    """
    if not raw or any(c.isupper() for c in raw):
        return None
    text = unicodedata.normalize("NFC", raw).replace("g̃", "ŋ").replace("ĝ", "ŋ")
    out: list[str] = []
    for ch in text:
        if ch in SUMERIAN_DIGITS:
            continue
        if ch in SUMERIAN_VOWELS:
            continue
        if ch == "ŋ":
            out.append("g")
            continue
        if ch in SUMERIAN_LARYNGEALS:
            continue
        if ch == "y":
            continue
        mapped = SUMERIAN_CONSONANTS.get(ch)
        if mapped is None:
            return None  # e.g. ʾ, or ORACC compound markup that slipped past the uppercase check
        out.append(mapped)
    return "".join(out) if out else None


def sumerian_epsd2(
    *, min_len: int = 2, max_len: int = 5, zip_path: str | Path | None = None
) -> Lexicon:
    """Sumerian citation forms from the ORACC epsd2/literary glossary (Old Babylonian
    literary corpus).

    3,605 entries, all with a non-empty citation form; deduped on (cf, gw) as
    `akkadian_oracc` is, though no duplicate currently exists in this file. Licence: CC0
    per the JSON's own `license` field (see module-level note above). Runs only under
    the Greek map: see `_sumerian_skeleton` for the folding rules, and note in
    particular that ḫ/h is dropped rather than mapped, for the same reason Hittite's ḫ
    is dropped, and that ʾ is treated as out-of-alphabet rather than folded onto
    anything, unlike ḫ.
    """
    src = Path(zip_path) if zip_path is not None else EPSD2_LITERARY_ZIP
    with zipfile.ZipFile(src) as zf:
        with zf.open(EPSD2_GLOSS_SUX_MEMBER) as fh:
            data = json.load(fh)

    seen_pairs: set[tuple[str, str]] = set()
    counts: Counter[str] = Counter()
    seen = 0
    for entry in data.get("entries", []):
        cf = (entry.get("cf") or "").strip()
        gw = (entry.get("gw") or "").strip()
        if not cf:
            continue
        key = (cf, gw)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        skel = _sumerian_skeleton(cf)
        if skel is None:
            continue
        if min_len <= len(skel) <= max_len:
            counts[skel] += 1
            seen += 1

    by_length: dict[int, set[str]] = {}
    for skeleton in counts:
        by_length.setdefault(len(skeleton), set()).add(skeleton)

    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=seen,
    )


LOADERS = {
    "strongs_hebrew": strongs_hebrew,
    "greek_lexicon": greek_archaic,
    "greek_archaic": greek_archaic,
    "greek_koine": greek_nt,
    "greek_lsj": greek_lsj,
    "ugaritic_cuc": ugaritic_cuc,
    "akkadian_oracc": akkadian_oracc,
    "hittite_kaikki": hittite_kaikki,
    "sumerian_epsd2": sumerian_epsd2,
}


def load_for(loader_name: str | None) -> Lexicon | None:
    """Resolve a registry ``lexicon.loader`` name. ``None`` when the hypothesis is blocked."""
    if not loader_name or loader_name == "none":
        return None
    loader = LOADERS.get(loader_name)
    if loader is None:
        raise KeyError(f"No lexicon loader registered for {loader_name!r}")
    return loader()
