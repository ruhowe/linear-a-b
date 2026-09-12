#!/usr/bin/env python3
"""Run additional lexicons through the frozen instrument, real and synthetic, per corpus.

    .venv/bin/python scripts/extra_lexicons.py --corpus lineara greek_lsj:greek
    .venv/bin/python scripts/extra_lexicons.py --corpus damos greek_lsj:greek ugaritic:semitic

Each argument is ``loader:map`` where the loader is a key in `hypotheses.lexicons.LOADERS`
and the map is ``greek`` or ``semitic``. Nothing about the instrument changes; this only
adds rows. The synthetic twin is always run alongside, because a real lexicon's z is only
readable against its own shape-matched control under the same map.

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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import aegean  # noqa: E402

from controlled_comparison import run_one, synthetic_like, word_sample  # noqa: E402
from hypotheses.lexicons import LOADERS  # noqa: E402
from hypotheses.phonologies import build_map  # noqa: E402
from hypotheses.secure_signs import SECURE_SIGNS  # noqa: E402
from semitic_null.phonology import ConsonantMap  # noqa: E402

MAPS = {"greek": "greek_syllabic", "semitic": "semitic_consonantal"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+", help="loader:map, e.g. greek_lsj:greek")
    ap.add_argument("--corpus", choices=["damos", "lineara"], default="lineara")
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
    args = ap.parse_args()

    corpus = aegean.load(args.corpus)
    inv = corpus.sign_inventory
    upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})  # noqa: E731
    maps = {k: upper(build_map(inv, v)) for k, v in MAPS.items()}
    secure = SECURE_SIGNS if args.secure_signs_only else None
    words = word_sample(corpus, list(maps.values()), args.words, args.seed, secure,
                         non_secure_only=args.non_secure_only)  # identical sample, restricted
    freq = collections.Counter(s for w in words for s in w)

    rows = []
    print(f"\n== {args.corpus}  words={len(words)}  perms={args.perms}  seed={args.seed}")
    print(f"{'lexicon':<40} {'types':>6} {'real':>8} {'null':>8} {'z':>7} {'se':>5} {'p':>7}")
    for spec in args.specs:
        loader_name, map_name = spec.split(":")
        lex = LOADERS[loader_name]()
        cmap = maps[map_name]
        for label, lx in ((f"{loader_name} / {map_name} (real)", lex),
                          (f"{loader_name} / {map_name} (synthetic)", synthetic_like(lex, args.seed))):
            r = run_one(label, cmap, lx, words, freq, args.perms, args.seed)
            r["types"] = lex.n_entries
            rows.append(r)
            print(f"{label:<40} {lex.n_entries:>6} {r['real']:>8.4f} {r['null_mean']:>8.4f} "
                  f"{r['z']:>+7.2f} {r['se_z']:>5.2f} {r['p']:>7.3f}", flush=True)

    tag = "-".join(s.split(":")[0] for s in args.specs)
    tag += ("" if args.seed == 0 else f"-seed{args.seed}") + ("" if args.perms == 100 else f"-p{args.perms}")
    if args.secure_signs_only:
        tag += "-secure25"
    if args.non_secure_only:
        tag += "-nonsecure"
    out = ROOT / "results" / f"extra_lexicons-{args.corpus}-{tag}.json"
    out.write_text(json.dumps({"corpus": args.corpus, "n_words": len(words), "perms": args.perms,
                               "seed": args.seed, "secure_signs_only": args.secure_signs_only,
                               "non_secure_only": args.non_secure_only, "rows": rows}, indent=2))
    print(f"\nwritten {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
