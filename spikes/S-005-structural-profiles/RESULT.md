# S-005 · Result

Ran `build_corpora.py` then `run.py` (2026-09-12). Full numbers in `results.json`
(aggregate only, per spikes/README.md rule 6 -- no word lists, no corpus text).
Respelling rules and every corpus's source/licence/caveats are recorded in
`~/.cache/linear-a-b/reference/s005/RESPELLING.md`; nothing from that cache is
quoted here beyond the aggregate counts already safe to state.

## Method, as actually run

Nine statistics per 988-word-type subsample, `src/kober` functions called
read-only exactly as `scripts/kober_run.py` / `kober.report.build_report` call
them (`stem_min=2`, 200 draws, seed 0): five **order-driven** (paradigm-count
ratio to N1 p99, max-alternation-support ratio to N2 p99, ending entropy,
prefix-channel paradigm ratio, medial-channel pair-count ratio to N1 p99) and
four **inventory-driven** (ending inventory size, sign inventory size, hapax
share, Heaps beta -- S-010's own definitions, adapted from a token stream to
this instrument's word-type unit; see `run.py`'s docstring). The medial
channel's consonant-sharing check and `kober.grid` are never run: both need
genuine Ventris values, and no sign label here is a real Linear B sign (every
respelled corpus uses invented CV-syllable identities).

**References built**: real Linear B (DAMOS, the known case), and six corpora
respelled into the same open-CV-syllable shape by the coda rule in
RESPELLING.md -- Greek (Iliad, the positive control: "Greek respelled" beside
real Linear B), Hittite, Akkadian, Sumerian, Ugaritic (the **weakest**
reference: a consonantal script vocalised by an invented rule), Etruscan
(fetched fresh for this spike; **far below target size**, see caveat below).
Twenty subsamples of 988 word types each, plus the full set:

- **Greek**: chunk model (contiguous span of the Iliad's own reading order,
  random start per seed, wrapped) -- the only source with a real reading
  order.
- **Hittite, Akkadian, Sumerian, Ugaritic**: random word-type subset -- these
  are dictionaries (ORACC glossaries, the CUC lemma list), and a dictionary's
  entry order is alphabetic/citation-number, not attested use.
- **Etruscan**: random word-type subset, but the pool itself has only 213
  usable respelled types (409 distinct Latin-transliterated forms before
  respelling, from the kaikki.org Wiktionary extract -- Etruscan's real
  recovered vocabulary is genuinely this small). Twenty subsamples of 170 (80%
  of the pool) substitute for the pre-registered 988; **every Etruscan number
  below is flagged and must be read as reduced-scale, not as 988-comparable.**
- **Linear B**: the tablet model, reusing the *exact* `documents_k` per seed
  that `scripts/kober_floor_sweep.py` found for 988-word-type subsamples
  (`results/kober-sweep/kober-sweep-tablet-size988-seed*.json`) -- the same
  twenty word-type sets F-022 already measured.
- **Linear A**: not subsampled. GORILA's own CERTAIN-WORD type count
  (`kober.words.extract_word_types`) is 988 already; SigLA is used at its own
  full size, 692.

## Statistics per corpus (mean ± population sd across 20 subsamples; Linear A at full size)

| statistic | linear_b | greek | hittite | akkadian | sumerian | ugaritic | etruscan | GORILA (full) | SigLA (full) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| paradigm ratio (real / N1 p99) | 1.62 ± 0.090 | 1.25 ± 0.045 | 1.30 ± 0.031 | 1.06 ± 0.036 | 0.93 ± 0.038 | 1.05 ± 0.027 | 1.14 ± 0.114 | 1.26 | 1.28 |
| max support ratio (real / N2 p99) | 1.50 ± 0.406 | 0.80 ± 0.217 | 1.56 ± 0.271 | 0.64 ± 0.123 | 0.67 ± 0.145 | 0.86 ± 0.125 | 1.27 ± 0.267 | 0.67 | 0.33 |
| ending entropy (bits) | 4.99 ± 0.058 | 5.53 ± 0.046 | 4.48 ± 0.040 | 4.11 ± 0.051 | 5.09 ± 0.019 | 3.60 ± 0.023 | 4.66 ± 0.056 | 5.86 | 5.69 |
| prefix-channel ratio (real / N1 p99) | 1.06 ± 0.056 | 1.03 ± 0.062 | 1.03 ± 0.030 | 0.97 ± 0.046 | 1.00 ± 0.034 | 1.00 ± 0.029 | 0.48 ± 0.137 | 1.19 | 1.18 |
| medial ratio (real / N1 p99) | 0.82 ± 0.077 | 0.78 ± 0.054 | 1.20 ± 0.056 | 0.95 ± 0.059 | 0.87 ± 0.049 | 1.06 ± 0.040 | 0.54 ± 0.094 | 0.71 | 0.61 |
| ending inventory size | 64.3 ± 3.5 | 75.6 ± 1.7 | 46.1 ± 2.0 | 47.8 ± 1.6 | 47.2 ± 0.6 | 19.0 ± 0.0 | 36.8 ± 0.9 | 106 | 82 |
| sign inventory size | 86.8 ± 2.4 | 88.3 ± 1.3 | 55.4 ± 1.0 | 66.3 ± 0.8 | 51.8 ± 0.4 | 22.0 ± 0.0 | 46.5 ± 1.4 | 158 | 106 |
| hapax share | 0.108 ± 0.030 | 0.028 ± 0.013 | 0.049 ± 0.020 | 0.026 ± 0.012 | 0.026 ± 0.015 | 0.000 ± 0.000 | 0.172 ± 0.023 | 0.399 | 0.255 |
| Heaps beta | 0.218 ± 0.018 | 0.260 ± 0.020 | 0.277 ± 0.024 | 0.305 ± 0.023 | 0.231 ± 0.017 | 0.089 ± 0.017 | 0.662 ± 0.014 | 0.323 | 0.301 |

Ugaritic's zero-variance inventory rows are real, not a bug: its 22-letter
folded consonant alphabet is small enough that any 988-word-type subsample of
the 3,475-type pool contains every letter, every time.

## Distance of Linear A from each reference

**Inventory check first (F-044's rule), before reading the order-driven
numbers.** Every reference's inventory-driven pooled distance is large --
GORILA's smallest is Linear B at 16.95, then Ugaritic at 13.58 (on a single
usable statistic, Heaps beta, the other three being undefined against
Ugaritic's zero-variance rows) -- because Linear A's own signary at this
corpus size is far larger than any reference's (158 signs at 988 types, where
Linear B at the same size attests 86.8): exactly the effect F-042 and F-044
already measured and named. This is expected, not new, and it means **no
inventory-driven number below should be read as similarity or difference in
kind** -- it is priced in before the order-driven reading starts.

**Order-driven pooled distance, ranked** (root-mean-square z across the five
order-driven statistics; a second column drops ending entropy alone, whose
near-zero subsample variance -- 0.02 to 0.06 bits for every reference --
inflates its z far past the other four and can dominate the pool by itself,
the same low-variance-inflates-z effect S-010 flagged for Greek's own sign
inventory):

| reference | GORILA: order (5 stats) | GORILA: order (4, no entropy) | SigLA: order (5 stats) | SigLA: order (4, no entropy) | inventory-driven (GORILA) |
|---|---:|---:|---:|---:|---:|
| **greek** (respelled, A-005) | **3.50** | **1.45** | **2.63** | **2.33** | 31.0 |
| **linear_b** (real) | 7.14 | 2.65 | 6.04 | 3.00 | 16.9 |
| etruscan (reduced scale) | 10.00 | 3.01 | 8.74 | 3.19 | 58.5 |
| akkadian | 15.77 | 4.19 | 14.52 | 4.99 | 63.2 |
| hittite | 16.17 | 5.37 | 14.65 | 6.29 | 55.7 |
| sumerian | 19.33 | 5.47 | 15.55 | 6.14 | 133.6 |
| ugaritic (weakest) | 44.36 | 6.82 | 41.26 | 8.12 | 13.6 (1 usable stat) |

The ranking is identical on both Linear A editions and under both readings of
the order-driven pool (with and without entropy): **Greek respelled by the
A-005 coda rule is the closest reference, real Linear B is the second
closest, and every other language sits further away, Ugaritic furthest of
all.** Full per-statistic z-scores are in `results.json`
(`distances.<subject>.<reference>.per_statistic_z`).

## Reading against the brief

**Interesting**, with three caveats that qualify how much weight it can bear.

Linear A's order-driven profile sits closer to "Greek written in a CV
syllabary" -- both the real case (Linear B) and this spike's own synthetic
respelling of the Iliad -- than to any of the five other references, on both
Linear A editions, whether or not the volatile entropy statistic is included.
That is the brief's own "Interesting" reading, close to verbatim: Linear A
sits nearer one part of the reference set than the rest on the order-driven
statistics, and the pattern replicates (GORILA and SigLA agree on the full
ranking; F-044 and S-010 both used edition-agreement as their own strongest
evidence for the same reason).

**Caveat 1: it is not "inside" Greek's spread.** Even at its best reading
(order, 4 statistics, SigLA), Linear A's pooled distance from Greek is 2.33 --
outside a typical 20-subsample spread, not inside it. The brief's literal
"inside one reference's spread" bar is not met by any reference; what holds is
the weaker, still real claim that Greek and real Linear B are *substantially
closer* than every other candidate.

**Caveat 2: corpus genre is a live confound.** Greek and Linear B are both
running administrative/literary text (tablets, epic verse); Hittite, Akkadian,
Sumerian and Ugaritic are all drawn from citation-form dictionaries and
glossaries here, not running text, because that is what survives digitally at
scale for those languages (RESPELLING.md). A citation-form lemma list may show
a different paradigm/alternation/medial-pair density than a real corpus of the
same language would, for reasons that have nothing to do with typology. This
spike cannot separate "Linear A resembles Greek-shaped text" from "Linear A
resembles running text of any kind, and the dictionary sources are the odd
ones out" -- both readings are consistent with the ranking above, and only the
first is the interesting one.

**Caveat 3: at 988 word types the answer key itself is barely readable.**
F-022 already found that real Greek under Linear B spelling only clears the
full stage-1 criterion in 7 to 8 of 20 tablet-model subsamples at this exact
size -- the size chosen here because it is Linear A's own. Order-driven
ratios for every reference in the table above cluster near 1 (chance), which
is consistent with F-022's floor: at 988 word types even the true positive
control is only weakly separated from its own null. Linear A "resembling
Greek most" at this size may partly be "every language looks similarly
chance-like at this size, and Greek's chance-like values happen to be the
ones nearest Linear A's own chance-like values" -- which is a real pattern
worth recording, not the same claim as "Linear A shows Greek-like structure."

**What survives.** The ranking itself: whatever is driving it, it is not
random, since it replicates across both Linear A editions, both statistic
groupings, and it puts the two Greek-shaped corpora together and apart from
the rest with a wide margin (order, 4 stats: 1.45-3.19 for Greek/Linear B
against 4.19-8.12 for everything else). That is a real structural fact about
this corpus size and this instrument, worth a rebuild (spikes/README.md rule
5) with running-text sources for the cuneiform languages before it can be read
as anything about Linear A's typology.

## Must not be read as

Evidence about which language Linear A writes (Kober 1948, p. 101). Every
respelling rule here is this spike's own invention -- the Ugaritic
vocalisation most of all, but also the uniform decision to drop every
laryngeal series and to fold aspirates everywhere, which makes every
respelled language look more alike than its real phonology does. A profile
match is a match of spelling-plus-morphology shape under these particular,
disclosed, arbitrary choices, layered on top of A-005's own already-stated
limit (Linear A followed Linear B's spelling rules is an assumption, not a
finding). Nothing here touches sound values for Linear A itself, consistent
with the CLAUDE.md invariant against treating its Linear-B-convention
transliteration as phonological evidence.

## Caveats per reference

- **Ugaritic (weakest).** Vocalised by an invented rule (insert /a/ after
  every consonant; the three aleph glyphs read as self-contained vowel
  syllables) because the script marks no vowel at all otherwise. This
  guarantees every consonant becomes its own syllable -- no coda is ever
  dropped, no cluster is ever simplified -- which is a real distortion toward
  longer, more regular words than any actual spelling of Ugaritic would give.
  Its inventory-driven statistics are degenerate (zero variance; a 22-letter
  alphabet is saturated by any 988-type subsample) and its order-driven
  distance is the largest of any reference on both editions.
- **Etruscan (far below target size).** Only 213 usable respelled types exist
  in this source at all (409 distinct Latin-transliterated forms from the
  kaikki.org Wiktionary extract, before the >=2-syllable filter) -- a fact
  about how little of the language survives legibly, not a fetch failure.
  Subsamples here are 170 word types (80% of the pool), not 988; its numbers
  are not on the same footing as the other six references and are reported
  with that flag attached everywhere they appear.
- **Hittite, Akkadian, Sumerian.** Dictionary/glossary sources (a Wiktionary
  extract; ORACC project glossaries), not running text -- see Caveat 2 above.
  Akkadian is specifically first-millennium BC royal/administrative registers,
  not the Old Babylonian period contemporary with the Minoan palaces.
- **Greek.** The Iliad's transmitted text has lost the digamma, so the
  w-series is rare in this respelling, the same conservative gap
  `hypothesis-harness.md` already notes for the etymological method's Greek
  controls.
- **All six synthetic references.** No laryngeal/pharyngeal consonant series
  exists in this respelling scheme (matching Linear B's own signary), and
  aspirates fold to their plain stop everywhere. Both choices make every
  language's respelling more alike the others than its real phonology is --
  the conservative direction for a "does X resemble Y" question, but a real
  loss of information, named in RESPELLING.md.

## Files

- `spikes/S-005-structural-profiles/build_corpora.py` -- builds every
  respelled reference corpus, writes RESPELLING.md.
- `spikes/S-005-structural-profiles/run.py` -- subsamples, profiles (via
  `src/kober`, read-only), aggregates, computes distances.
- `results.json` -- aggregate numbers only.
- `~/.cache/linear-a-b/reference/s005/` -- the private corpora and
  RESPELLING.md (outside the repo, never committed).
