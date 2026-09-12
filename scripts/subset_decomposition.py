#!/usr/bin/env python3
"""Subset decomposition under one null: the valid form of a sign-set sensitivity.

    .venv/bin/python scripts/subset_decomposition.py --seed 0 --write

Protocol 1.0's null recomputes its frequency bands from the sampled words, so any flag
that restricts the pool (`--secure-signs-only`, `--non-secure-only`) changes the null as
well as the words, and the resulting z is not comparable with the full-sample z. This
script draws the protocol 1.0 sample and its 100 permuted maps once, then scores the
same maps on the full sample and on its secure-only and non-secure subsets. The gap
(real minus null mean) is per word and comparable across subsets; z is not, because the
null sd grows as the subset shrinks. Written for FINDINGS F-014 after the restricted-pool
runs were found to be confounded. Assumptions: A-001, A-010, A-042.
"""
from __future__ import annotations
import argparse, json, random, statistics, collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
import aegean
from controlled_comparison import word_sample, statistic
from hypotheses.lexicons import LOADERS
from hypotheses.phonologies import build_map
from hypotheses.run import frequency_matched_permute
from hypotheses.secure_signs import SECURE_SIGNS
from semitic_null.phonology import ConsonantMap
from unrelated_controls import load_control

corpus = aegean.load("lineara"); inv = corpus.sign_inventory
upper = lambda m: ConsonantMap({k.upper(): v for k, v in m.mapping.items()})
gmap = upper(build_map(inv, "greek_syllabic")); smap = upper(build_map(inv, "semitic_consonantal"))
ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--perms", type=int, default=100)
ap.add_argument("--write", action="store_true"); args = ap.parse_args(); seed = args.seed
words = word_sample(corpus, [gmap, smap], 400, seed)
sec = [w for w in words if all(s in SECURE_SIGNS for s in w)]
non = [w for w in words if not all(s in SECURE_SIGNS for s in w)]
print(f"seed {seed}: full {len(words)}, secure-only {len(sec)}, non-secure {len(non)}")
freq = collections.Counter(s for w in words for s in w)
lexicons = [("Hebrew", smap, LOADERS["strongs_hebrew"]()), ("Basque", smap, load_control("eu")),
            ("Turkish", smap, load_control("tr")), ("Greek archaic", gmap, LOADERS["greek_archaic"]())]
out = []
for name, cmap, lex in lexicons:
    rng = random.Random(seed)
    perms = [frequency_matched_permute(cmap, rng, freq) for _ in range(args.perms)]
    row = []
    for label, ws in (("full", words), ("secure", sec), ("non-secure", non)):
        real = statistic(cmap, lex, ws)
        nulls = [statistic(p, lex, ws) for p in perms]
        m, sd = statistics.fmean(nulls), statistics.pstdev(nulls)
        row.append(f"{label} z={(real-m)/sd:+.2f} (gap {real-m:+.4f}, sd {sd:.4f})")
        out.append({"lexicon": name, "map": "semitic" if cmap is smap else "greek", "subset": label, "n_words": len(ws),
                    "real": real, "null_mean": m, "null_sd": sd, "gap": real - m, "z": (real - m) / sd if sd else 0.0})
    print(f"{name:<14}", " | ".join(row))

if args.write:
    p = ROOT / "results" / f"subset_decomposition-lineara-seed{seed}.json"
    p.write_text(json.dumps({"protocol": {"version": "1.0", "variant": "subset decomposition, one null"},
                             "seed": seed, "perms": args.perms, "n_full": len(words), "n_secure": len(sec),
                             "n_non_secure": len(non), "rows": out}, indent=2))
    print("written", p.relative_to(ROOT))
