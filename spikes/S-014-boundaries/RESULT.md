# S-014 result: Linear A's within-word predicted-boundary rate matches Linear B's at
matched size

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json`. Barber's independence test
(`docs/works/barber1974.md`, ch. IX) computed from each corpus's own text: for every
ordered sign pair, expected count under independence from the corpus's own single-sign
marginals against the observed in-word digram count, flagged as a predicted boundary at
factor 6 (Barber's own criterion) and, for sensitivity, 4 and 8. No pair set is
transferred between corpora — every corpus and every subsample rebuilds its own table
from its own text; what carries over from Barber's calibration is the choice of factor,
not any specific pair.

## Full corpora

| corpus | signs seen | in-word digrams | rate/1,000 at factor 4 | at factor 6 | at factor 8 |
|---|---:|---:|---:|---:|---:|
| Linear B (DĀMOS, full) | 103 | 23,416 | 27.37 | 13.28 | 7.47 |
| Linear A (GORILA) | 158 | 2,638 | 0.38 | 0.00 | 0.00 |
| Linear A (SigLA) | 157 | 1,736 | 0.58 | 0.00 | 0.00 |

## Linear B, twenty tablet-model subsamples at Linear A (GORILA)'s size

Target 2,638 in-word digrams (GORILA's own count); document count bisected per seed as
`scripts/kober_floor_sweep.py` bisects for word types, all twenty within the 2% tolerance
(k ranged 523-792 documents, mean 667, against 5,932 full corpus).

| factor | subsample min | subsample max | subsample mean | Linear A (GORILA) value | GORILA vs range |
|---|---:|---:|---:|---:|---|
| 4 | 0.379 | 4.108 | 2.025 | 0.379 | at the minimum |
| 6 | 0.000 | 0.753 | 0.113 | 0.000 | at the minimum (16/20 subsamples also 0) |
| 8 | 0.000 | 0.000 | 0.000 | 0.000 | matches exactly (degenerate range) |

At every factor, Linear A's within-word rate sits at or below the low end of Linear B's
own matched-size spread, never above it. Factor 8 finds no predicted-boundary digram
occurring within a word in any of the twenty Linear-B subsamples or in either Linear A
edition — a criterion too strict to say anything at this size. Factor 6, Barber's own
choice, finds a small but non-zero rate in 4 of 20 Linear B subsamples (0.38-0.75 per
1,000) and none in Linear A; factor 4 is the only one where every subsample and both
corpora register a non-zero rate, and Linear A still sits at the bottom of the range
rather than above it.

## Reverse check: real word-to-word boundaries (GORILA and Linear B full corpus)

At every point on a line where one eligible word ends and the next begins (SigLA excluded,
no line structure), the fraction of those real boundary pairs that the corpus's own
factor-6 predicted-boundary set also flags:

| corpus | actual boundary instances | fraction flagged at factor 4 | at factor 6 | at factor 8 |
|---|---:|---:|---:|---:|
| Linear B (DĀMOS, full) | 5,057 | 0.596 | 0.519 | 0.448 |
| Linear A (GORILA) | 129 | 0.496 | 0.496 | 0.496 |

Roughly half of real word boundaries are flagged as predicted boundaries in both scripts,
at every factor tested (GORILA's fraction happens to be identical across factors because
the small set of pairs crossing its 129 real boundaries doesn't change membership between
4, 6 and 8 at this size). The two corpora's hit rates sit within about seven points of
each other; neither shows the criterion working much better or worse on real dividers
than on the other script's.

## Reading against the brief

**Nothing**, in the brief's own terms: the rates match. Linear A does not show more
within-word predicted boundaries than Linear B at matched size at any of the three
factors — at factor 6, Barber's own criterion, Linear A's rate (0.00 per 1,000) sits
exactly at the bottom of Linear B's twenty-subsample range (0.00-0.75, mean 0.11), tied
with sixteen of the twenty subsamples rather than exceeding any of them. Factor 4 shows
the same pattern more clearly since it is the only threshold with no zero values to tie
on: Linear A's 0.38 is closest to the range's own minimum (0.379), nowhere near its mean
(2.02) or maximum (4.11). If dividers under-segment Linear A relative to Linear B, this
statistic does not see it, at any of the three factors tried.

The reverse check adds a second negative: real word boundaries are flagged by the
factor-six criterion about as often in Linear A (49.6%) as in Linear B (51.9%), so the
criterion is not silently failing on Linear A's own dividers relative to Linear B's — it
performs the same middling job (catching roughly half of real boundaries while also, per
the within-word rates above, rarely firing inside a word) on both scripts. Read alongside
the within-word result, the honest summary is that Barber's digram test is not sensitive
enough at Linear A's size to distinguish it from a Linear-B corpus of matched size, in
either direction — a small-sample floor, not evidence that the dividers are right or
wrong.

Must not be read as a re-segmentation of any text: no word division in either corpus was
touched or proposed here, only the corpus-level rate of a diagnostic statistic.
