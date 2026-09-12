#!/usr/bin/env python3
"""Protocol 1.1: does the Northwest Semitic advantage survive removing the laryngeals?

    .venv/bin/python scripts/laryngeal_test.py --corpus lineara --perms 100

Tests explanation 3 in FINDINGS F-011. Under the Semitic map every Linear A vowel sign
may expand to ʾ, ʿ, h, ḥ or nothing, and Linear A is vowel-heavy, so its words generate
many laryngeal-bearing candidates. Only the Hebrew and Ugaritic lexicons carry that full
inventory; Akkadian has lost ʿ and h, and the folded unrelated lexicons have only h. If
that asymmetry is what separates Northwest Semitic from the pack, deleting laryngeals
everywhere should collapse the gap.

This is a change to the map, so it is a new protocol version, not a rerun of 1.0. Every
other component (expansion, statistic, null, sample, permutation count, synthetic twin)
is inherited unchanged from `controlled_comparison.py`.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

from controlled_comparison import run_one, synthetic_like, word_sample  # noqa: E402
from hypotheses.lexicons import LOADERS  # noqa: E402
from hypotheses.phonologies import build_map  # noqa: E402
from semitic_null.lexicon import Lexicon  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402
from unrelated_controls import load_control  # noqa: E402

PROTOCOL_VERSION = "1.1-laryngeal-stripped"
LARYNGEALS = frozenset({"ʾ", "O", "h", "H"})


def strip_lexicon(lex: Lexicon, min_len: int = 2, max_len: int = 5) -> Lexicon:
    counts: collections.Counter = collections.Counter()
    for skel, n in lex.counts.items():
        s = "".join(c for c in skel if c not in LARYNGEALS)
        if min_len <= len(s) <= max_len:
            counts[s] += n
    by_len: dict[int, set[str]] = {}
    for s in counts:
        by_len.setdefault(len(s), set()).add(s)
    return Lexicon({k: frozenset(v) for k, v in by_len.items()}, dict(counts),
                   frozenset("".join(counts)), lex.n_entries)


def strip_map(cmap: ConsonantMap) -> ConsonantMap:
    return ConsonantMap({k: frozenset(v - LARYNGEALS) for k, v in cmap.mapping.items()})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", choices=["damos", "lineara"], default="lineara")
    ap.add_argument("--words", type=int, default=400)
    ap.add_argument("--perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--only", nargs="*", help="substring filter on lexicon names")
    args = ap.parse_args()

    corpus = aegean.load(args.corpus)
    inv = corpus.sign_inventory
    upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})  # noqa: E731
    gmap = upper(build_map(inv, "greek_syllabic"))
    smap_full = upper(build_map(inv, "semitic_consonantal"))
    smap = strip_map(smap_full)
    # Same sample as protocol 1.0 for this corpus and seed: coverage is decided on the
    # unstripped maps so the word list is identical.
    words = word_sample(corpus, [gmap, smap_full], args.words, args.seed)
    freq = collections.Counter(s for w in words for s in w)

    lexicons = [
        ("Ugaritic", LOADERS["ugaritic_cuc"]()),
        ("Hebrew, Strong's", LOADERS["strongs_hebrew"]()),
        ("Akkadian", LOADERS["akkadian_oracc"]()),
        ("Basque", load_control("eu")),
        ("Turkish", load_control("tr")),
        ("Arabic (frequency list)", load_control("ar")),
        ("Modern Hebrew (frequency list)", load_control("he")),
    ]
    if args.only:
        lexicons = [(n, l) for n, l in lexicons if any(o.lower() in n.lower() for o in args.only)]
    rows = []
    print(f"\n== {args.corpus}  protocol {PROTOCOL_VERSION}  words={len(words)}  perms={args.perms}  seed={args.seed}")
    print(f"{'lexicon, laryngeals stripped':<36} {'real':>8} {'null':>8} {'z':>7} {'se':>5} {'p':>7}")
    for name, lex in lexicons:
        lx = strip_lexicon(lex)
        for label, l2 in ((f"{name} (real)", lx), (f"{name} (synthetic)", synthetic_like(lx, args.seed))):
            r = run_one(label, smap, l2, words, freq, args.perms, args.seed)
            rows.append(r)
            print(f"{label:<36} {r['real']:>8.4f} {r['null_mean']:>8.4f} {r['z']:>+7.2f} {r['se_z']:>5.2f} {r['p']:>7.3f}", flush=True)

    tag = "" if not args.only else "-" + "-".join(o.lower().replace(" ", "_") for o in args.only)
    tag += ("" if args.seed == 0 else f"-seed{args.seed}") + ("" if args.perms == 100 else f"-p{args.perms}")
    out = ROOT / "results" / f"laryngeal_test-{args.corpus}{tag}.json"
    out.write_text(json.dumps({"protocol": {"version": PROTOCOL_VERSION,
                                             "change": "laryngeals removed from all lexicons and from vowel-sign options"},
                               "corpus": args.corpus, "n_words": len(words), "perms": args.perms,
                               "seed": args.seed, "rows": rows}, indent=2))
    print(f"\nwritten {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
