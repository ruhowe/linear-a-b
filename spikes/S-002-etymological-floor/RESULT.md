# S-002 result: the etymological method's own floor

Run 2026-09-12. `run.py`, protocol 1.0 unchanged, Greek map, three real lexicons
(Greek archaic, Finnish, Sumerian ePSD2), 400-word protocol sample, 100
permutations, protocol seed 0. Twenty tablet-model subsample seeds (0-19) at
targets 988 and 1,875 word types; the 2,750 target and the full corpus both
collapse to the identical full-corpus run, for the reason below. Aggregate
numbers only, in `results.json`.

**The pool ceiling.** Protocol 1.0's own word pool (WORD, CERTAIN, 2 to 4
signs, covered by both the Greek and Semitic consonant maps) on the full,
unsubsampled Linear B corpus is **2,548** word types, not 3,768. The 3,768
figure used elsewhere in this repo for size-matching (F-022, claims.md) counts
differently: any word of 2 or more signs, no map-coverage filter, via
`kober.words.extract_word_types`. A document subsample's pool can only be
smaller than or equal to the full corpus's own pool, so a target of 2,750 or
3,768 is unreachable by subsampling at every seed, and bisection falls back to
every document in the corpus. `word_sample` on the same corpus at the same
protocol seed then draws the identical 400 words, so the 2,750 row (all 20
nominal subsamples) and the full-corpus row are one run repeated, not
twenty-one independent ones. `run.py` detects this and reuses the single
computed result rather than repeating the permutation work.

## Results by size

| target size | pool (median, range) | Greek z (median, range) | Finnish z (median, range) | Sumerian z (median, range) | Greek's lead over the better wrong language, z (median, range) | lead, per-word gap (median, range) | count of 20 with z-lead ≥ 2 |
|---|---|---|---|---|---|---|---|
| 988 | 988 (983-994) | +2.65 (+1.21 to +3.94) | +1.95 (+0.88 to +2.89) | +1.10 (-0.68 to +2.19) | +0.63 (-0.64 to +1.65) | +0.083 (+0.040 to +0.146) | 0 / 20 |
| 1,875 | 1,875 (1,871-1,879) | +2.51 (+0.79 to +3.42) | +1.95 (+0.45 to +3.06) | +0.84 (-0.28 to +2.53) | +0.64 (-0.58 to +1.30) | +0.075 (+0.016 to +0.120) | 0 / 20 |
| 2,750 (unreachable; full corpus reused for all 20 seeds) | 2,548 (fixed) | +2.78 | +2.25 | +2.31 | +0.47 | +0.085 | 0 / 20 |
| "3,768" (the full corpus, one run) | 2,548 | +2.78 | +2.25 | +2.31 | +0.47 | +0.085 | 0 / 1 |

"z-lead ≥ 2" reads BRIEF.md's "two standard errors" as two z units, stated here
because the brief does not fix which of the two a standard error means in this
context.

Every lead, at every size, sits below 2. At 988 and 1,875 the range even
crosses zero (Greek scoring *below* the better of Finnish and Sumerian in 1 of
20 and 2 of 20 subsamples respectively), which is noise around a small median
lead, not a trend. The per-word gap lead is small and stable across sizes,
around 0.07 to 0.09, showing no growth from 988 word types up to the full
corpus.

## Reading against the brief

**Nothing.** No subsample, at any size from 988 word types to the full corpus,
separates Greek from the better of Finnish and Sumerian by two z units or more
(0 of 20 at 988, 0 of 20 at 1,875, 0 of 20 at 2,750, 0 of 1 at the full
corpus), matching the brief's stated expectation exactly. The instrument's
floor for this separation exceeds the whole of Linear B, which is a sharper
statement than "cannot choose a language": more Linear B, at the corpus's own
current size, does not move Greek's lead over the wrong real-language controls
at all, let alone past a two-unit bar. The pool-ceiling finding sets the actual
upper bound this spike could test: protocol 1.0's dual-map-covered pool on
Linear B never exceeds 2,548 word types, so "the full corpus" and "2,750 word
types" were never two different tests here, they are the same test named
twice.
