# S-013 result: reversing one support type's words does not raise the paradigm ratio

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json`. Stem_min 2, 100 draws per
N1 null, primary seed 0, noise measured over seeds 0-19. `PYTHONHASHSEED=0` is pinned by
the script (it re-executes itself once if unset) because `kober.nulls._group_by_length`
groups words by length via a dict built from `frozenset` iteration order, which depends
on Python's per-process string hash randomisation, not the seed argument: two runs of
this script gave different numbers before that was pinned down, confirmed by diffing
`results.json` across runs. This is a latent gap in `src/kober/nulls.py`'s own
reproducibility claim, not fixed here (nothing under `src/` is touched by a spike); it is
worth a CHANGELOG/ASSUMPTIONS note on its own.

Sanity check first: reversing every word in the corpus (documents ungrouped, S-001's
whole-corpus mirror) reproduces the unreversed corpus's prefix channel exactly, both
corpora, both by paradigm count (707 = 707 on Linear B, 88 = 88 on Linear A) and by the
full alternation-support table once each ending is reversed back to real orientation
(`matches_baseline_prefix_alternation_support_exactly: true`, both corpora) — F-037's
bijection, confirmed independently of S-001's own Linear B run and extended here to
Linear A for the first time.

## Qualifying support types (>= 50 eligible word tokens)

| corpus | support type | tokens |
|---|---|---:|
| Linear B | tablet | 9,894 |
| Linear B | nodule, sealed | 115 |
| Linear B | stirrup jar | 62 |
| Linear A | tablet | 848 |
| Linear A | stone vessel | 259 |
| Linear A | roundel | 69 |
| Linear A | clay vessel | 59 |

## Ratio (ending-channel paradigm count / N1 null mean), seed 0, against the unreversed
baseline and its 20-seed noise

| corpus | condition | ratio | change vs baseline | change in noise-sd units |
|---|---|---:|---:|---:|
| Linear B | baseline (unreversed) | 1.5283 | — | — |
| Linear B | nodule, sealed reversed | 1.5310 | +0.0027 | +0.84 |
| Linear B | stirrup jar reversed | 1.5287 | +0.0003 | +0.10 |
| Linear B | tablet reversed | 1.1327 | −0.3957 | **−122.37** |
| Linear A | baseline (unreversed) | 1.5268 | — | — |
| Linear A | clay vessel reversed | 1.5252 | −0.0016 | −0.18 |
| Linear A | roundel reversed | 1.5183 | −0.0086 | −0.94 |
| Linear A | stone vessel reversed | 1.4281 | −0.0987 | **−10.84** |
| Linear A | tablet reversed | 1.5124 | −0.0144 | −1.58 |

Baseline noise (population sd of the ratio across 20 N1 seeds, same unreversed word set):
Linear B 0.00323, Linear A 0.00910 — both far smaller than the paradigm counts they are
measuring noise around, which is what makes the "tablet" and "stone vessel" changes
readable as real rather than as seed noise.

## Reading against the brief

**Nothing**, in the brief's own terms: no support type's reversal raises the ratio above
the unreversed corpus's own ratio, on either corpus, at any margin beyond noise. Two of
three Linear B support types and three of four Linear A support types move by under one
noise-sd in either direction — reversing a minority support type's words does not
measurably change the ending channel's structure. The two large moves are both drops, not
rises: reversing Linear B's "tablet" documents (98% of the corpus's eligible tokens) pulls
the ratio down by 122 noise-sd units, because at that share the corpus is close to the
S-001 all-reversed condition and the statistic is sliding toward the (lower) prefix-channel
ratio, not toward a stronger ending-channel signal. Reversing Linear A's "stone vessel"
documents (259 of 1,373 tokens, the largest non-tablet group) drops the ratio by nearly 11
noise-sd units for the same reason at smaller scale — a real, measurable effect, but a
weakening, the opposite of what "interesting" requires.

No support type on either corpus shows the signature the brief set out to detect: a rise
in structure from reversal. The result answers the question stated in the brief's "must
not be read as" already — it is a consistency check on the transcription, not a claim
about how any inscription was actually read — and the consistency check comes back clean
for every minority support type tested, on both scripts.
