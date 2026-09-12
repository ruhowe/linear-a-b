#!/usr/bin/env python3
"""Do unrelated real languages also beat their synthetic controls on Linear A?

    .venv/bin/python scripts/unrelated_controls.py --corpus lineara --perms 100

The frozen protocol gave Hebrew z = +2.62 on Linear A against a shape-matched synthetic
lexicon, and +0.30 on Linear B. Before that is read as anything about Semitic, the
obvious alternative must be priced: every real language has phonotactic structure that a
random-string lexicon lacks, so *any* real lexicon might beat its synthetic twin on Linear
A through the same permissive map. If Finnish, Turkish, Basque and Hungarian do too, the
Hebrew excess is generic. If only Hebrew does, it is specific.

Same instrument as `controlled_comparison.py`, unchanged: same expansion, statistic, null,
word sample and permutation count. Only the lexicon varies. Each control runs through the
Semitic consonantal map by default, because that is the map the Hebrew result came from
and the map is part of what is being tested. `--map greek` reruns the same lexicons
through the Greek map instead, for whichever hypothesis under test needs an unrelated
Latin-script control under that map (e.g. Hittite, which only runs under Greek at all).

Lexicons: FrequencyWords 2018 lists (hermitdave, from OpenSubtitles), top 50,000 word
forms with counts. Modern subtitle vocabulary, which is a limitation and also the point:
nobody proposes these languages for Minoan, so any signal they show is artifact by
construction. Orthography is folded crudely onto the Hebrew key alphabet; the synthetic
twin is built from the folded lexicon, so the folding cannot favour the real one.

--secure-signs-only and --non-secure-only (A-001 sensitivities, not a protocol change).
Protocol 1.0 above is unchanged by either; both are off by default and mutually
exclusive. Passed through to `word_sample` in `controlled_comparison.py`, the same
sampler this script already shares with it, so the restriction lands on an identical
pool. `--secure-signs-only` restricts the sample pool to word types spelled entirely
with Meißner and Steele's 25 demonstrably shared signs (`src/hypotheses/secure_signs.py`)
before sampling; `--non-secure-only` restricts it to the complement, word types using at
least one sign outside that set. Output filenames gain a `-secure25` or `-nonsecure`
tag. See FINDINGS F-014.
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

from controlled_comparison import run_one, synthetic_like, word_sample  # noqa: E402
from hypotheses.phonologies import build_map  # noqa: E402
from hypotheses.secure_signs import SECURE_SIGNS  # noqa: E402
from semitic_null.lexicon import Lexicon  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402

REF = Path.home() / ".cache" / "linear-a-b" / "reference"

# Latin-script consonants folded onto the Hebrew skeleton alphabet used by the Semitic
# map (see semitic_null.lexicon.HEBREW_CONSONANTS). Vowels are dropped. Digraphs are
# handled per language before single letters. Anything unmapped drops the word.
#
# This alphabet (b d g h k l m n p r s t v/w y z q f->p c->k x->ks j->y, plus the
# per-language digraph folds C H O S T) was built for the Semitic map and is reused
# unchanged for --map greek. The Greek map's own alphabet is narrower (b d g k l m n p
# r s t w z, see phonologies.SERIES_TO_GREEK), so folded words carrying h, q, y, or a
# digraph target of C/H/O/S/T contain a symbol the Greek map itself never emits from a
# Linear A/B sign and so can never be matched under it. That is acceptable rather than a
# bug: it applies identically to the real lexicon and its synthetic twin (built from the
# same folded counts), so it does not favour either side of the comparison it is used in.
BASE = {"b": "b", "d": "d", "g": "g", "h": "h", "k": "k", "l": "l", "m": "m", "n": "n",
        "p": "p", "r": "r", "s": "s", "t": "t", "v": "w", "w": "w", "y": "y", "z": "z",
        "q": "q", "f": "p", "c": "k", "x": "ks", "j": "y"}
DIGRAPHS = {
    "fi": {},
    "tr": {"ç": "t", "ş": "C", "ğ": "", "c": "d", "j": "z"},
    "hu": {"sz": "s", "zs": "z", "cs": "t", "gy": "d", "ny": "n", "ty": "t", "ly": "y", "dz": "z", "s": "C"},
    "eu": {"tx": "t", "tz": "s", "ts": "s", "x": "C", "z": "s", "ñ": "n", "ll": "l", "rr": "r"},
}
VOWELS = set("aeiouyáéíóöőúüűâîûäåœ")

# Two Semitic-language frequency lists built by the same OpenSubtitles pipeline as the
# unrelated ones. They test explanation 2 in FINDINGS F-011: if a Hebrew *frequency list*
# scores like Finnish and Basque rather than like Strong's, the Northwest Semitic advantage
# was about lexicon type, not language. Arabic is Central Semitic and a further sibling.
ARABIC_CONSONANTS = {
    "ا": "ʾ", "أ": "ʾ", "إ": "ʾ", "آ": "ʾ", "ء": "ʾ", "ؤ": "ʾ", "ئ": "ʾ",
    "ب": "b", "ت": "t", "ث": "C", "ج": "g", "ح": "H", "خ": "H", "د": "d", "ذ": "d",
    "ر": "r", "ز": "z", "س": "s", "ش": "C", "ص": "S", "ض": "S", "ط": "T", "ظ": "S",
    "ع": "O", "غ": "O", "ف": "p", "ق": "q", "ك": "k", "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "و": "w", "ي": "y", "ة": "t", "ى": "",
}
ARABIC_IGNORE = set("\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0640")


def _arabic_skeleton(word: str) -> str | None:
    out = []
    for ch in word:
        if ch in ARABIC_IGNORE:
            continue
        if ch in ARABIC_CONSONANTS:
            out.append(ARABIC_CONSONANTS[ch])
        else:
            return None
    s = "".join(out)
    return s or None


def _hebrew_skeleton(word: str) -> str | None:
    from semitic_null.lexicon import skeleton as heb
    s = heb(word)
    # reject words carrying non-Hebrew characters (digits, Latin), which heb() would silently drop
    if any(c.isalpha() and not ("\u05d0" <= c <= "\u05ea") for c in word):
        return None
    return s or None


def skeleton(word: str, lang: str) -> str | None:
    if lang == "ar":
        return _arabic_skeleton(word)
    if lang == "he":
        return _hebrew_skeleton(word)
    w = word.lower()
    out = []
    i = 0
    dig = DIGRAPHS.get(lang, {})
    while i < len(w):
        two = w[i:i + 2]
        if two in dig:
            out.append(dig[two]); i += 2; continue
        ch = w[i]
        if ch in dig:
            out.append(dig[ch])
        elif ch in BASE:
            out.append(BASE[ch])
        elif ch in VOWELS or ch in "'-":
            pass
        else:
            return None
        i += 1
    s = "".join(out)
    return s if s else None


def load_control(lang: str, min_len: int = 2, max_len: int = 5) -> Lexicon:
    path = REF / f"freq_{lang}_50k.txt"
    counts: collections.Counter = collections.Counter()
    seen = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        sk = skeleton(parts[0], lang)
        if sk and min_len <= len(sk) <= max_len:
            counts[sk] += 1  # type count per skeleton, matching the Greek/Hebrew loaders
            seen += 1
    by_len: dict[int, set[str]] = {}
    for s in counts:
        by_len.setdefault(len(s), set()).add(s)
    return Lexicon({k: frozenset(v) for k, v in by_len.items()}, dict(counts),
                   frozenset("".join(counts)), seen)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", choices=["damos", "lineara"], default="lineara")
    ap.add_argument("--words", type=int, default=400)
    ap.add_argument("--perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--langs", nargs="+", default=["fi", "tr", "eu", "hu"],
                    help="fi tr eu hu (default, the unrelated controls); he ar (Semitic frequency lists)")
    ap.add_argument("--map", choices=["semitic", "greek"], default="semitic",
                    help="scoring map for the folded lexicons; default keeps every existing "
                         "invocation and output filename unchanged")
    secure_group = ap.add_mutually_exclusive_group()
    secure_group.add_argument("--secure-signs-only", action="store_true",
                    help="A-001 sensitivity, not protocol 1.0 itself: restrict the sample "
                         "pool to word types spelled entirely with Meissner and Steele's "
                         "25 demonstrably shared signs before sampling. Off by default.")
    secure_group.add_argument("--non-secure-only", action="store_true",
                    help="A-001 sensitivity, not protocol 1.0 itself: restrict the sample "
                         "pool to the complement of --secure-signs-only, word types using "
                         "at least one sign outside Meissner and Steele's 25 demonstrably "
                         "shared signs. Off by default; mutually exclusive with "
                         "--secure-signs-only.")
    args = ap.parse_args()

    corpus = aegean.load(args.corpus)
    inv = corpus.sign_inventory
    upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})  # noqa: E731
    gmap = upper(build_map(inv, "greek_syllabic"))
    smap = upper(build_map(inv, "semitic_consonantal"))
    secure = SECURE_SIGNS if args.secure_signs_only else None
    words = word_sample(corpus, [gmap, smap], args.words, args.seed, secure,
                         non_secure_only=args.non_secure_only)  # identical sample, restricted
    freq = collections.Counter(s for w in words for s in w)
    scoring_map = gmap if args.map == "greek" else smap
    map_name = "greek_syllabic" if args.map == "greek" else "semitic_consonantal"

    rows = []
    print(f"\n== {args.corpus}  words={len(words)}  perms={args.perms}  map={args.map}  seed={args.seed}")
    print(f"{'lexicon':<34} {'types':>6} {'real':>8} {'null':>8} {'z':>7} {'se':>5} {'p':>7}")
    NAMES = {"fi": "Finnish", "tr": "Turkish", "eu": "Basque", "hu": "Hungarian",
             "he": "Hebrew (modern, frequency list)", "ar": "Arabic (frequency list)"}
    for lang in args.langs:
        name = NAMES[lang]
        lex = load_control(lang)
        for label, lx in ((f"{name} (real)", lex), (f"{name} (synthetic)", synthetic_like(lex, args.seed))):
            r = run_one(label, scoring_map, lx, words, freq, args.perms, args.seed)
            r["types"] = lex.n_entries
            rows.append(r)
            print(f"{label:<34} {lex.n_entries:>6} {r['real']:>8.4f} {r['null_mean']:>8.4f} "
                  f"{r['z']:>+7.2f} {r['se_z']:>5.2f} {r['p']:>7.3f}", flush=True)

    tag = "" if args.langs == ["fi", "tr", "eu", "hu"] else "-" + "-".join(args.langs)
    tag += ("" if args.seed == 0 else f"-seed{args.seed}") + ("" if args.perms == 100 else f"-p{args.perms}")
    tag += "" if args.map == "semitic" else "-greekmap"
    if args.secure_signs_only:
        tag += "-secure25"
    if args.non_secure_only:
        tag += "-nonsecure"
    out = ROOT / "results" / f"unrelated_controls-{args.corpus}{tag}.json"
    out.write_text(json.dumps({"corpus": args.corpus, "n_words": len(words), "perms": args.perms,
                               "seed": args.seed, "map": map_name,
                               "secure_signs_only": args.secure_signs_only,
                               "non_secure_only": args.non_secure_only, "rows": rows}, indent=2))
    print(f"\nwritten {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
