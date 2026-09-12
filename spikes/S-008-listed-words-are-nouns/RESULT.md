# S-008 · Result

Ran `run.py` (2026-09-12). Full numbers in `results.json` (aggregate only, per
spikes/README.md rule 6 — no word lists, no corpus text; ending labels with
counts are kept, as the task allows). `.venv/bin/python spikes/S-008-listed-words-are-nouns/run.py`,
total wall time 17.5s.

## Method, as actually run

**"Listed"** is `kober.lists.extract_listed_words`'s own definition, reused
unchanged: a CERTAIN WORD token of two or more normalised signs, followed on
its line (skipping separators) by a logogram or numeral. This is the
definition F-030 already built Kober's Assumptions 4, 6 and 7 on; a word
*type* counts as listed if any of its occurrences meets it. Everything else
is "not listed". Stage 1's own splitting (`kober.paradigms.ending_channel`,
`stem_min=2`) and N1 null (`kober.nulls.run_n1`, 200 draws) run separately on
each set's own word-type frontset.

**Hapax share** is the fraction of a set's word types with corpus-wide token
frequency 1 (frequency measured over the whole corpus, not just within the
set). **Ending inventory and entropy** are computed over word *types*, at the
last sign and the last two signs; entropy is also reported normalised by
`log2(inventory size)` so sets of very different size are comparable.
**Paradigm ratio** is stage 1's own paradigm count (stems with two or more
endings) divided by its N1 null mean, at `stem_min=2`, 200 draws, seeds 0 and
1 — the two seeds agree to three decimal places everywhere they were both
computed, so seed 1 is not tabulated separately below.

**DAMOS's own morphological annotation.** Checked before running anything
else: `Token.annotations` on DAMOS carries exactly one key, `apparatus`
(editorial notes such as "vacat" or "verso"), on 12,167 of the corpus's
tokens. No part-of-speech, lemma or case tag is reachable through pyaegean
without a new fetch, so the part-of-speech check below uses the
reference-list proxy only, as the brief anticipated.

**Part-of-speech proxy (Linear B only).** `reference.is_grammar` classifies a
*pair* of endings, not one ending, so a single ending is graded from the real
corpus's own attested alternations: for every alternation in a set's ending
channel, both its endings are tagged with whatever rule (`reference.py`,
version 3, the only version carrying the infinitive rule) matched that pair.
An ending is "verb/participle/infinitive only" if every rule it was ever
tagged with, across every alternation it appears in within that set, is one
of `verb`, `participle`, `infinitive`, and it was tagged with at least one
rule at all. A word type is counted if either its last sign or its last two
signs qualifies. Endings with no attested grammatical alternation in that set
are left unclassified, counted in neither direction.

**Transfer test.** Linear B's own sampling noise on each listed-minus-not-listed
difference is measured from twenty tablet-model subsamples at 988 word types
(`kober.words.subsample_document_ids`, bisected on document count exactly as
`scripts/kober_floor_sweep.py` does, seeds 0-19, tolerance 2%), matching
GORILA's own size. Linear A's own differences (both editions) are read
against that noise band.

## SigLA has no listed words under this definition — a segmentation artifact

SigLA returns **zero** listed word types: `extract_listed_words` requires the
following logogram or numeral to sit on the same line as the word, and SigLA's
`Document.line_tokens` puts exactly one token per line (verified directly:
every line in a sampled SigLA document with logograms, e.g. ARKH 3a, holds a
single token). A word and the logogram that follows it on the real tablet are
therefore never "on its line" together in this edition's representation, so
the check can never fire. SigLA also carries no NUMERAL tokens at all (721
LOGOGRAM, 1,895 WORD, 0 NUMERAL, corpus-wide) and no SEPARATOR tokens, unlike
GORILA (2,211 LOGOGRAM, 1,621 NUMERAL, 524 SEPARATOR). This is a property of
the SigLA loader's line segmentation, not a fact about the tablets — the same
segmentation-sensitivity theme A-002 already names for this edition pair. The
transfer test below therefore runs on GORILA only; SigLA's row is reported as
undefined, not as zero evidence.

## Per-set statistics

| corpus/edition | set | n types | hapax share | ending inv. (last 1 / last 2) | diversity (last 1 / last 2) | entropy bits (last 1 / last 2) | entropy normalised (last 1 / last 2) | paradigm ratio (seed 0) |
|---|---|---:|---:|---|---|---|---|---:|
| Linear B (DAMOS) | listed | 1,873 | 0.576 | 76 / 867 | 0.041 / 0.463 | 5.012 / 9.187 | 0.802 / 0.941 | 1.522 |
| Linear B (DAMOS) | not listed | 1,895 | 0.767 | 71 / 910 | 0.037 / 0.480 | 5.036 / 9.294 | 0.819 / 0.946 | 1.621 |
| Linear A (GORILA) | listed | 541 | 0.782 | 91 / 449 | 0.168 / 0.830 | 5.777 / 8.700 | 0.888 / 0.987 | 1.640 |
| Linear A (GORILA) | not listed | 447 | 0.908 | 79 / 385 | 0.177 / 0.861 | 5.715 / 8.487 | 0.907 / 0.988 | 1.853 |
| Linear A (SigLA) | listed | 0 | — | — | — | — | — | — |
| Linear A (SigLA) | not listed | 692 | 0.835 | 82 / 546 | 0.118 / 0.789 | 5.693 / 8.954 | 0.896 / 0.985 | 1.586 |

Linear B's 3,768 word types split 1,873 listed / 1,895 not listed, almost
evenly. GORILA's 988 split 541 / 447. Every set's paradigm count exceeds its
own N1 null mean (ratio > 1 throughout), the expected stage-1 signal on
inflected or semi-templatic text, on both scripts and every set.

## Differences (listed minus not listed), against Linear B's own sampling noise

The noise column is the mean and population sd of this same difference across
Linear B's twenty tablet-model subsamples at 988 word types, seed 0 null
throughout. `z` is GORILA's difference expressed in units of that noise sd.

| metric | Linear B (full, 3,768) | Linear B noise at 988 (mean ± sd) | GORILA (988) | z (GORILA vs. LB noise) |
|---|---:|---:|---:|---:|
| hapax share | −0.191 | −0.113 ± 0.029 | −0.126 | −0.47 |
| ending diversity, last 1 | +0.003 | +0.028 ± 0.013 | −0.009 | −2.83 |
| ending diversity, last 2 | −0.017 | +0.050 ± 0.035 | −0.031 | −2.35 |
| entropy, last 1 (bits) | −0.024 | +0.069 ± 0.110 | +0.062 | −0.06 |
| entropy, last 2 (bits) | −0.107 | −0.164 ± 0.113 | +0.213 | +3.33 |
| entropy, last 1, normalised | −0.017 | +0.010 ± 0.013 | −0.019 | −2.24 |
| entropy, last 2, normalised | −0.004 | +0.009 ± 0.005 | −0.001 | −1.92 |
| paradigm ratio (seed 0) | −0.099 | +0.030 ± 0.302 | −0.214 | −0.80 |

Two things stand out. First, four of the eight metrics disagree in sign
between Linear B's own full corpus and Linear B's own 988-subsample mean
(ending diversity last 1 and last 2, entropy last 2, entropy last 1
normalised) — the listed/not-listed ending-inventory and entropy differences
on Linear B are themselves not stable under subsampling to Linear A's scale,
before Linear A ever enters the comparison. Second, GORILA's differences
land within about half a noise sd of Linear B's own subsample noise for
hapax share, entropy (last 1) and the paradigm ratio, but three to three and
a third sd away, several with the opposite sign, for both ending-diversity
metrics and entropy at the last two signs.

## Part-of-speech proxy, Linear B only

| set | n types | classified (any rule) | verb/participle/infinitive only | share of all types | share of classified |
|---|---:|---:|---:|---:|---:|
| listed | 1,873 | 1,663 | 0 | 0.000 | 0.000 |
| not listed | 1,895 | 1,694 | 0 | 0.000 | 0.000 |

Zero, in both sets. Every ending that ever matched a verb, participle or
infinitive rule in an attested alternation also matched a noun- or
adjective-type rule via some other attested alternation somewhere in the same
set — for example the bare vowel-E ending that rule 9 (verb, third singular)
reads also satisfies rule 7 (consonant-stem noun case) whenever it pairs with
a different partner. The proxy never separates the two sets because it never
fires as designed: this reference list's rules are not mutually exclusive at
the level of a single ending, only at the level of one already-paired
alternation, so grading endings one at a time collapses every ending into
"could be either." This is the weak proxy the brief asked to flag, confirmed
weak in the strongest possible way — it produced no signal to read at all.

## Reading against the brief

**Nothing.** The brief's own "Nothing" clause reads: "The signatures do not
separate on Linear B, so the proxy cannot test her assumption." That is what
happened. On Linear B itself, only two of the eight statistics show a
listed-vs-not-listed difference that clears the tablet-model sampling noise
in the same direction the full corpus shows: hapax share (listed words are
attested more often each) and, more weakly, the paradigm ratio. Both are
frequency effects — words that recur across many list entries (commodity
terms, place names, personnel headings) are by construction less often a
corpus hapax, whether or not "noun" is the right description — not the
ending-inventory or entropy signature a closed nominal case-and-gender class
would be expected to leave. That ending-inventory and entropy signature is
small on the full Linear B corpus, and unstable in sign under Linear B's own
subsampling to Linear A's scale before any transfer question is asked. The
part-of-speech proxy, the one check built to speak to "noun" directly rather
than to frequency, fired zero times in either direction.

What does transfer to GORILA is the frequency effect: hapax share and the
paradigm ratio land within about half a Linear-B-noise standard deviation of
Linear B's own value at matched scale, same direction both times. What does
not transfer, or transfers with the wrong sign, is the ending-diversity and
entropy half of the signature — the half that would actually speak to "these
are a grammatically narrow class." SigLA cannot be read on this question at
all: its line segmentation makes every word type "not listed" by
construction, a fact about the edition's representation in pyaegean, not
about the tablets.

## Must not be read as

A classification of any Linear A word, or a measurement of Kober's
Assumption 3 itself. It is a proxy for a proxy: ending statistics standing in
for a part-of-speech answer key this repository does not hold, checked
against a reference list whose rules were written from Mycenaean grammar and
are not mutually exclusive at the single-ending level. Nothing here says
whether Linear A's listed words are nouns, proper nouns, or anything else.
The SigLA zero is a segmentation fact about one pyaegean edition, not a
finding about Linear A tablets.
