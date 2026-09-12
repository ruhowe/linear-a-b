# S-003b result: Packard's Knossos toponym test, values permuted at every position

Ran 2026-09-12. Protocol version: n/a (spike, not main line). Code: `run.py`. Raw
numbers: `results.json`. Lexicon sources and per-entry provenance: reused unchanged from
S-003, cached at `~/.cache/linear-a-b/reference/s003-knossos-lexicons.json`
(corpus-derived, outside the repo per corpus-sources.md).

## Lexicons

Unchanged from S-003: 32 of 33 candidate Knossos toponyms attested as WORD/CERTAIN types
in DAMOS (`di-ka-ta` dropped, only `di-ka-ta-de`/`di-ka-ta-jo` attested), and a 32-entry
personal-name control, the most frequent non-toponym WORD/CERTAIN types on the Knossos
Da-Dv sheep series. See S-003's RESULT.md for the full construction; `run.py` here loads
S-003's `run.py` as a module and calls its lexicon functions directly rather than
re-deriving them.

## Sign inventory and bands

Labels occurring in a 3+-sign Linear A WORD/CERTAIN type that are also a Linear B sign
label (the set eligible for a value assignment): 53 on GORILA (607 3+-sign word types),
55 on SigLA (443 word types). Every one of these labels is a syllabogram in the Linear B
sign inventory; the overlap includes no ideogram, symbol or monogram label on either
edition. Ranked by whole-corpus WORD/CERTAIN token frequency (not the 3+-sign subset)
and split into contiguous bands of ten:

- GORILA: `[10, 10, 10, 10, 10, 3]`
- SigLA: `[10, 10, 10, 10, 10, 5]`

and, as a sensitivity, four contiguous near-equal bands:

- GORILA: `[14, 13, 13, 13]`
- SigLA: `[14, 14, 14, 13]`

The last groups-of-ten band on both editions is smaller than ten, which matters only for
the Packard nine-rotation reproduction below: a rotation by k where k is a multiple of
that band's own size leaves it at identity for that one decipherment (k = 3, 6, 9 on
GORILA's 3-sign band; k = 5 on SigLA's 5-sign band). It does not affect the 200-draw
permutation null, which draws an independent random permutation per band regardless of
size.

## Match counts

**GORILA**, groups of ten:

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile | Packard 9-rotation mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 6 | 0.80 | 1.14 | 3.0 | 5.0 | 100.0 | 0.67 |
| toponyms | 4= | 3 | 0.00 | 0.00 | 0.0 | 0.0 | 100.0 | 0.00 |
| personal names (control) | 3= | 1 | 0.76 | 1.08 | 3.0 | 3.0 | 67.0 | 0.33 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 | 0.00 |

**GORILA**, four bands (sensitivity):

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile |
|---|---|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 6 | 0.69 | 1.02 | 2.0 | 4.0 | 99.5 |
| toponyms | 4= | 3 | 0.01 | 0.07 | 0.0 | 0.0 | 100.0 |
| personal names (control) | 3= | 1 | 0.49 | 0.85 | 2.0 | 3.0 | 78.0 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 |

**SigLA**, groups of ten:

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile | Packard 9-rotation mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 5 | 0.51 | 0.73 | 2.0 | 3.0 | 100.0 | 0.44 |
| toponyms | 4= | 1 | 0.00 | 0.00 | 0.0 | 0.0 | 100.0 | 0.00 |
| personal names (control) | 3= | 0 | 0.35 | 0.62 | 1.0 | 3.0 | 35.2 | 0.22 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 | 0.00 |

**SigLA**, four bands (sensitivity):

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile |
|---|---|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 5 | 0.49 | 0.77 | 2.0 | 3.0 | 100.0 |
| toponyms | 4= | 1 | 0.00 | 0.00 | 0.0 | 0.0 | 100.0 |
| personal names (control) | 3= | 0 | 0.28 | 0.58 | 1.0 | 2.0 | 38.8 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 |

**Packard 1974, Table 14, p.98** (nine random decipherments, Knossos names only, for
comparison, not recomputed here):

| class | Linear B values | mean of his 9 random |
|---|---:|---:|
| 3 equal | 13 | 3.0 |
| 4 signs equal | 2 | 0.0 |

His mean of 3.0 for the 3-equal class sits close to this run's 200-draw null means
(0.51 to 0.80 across editions and band structures) once every position, not just the
third, is put under the null: the nine-rotation reproduction above gives 0.22 to 0.67,
lower still than his own reported 3.0. The gap between Packard's 3.0 and this run's
nine-rotation reproduction of his own scheme (0.22 to 0.67) is not explained by corpus
differences, since the reproduction uses the current GORILA and SigLA corpora directly;
it is explained by his 34-word alternation appendix (a different evidence class,
pp. 75-80) being conflated with the Table 14 name-matching figures in places the archive.org text
scrambled, or by his nine hand-built decipherments differing in some mechanical detail
this reconstruction does not capture. Either way, the 200-draw null is the number to
read, not the nine-rotation reproduction, which is reported only so his own figure has
something exact to sit beside.

## Reading against the brief

**Interesting.** On both editions and both band structures, the real toponym count
clears the null's 99th percentile: 100.0th percentile in three of four cases and 99.5th
in the fourth (GORILA, four-band sensitivity, 3=), against a personal-name control that
never rises above its own 78th percentile anywhere in the table. The six GORILA 3=
matches are `da-ta-ra` and `da-ta-re` against `da-ta-ra-mo`, and three exact
Linear A/B identities long noted in the field: `pa-i-to` (Phaistos), `se-to-i-ja`, and
`su-ki-ri-ta` (the last matching twice, once exactly and once against a longer Linear A
form sharing its first three signs). The three GORILA 4= matches are the same
`se-to-i-ja` and `su-ki-ri-ta` identities plus one consonant-level match on a longer
`su-ki-ri-ta`-prefixed form.

This reverses S-003's "nothing" verdict, which the review at the foot of S-003's own
RESULT.md had already withdrawn: that run's null fixed the first two sign positions as a
corpus fact and only let the third vary, handing the null most of the real count before
a single draw was taken. Here every position of every word is read through the current
value assignment, real or null, so a null draw has to earn all of its identical
positions by chance exactly as the real (identity) assignment does. Under that
corrected construction the toponym match count holds up on both the current GORILA
corpus and the independently-annotated SigLA edition, and the personal-name control,
matched for site, script and lexicon size, does not separate from its own null on
either edition or match class.

**Caveat.** The match criterion in this run is literal label identity at the fixed
positions (Packard's own "3="/"4=" definition, Table 14) with a shared-consonant
allowance only at the one differing position. Packard's own hand-collected matches
(docs/works/packard1974.md, pp. 91-93) admitted looser parallels than this, so this
result should be read as: the toponym argument holds up under a stricter, exactly
specified version of Packard's own test and a properly characterised 200-draw null. It
is not a re-endorsement of every match Packard counted by eye, and it must not be read
as support for any value set beyond the six matched pairs themselves, or for any
language of Linear A.
