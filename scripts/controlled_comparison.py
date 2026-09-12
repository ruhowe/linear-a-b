#!/usr/bin/env python3
"""The frozen protocol: one instrument, calibrated on Linear B, applied once to Linear A.

    .venv/bin/python scripts/controlled_comparison.py            # both corpora
    .venv/bin/python scripts/controlled_comparison.py --corpus lineara --perms 60

Why this file exists. The interactive runs on 2026-09-11 tuned the instrument on Linear B
(four statistics tried, three expansion settings, several null designs) until it could
detect Greek in Greek. That is legitimate calibration on a corpus whose answer is known,
but only if the tuned instrument is then frozen and applied to Linear A without further
adjustment. This script is the freeze. Change it and the Linear A result is no longer a
test.

Three corrections to the interactive runs, all reviewer-level rather than new science:

1. Words are a seeded random sample, not the alphabetically first N, which over-sampled
   vowel-initial words.
2. Every hypothesis on a corpus scores the same word set and the same permutation count.
3. Each real lexicon is paired with a synthetic control built under the SAME phonology
   map: identical skeleton-length profile and consonant frequencies, random content. A
   z-score is only comparable to another z-score from the same map, so the question
   "does Greek beat a false lexicon" is answered against synthetic-Greek, not against
   Hebrew. Hebrew-vs-synthetic-Hebrew answers the Semitic question the same way.

Success criterion on Linear B, stated before running: real Greek must beat synthetic
Greek clearly, and Hebrew must not beat synthetic Hebrew. If either fails the instrument
is not calibrated and the Linear A numbers are not to be read.

--secure-signs-only and --non-secure-only (A-001 sensitivities, not a protocol change).
Protocol 1.0 above is unchanged by either; both are off by default and mutually
exclusive. Meißner and Steele's Table 1 lists 25 signs whose Linear A/B value
equivalence is demonstrable rather than assumed by shape (`src/hypotheses/secure_signs.py`,
citing `docs/works/meissner_steele_preprint.md`). Every other Linear A sign carries a
Linear B value applied to a graphically similar sign, which A-001 in ASSUMPTIONS.md flags
as a stated limit. `--secure-signs-only` restricts the sample pool to word types spelled
entirely with those 25 signs, before sampling, and reports the surviving pool size; below
100 surviving word types the run does not happen and the count is reported as underpowered
instead. `--non-secure-only` restricts the pool to the complement, word types using at
least one sign outside that set. Output filenames gain a `-secure25` or `-nonsecure` tag
so they never overwrite the unrestricted protocol 1.0 results. See FINDINGS F-014.

--exclude-underdotted (A-004 sensitivity, not a protocol change). Protocol 1.0 above is
unchanged by this flag; it is off by default. Measured 2026-09-11
(`scripts/lineara_underdots.py`): this transcription chain carries no Leiden underdot
(U+0323) at all, so the DAMOS problem recorded in `docs/ai_context/corpus-sources.md`
(the CERTAIN status not checking for it) does not recur in that form here. What does
survive into CERTAIN WORD tokens of 2 to 4 signs is 246 of 3,336 sampled sign positions
(7.4%) carrying an asterisk-numbered, phonetically unidentified sign label (e.g. `*301`)
-- GORILA's catalogue convention for a sign shape with no assigned Linear B value, not
textual damage. This flag drops any word type carrying such a sign, or a bracket, query
mark, span bracket or unexpected lower-case letter, from the sample pool before sampling.
See ASSUMPTIONS A-004.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import math
import random
import statistics
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import ReadingStatus, TokenKind  # noqa: E402

from hypotheses.lexicons import greek_archaic, strongs_hebrew  # noqa: E402
from hypotheses.phonologies import build_map  # noqa: E402
from hypotheses.run import frequency_matched_permute  # noqa: E402
from hypotheses.secure_signs import SECURE_SIGNS  # noqa: E402
from semitic_null.lexicon import Lexicon  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402

# Bump on ANY change that could move a result, and add a CHANGELOG.md entry in the same
# change. Every results file written by this script carries this stamp.
PROTOCOL_VERSION = "1.0"

CODA = ["l", "r", "m", "n", "s"]  # consonants Mycenaean omits before another consonant
FINAL = ["", "s", "n", "r"]  # consonants it omits word-finally
MAX_OMITTED = 1  # at most one omitted coda per word; Greek words rarely carry more
MIN_LEN, MAX_LEN = 2, 6

# Leiden span-delimiting brackets that should never appear inside a CERTAIN sign label
# (see A-004 / scripts/lineara_underdots.py). Lacuna brackets and "?" are covered
# separately below since they are also apparatus in their own right.
_SPAN_BRACKETS = "⸤⸥〚〛⟦⟧⌞⌟⌜⌝"


def _sign_is_marked(sign: str) -> bool:
    """Whether one CERTAIN-token sign label carries a Leiden damage/uncertainty mark,
    is phonetically unidentified (asterisk-numbered, e.g. ``*301``), or shows some
    other anomaly that should not have survived into ``CERTAIN`` status.

    Measured 2026-09-11 on the loaded ``lineara`` corpus: no sign label carries a
    combining dot below (none exist in this transcription chain at all) and none
    carries a bracket, query mark or span bracket (``classify()`` already routes
    those to ``UNCLEAR``/``RESTORED`` before a token can reach ``CERTAIN``). The one
    mark that does survive is the asterisk of an unidentified sign. All checks are
    kept here regardless, so the flag stays correct if the loader or corpus changes.
    """
    if "̣" in unicodedata.normalize("NFD", sign):
        return True
    if "*" in sign:  # unidentified sign, bare (*301) or ligatured (VIR+*307)
        return True
    if any(ch in sign for ch in "[]?" + _SPAN_BRACKETS):
        return True
    if "-" in sign:
        return True
    return any(ch.islower() for ch in sign)


def expand(signs, cmap: ConsonantMap, max_ins: int = MAX_OMITTED):
    """Consonant skeletons a spelling could stand for under the known Mycenaean rules."""
    base = []
    for s in signs:
        opts = cmap.get(s)
        if opts is None:
            return None
        base.append(sorted(opts) if opts else [""])
    out = set()
    slots = range(1, len(signs))
    for stem in itertools.product(*base):
        for k in range(max_ins + 1):
            for pos in itertools.combinations(slots, k):
                for fills in itertools.product(CODA, repeat=k):
                    parts = list(stem)
                    for p, f in zip(pos, fills):
                        parts[p] = f + parts[p]
                    core = "".join(parts)
                    for fin in FINAL:
                        out.add(core + fin)
    return {s for s in out if MIN_LEN <= len(s) <= MAX_LEN}


def statistic(cmap: ConsonantMap, lex: Lexicon, words) -> float:
    """Mean over words of log(1 + mean lexicon count over the word's candidates).

    Chosen on Linear B as the best of four tried; frozen here. The count is the number
    of distinct lexicon entries sharing a skeleton, so it rewards landing on skeletons
    many real words share rather than merely landing on any attested one.
    """
    vals = []
    for sg in words:
        cands = expand(sg, cmap)
        if not cands:
            continue
        vals.append(math.log1p(sum(lex.counts.get(s, 0) for s in cands) / len(cands)))
    return statistics.fmean(vals) if vals else 0.0


def synthetic_like(lex: Lexicon, seed: int) -> Lexicon:
    """A false lexicon with this lexicon's length profile and consonant frequencies.

    Every real skeleton is replaced by a random string of the same length drawn from
    the lexicon's own consonant unigram distribution, keeping its count. Real words are
    destroyed; everything a permissive matcher could exploit about shape and frequency
    is preserved. This is the control a z-score under the same map must beat.
    """
    rng = random.Random(seed)
    unigram = collections.Counter()
    for skel, n in lex.counts.items():
        for ch in skel:
            unigram[ch] += n
    letters = list(unigram)
    weights = [unigram[c] for c in letters]
    counts: collections.Counter = collections.Counter()
    for skel, n in lex.counts.items():
        fake = "".join(rng.choices(letters, weights=weights, k=len(skel)))
        counts[fake] += n
    by_len: dict[int, set[str]] = {}
    for s in counts:
        by_len.setdefault(len(s), set()).add(s)
    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_len.items()},
        counts=dict(counts),
        inventory=frozenset("".join(counts)),
        n_entries=lex.n_entries,
    )


def word_pool(corpus, maps: list[ConsonantMap], secure_signs: frozenset[str] | None = None,
              exclude_underdotted: bool = False, non_secure_only: bool = False):
    """Word types covered by every map given, before sampling.

    ``secure_signs``, if given, drops any word type using a sign outside that set. This
    is the A-001 sensitivity restriction (`--secure-signs-only`), not part of protocol
    1.0's own sampling rule. ``non_secure_only``, if set, is the complement restriction
    (`--non-secure-only`): it drops any word type spelled entirely with
    Meißner and Steele's 25 secure signs, keeping only word types using at least one
    sign outside that set. Mutually exclusive with ``secure_signs`` in practice, since
    the two ask opposite questions of the same 25-sign set. ``exclude_underdotted``, if
    set, drops any word type carrying a Leiden damage mark or an unidentified sign label
    (`_sign_is_marked`). This is the A-004 sensitivity restriction
    (`--exclude-underdotted`), likewise not part of protocol 1.0.
    """
    pool = set()
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                continue
            if not 2 <= len(tok.signs) <= 4:
                continue
            if exclude_underdotted and any(_sign_is_marked(s) for s in tok.signs):
                continue
            sg = tuple(s.upper() for s in tok.signs)
            if secure_signs is not None and not set(sg) <= secure_signs:
                continue
            if non_secure_only and set(sg) <= SECURE_SIGNS:
                continue
            if all(m.covered(sg) for m in maps):
                pool.add(sg)
    return sorted(pool)


def word_sample(corpus, maps: list[ConsonantMap], n: int, seed: int,
                 secure_signs: frozenset[str] | None = None,
                 exclude_underdotted: bool = False, non_secure_only: bool = False):
    """Seeded random sample of word types covered by every map given."""
    pool = word_pool(corpus, maps, secure_signs, exclude_underdotted, non_secure_only)
    rng = random.Random(seed)
    return pool if len(pool) <= n else sorted(rng.sample(pool, n))


def run_one(label, cmap, lex, words, freq, perms, seed) -> dict:
    real = statistic(cmap, lex, words)
    rng = random.Random(seed)
    nulls = [statistic(frequency_matched_permute(cmap, rng, freq), lex, words) for _ in range(perms)]
    mean = statistics.fmean(nulls)
    sd = statistics.pstdev(nulls)
    z = (real - mean) / sd if sd else 0.0
    at_least = sum(1 for x in nulls if x >= real)
    return {
        "label": label,
        "n_words": len(words),
        "real": real,
        "null_mean": mean,
        "null_sd": sd,
        "z": z,
        "se_z": (1 / math.sqrt(perms)) * math.sqrt(1 + z * z / 2),
        "p": (at_least + 1) / (perms + 1),
        "perms": perms,
    }


def run_corpus(name: str, n_words: int, perms: int, seed: int,
               secure_signs_only: bool = False, exclude_underdotted: bool = False,
               non_secure_only: bool = False) -> dict:
    corpus = aegean.load(name)
    inv = corpus.sign_inventory
    upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})  # noqa: E731
    gmap = upper(build_map(inv, "greek_syllabic"))
    smap = upper(build_map(inv, "semitic_consonantal"))

    secure = SECURE_SIGNS if secure_signs_only else None
    n_pool = len(word_pool(corpus, [gmap, smap], secure, exclude_underdotted, non_secure_only))
    if (secure_signs_only or non_secure_only) and n_pool < 100:
        return {
            "corpus": name, "secure_signs_only": secure_signs_only,
            "non_secure_only": non_secure_only, "n_pool": n_pool,
            "n_words": 0, "perms": perms, "seed": seed, "rows": [],
            "underpowered": True,
        }

    words = word_sample(corpus, [gmap, smap], n_words, seed, secure, exclude_underdotted,
                         non_secure_only)
    freq = collections.Counter(s for w in words for s in w)

    greek = greek_archaic()
    hebrew = strongs_hebrew()
    rows = [
        run_one("Greek, archaic (real)", gmap, greek, words, freq, perms, seed),
        run_one("Greek map, synthetic lexicon (control)", gmap, synthetic_like(greek, seed), words, freq, perms, seed),
        run_one("Hebrew, Strong's (real)", smap, hebrew, words, freq, perms, seed),
        run_one("Hebrew map, synthetic lexicon (control)", smap, synthetic_like(hebrew, seed), words, freq, perms, seed),
    ]
    return {
        "corpus": name, "n_words": len(words), "n_pool": n_pool,
        "secure_signs_only": secure_signs_only, "non_secure_only": non_secure_only,
        "exclude_underdotted": exclude_underdotted,
        "perms": perms, "seed": seed, "rows": rows,
    }


def fmt(block: dict) -> str:
    header = f"\n== {block['corpus']}  words={block['n_words']}  perms={block['perms']}  seed={block['seed']}"
    if block.get("secure_signs_only"):
        header += f"  secure25 pool={block['n_pool']}"
    if block.get("non_secure_only"):
        header += f"  nonsecure pool={block['n_pool']}"
    if block.get("exclude_underdotted"):
        header += "  exclude-underdotted"
    if block.get("underpowered"):
        restriction = "secure-25" if block.get("secure_signs_only") else "non-secure"
        return header + f"\nUNDERPOWERED: {block['n_pool']} word types survive the {restriction} " \
                         "restriction, fewer than 100. Not run."
    lines = [header, f"{'hypothesis':<42} {'real':>8} {'null':>8} {'z':>7} {'se':>5} {'p':>7}"]
    for r in block["rows"]:
        lines.append(f"{r['label']:<42} {r['real']:>8.4f} {r['null_mean']:>8.4f} "
                     f"{r['z']:>+7.2f} {r['se_z']:>5.2f} {r['p']:>7.3f}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", choices=["damos", "lineara", "both"], default="both")
    ap.add_argument("--words", type=int, default=400)
    ap.add_argument("--perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
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
    ap.add_argument("--exclude-underdotted", action="store_true",
                     help="A-004 sensitivity, not protocol 1.0 itself: drop word types "
                          "carrying a Leiden damage mark or an unidentified sign label "
                          "from the sample pool before sampling. Off by default.")
    args = ap.parse_args()

    names = ["damos", "lineara"] if args.corpus == "both" else [args.corpus]
    out = {"protocol": {
        "version": PROTOCOL_VERSION,
        "expansion": f"Mycenaean rules, max {MAX_OMITTED} omitted coda, finals {FINAL[1:]}",
        "statistic": "log1p(mean lexicon count over candidates), averaged over words",
        "null": "frequency_matched_permute, 4 bands",
        "control": "synthetic lexicon with matched length profile and consonant unigrams, same map",
        "criterion": "Linear B: real Greek >> synthetic Greek; Hebrew ~ synthetic Hebrew. Else uncalibrated.",
        "secure_signs_only": args.secure_signs_only,
        "non_secure_only": args.non_secure_only,
        "exclude_underdotted": args.exclude_underdotted,
    }, "blocks": []}
    for name in names:
        block = run_corpus(name, args.words, args.perms, args.seed,
                            args.secure_signs_only, args.exclude_underdotted,
                            args.non_secure_only)
        out["blocks"].append(block)
        print(fmt(block), flush=True)
    suffix = "" if args.corpus == "both" else f"-{args.corpus}"
    if args.secure_signs_only:
        suffix += "-secure25"
    if args.non_secure_only:
        suffix += "-nonsecure"
    if args.exclude_underdotted:
        suffix += "-exunderdot"
    path = ROOT / "results" / f"controlled_comparison{suffix}.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"\nwritten {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
