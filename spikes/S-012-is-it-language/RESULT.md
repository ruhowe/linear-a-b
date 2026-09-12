# S-012 result: is Linear A writing language at all, by the Indus-debate measures

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json`. Linear A: `aegean.load("lineara")`
(GORILA), whole corpus, 6,406 tokens (CLAUDE.md's scale constraint, reproduced here as
`sum(len(d.tokens) for d in corpus.documents)`). Linear B: `aegean.load("damos")`, full
corpus once and twenty tablet-model subsamples bisected to that same 6,406-token budget
(`kober.words.subsample_document_ids`, A-063's device) — achieved counts ranged 6,368 to
6,446 (635 to 752 documents), every seed within the 2% tolerance, worst relative error
0.62%. Two sequence-forming variants throughout: **line** (one sequence per document
line, boundary symbol between WORD tokens) and **word type** (`kober.words.extract_word_types`,
each distinct word once, no boundary). Both external references were reachable: NCBI
`NC_000913.3:1-20000` (a 20,000 bp *E. coli* K-12 fragment, 6,666 codons, public domain)
and Parker's 1894 *Glossary of Terms used in Heraldry* (4,516 blazons, public domain, via
karlwilcox.com/heraldry's open republication) — both cached at
`~/.cache/linear-a-b/reference/`, outside the repo per the licensing invariants.

## Table 1: the measures, line variant (bits unless noted)

Linear B matched and the five references are twenty seeded draws each; figures are
median [min, max]. Linear A and Linear B full are single deterministic values.

| measure | Linear A | Linear B matched | Linear B full | shuffled LB (ref 1) | iid, LA freq (ref 2) | Markov-1, LA fit (ref 3) | DNA codons (ref 4) | heraldic blazons (ref 5) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alphabet size | 159 | 84 [82, 89] | 104 | 84 [79, 89] | 136 [129, 143] | 136 [129, 142] | 64 [64, 64] | 817 [781, 869] |
| unigram entropy | 5.898 | 5.470 [5.401, 5.537] | 5.487 | 5.462 [5.392, 5.541] | 5.874 [5.838, 5.917] | 5.880 [5.835, 5.944] | 5.877 [5.848, 5.894] | 6.997 [6.937, 7.135] |
| cond. entropy, bigram MLE | 3.961 | 3.668 [3.436, 3.886] | 4.103 | 4.437 [4.308, 4.518] | 4.663 [4.632, 4.691] | 3.560 [3.512, 3.618] | 4.767 [4.748, 4.782] | 2.738 [2.640, 2.838] |
| cond. entropy, bigram add-half | 7.015 | 5.473 [5.273, 5.617] | 4.708 | 5.904 [5.808, 6.043] | 6.851 [6.759, 6.942] | 6.663 [6.556, 6.758] | 5.636 [5.629, 5.643] | 9.656 [9.589, 9.747] |
| ratio, cond./unigram, MLE | 0.671 | 0.670 [0.634, 0.705] | 0.748 | 0.810 [0.796, 0.822] | 0.794 [0.785, 0.803] | 0.605 [0.593, 0.620] | 0.811 [0.808, 0.816] | 0.391 [0.374, 0.404] |
| ratio, cond./unigram, add-half | 1.189 | 1.001 [0.974, 1.018] | 0.858 | 1.083 [1.064, 1.097] | 1.166 [1.155, 1.178] | 1.130 [1.112, 1.145] | 0.959 [0.956, 0.964] | 1.378 [1.366, 1.388] |
| block entropy n=2 | 9.696 | 9.098 [8.795, 9.360] | 9.547 | 9.883 [9.727, 10.017] | 10.518 [10.480, 10.564] | 9.428 [9.382, 9.485] | 10.638 [10.593, 10.670] | 9.648 [9.574, 9.792] |
| block entropy n=3 | 10.028 | 10.233 [9.797, 10.638] | 11.478 | 10.585 [10.516, 10.630] | 10.672 [10.663, 10.679] | 10.463 [10.418, 10.492] | 10.674 [10.660, 10.680] | 10.169 [10.103, 10.258] |
| block entropy n=4 | 9.430 | 10.398 [9.861, 10.877] | 12.229 | 9.901 [9.893, 9.905] | 9.905 [9.903, 9.905] | 9.891 [9.877, 9.903] | 9.905 [9.901, 9.905] | 9.813 [9.772, 9.843] |

Block entropy n=1 reproduces unigram entropy exactly in every group, as the two formulas
predict (a sliding window of length 1 is the unigram distribution); this is an internal
consistency check, not a separate row.

## Table 2: distance from Linear A, in units of Linear B matched's own twenty-seed spread (stdev)

| measure | to LB matched | to LB full | to ref 1 (shuffled LB) | to ref 2 (iid) | to ref 3 (Markov-1) | to ref 4 (DNA) | to ref 5 (blazons) |
|---|---:|---:|---:|---:|---:|---:|---:|
| unigram entropy | +10.05 | +9.63 | +10.23 | +0.58 | +0.42 | +0.50 | -25.73 |
| cond. entropy, MLE | +3.06 | -1.50 | -4.99 | -7.35 | +4.20 | -8.45 | +12.81 |
| cond. entropy, add-half | +15.01 | +22.44 | +10.81 | +1.60 | +3.43 | +13.42 | -25.69 |
| ratio, MLE | +0.11 | -5.36 | -9.74 | -8.58 | +4.64 | -9.81 | +19.72 |
| ratio, add-half | +14.21 | +24.98 | +8.00 | +1.74 | +4.46 | +17.37 | -14.25 |
| block entropy n=2 | +4.39 | +1.09 | -1.38 | -6.04 | +1.96 | -6.92 | +0.35 |
| block entropy n=3 | -1.02 | -7.26 | -2.79 | -3.22 | -2.18 | -3.23 | -0.71 |
| block entropy n=4 | -4.34 | -12.56 | -2.11 | -2.13 | -2.07 | -2.13 | -1.72 |

Negative means Linear A's value is below the comparison group's median (more predictable
/ lower entropy); positive means above.

## Word-type variant: corroboration, not a repeat

988 Linear A word types (A-038's >= 2-sign unit), Linear B matched at the same 6,406-token
budget, 3,768-word-type full Linear B. The pattern in Table 2 holds: ratio-MLE distance to
Linear B matched is +1.08 SD (LA 0.687 vs LB matched median 0.677 [0.666, 0.699]), block
n=3 is -1.13 SD (9.814 vs 9.921 [9.721, 10.091]), block n=4 is -2.15 SD (8.626 vs 8.894
[8.644, 9.095]) — all inside or just past Linear B's own noise floor, as in the line
variant. Block n=2 again departs further (+4.78 SD, 9.851 vs 9.619 [9.548, 9.741]), and
unigram entropy and add-half conditional entropy again separate Linear A from Linear B by
a wide margin (distance +9.76 SD and +21.55 SD) for the same reason given below. The two
ways of forming sequences agree on which measures separate Linear A from Linear B and by
roughly how much; neither is an artifact of the other.

## The alphabet-size artifact

Linear A's line-based alphabet is 159 signs; Linear B matched at the identical 6,406-token
budget attests only 84 (full Linear B, 38,563 tokens of running text, attests 104 — fewer
than Linear A's 6,406-token slice, despite six times the text). This is a corpus fact, not
a processing choice: Linear A carries many singly- or rarely-attested signs (undeciphered,
uncommon syllabograms) that a same-sized slice of Linear B does not. Two consequences
follow mechanically, independent of any linguistic property:

1. **Unigram entropy rises with attested alphabet size**, roughly toward log2(alphabet).
   Linear A's 5.898 bits sits close to the three references built to have no order at all
   (ref 2 iid 5.874, ref 3 Markov-1 5.880, ref 4 DNA 5.877, all near Linear A because their
   alphabets were fitted to Linear A's own 136-159-sign profile) and far from Linear B
   (5.470-5.487, alphabet 84-104) — a gap that reflects signary size, not word-order
   structure, since none of unigram entropy's inputs involve order.
2. **Add-half smoothing is dominated by alphabet size once alphabet² approaches sample
   size.** With delta=0.5, the smoothed grid adds `0.5 * alphabet²` synthetic mass: for
   Linear A's line variant that is 0.5 x 159² = 12,640, against roughly 2,896 real
   sign-bigram observations — over 80% synthetic. The result is pulled toward
   log2(alphabet) = 7.31 bits; Linear A's observed 7.015 is 96% of that ceiling. Linear B
   matched's own ceiling is only log2(84) = 6.39 bits, and its observed 5.473 is 86% of
   *that* lower ceiling. Both groups are pulled toward their own alphabet-size ceiling by
   the same mechanism; Linear A's ceiling is simply much higher, at this corpus scale,
   because its attested signary is. This is Sproat's objection made visible with a real
   positive control rather than argued in the abstract: naive additive smoothing at this
   sample size measures alphabet size at least as much as it measures word-formation
   structure, and reporting only the smoothed number (as Rao's original conditional-entropy
   figure did) would have been read as evidence against Linear A being language, when it is
   evidence about its signary.

The plain MLE conditional entropy and the MLE ratio are not immune to sample-size effects
either (both are known to be biased downward as alphabet size grows relative to sample
size — visible here in reference 5, whose 817-word alphabet against ~4,140 words gives an
implausibly low MLE conditional entropy, 2.738, and a correspondingly inflated add-half
ratio, 1.378, in the opposite direction from Linear A's), but they are far less sensitive
to it than raw unigram entropy or additive smoothing are, which is why Table 2's block-
entropy and MLE-ratio rows are weighted more heavily in the reading below.

## Reference reachability and caveats

- **Shuffled Linear B (ref 1)**: each of the twenty tablet-model draws, pooled in a
  seeded-shuffled order and cut to Linear A's own sequence-length list, each resulting
  chunk internally shuffled. Keeps Linear B's own unigram profile, destroys order.
- **iid from Linear A's own unigram frequencies (ref 2)** and **Markov-1 fitted to Linear
  A's own bigram counts (ref 3)**: both share Linear A's own alphabet by construction
  (136 vs Linear A's 159 — slightly smaller because a 20-seed sample does not always draw
  every hapax sign). Reference 3's own re-estimated MLE conditional entropy (3.560) is
  known to be biased low relative to the true generating model, since re-estimating MLE
  statistics from data sampled from a fitted model of similar size under-counts the
  model's real conditional entropy (a standard small-sample estimation bias) — the +4.20
  SD gap between Linear A and reference 3 on MLE conditional entropy should not be read as
  "Linear A exceeds first-order structure" on that number alone; the block-entropy n=3
  gap (-2.18 SD, Linear A *below* its own Markov-1 resample) is the more informative of
  the two, since block entropy is not subject to the same re-estimation bias in the same
  direction, and points toward Linear A carrying detectable structure beyond a
  bigram-only model rather than less.
- **DNA codons (ref 4)**: reached. NCBI `NC_000913.3` positions 1-20,000, a real *E. coli*
  genome fragment, not a designed gene selection — some of it is non-coding, so "codon"
  here means "nucleotide triplet," not necessarily an in-frame codon of an annotated gene.
  Twenty seeds rotate the 6,666-codon stream to a random start and slice without internal
  shuffling, preserving whatever real local structure the fragment carries.
- **Heraldic blazons (ref 5)**: reached, but the lowest-confidence reference. Parker's
  1894 glossary, tokenised word-for-word (lower-cased, boundary inserted only at a comma
  or semicolon in the source text) rather than by heraldic sign class (tincture / ordinary
  / charge), which this script does not attempt to reconstruct. Its resulting alphabet
  (781-869 distinct English words) is four to five times Linear A's, which is why its MLE
  and add-half figures are the most extreme in both tables. Treat this row as illustrative
  of what an unrelated, much larger-vocabulary formulaic genre looks like on these
  measures, not as a calibrated sign-system control at Linear A's own scale.

## Reading against the brief

**Nothing**, read carefully: on the measures least distorted by alphabet size (the MLE
ratio of conditional to unigram entropy, and block entropy at n=2 and n=3, all matched
either to Linear B directly or to references built on Linear A's own alphabet), Linear A
sits with Linear B within a few standard deviations of Linear B's own resampling noise
(ratio-MLE: +0.11 SD in the line variant, +1.08 SD in the word-type variant; block n=3:
-1.02 and -1.13 SD) and clearly separated from the references built to carry no order —
iid (-8.58 SD) and shuffled Linear B (-9.74 SD) on the MLE ratio, both directions confirmed
by block entropy n=2 and n=3. Linear A's real sign sequences are far more predictable than
chance permits, at a strength comparable to Linear B's, and this holds under both ways of
forming sequences, which is exactly the "gives the Indus debate a calibration point it
never had" reading the brief names as uninteresting-but-useful.

The two measures that instead put Linear A with the non-linguistic references — raw
unigram entropy and add-half-smoothed conditional entropy, the exact pairing Rao's
original paper reported and Sproat's critique targeted — do so for a diagnosed,
alphabet-size reason rather than an unexplained one: Linear A's signary is genuinely
larger than a same-sized slice of Linear B's, and naive additive smoothing at a sample
this small measures that signary size at least as much as it measures word-order
structure. Having Linear B as a real positive control at matched scale is what makes this
diagnosis possible rather than speculative, which is the addition this spike makes to the
Indus-debate method: the same reversal Sproat demonstrated with invented non-linguistic
controls reappears here on a script assumed to write language, from its own sibling
script's numbers, not from an argument about what a control should look like.

Must not be read as anything about which language Linear A writes, or as a finding: this
spike touches only aggregate sign-sequence statistics on both scripts, and BRIEF.md's
scope rule applies regardless of which reading came out ahead.
