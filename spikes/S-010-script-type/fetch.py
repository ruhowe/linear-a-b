#!/usr/bin/env python3
"""Fetch and build the reference corpora for S-010 (spikes/S-010-script-type/BRIEF.md).

Builds, for Linear A (the subject) and six typological references, one JSON file
of **word-token sequences of sign tokens** under
``~/.cache/linear-a-b/reference/script-types/`` (outside the repo: corpus-sources.md
Invariants, "never commit fetched corpus data into this repo"), plus a README in that
folder recording source, URL, licence and how each corpus's tokens were formed.

Output shape, one file per corpus::

    {
      "corpus": "<name>",
      "role": "<what this corpus is for in S-010>",
      "source": "...", "url": "...", "licence": "...",
      "how_tokens_were_formed": "...",
      "n_documents": N, "n_word_tokens": N, "n_sign_tokens": N,
      "documents": [ [ ["A","RO"], ["PA","I","TO"], ... ], ... ]
    }

``documents`` is a list of documents; each document a list of words; each word a
list of sign-token strings, in the order the source gives them (see each builder's
docstring for what "order" means for that source — exact reading order for Linear
A/B, Greek and Egyptian; a corpus-index reconstruction for Akkadian; no order claim
beyond file order for Ugaritic and Sumerian, which the statistics used here do not
need beyond a stable, reproducible enumeration).

Reference (2)-(6) sources live under ``~/.cache/linear-a-b/reference/`` (oracc/,
cuc-v0.2.7.zip predate this script; aes/ and lunyu-chapters.json are fetched here,
idempotently — skipped if already present). Linear A/B and Greek go through
pyaegean, which does its own caching under ``~/.cache/pyaegean/``.

Run: ``.venv/bin/python spikes/S-010-script-type/fetch.py`` (rebuilds everything), or
``--only linear_b,ugaritic`` for a subset. ``--force-download`` re-fetches the AES and
Lunyu source files even if already cached.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
import aegean.greek as greek  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from linearb_restore.normalise import normalise_text  # noqa: E402

REFERENCE_DIR = Path.home() / ".cache" / "linear-a-b" / "reference"
OUT_DIR = REFERENCE_DIR / "script-types"
AES_DIR = REFERENCE_DIR / "aes"
ORACC_DIR = REFERENCE_DIR / "oracc"
CUC_ZIP = REFERENCE_DIR / "cuc-v0.2.7.zip"
LUNYU_CHAPTERS_PATH = REFERENCE_DIR / "lunyu-chapters.json"

Word = list[str]
Doc = list[Word]

_SPLIT_RE = re.compile(r"[-.]")
_BRACE_RE = re.compile(r"(\{[^{}]*\})")


def _split_sign_form(form: str) -> Word | None:
    """Split a hyphen/dot-delimited transliteration into sign tokens.

    A ``{...}`` determinative (ORACC/Akkadian convention, e.g. ``{TUG2}pi-i-DA``)
    is split off as its own token first, so it never fuses with the sign it
    precedes; the remainder is then split on hyphen/dot as usual.

    Returns ``None`` (drop the whole word) if any resulting segment is empty or an
    unknown-sign placeholder (``x``/``X``, ORACC and AES's shared convention for
    an illegible sign) — a whole-word exclusion rather than dropping just the
    damaged sign, so no word's length is silently shortened by a guess.
    """
    parts: list[str] = []
    for piece in _BRACE_RE.split(form):
        if not piece:
            continue
        if piece.startswith("{") and piece.endswith("}"):
            parts.append(piece)
        else:
            parts.extend(_SPLIT_RE.split(piece))
    if not parts or any(p.strip() == "" or p.strip().lower() == "x" for p in parts):
        return None
    return parts


# --------------------------------------------------------------------------- #
# (1) Linear B (DAMOS), and the two Linear A editions (the subject, not a
# reference) — all through the same pyaegean Document/Token model.
# --------------------------------------------------------------------------- #


def _build_from_aegean_corpus(corpus_id: str) -> list[Doc]:
    """CERTAIN WORD tokens from an aegean corpus, signs normalised and upper-cased.

    Same status/kind filter and label normalisation as ``src/kober/words.py``
    (``linearb_restore.normalise.normalise_text``, which merges underdot variants
    into their plain form — built for DAMOS; corpus-sources.md HENGE A-039 notes
    it is untested on Linear A. Applied to both editions here anyway, for identical
    treatment, flagged in RESULT.md).

    Unlike ``kober.words.extract_word_types``, this keeps **tokens**, not
    deduplicated **types** (S-010's inventory-growth and frequency statistics need
    repetition), and does **not** drop one-sign words (S-010's each-sign-a-word
    check needs the true word-length distribution). Note DAMOS's own tokenizer
    (``aegean.scripts.linearb.loader.classify``) only emits ``WORD`` for tokens
    containing a hyphen, so a genuine one-sign DAMOS token is typed ``UNKNOWN`` and
    is invisible here regardless of this filter — a loader convention, not a claim
    that one-sign Linear B words don't occur (linearb-restoration.md HENGE, loader
    trap 2).
    """
    corpus = aegean.load(corpus_id)
    documents: list[Doc] = []
    for doc in corpus.documents:
        words: Doc = []
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            signs: Word = []
            for label in tok.signs:
                norm, _had_underdot, _had_span = normalise_text(label)
                signs.append(norm.upper())
            if signs:
                words.append(signs)
        if words:
            documents.append(words)
    return documents


def build_linear_b() -> list[Doc]:
    return _build_from_aegean_corpus("damos")


def build_linear_a_gorila() -> list[Doc]:
    return _build_from_aegean_corpus("lineara")


def build_linear_a_sigla() -> list[Doc]:
    return _build_from_aegean_corpus("sigla")


# --------------------------------------------------------------------------- #
# (2) Ugaritic — Copenhagen Ugaritic Corpus (CACCHT), cached zip.
# --------------------------------------------------------------------------- #


def build_ugaritic() -> list[Doc]:
    """One document per KTU tablet, words in file (line) order; tokens are letters.

    ``auto_parsing/0.2.6/*.tsv`` (278 tablets; ``reviewed/`` is a single
    hand-checked tablet, too little on its own). Column 2 ("surface form") is the
    consonantal transliteration of the word as one string with no internal
    separators (Ugaritic is a 30-letter alphabet, not a syllabary), so "tokens are
    letters" per the brief means ``list(surface_form)`` — one Python string
    character per letter sign. A handful of Ugaritic letters are a base letter plus
    a combining diacritic (two Unicode code points); this splits those into two
    tokens, a known small over-count, not corrected here. Rows whose surface form
    is empty, ``?`` or ``x`` (illegible) are dropped; ``#``-prefixed rows are
    tablet/line headers, not words.
    """
    documents: list[Doc] = []
    with zipfile.ZipFile(CUC_ZIP) as z:
        names = sorted(
            n
            for n in z.namelist()
            if n.startswith("DT-UCPH-cuc-03a334e/auto_parsing/0.2.6/") and n.endswith(".tsv")
        )
        for name in names:
            text = z.read(name).decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(text), delimiter="\t")
            next(reader, None)  # header row
            words: Doc = []
            for row in reader:
                if not row or not row[0] or row[0].lstrip().startswith("#"):
                    continue
                if len(row) < 2:
                    continue
                surface = row[1].strip()
                if not surface or surface in ("x", "?"):
                    continue
                signs = list(surface)
                if signs:
                    words.append(signs)
            if words:
                documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# (3a) Sumerian — ORACC epsd2/literary, per-text corpusjson.
# --------------------------------------------------------------------------- #


def build_sumerian() -> list[Doc]:
    """One document per epsd2/literary text, words in true line/word order.

    Only ``epsd2-literary.zip`` carries per-text ``corpusjson/*.json`` files in this
    cache (rinap/ribo/saao ship only pre-built indexes — see ``build_akkadian``).
    Each file's ``cdl`` tree is walked for ``"node": "l"`` (lexical) leaves whose
    ``f.lang`` is ``sux`` or ``sux-x-emesal`` (the two Sumerian dialect tags present;
    ``akk``/``akk-x-oldbab`` leaves are the bilingual glosses, excluded here and too
    few — roughly 400 instances corpus-wide — to serve as the Akkadian reference on
    their own, hence ``build_akkadian``). ``f.form`` is the sign-level
    transliteration, hyphen/dot separated, Sumerian logograms conventionally already
    lower-case with subscript-numeral homophone marking (e.g. ``bur12``) — kept
    as-is; only whole words containing an illegible ``x``/``X`` segment are dropped.
    """
    documents: list[Doc] = []
    with zipfile.ZipFile(ORACC_DIR / "epsd2-literary.zip") as z:
        names = sorted(
            n
            for n in z.namelist()
            if n.startswith("epsd2/literary/corpusjson/") and n.endswith(".json")
        )
        for name in names:
            data = json.loads(z.read(name))
            words: Doc = []

            def walk(node: object) -> None:
                if isinstance(node, dict):
                    if node.get("node") == "l" and "f" in node:
                        f = node["f"]
                        if f.get("lang") in ("sux", "sux-x-emesal"):
                            signs = _split_sign_form(f.get("form", ""))
                            if signs:
                                words.append(signs)
                    for value in node.values():
                        walk(value)
                elif isinstance(node, list):
                    for item in node:
                        walk(item)

            walk(data.get("cdl"))
            if words:
                documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# (3b) Akkadian — ORACC ribo (Royal Inscriptions of Babylonia Online).
# --------------------------------------------------------------------------- #

_AKK_INSTANCE_RE = re.compile(r"^(?P<textid>[^;]+);w=(?P<w>\d+);u=(?P<u>\d+)$")


_AKK_SOURCES = [
    ("ribo.zip", "ribo/index-akk.json", "ribo"),
    ("saao.zip", "saao/index-akk.json", "saao"),
    # rinap.zip's index-akk.json uses a different, sparser instance-id scheme
    # (a single opaque, multiple-of-10 global id, not textid;w=;u=) that resolves
    # to only ~3,650 words after dedup, versus 13,958 (ribo) and 37,419 (saao) —
    # excluded rather than adding a second reconstruction method for a small gain.
]


def build_akkadian() -> list[Doc]:
    """One document per ribo/saao text, words reconstructed from each corpus-wide index.

    ribo.zip and saao.zip (like rinap.zip) ship no per-text corpusjson in this
    cache, only pre-built indexes. Each ``index-akk.json``'s ``keys`` list is an
    inverted index: every entry is a distinct Akkadian transliterated word form
    with the list of ``<textid>;w=<word position>;u=<line/unit>`` positions it
    occurs at. This function inverts it back: keep only entries that look like
    sign-level transliteration (drop anything containing ``[``/``]``/``(``/``)``,
    which marks a dictionary-citation-form entry rather than a transliterated one
    — e.g. ``"šīlān[in the sunset]"`` — and any word with an illegible ``x``/``X``
    segment), split each surviving form into sign tokens, then for every instance
    place that sign-token word at ``(textid, u, w)`` and, per text, sort by
    ``(u, w)`` to recover word order. A large number of identical duplicate
    positions exist in both source indexes (the same string listed against one
    slot two or three times — ribo's raw instance count is 116,943 against 13,958
    distinct slots); the first seen wins per slot, so nothing is multiply counted.
    ribo and saao are combined (document ids prefixed by source to keep them
    distinct) purely for scale — 13,958 + 37,419 words — both being Akkadian royal/
    administrative registers, the same genre pairing DAMOS itself spans.

    This reconstruction is coarser than Sumerian's direct corpusjson walk: it
    recovers within-text word order, not any claim about cross-text order, and
    inherits whatever indexing artefacts exist in ribo/saao's own indexes.
    """
    documents: list[Doc] = []
    for zip_name, member, tag in _AKK_SOURCES:
        with zipfile.ZipFile(ORACC_DIR / zip_name) as z:
            data = json.loads(z.read(member))

        positions: dict[tuple[str, int, int], Word] = {}
        for entry in data["keys"]:
            key = entry["key"]
            if any(c in key for c in "[]()"):
                continue
            signs = _split_sign_form(key)
            if signs is None:
                continue
            for inst in entry["instances"]:
                m = _AKK_INSTANCE_RE.match(inst)
                if not m:
                    continue
                slot = (m["textid"], int(m["u"]), int(m["w"]))
                positions.setdefault(slot, signs)

        by_text: dict[str, list[tuple[int, int, Word]]] = defaultdict(list)
        for (textid, u, w), signs in positions.items():
            by_text[textid].append((u, w, signs))

        for textid in sorted(by_text):
            items = sorted(by_text[textid], key=lambda t: (t[0], t[1]))
            words = [signs for _u, _w, signs in items]
            if words:
                documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# (4) Egyptian — AES (Ancient Egyptian Sentences), sawlit sub-corpus.
# --------------------------------------------------------------------------- #

AES_SAWLIT_URL = (
    "https://raw.githubusercontent.com/simondschweitzer/aes/master/files/aes/_aes_sawlit.json"
)
AES_README_URL = "https://raw.githubusercontent.com/simondschweitzer/aes/master/README.md"


def fetch_egyptian_source(force: bool = False) -> None:
    AES_DIR.mkdir(parents=True, exist_ok=True)
    target = AES_DIR / "_aes_sawlit.json"
    if force or not target.exists():
        urllib.request.urlretrieve(AES_SAWLIT_URL, target)
    readme = AES_DIR / "aes-upstream-README.md"
    if force or not readme.exists():
        urllib.request.urlretrieve(AES_README_URL, readme)


def build_egyptian() -> list[Doc]:
    """One document per AES sentence (sawlit = literary texts), words in sentence order.

    The Ramses corpus is not openly downloadable (BRIEF.md); AES (Schweitzer
    2020-21, built from the AED-TEI database; its README states CC BY-SA 4.0,
    though GitHub detects no LICENSE file at the repo root — used here for internal
    aggregate analysis only, not redistributed, the same treatment this repo gives
    other no-machine-readable-license sources, see corpus-sources.md on
    NeuroDecipher) is the open alternative the brief names as a fallback: over
    100,000 sentences of transcribed and Gardiner-coded Egyptian. ``sawlit``
    (Middle Egyptian literary texts — the same genre and period as Sinuhe and the
    Shipwrecked Sailor, though not restricted to those two works) is used rather
    than a smaller sub-corpus, for scale.

    Each word-token object's ``hiero`` field ("only if the writing of the word form
    is complete", per the AES README) is the hyphen-separated Gardiner-code writing
    in word order, e.g. ``"E10-R7-Z1-N35-N1"``; tokens without a ``hiero`` field
    (about 55% of AES word tokens in ``sawlit`` — writing incomplete or not encoded)
    are dropped rather than guessed at. Determinatives and logograms are ordinary
    Gardiner codes in this field and are kept as single sign tokens, per the brief.
    """
    data = json.loads((AES_DIR / "_aes_sawlit.json").read_text(encoding="utf-8"))
    documents: list[Doc] = []
    for _sid, sentence in data.items():
        words: Doc = []
        for tok in sentence.get("token", []):
            hiero = tok.get("hiero")
            if not hiero:
                continue
            signs = [p for p in hiero.split("-") if p]
            if signs:
                words.append(signs)
        if words:
            documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# (5) Chinese — Analects (Lunyu), Chinese Wikisource.
# --------------------------------------------------------------------------- #

LUNYU_CHAPTER_TITLES = [
    "學而第一", "爲政第二", "八佾第三", "里仁第四", "公冶長第五", "雍也第六",
    "述而第七", "泰伯第八", "子罕第九", "鄉黨第十", "先進第十一", "顏淵第十二",
    "子路第十三", "憲問第十四", "衞靈公第十五", "季氏第十六", "陽貨第十七",
    "微子第十八", "子張第十九", "堯曰第二十",
]
_CJK_RE = re.compile(r"[一-鿿]")


def fetch_chinese_source(force: bool = False) -> None:
    if not force and LUNYU_CHAPTERS_PATH.exists():
        return
    chapters: dict[str, str] = {}
    for title in LUNYU_CHAPTER_TITLES:
        page = "論語/" + title
        url = "https://zh.wikisource.org/w/index.php?title=" + urllib.parse.quote(page) + "&action=raw"
        req = urllib.request.Request(url, headers={"User-Agent": "linear-a-b-research/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            chapters[title] = resp.read().decode("utf-8")
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    LUNYU_CHAPTERS_PATH.write_text(
        json.dumps(chapters, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def build_chinese() -> list[Doc]:
    """One document per Analects chapter, words are single characters, in chapter order.

    Chinese Wikisource (zh.wikisource.org), the raw wikitext of each of the
    Analects' 20 traditional chapters (先秦, public domain as a c. 5th-century BCE
    text; the wikitext itself is Wikisource's transcription, CC BY-SA 4.0). Wikitext
    markup, transclusion syntax and any non-Chinese characters are stripped by
    keeping only code points in the CJK Unified Ideographs block
    (U+4E00-U+9FFF); each surviving character is one one-character "word" — per the
    brief, "tokens are characters" for a logographic control means the word/sign
    distinction collapses entirely, which is the point of including it.
    """
    data = json.loads(LUNYU_CHAPTERS_PATH.read_text(encoding="utf-8"))
    documents: list[Doc] = []
    for _title, wikitext in data.items():
        chars = _CJK_RE.findall(wikitext)
        words: Doc = [[c] for c in chars]
        if words:
            documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# (6) Greek — Homer's Iliad via pyaegean's own Perseus loader.
# --------------------------------------------------------------------------- #


def build_greek() -> list[Doc]:
    """One document per book of the Iliad, words in text order; tokens are letters.

    ``aegean.greek.load_work("tlg0012.tlg001")`` (Perseus canonical-greekLit,
    already used elsewhere in this repo; CC BY-SA per Perseus's standard terms).
    Each WORD token's text is passed through ``aegean.greek.strip_diacritics``
    (drops accents, breathings and iota subscript, keeping the base letter — a
    Greek "sign" for this comparison is one of the 24 alphabet letters, not an
    accented variant) and lower-cased; ``list(word)`` then gives one token per
    letter. Punctuation is not a token (``TokenKind.WORD`` already excludes it).
    """
    corpus = greek.load_work("tlg0012.tlg001")
    documents: list[Doc] = []
    for doc in corpus.documents:
        words: Doc = []
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD:
                continue
            text = greek.strip_diacritics(tok.text).lower()
            signs = [ch for ch in text if ch.isalpha()]
            if signs:
                words.append(signs)
        if words:
            documents.append(words)
    return documents


# --------------------------------------------------------------------------- #
# Registry, I/O, README
# --------------------------------------------------------------------------- #

BUILDERS: dict[str, "tuple[callable, str, str, str, str, str]"] = {
    # name: (builder, role, source, url, licence, how_tokens_were_formed)
    "linear_b": (
        build_linear_b,
        "reference (1): CV syllabary, the known case",
        "DAMOS (Aurora 2015) via aegean.load('damos')",
        "https://damos.hf.uio.no",
        "CC BY-NC-SA 4.0 (content); GPL-3.0 (software)",
        "CERTAIN WORD tokens; Token.signs normalised (linearb_restore.normalise, "
        "underdot merge) and upper-cased; one-sign words kept where the DAMOS "
        "tokenizer emits them as WORD (rare — see build docstring).",
    ),
    "ugaritic": (
        build_ugaritic,
        "reference (2): consonantal alphabet",
        "Copenhagen Ugaritic Corpus (CACCHT project), cuc-v0.2.7 zip, auto_parsing/0.2.6",
        "https://github.com/DT-UCPH/cuc (Zenodo DOI 10.5281/zenodo.10695308)",
        "CC BY-NC 4.0",
        "One document per KTU tablet; 'surface form' column per word, split into "
        "individual Unicode characters (letters); illegible (x/?) and blank rows dropped.",
    ),
    "sumerian": (
        build_sumerian,
        "reference (3a): logosyllabic",
        "ORACC epsd2/literary, per-text corpusjson (in epsd2-literary.zip)",
        "http://oracc.org/epsd2/literary",
        "CC0 (per file license field)",
        "sux/sux-x-emesal 'l' nodes' f.form, split on hyphen/dot; words with an "
        "illegible x/X segment dropped whole.",
    ),
    "akkadian": (
        build_akkadian,
        "reference (3b): logosyllabic",
        "ORACC ribo (Royal Inscriptions of Babylonia Online) + saao (State Archives "
        "of Assyria Online), index-akk.json in each zip",
        "http://oracc.org/ribo and http://oracc.org/saao",
        "CC BY-SA (per ORACC's standard terms)",
        "Sign-level forms from each corpus's word index, reconstructed into "
        "per-text word order from each instance's (unit, word-position) tag, ribo "
        "and saao concatenated for scale — see build_akkadian docstring for the "
        "coarseness this implies.",
    ),
    "egyptian": (
        build_egyptian,
        "reference (4): mixed logograms/phonograms/determinatives, no vowels marked",
        "AES (Ancient Egyptian Sentences, Schweitzer 2020-21), sawlit sub-corpus",
        "https://github.com/simondschweitzer/aes",
        "CC BY-SA 4.0 per the AES README; GitHub detects no LICENSE file at the repo "
        "root — treated as internal-analysis-only, not redistributed",
        "Word tokens' 'hiero' field (Gardiner codes, hyphen-separated, in word "
        "order) where present (~45% of sawlit word tokens); logograms and "
        "determinatives kept as single Gardiner-code tokens.",
    ),
    "chinese": (
        build_chinese,
        "reference (5): logographic",
        "The Analects (Lunyu), Chinese Wikisource, 20 traditional chapters",
        "https://zh.wikisource.org/wiki/論語",
        "Public domain (source text, c. 5th century BCE); CC BY-SA 4.0 (Wikisource's "
        "transcription)",
        "Wikitext fetched raw per chapter; every CJK Unified Ideographs character "
        "kept in order as a one-character word (tokens are characters, per the brief).",
    ),
    "greek": (
        build_greek,
        "reference (6): alphabet, second instance",
        "Homer, Iliad, via aegean.greek.load_work('tlg0012.tlg001') (Perseus canonical-greekLit)",
        "https://github.com/PerseusDL/canonical-greekLit",
        "CC BY-SA 4.0 (Perseus Digital Library standard terms)",
        "WORD tokens, diacritics stripped and lower-cased, then split into "
        "individual letters (tokens are letters, the alphabetic case).",
    ),
    "linear_a_gorila": (
        build_linear_a_gorila,
        "subject (GORILA edition), not a reference",
        "GORILA transcription chain via aegean.load('lineara')",
        "see corpus-sources.md Source landscape",
        "see corpus-sources.md Source landscape (edition-derived; no clear licence upstream)",
        "Same processing as linear_b (CERTAIN WORD tokens, normalised, upper-cased "
        "sign labels) — sign identity labels used as IDs only, not as phonetic "
        "evidence (CLAUDE.md invariant).",
    ),
    "linear_a_sigla": (
        build_linear_a_sigla,
        "subject (SigLA edition), not a reference",
        "SigLA via aegean.load('sigla')",
        "https://sigla.phis.me",
        "CC BY-NC-SA 4.0",
        "Same processing as linear_b.",
    ),
}


def _counts(documents: list[Doc]) -> tuple[int, int, int]:
    n_words = sum(len(d) for d in documents)
    n_signs = sum(len(w) for d in documents for w in d)
    return len(documents), n_words, n_signs


def write_corpus(name: str) -> dict:
    builder, role, source, url, licence, how = BUILDERS[name]
    documents = builder()
    n_docs, n_words, n_signs = _counts(documents)
    payload = {
        "corpus": name,
        "role": role,
        "source": source,
        "url": url,
        "licence": licence,
        "how_tokens_were_formed": how,
        "n_documents": n_docs,
        "n_word_tokens": n_words,
        "n_sign_tokens": n_signs,
        "documents": documents,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{name}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"{name}: {n_docs} documents, {n_words} words, {n_signs} signs -> {out_path}")
    return payload


def write_readme(built: dict[str, dict]) -> None:
    lines = [
        "# script-types/ — S-010 reference corpora",
        "",
        "Built by `spikes/S-010-script-type/fetch.py`. Outside the repo on purpose "
        "(corpus-sources.md Invariants: never commit fetched corpus data). Each "
        "`<corpus>.json` is a sequence of documents, each a sequence of words, each "
        "word a sequence of sign-token strings — see the module docstring in "
        "`fetch.py` for the exact schema.",
        "",
        "| corpus | role | n_documents | n_words | n_signs | source | licence |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, (_builder, role, source, url, licence, _how) in BUILDERS.items():
        payload = built.get(name)
        if payload is None:
            lines.append(f"| {name} | {role} | (not built this run) | | | {source} | {licence} |")
            continue
        lines.append(
            f"| {name} | {role} | {payload['n_documents']} | {payload['n_word_tokens']} | "
            f"{payload['n_sign_tokens']} | [{source}]({url}) | {licence} |"
        )
    lines.append("")
    lines.append("## How tokens were formed, per corpus")
    lines.append("")
    for name, (_builder, _role, _source, _url, _licence, how) in BUILDERS.items():
        lines.append(f"- **{name}**: {how}")
    lines.append("")
    lines.append(
        "## Licensing note\n\n"
        "Ugaritic (CC BY-NC 4.0) and SigLA (CC BY-NC-SA 4.0) are NonCommercial, same "
        "obligation as DAMOS. AES's licence is stated in its README (CC BY-SA 4.0) "
        "but not machine-readable on GitHub (no LICENSE file); treated the same way "
        "this repo treats other no-machine-readable-licence sources — internal "
        "aggregate analysis only, never redistributed. GORILA's licence is unresolved "
        "upstream (see corpus-sources.md Open questions); used here only as the "
        "subject under test, and only sign-identity labels are used, never as "
        "phonetic or linguistic evidence. Nothing derived from any of these sources "
        "leaves this cache: `results.json` and `RESULT.md` in the spike folder carry "
        "aggregate numbers only, per spikes/README.md rule 6."
    )
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'README.md'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--only",
        type=str,
        default=None,
        help="comma-separated subset of corpus names to (re)build (default: all)",
    )
    ap.add_argument(
        "--force-download",
        action="store_true",
        help="re-fetch AES and Lunyu source files even if already cached",
    )
    args = ap.parse_args()

    fetch_egyptian_source(force=args.force_download)
    fetch_chinese_source(force=args.force_download)

    names = args.only.split(",") if args.only else list(BUILDERS)
    built: dict[str, dict] = {}
    for name in names:
        if name not in BUILDERS:
            raise SystemExit(f"unknown corpus {name!r}; choices are {sorted(BUILDERS)}")
        built[name] = write_corpus(name)

    # README always reflects the full registry; re-read any file not rebuilt this
    # run so its counts still appear.
    full: dict[str, dict] = {}
    for name in BUILDERS:
        if name in built:
            full[name] = built[name]
            continue
        path = OUT_DIR / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            full[name] = {
                "n_documents": data["n_documents"],
                "n_word_tokens": data["n_word_tokens"],
                "n_sign_tokens": data["n_sign_tokens"],
            }
    write_readme(full)


if __name__ == "__main__":
    main()
