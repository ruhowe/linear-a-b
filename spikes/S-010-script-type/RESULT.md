# S-010 · Result

Ran `fetch.py` then `run.py` (2026-09-12). Full numbers in `results.json`
(aggregate only, per spikes/README.md rule 6 — no sign labels, no word lists,
no corpus text). Reference corpora and how their tokens were formed are recorded
in `~/.cache/linear-a-b/reference/script-types/README.md`.

## Method, as actually run

- **Target size.** The brief says "Linear A's token count of about 6,400 signs".
  corpus-sources.md's own measured figures show the "6,406" CLAUDE.md quotes is a
  word-level Token count, not a sign-occurrence count (GORILA's actual
  CERTAIN-WORD sign count is 4,011; SigLA's is 3,379). Rather than resolve which
  the brief meant, every reference was subsampled to a fixed 6,400 *sign* tokens
  — the round number both documents already use as shorthand for "Linear A's
  scale" — and Linear A itself (both editions) was measured at full size,
  unsampled, since it is the subject, not one of the six references being
  matched to it.
- **Subsampling**, 20 seeds (0-19) per reference: Linear B by the tablet model
  (documents in a random order, accumulated to >= the target, mirroring
  `scripts/kober_floor_sweep.py`); the other six by contiguous chunks of each
  corpus's own word stream, a random start point per seed, wrapping around the
  stream's end for the five references smaller than 128,000 signs (all but
  Sumerian, Egyptian and Greek — stated per the brief's requirement, not hidden).
- **Kober-grid signature**, built directly from the brief's description, not
  `src/kober/grid.py` (which is specific to Linear B's stem/ending model and
  Linear B's own known consonant values — inapplicable to an unknown or foreign
  script). Word *types* in a subsample are grouped by (length, all positions but
  one); every pair sharing such a group differs at exactly that one position and
  contributes a weighted edge between the two differing signs. Classes are the
  edge graph's connected components (union-find); "modularity" is Newman's Q for
  that partition. The shuffled control independently permutes each position's
  column of signs within each word-length class (20 draws), destroying
  cross-position co-occurrence while keeping each position's own sign frequency.
- **Distance**: per statistic, `(Linear A value − reference mean) / reference sd`
  across that reference's 20 subsamples; pooled distance is the RMS of the ten
  per-statistic z-scores with a usable (non-zero) sd. A reference with very low
  natural subsample variance (Greek, whose 563,230-sign corpus barely varies chunk
  to chunk) turns any real difference into a large z-score — this is the
  standardisation the brief asks for, not a bug, but it means pooled distances are
  only comparable as a *ranking*, not on a shared absolute scale.
- **Noise floor**: for every reference, each of its own 20 subsamples' pooled
  distance from that reference's own aggregate (same formula used against Linear
  A) — how far pure subsampling noise alone moves a same-population sample.

## Statistics per corpus (mean ± population sd across 20 subsamples; Linear A at full corpus size)

| statistic | linear_b | ugaritic | sumerian | akkadian | egyptian | chinese | greek | GORILA (full) | SigLA (full) |
|---|---|---|---|---|---|---|---|---|---|
| sign inventory @ ~6400 signs | 87 ± 3 | 30 ± 1 | 612 ± 66 | 2421 ± 56 | 340 ± 52 | 825 ± 46 | 26 ± 0 | 158 | 157 |
| Heaps beta | 0.150 ± 0.020 | 0.073 ± 0.033 | 0.539 ± 0.055 | 0.876 ± 0.025 | 0.481 ± 0.061 | 0.647 ± 0.040 | 0.031 ± 0.016 | 0.339 | 0.317 |
| sign hapax share | 0.088 ± 0.035 | 0.005 ± 0.012 | 0.332 ± 0.038 | 0.649 ± 0.009 | 0.275 ± 0.035 | 0.407 ± 0.022 | 0.000 ± 0.000 | 0.361 | 0.350 |
| word length (signs), mean | 3.326 ± 0.047 | 2.771 ± 0.079 | 2.266 ± 0.117 | 1.385 ± 0.023 | 2.821 ± 0.163 | 1.000 ± 0.000 | 5.010 ± 0.070 | 2.921 | 2.057 |
| Zipf slope (top 50) | -0.620 ± 0.018 | -1.215 ± 0.101 | -0.569 ± 0.046 | -0.768 ± 0.036 | -0.975 ± 0.047 | -0.853 ± 0.028 | -1.133 ± 0.022 | -0.661 | -0.611 |
| positional entropy: first (bits) | 5.107 ± 0.048 | 4.358 ± 0.057 | 7.576 ± 0.202 | 9.557 ± 0.129 | 5.952 ± 0.296 | 7.590 ± 0.138 | 3.921 ± 0.057 | 5.553 | 5.820 |
| positional entropy: medial (bits) | 5.617 ± 0.032 | 4.279 ± 0.122 | 6.549 ± 0.284 | 7.095 ± 0.101 | 5.806 ± 0.157 | n/a (no words ≥3 signs) | 4.103 ± 0.010 | 5.509 | 5.521 |
| positional entropy: last (bits) | 4.913 ± 0.037 | 3.901 ± 0.117 | 7.263 ± 0.167 | 9.657 ± 0.108 | 5.282 ± 0.372 | 7.590 ± 0.138 | 3.176 ± 0.035 | 5.766 | 6.060 |
| bigram cond. entropy, ML (bits) | 3.813 ± 0.070 | 3.182 ± 0.172 | 2.368 ± 0.182 | 2.903 ± 0.082 | 3.049 ± 0.188 | n/a (no bigrams) | 3.380 ± 0.017 | 3.887 | 3.754 |
| bigram cond. entropy, add-half (bits) | 5.280 ± 0.066 | 3.525 ± 0.167 | 8.575 ± 0.279 | 8.504 ± 0.127 | 7.526 ± 0.439 | n/a | 3.572 ± 0.015 | 6.599 | 6.118 |
| Kober-grid modularity | 0.000 ± 0.001 | 0.000 ± 0.000 | 0.006 ± 0.004 | 0.452 ± 0.203 | 0.050 ± 0.043 | n/a | 0.000 ± 0.000 | 0.021 | 0.001 |
| Kober-grid classes, mean n | 1.1 ± 0.2 | 1.0 ± 0.0 | 7.5 ± 2.4 | 22.2 ± 3.8 | 9.2 ± 2.8 | 0.0 ± 0.0 | 1.0 ± 0.0 | 4 | 2 |

Chinese has no medial/bigram/grid entries because every "word" is one character
by construction (tokens are characters, per the brief) — there is no second
sign to condition on. This makes Chinese the each-sign-is-a-word calibration
case for the word-length row, not a gap in the method.

## Distance of Linear A from each reference

| reference | pooled distance: GORILA | pooled distance: SigLA | n stats used | self noise floor (mean, max) |
|---|---:|---:|---:|---|
| egyptian | 2.98 | 3.58 | 10/10 | 0.92, 2.32 |
| sumerian | 6.12 | 5.46 | 10/10 | 0.90, 2.52 |
| chinese | 10.07 | 9.39 | 5/5 | 0.96, 1.79 |
| linear_b | 15.67 | 14.83 | 10/10 | 0.94, 1.69 |
| ugaritic | 15.58 | 16.36 | 9/9 | 0.94, 1.63 |
| akkadian | 29.76 | 22.59 | 10/10 | 0.98, 1.37 |
| greek | 93.38 | 86.47 | 8/8 | 0.96, 1.68 |

Both GORILA and SigLA rank the seven references identically: Egyptian closest,
then Sumerian, then Chinese, then Linear B and Ugaritic close together, then
Akkadian, then Greek by a wide margin. The two editions disagree in the
literature over roughly a third of their overlapping documents (linearb-restoration.md
HENGE, F-023), so this ranking replicating across both is the strongest evidence
in this spike, stronger than either edition's number on its own.

## Reading against the brief

**Linear A sits nearest a non-syllabic reference — Egyptian, the mixed
logogram/phonogram/determinative system — by a margin larger than every
reference's own self-noise floor, replicated on both independent editions.**
That is the brief's own "Interesting" criterion, stated almost verbatim. Egyptian's
pooled distance (2.98 GORILA, 3.58 SigLA) is roughly a third of the next-closest
non-syllabic reference (Sumerian, another mixed logosyllabic system, 5.46-6.12)
and about a fifth of Linear B's own distance (14.83-15.67) — and Linear B is the
system Linear A is conventionally assumed to resemble. The margin is not huge in
absolute terms (Egyptian's distance is only about 1.3-1.9x the largest
single-subsample self-noise floor seen anywhere, Sumerian's 2.52), so this reads
as a real but moderate signal at this corpus size, not a decisive break — exactly
the caution the brief's own "Nothing" clause anticipates, without quite landing
there, since Egyptian is not merely "equidistant among several" but consistently
and by some margin the nearest, on both editions.

**The each-sign-a-word hypothesis is excluded outright.** GORILA's mean word
length is 2.92 signs (median 3), SigLA's is 2.06 (median 2); Chinese, built here
as the literal calibration case (word = one character, by construction), has mean
1.00 with zero variance. Neither Linear A edition is remotely close to that. The
edition gap itself matters here: SigLA carries 695 one-sign "words" (42% of its
1,643) where GORILA's loader yields none at all (`aegean.scripts.linearb.loader`-
style tokenizers, reused for both editions here, only emit `WORD` when a token
contains a hyphen — see `fetch.py`'s `_build_from_aegean_corpus` docstring), so
SigLA's shorter mean is partly a tokenizer artefact, not only a codicological
fact, and even taking it at face value it is still nearly double the one-sign
prediction. Inventory size tells the same story from the other side: a genuine
one-sign-per-word system needs an inventory approaching the running word count
(Chinese: 825 distinct characters in a 6,400-character/word window, one new
character roughly every 8 tokens); Linear A's inventory (158 GORILA, 157 SigLA)
grows far more slowly than its running sign count (4,011 / 3,379) — a Heaps beta
of 0.32-0.34, in between Ugaritic's alphabet-like 0.07 and the logographic/
logosyllabic references' 0.48-0.88. Both the length and the inventory checks the
brief asks for agree, and agree with each other, in ruling this reading out.

**The Kober-grid signature did not behave as the brief's own worked example
predicted, on the positive control.** A CV syllabary is supposed to show real
consonant/vowel classes here; Linear B's own modularity (0.000 ± 0.001, mean 1.1
classes across 20 subsamples) is statistically indistinguishable from the two
pure alphabets (Ugaritic and Greek, both 0.000 ± 0.000) rather than standing apart
from them, at this method and this corpus size. Only Akkadian (0.452 ± 0.203, ~22
classes) and, more weakly, Egyptian (0.050 ± 0.043, ~9 classes) and Sumerian
(0.006 ± 0.004, ~7 classes) show real structure — logosyllabic systems, not the
syllabary this signature was supposed to flag. This generic version (any
position, not just the ending position `src/kober/grid.py` restricts to) is
plausibly too permissive: at Linear B's own scale it forms one large connected
component rather than separated classes, the same failure mode already recorded
independently for the ending-restricted version at this corpus size (F-026,
"Kober 0.4 fails; slot context is uninformative on Linear B"; F-027 replicates
Kober's own scale-dependent result on Greek). Linear A's own grid modularity
(0.021 GORILA, 0.001 SigLA) sits inside the alphabet/Linear-B band, not the
logosyllabic one — which, read alongside the other nine statistics pointing at
Egyptian, is at least consistent rather than contradictory, but this one
statistic should not be leaned on alone; it did not do its job on the corpus
where the answer is already known.

**Overall reading.** On the statistics that behaved as expected (inventory
growth, hapax share, word length, positional and bigram entropy, Zipf slope),
Linear A sits closer to a mixed logogram/phonogram/determinative system than to
the CV-syllabary reading the main line assumes throughout — a result that, if it
held up under a rebuild (spikes/README.md rule 5), would put a genuine open
question in front of A-040 rather than confirm it. It must not be read as, and is
not being read as, a claim about which language Linear A writes (Kober 1948, p.
101, quoted in the brief) — nothing here touches values, only sign-identity
statistics, consistent with the CLAUDE.md invariant against treating Linear A's
Linear-B-convention transliteration as phonological evidence.
