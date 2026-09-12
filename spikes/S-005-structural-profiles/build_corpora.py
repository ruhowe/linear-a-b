#!/usr/bin/env python3
"""S-005: build the private respelled reference corpora (spikes/S-005-structural-profiles/BRIEF.md).

Every source is turned into a set (or, for Greek, an ordered stream) of
**word types spelled as Linear-B-style open CV syllables** -- a tuple of sign
labels like ``("PE", "MA")`` -- so that ``run.py`` can hand them straight to
``src/kober`` exactly as it does Linear A and Linear B word types. Nothing
here is a real Linear B sign label: these are invented syllable identities
(one string per onset-consonant/vowel combination), so the medial channel's
consonant-sharing check (which consults ``kober.values.consonant_of``,
genuine Ventris values) is never run on them -- ``run.py`` only reads
``pair_count`` from the medial channel, never the consonant fraction.

Output, all outside the repo (corpus-sources.md Invariants -- never commit
fetched or derived corpus data):

- ``~/.cache/linear-a-b/reference/s005/RESPELLING.md`` -- every respelling
  rule, written down once, in prose, per spikes/README.md rule 6 (aggregate
  only in the repo; the rules themselves are not corpus content, but the
  brief asks that even the rule statements live beside the corpora, not in
  the repo, so they travel with the data they describe).
- ``~/.cache/linear-a-b/reference/s005/<name>.json`` -- one file per
  reference: metadata (source, licence, counts, order-model) plus either
  ``types`` (a dictionary source: an unordered list of sign-tuples) or
  ``token_stream`` (an ordered source: the full respelled stream, word by
  word, in reading order, so ``run.py`` can cut contiguous chunks from it).

Run: ``.venv/bin/python spikes/S-005-structural-profiles/build_corpora.py``
(rebuilds everything; ``--only greek,hittite`` for a subset).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hypotheses.lexicons import (  # noqa: E402
    AKKADIAN_CONSONANTS,
    GREEK_CLUSTERS,
    GREEK_CONSONANTS,
    HITTITE_CONSONANTS,
    HITTITE_LARYNGEAL,
    HITTITE_VOWELS,
    KAIKKI_HITTITE_PATH,
    ORACC_DIR,
    SUMERIAN_CONSONANTS,
    SUMERIAN_DIGITS,
    SUMERIAN_LARYNGEALS,
    SUMERIAN_VOWELS,
    UGARITIC_CONSONANTS,
    UGARITIC_LEXICON_PATH,
    _CUNEIFORM_RE,
    _hittite_is_latin,
    _ORACC_LOGOGRAM_RE,
    _ugaritic_skeleton,
)

REFERENCE_DIR = Path.home() / ".cache" / "linear-a-b" / "reference"
OUT_DIR = REFERENCE_DIR / "s005"
ETRUSCAN_DIR = REFERENCE_DIR / "etruscan"
ETRUSCAN_KAIKKI_URL = "https://kaikki.org/dictionary/Etruscan/kaikki.org-dictionary-Etruscan.jsonl"
ETRUSCAN_KAIKKI_PATH = ETRUSCAN_DIR / "kaikki-etruscan.jsonl"
_OLD_ITALIC_RE = re.compile("[\U00010300-\U0001032F]")

Word = tuple[str, ...]

# --------------------------------------------------------------------------- #
# The shared open-syllable respelling core -- the "coda rule".
# --------------------------------------------------------------------------- #


def syllabify(phonemic: list[tuple[str, bool]]) -> Word | None:
    """``phonemic``: a sequence of ``(letter, is_vowel)`` pairs already folded
    onto one language's own consonant/vowel alphabet (see each
    ``*_phonemic`` function below). Produces the open-syllable spelling a
    CV syllabary like Linear B's would give it:

    - **Cluster simplification.** A run of consonants before a vowel
      contributes only its *last* member (the one adjacent to the vowel);
      earlier consonants in the cluster are dropped, exactly as Mycenaean
      spelling drops them (``sperma`` -> ``pe-ma``, not ``spe-ma`` or
      ``se-pe-ma``).
    - **Coda drop.** A consonant with no following vowel at all -- a
      word-final cluster -- is dropped outright, no echo vowel. This is
      the brief's own stated simplification and is coarser than real
      Mycenaean orthography, which sometimes echoes a final stop with a
      copy of the preceding vowel (``wanaks`` -> ``wa-na-ka``, not
      ``wa-na``); the coarser rule is what was asked for and is applied
      identically to every language, so the coarsening cannot favour one
      language over another.
    - **Diphthong collapse.** A run of consecutive vowels keeps only the
      first; Linear B does not write the off-glide of a diphthong.

    Returns ``None`` for an empty result (e.g. a word of pure, unwritable
    consonants).
    """
    syllables: list[str] = []
    pending_consonant: str | None = None
    prev_was_vowel = False
    for letter, is_vowel in phonemic:
        if is_vowel:
            if prev_was_vowel:
                continue
            syllables.append((pending_consonant or "") + letter)
            pending_consonant = None
            prev_was_vowel = True
        else:
            pending_consonant = letter
            prev_was_vowel = False
    if not syllables:
        return None
    return tuple(s.upper() for s in syllables)


def finalize(words: set[Word], min_signs: int = 2) -> set[Word]:
    """Drop words of fewer than ``min_signs`` syllables (kober.words's own
    "words of one sign are dropped" rule, A-035) -- applied here rather than
    left to the caller, so every cached corpus is already in kober's shape."""
    return {w for w in words if len(w) >= min_signs}


# --------------------------------------------------------------------------- #
# Greek -- Homer's Iliad, Perseus via pyaegean. Has real reading order.
# --------------------------------------------------------------------------- #

GREEK_VOWELS = frozenset("αειουηω")


def greek_phonemic(word: str) -> list[tuple[str, bool]] | None:
    decomposed = unicodedata.normalize("NFD", word.lower())
    out: list[tuple[str, bool]] = []
    for ch in decomposed:
        if ch in GREEK_VOWELS:
            out.append((ch, True))
        elif ch in GREEK_CLUSTERS:
            for c in GREEK_CLUSTERS[ch]:
                out.append((c, False))
        elif ch in GREEK_CONSONANTS:
            out.append((GREEK_CONSONANTS[ch], False))
        # else: combining accent/breathing/iota-subscript mark, or a
        # character outside the 24-letter alphabet -- skipped, as
        # lexicons.greek_skeleton also skips them.
    return out or None


def build_greek() -> dict:
    import aegean.greek as greek
    from aegean.core.model import TokenKind

    corpus = greek.load_work("tlg0012.tlg001")
    stream: list[Word] = []
    n_tokens = 0
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD:
                continue
            n_tokens += 1
            phon = greek_phonemic(tok.text or "")
            if phon is None:
                continue
            word = syllabify(phon)
            if word is not None and len(word) >= 2:
                stream.append(word)
    return {
        "language": "greek_iliad",
        "role": "positive control: Greek respelled by the A-005 coda rule, beside real Linear B",
        "source": "Homer, Iliad, via aegean.greek.load_work('tlg0012.tlg001') (Perseus canonical-greekLit)",
        "url": "https://github.com/PerseusDL/canonical-greekLit",
        "licence": "CC BY-SA 4.0 (Perseus Digital Library standard terms)",
        "ordered": True,
        "n_source_tokens": n_tokens,
        "n_stream_words": len(stream),
        "n_distinct_types": len(set(stream)),
        "token_stream": [list(w) for w in stream],
    }


# --------------------------------------------------------------------------- #
# Hittite -- kaikki.org Wiktionary extract. Dictionary; no reading order.
# --------------------------------------------------------------------------- #

_MACRON_FOLD = {"ā": "a", "ē": "e", "ī": "i", "ū": "u"}


def hittite_phonemic(raw: str) -> list[tuple[str, bool]] | None:
    if not raw or any(c.isupper() for c in raw):
        return None
    text = raw.replace("-", "").replace("=", "").replace(" ", "")
    text = "".join(c for c in text if not ("⁰" <= c <= "₟" or c == "°"))
    out: list[tuple[str, bool]] = []
    for ch in text:
        ch_plain = _MACRON_FOLD.get(ch, ch)
        if ch_plain in HITTITE_VOWELS or ch_plain in "aeiu":
            out.append((ch_plain, True))
            continue
        if ch == HITTITE_LARYNGEAL:
            # Laryngeal: no series in this synthetic CV syllabary (it has
            # none either, matching Linear B's own lack of one) -- dropped
            # without leaving a coda trace, same treatment every other
            # dropped consonant gets.
            continue
        mapped = HITTITE_CONSONANTS.get(ch)
        if mapped is None:
            return None  # unmapped character (stray IPA, punctuation): skip whole word
        out.append((mapped, False))
    return out or None


def build_hittite() -> dict:
    types: set[Word] = set()
    n_raw = 0
    n_entries = 0
    with KAIKKI_HITTITE_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("pos") == "character":
                continue  # a Sumerogram/Akkadogram logogram entry, not a Hittite word
            n_entries += 1
            for f in entry.get("forms", []) or []:
                w = (f.get("form") or "").strip()
                if not w or not _hittite_is_latin(w) or _CUNEIFORM_RE.search(w):
                    continue
                if "(" in w or ")" in w:
                    continue  # optional/variant spelling marker
                n_raw += 1
                phon = hittite_phonemic(w)
                if phon is None:
                    continue
                word = syllabify(phon)
                if word is not None:
                    types.add(word)
    types = finalize(types)
    return {
        "language": "hittite_kaikki",
        "role": "reference: Anatolian, cuneiform syllabary via Latin transliteration",
        "source": "kaikki.org Wiktionary extract for Hittite",
        "url": "https://kaikki.org/dictionary/Hittite/",
        "licence": "CC BY-SA 4.0 (inherited from Wiktionary)",
        "ordered": False,
        "n_source_entries": n_entries,
        "n_raw_latin_forms": n_raw,
        "n_distinct_types": len(types),
        "types": [list(w) for w in sorted(types)],
    }


# --------------------------------------------------------------------------- #
# Akkadian -- ORACC saao/rinap/ribo glossaries. Dictionary; no reading order.
# --------------------------------------------------------------------------- #

_AKK_MACRON_FOLD = {"ā": "a", "ē": "e", "ī": "i", "ū": "u", "â": "a", "ê": "e", "î": "i", "û": "u"}
_AKKADIAN_VOWELS = frozenset("aeiu")


def akkadian_phonemic(cf: str) -> list[tuple[str, bool]] | None:
    if not cf or _ORACC_LOGOGRAM_RE.search(cf) or " " in cf:
        return None
    out: list[tuple[str, bool]] = []
    for ch in cf.lower():
        ch_plain = _AKK_MACRON_FOLD.get(ch, ch)
        if ch_plain in _AKKADIAN_VOWELS:
            out.append((ch_plain, True))
            continue
        if ch in ("h", "ḫ", "ʾ"):
            # Laryngeal/glottal: dropped, same reasoning as Hittite's ḫ and
            # Sumerian's ḫ/h below -- no series in this synthetic syllabary.
            continue
        mapped = AKKADIAN_CONSONANTS.get(ch)
        if mapped is None:
            return None  # unmapped character: skip whole word, same rule as Hittite/Sumerian
        out.append((mapped, False))
    return out or None


def build_akkadian(projects: tuple[str, ...] = ("saao", "rinap", "ribo")) -> dict:
    types: set[Word] = set()
    seen_pairs: set[tuple[str, str]] = set()
    n_raw = 0
    for project in projects:
        zip_path = ORACC_DIR / f"{project}.zip"
        if not zip_path.exists():
            continue
        with zipfile.ZipFile(zip_path) as zf:
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
            n_raw += 1
            phon = akkadian_phonemic(cf)
            if phon is None:
                continue
            word = syllabify(phon)
            if word is not None:
                types.add(word)
    types = finalize(types)
    return {
        "language": "akkadian_oracc",
        "role": "reference: Semitic, cuneiform syllabary, citation-form transliteration",
        "source": "ORACC saao + rinap + ribo project glossaries (gloss-akk.json)",
        "url": "http://oracc.museum.upenn.edu",
        "licence": "CC0 (per each project's own license field)",
        "period_note": (
            "First-millennium BC Neo-Assyrian/Neo-Babylonian royal and scholarly registers, "
            "not the Old Babylonian period contemporary with the Minoan palaces (see lexicons.py)."
        ),
        "ordered": False,
        "n_raw_entries_deduped": n_raw,
        "n_distinct_types": len(types),
        "types": [list(w) for w in sorted(types)],
    }


# --------------------------------------------------------------------------- #
# Sumerian -- ORACC epsd2/literary glossary. Dictionary; no reading order.
# --------------------------------------------------------------------------- #


def sumerian_phonemic(raw: str) -> list[tuple[str, bool]] | None:
    if not raw or any(c.isupper() for c in raw):
        return None
    text = unicodedata.normalize("NFC", raw).replace("g̃", "ŋ").replace("ĝ", "ŋ")
    out: list[tuple[str, bool]] = []
    for ch in text:
        if ch in SUMERIAN_DIGITS:
            continue
        if ch in SUMERIAN_VOWELS:
            out.append((ch, True))
            continue
        if ch == "ŋ":
            out.append(("g", False))
            continue
        if ch in SUMERIAN_LARYNGEALS:
            continue  # ḫ/h: no laryngeal series here, same as Hittite/Akkadian
        if ch == "y":
            continue  # glide, dropped as the skeleton function also drops it
        mapped = SUMERIAN_CONSONANTS.get(ch)
        if mapped is None:
            return None  # e.g. ʾ, or stray compound markup
        out.append((mapped, False))
    return out or None


def build_sumerian() -> dict:
    zip_path = ORACC_DIR / "epsd2-literary.zip"
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open("epsd2/literary/gloss-sux.json") as fh:
            data = json.load(fh)
    types: set[Word] = set()
    seen_pairs: set[tuple[str, str]] = set()
    n_raw = 0
    for entry in data.get("entries", []):
        cf = (entry.get("cf") or "").strip()
        gw = (entry.get("gw") or "").strip()
        if not cf:
            continue
        key = (cf, gw)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        n_raw += 1
        phon = sumerian_phonemic(cf)
        if phon is None:
            continue
        word = syllabify(phon)
        if word is not None:
            types.add(word)
    types = finalize(types)
    return {
        "language": "sumerian_epsd2",
        "role": "reference: language isolate, cuneiform syllabary, citation-form transliteration",
        "source": "ORACC epsd2/literary glossary (Old Babylonian literary corpus)",
        "url": "http://oracc.org/epsd2/literary",
        "licence": "CC0 (per the file's own license field)",
        "ordered": False,
        "n_raw_entries_deduped": n_raw,
        "n_distinct_types": len(types),
        "types": [list(w) for w in sorted(types)],
    }


# --------------------------------------------------------------------------- #
# Ugaritic -- Copenhagen Ugaritic Corpus lemma list. Consonantal alphabet.
# The weakest reference: vocalised by an invented, stated rule.
# --------------------------------------------------------------------------- #

_UGARITIC_ALEPH_VOWELS = {"a": "a", "i": "i", "u": "u"}


def ugaritic_phonemic(raw: str) -> list[tuple[str, bool]] | None:
    """Vocalise one Ugaritic headword: insert the vowel /a/ after every plain
    consonant, since the script marks no vowel except through the three
    aleph glyphs (a/i/u), which are read here as self-contained vowel
    syllables carrying their own vowel quality. Root-pattern entries
    (``/ʔ-b-d/``) have their slashes and hyphens stripped first, per
    ``lexicons._ugaritic_skeleton``'s own reading of that notation."""
    text = raw.strip()
    is_root = text.startswith("/") and text.endswith("/") and text.count("/") == 2
    if is_root:
        text = text.strip("/").replace("-", "")
    out: list[tuple[str, bool]] = []
    for ch in text:
        if ch in _UGARITIC_ALEPH_VOWELS:
            out.append((_UGARITIC_ALEPH_VOWELS[ch], True))
            continue
        mapped = UGARITIC_CONSONANTS.get(ch)
        if mapped is None:
            continue  # punctuation etc., already excluded at the whole-word level
        out.append((mapped, False))
        out.append(("a", True))  # the stated vocalisation rule
    return out or None


def build_ugaritic() -> dict:
    types: set[Word] = set()
    n_raw = 0
    n_kept = 0
    for line in UGARITIC_LEXICON_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        raw = cols[0].strip() if cols else ""
        if not raw:
            continue
        n_raw += 1
        if _ugaritic_skeleton(raw) is None:
            continue  # reuse the same exclusion rules (damaged/reconstructed,
            # mid-word slash alternation, colon-marked ambiguity)
        n_kept += 1
        phon = ugaritic_phonemic(raw)
        if phon is None:
            continue
        word = syllabify(phon)
        if word is not None:
            types.add(word)
    types = finalize(types)
    return {
        "language": "ugaritic_cuc",
        "role": "reference: WEAKEST -- consonantal alphabet, vocalised by an invented rule, not a real spelling",
        "source": "Copenhagen Ugaritic Corpus (CACCHT project), DULAT-based lemma list",
        "url": "https://github.com/DT-UCPH/cuc (Zenodo DOI 10.5281/zenodo.10695308)",
        "licence": "CC BY-NC 4.0 (per the corpus repo's own README)",
        "ordered": False,
        "n_raw_headwords": n_raw,
        "n_after_exclusions": n_kept,
        "n_distinct_types": len(types),
        "types": [list(w) for w in sorted(types)],
    }


# --------------------------------------------------------------------------- #
# Etruscan -- kaikki.org Wiktionary extract, fetched fresh (S-005's own
# addition; no earlier spike cached this). Small by construction: the real
# Etruscan lexical stock recovered by Wiktionary is a few hundred words.
# --------------------------------------------------------------------------- #

_ETRUSCAN_VOWELS = frozenset("aeiou")
# th/kh/ph (Latin digraph spelling) and the Greek-letter spelling kaikki's
# extract mixes in (θ/χ/φ) both notate the same three aspirated stops;
# folded to their plain stop, the same aspirate-folding convention Greek's
# own respelling gets, since this synthetic syllabary has no aspiration series.
_ETRUSCAN_DIGRAPHS = {"th": "t", "kh": "k", "ph": "p", "θ": "t", "χ": "k", "φ": "p", "ϕ": "p"}
_ETRUSCAN_CONSONANTS: dict[str, str] = {
    "b": "b", "c": "k", "d": "d", "f": "p", "g": "k",
    "k": "k", "l": "l", "m": "m", "n": "n", "p": "p", "q": "k", "r": "r",
    "s": "s", "z": "s", "ś": "s",  # ś/z (obstruent/affricate) fold to s, no separate series here
    "t": "t", "v": "w", "x": "k",  # x (/ks/): cluster, kept as k (adjacent-to-vowel wins downstream)
}


def _fetch_etruscan(force: bool = False) -> None:
    ETRUSCAN_DIR.mkdir(parents=True, exist_ok=True)
    if force or not ETRUSCAN_KAIKKI_PATH.exists():
        urllib.request.urlretrieve(ETRUSCAN_KAIKKI_URL, ETRUSCAN_KAIKKI_PATH)


def etruscan_phonemic(raw: str) -> list[tuple[str, bool]] | None:
    """Etruscan is written here in Latin transliteration only (kaikki's own
    romanizations); its case (proper names are capitalised, ordinary words
    are not) carries no phonemic information, unlike Hittite's uppercase
    Sumerogram convention, so it is folded away rather than used to exclude
    the word."""
    text = raw.strip().lower()
    if not text or "-" in text or " " in text or "'" in text:
        return None
    for dg, repl in _ETRUSCAN_DIGRAPHS.items():
        text = text.replace(dg, repl)
    out: list[tuple[str, bool]] = []
    for ch in text:
        if ch in _ETRUSCAN_VOWELS:
            out.append((ch, True))
            continue
        if ch == "h":
            continue  # laryngeal: no series here, same as every other language
        mapped = _ETRUSCAN_CONSONANTS.get(ch)
        if mapped is None:
            return None  # unmapped character: skip whole word
        out.append((mapped, False))
    return out or None


def _etruscan_latin_reading(entry: dict) -> str | None:
    word = entry.get("word", "") or ""
    if word and not _OLD_ITALIC_RE.search(word):
        return word
    for ht in entry.get("head_templates", []) or []:
        tr = ht.get("args", {}).get("tr")
        if tr and not _OLD_ITALIC_RE.search(tr):
            return tr
    for f in entry.get("forms", []) or []:
        if "romanization" in (f.get("tags") or []):
            w = f.get("form", "") or ""
            if w and not _OLD_ITALIC_RE.search(w):
                return w
    return None


def build_etruscan(force_download: bool = False) -> dict:
    _fetch_etruscan(force=force_download)
    types: set[Word] = set()
    latin_forms: set[str] = set()
    n_entries = 0
    with ETRUSCAN_KAIKKI_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            n_entries += 1
            got = _etruscan_latin_reading(entry)
            if got:
                latin_forms.add(got)
            # also harvest every Latin-script inflected form the entry lists
            for f in entry.get("forms", []) or []:
                w = f.get("form", "") or ""
                if w and w != "-" and not _OLD_ITALIC_RE.search(w):
                    latin_forms.add(w)
    for w in latin_forms:
        phon = etruscan_phonemic(w)
        if phon is None:
            continue
        word = syllabify(phon)
        if word is not None:
            types.add(word)
    types = finalize(types)
    return {
        "language": "etruscan_kaikki",
        "role": (
            "reference: isolate, alphabetic (not syllabic) in its own script; SMALL BY CONSTRUCTION -- "
            "see caveat below"
        ),
        "source": "kaikki.org Wiktionary extract for Etruscan",
        "url": "https://kaikki.org/dictionary/Etruscan/",
        "licence": "CC BY-SA 4.0 (inherited from Wiktionary)",
        "size_caveat": (
            f"Only {len(latin_forms)} distinct Latin-transliterated word forms exist in this "
            "extract at all (headwords plus every listed inflected form, romanizations included), "
            "against the pre-registered target of 988 -- Etruscan's real recovered vocabulary is "
            "genuinely this small, not an artefact of the fetch. run.py handles this corpus at "
            "reduced size and flags every statistic computed from it."
        ),
        "ordered": False,
        "n_source_entries": n_entries,
        "n_distinct_latin_forms": len(latin_forms),
        "n_distinct_types": len(types),
        "types": [list(w) for w in sorted(types)],
    }


# --------------------------------------------------------------------------- #
# Orchestration and RESPELLING.md
# --------------------------------------------------------------------------- #

BUILDERS = {
    "greek": build_greek,
    "hittite": build_hittite,
    "akkadian": build_akkadian,
    "sumerian": build_sumerian,
    "ugaritic": build_ugaritic,
    "etruscan": build_etruscan,
}

RESPELLING_MD = """\
# RESPELLING.md -- S-005's respelling rules

Every rule used to turn a source language into a Linear-B-style open-CV-syllable
corpus for `spikes/S-005-structural-profiles/`. Kept beside the corpora, outside
the repo (spikes/README.md rule 6; corpus-sources.md Invariants). Code:
`spikes/S-005-structural-profiles/build_corpora.py`.

## Sign identity

Every "sign" here is an invented syllable label (`"PA"`, `"A"`, ...), not a real
Linear B glyph name. `kober.paradigms`, `kober.nulls` and `kober.medial.pair_count`
only ever compare sign *identity*, so this is sufficient for stage 1, the medial
pair count and their nulls. It is **not** sufficient for `kober.grid` or the
medial channel's consonant-sharing check, both of which consult
`kober.values.consonant_of` against genuine Ventris values -- `run.py` never
calls either on these corpora.

## The shared coda rule (`syllabify`)

Every phonemicizer below reduces its source word to a list of `(letter,
is_vowel)` pairs on its own consonant/vowel alphabet; `syllabify` then applies,
identically for every language:

1. **Cluster simplification.** Of a run of consonants before a vowel, only the
   one immediately adjacent to the vowel survives; earlier members of the
   cluster are dropped. (`sperma` -> folded s,p,e,r,m,a -> `PE-MA`, matching
   the real Mycenaean spelling of the word.)
2. **Coda drop.** A consonant with nothing following it at all -- a word-final
   cluster -- is dropped outright, with no echo vowel. This is coarser than
   real Mycenaean orthography (which sometimes echoes a final stop with the
   preceding vowel, `wanaks` -> `wa-na-ka`) but is the rule the brief asked
   for, and it is applied identically to every language, so no language is
   favoured or penalised by the coarsening relative to another.
3. **Diphthong collapse.** A run of consecutive vowels keeps only the first.

Words respelled to fewer than two syllables are dropped, matching
`kober.words`'s own "words of one sign are dropped" rule.

**No laryngeal or pharyngeal series exists in this synthetic syllabary**,
matching Linear B's own signary: Hittite and Sumerian's ḫ/h, Akkadian's ḫ/h/ʾ,
and Etruscan's h are all dropped without leaving a coda trace -- the same
treatment any other dropped consonant gets. This is a real information loss,
named rather than hidden, and it makes every affected language's respelling
*more* alike the others than their real phonologies are, which is the
conservative direction for a "does X resemble Y" question.

## Per-language phonemicization

- **Greek** (Iliad, Perseus, real reading order): NFD-decomposed, lower-cased,
  accents/breathings dropped (as `lexicons.greek_skeleton` also drops them);
  consonants folded via `lexicons.GREEK_CONSONANTS`/`GREEK_CLUSTERS` (aspirates
  to their plain stop, ξ/ψ expanded to their two-consonant cluster); vowels
  α ε η ι ο υ ω kept. The digamma is absent from the transmitted Iliad text, so
  the w-series is naturally rare here, same caveat `lexicons.py` already
  states for the etymological method's Greek controls.
- **Hittite** (kaikki.org Wiktionary extract, dictionary order only): every
  entry's own inflected "forms" list (not just the 67 entries whose headword
  is itself Latin-scripted) is used, since most entries carry their Latin
  reading only there -- 13,390 distinct lowercase Latin forms, well past the
  67 the existing `lexicons.hittite_kaikki` loader uses for lexicon matching.
  Consonants via `lexicons.HITTITE_CONSONANTS` (š folds to s); vowels a e i u
  with macrons stripped; ḫ dropped (see above). A word containing any
  character outside this alphabet (stray IPA transcription, which this
  Wiktionary extract mixes in for some entries) is skipped whole rather than
  guessed at.
- **Akkadian** (ORACC saao + rinap + ribo glossaries, dictionary order only):
  citation forms (`cf`), deduped on `(cf, gw)` as `lexicons.akkadian_oracc`
  does; Sumerogram/logogram entries (digit or `.` in `cf`, per
  `lexicons._ORACC_LOGOGRAM_RE`) and multi-word citation forms (a literal
  space) excluded; consonants via `lexicons.AKKADIAN_CONSONANTS` except ḫ/h/ʾ,
  dropped (see above); vowels a e i u, macron and circumflex length folded
  away. First-millennium BC royal/administrative registers, not the Minoan
  palaces' period -- see `lexicons.akkadian_oracc`'s own period note.
- **Sumerian** (ORACC epsd2/literary glossary, dictionary order only): citation
  forms, deduped on `(cf, gw)`; ORACC's own compound/uncertain-reading markup
  (any uppercase letter) excludes the whole entry, as `lexicons.sumerian_epsd2`
  does; consonants via `lexicons.SUMERIAN_CONSONANTS` (ŋ/ĝ/g̃ folded to g); ḫ/h
  dropped; y (glide) dropped; ʾ excluded (out-of-alphabet, as
  `lexicons._sumerian_skeleton` treats it).
- **Ugaritic -- the weakest reference, consonantal script vocalised by an
  invented rule.** The Copenhagen Ugaritic Corpus lemma list marks no vowel
  except through its three aleph glyphs (a/i/u); the rule applied is: **every
  plain consonant is followed by an inserted /a/**, and the three aleph
  glyphs are read as self-contained vowel syllables carrying their own vowel
  quality (so `a`/`i`/`u` each become a bare V syllable, not a consonant plus
  /a/). This means every Ugaritic consonant becomes its own CV syllable by
  construction -- there is never a coda to drop, and cluster simplification
  never fires -- which will tend to make Ugaritic's respelled words longer
  and its stem/ending structure more regular than any real spelling of the
  language would be. This is exactly the distortion a stated, arbitrary
  vocalisation rule was always going to cause, and it is the reason this
  reference is labelled the weakest one throughout `RESULT.md`. Exclusions
  (damaged/reconstructed headwords, mid-word slash alternations, colon-marked
  s/ś ambiguity) reuse `lexicons._ugaritic_skeleton`'s own predicate; kept
  root-pattern entries (`/ʔ-b-d/`) have their slashes and internal hyphens
  stripped before vocalisation, per that function's own reading of the
  notation.
- **Etruscan** (kaikki.org Wiktionary extract, fetched by this spike, cached
  at `~/.cache/linear-a-b/reference/etruscan/kaikki-etruscan.jsonl`, dictionary
  order only): every entry's Latin transliteration (the `word` field itself
  when already Latin, else its head-template `tr`, else any "romanization"
  form) plus every other Latin-script form in its inflection table, unioned
  and deduped. Digraphs th/kh/ph (aspirate stops, a series Etruscan is
  believed to contrast with plain t/k/p) fold to the plain stop, the same
  aspirate-folding convention Greek gets; ś/z fold to s (no separate sibilant
  series here); h (laryngeal) dropped; x (a ks cluster) kept as k (the
  syllable-adjacent member survives cluster simplification downstream, as
  intended). **Etruscan's real recovered vocabulary in this source is only a
  few hundred words** -- far short of the pre-registered 988 -- which is a
  fact about how little of the language survives legibly, not a fetch
  failure; `run.py` runs it at reduced size and flags every statistic drawn
  from it.

## Chunk model vs random-subset model, and why

Only Greek (the Iliad, read start to finish) has a real reading order in the
source used here. Every other source is a *dictionary* -- an alphabetised or
citation-number-ordered glossary (ORACC, the CUC lemma list, the two kaikki.org
Wiktionary extracts) -- whose entry order is a lexicographic or database
artefact, not an attested sequence of use. Per the brief ("contiguous runs of
the source text where it has an order, else random word-type subsets"):

- **Greek**: chunk model. A random start point per seed into the full ordered
  token stream (before deduplication), walked forward (wrapping at the
  stream's end) until 988 distinct respelled types have been seen.
- **Hittite, Akkadian, Sumerian, Ugaritic, Etruscan**: random word-type subset,
  `random.Random(seed).sample` over the sorted type pool -- no order claim is
  made or available.
- **Linear B**: the tablet model (documents removed), reusing the exact
  `documents_k` values `scripts/kober_floor_sweep.py` found for each of its 20
  seeds at 988 word types (`results/kober-sweep/kober-sweep-tablet-size988-seed*.json`),
  so this spike's Linear B subsamples are the *same* word-type sets that
  finding already measured, not a fresh draw.
- **Linear A**: not subsampled at all. GORILA's own CERTAIN-WORD, >=2-sign type
  count is already ~988 (`kober.words.extract_word_types`); SigLA is used at
  its own full size (~692-988 depending on the exact filter), per the brief.
"""


def write_readme() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "RESPELLING.md").write_text(RESPELLING_MD, encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'RESPELLING.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", type=str, default=None, help="comma-separated subset of {%s}" % ",".join(BUILDERS))
    ap.add_argument("--force-download", action="store_true", help="re-fetch the Etruscan source even if cached")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = args.only.split(",") if args.only else list(BUILDERS)
    for name in names:
        if name not in BUILDERS:
            raise SystemExit(f"unknown corpus {name!r}; choices are {sorted(BUILDERS)}")
        kwargs = {"force_download": args.force_download} if name == "etruscan" else {}
        payload = BUILDERS[name](**kwargs)
        out_path = OUT_DIR / f"{name}.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        n = payload.get("n_distinct_types")
        print(f"{name}: {n} distinct respelled types -> {out_path}")

    write_readme()


if __name__ == "__main__":
    main()
