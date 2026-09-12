# Changelog

Versioned history of every test protocol in this repository. Commit logs record what
changed in the code; this records what changed in the *method*, why, and what the result
was under each version, so a number quoted anywhere can be traced to the protocol that
produced it.

Rules. A protocol gets a new version whenever anything that could move a result changes:
the statistic, the null, the expansion rules, the sampling, the lexicon set, the
permutation count. Results are reported with their version. Superseded versions stay
listed with what was wrong about them, because the wrong versions are where the lessons
are. Add the entry in the same change as the code, per HENGE rule 5.

Version numbers: `major.minor`. Minor for a change that keeps results comparable with the
previous version; major for one that does not. `1.0` marks the first version that was
frozen before being applied to Linear A.

---

## Etymological method (dictionary matching)

Does a candidate language's dictionary fit Linear A better than scrambled sign values
would? Named per `docs/ai_context/terminology.md`; earlier entries call this the
lexicon-matching instrument. Code: `src/semitic_null/` (versions 0.1 to 0.2), `src/hypotheses/` (0.3 onward),
`scripts/controlled_comparison.py` (1.0 onward).

### Lexicons added under 1.0 — 2026-09-11 · no protocol change

Two loaders in `src/hypotheses/lexicons.py`, both scored under the Greek map because
neither language writes a Semitic consonant inventory: `hittite_kaikki` (Wiktionary via
kaikki.org, CC BY-SA 4.0; ḫ dropped, see ASSUMPTIONS A-018) and `sumerian_epsd2` (ORACC
ePSD2-literary, CC0; ŋ folded to g, ʾ-bearing entries excluded). Finnish and Basque gain a
`--map greek` option in `scripts/unrelated_controls.py` so the Greek map has wrong
real-language controls of its own; the default and every existing filename are unchanged.

Reading, written before the results existed: Hittite stands for the Anatolian hypothesis
only as a proxy (A-025) and the Wiktionary list is a stopgap (A-024), so a null result on
Linear A is interpretable only if Hittite also scores on Linear B above the wrong
controls; otherwise the lexicon is too small to test anything. Sumerian is a wrong answer
by construction; its score is the bar for the Greek map.

Outcomes (FINDINGS F-013): Hittite scores nothing on either corpus, so the Anatolian test
is uninformative rather than negative. Sumerian fits Greek text at +2.31, Finnish at
+2.25, which puts the Greek positive control's lead over wrong real languages at about
one sample standard error and downgrades the strength of F-008.

### 1.1-laryngeal-stripped — 2026-09-11 · diagnostic variant of 1.0, pre-registered

`scripts/laryngeal_test.py`. Identical to 1.0 except that ʾ, ʿ, h, ḥ are deleted from every
lexicon's skeletons and from every sign's phoneme options, so vowel signs contribute
nothing, as under the Greek map. Purpose: test explanation 3 of FINDINGS F-011, that the
Northwest Semitic advantage on Linear A comes from Hebrew and Ugaritic being the only
lexicons able to match the laryngeal-bearing candidates that Linear A's vowel-heavy words
generate.

Reading, written before the results existed: if Ugaritic and Hebrew fall into the range
of Basque and Turkish on Linear A under 1.1, explanation 3 holds and F-011 closes as an
artifact of the map. If they stay above, the laryngeals are not the cause and explanations
1, 2 and 4 remain.

Run alongside, under 1.0 unchanged, `scripts/unrelated_controls.py --langs he ar`: Modern
Hebrew and Arabic frequency lists from the same OpenSubtitles pipeline as the four
unrelated controls. Reading, written before the results existed: a Hebrew frequency list
scoring with Finnish and Basque rather than with Strong's and Ugaritic points to lexicon
type (explanation 2); scoring with Strong's and Ugaritic points to language (explanation
1). Arabic, Central Semitic, tells whether any effect is Northwest Semitic-wide.

Also queued under 1.0: Ugaritic and Hebrew at 400 permutations on both corpora, and a
second word sample (seed 1) for every Semitic-map lexicon on Linear A.

Outcomes, recorded after the runs (FINDINGS F-012): the laryngeal channel accounts for
part of the pattern (Ugaritic's lead halves; Hebrew's rise reverses; Hebrew becomes the
best fit on Greek text once laryngeals are removed); lexicon shape accounts for most of
the rest (a Modern Hebrew frequency list scores +0.59 against Strong's +2.44); the second
sample moves every score by 0.5 to 1.3. Arabic under 1.1 fell from +2.37 to +0.90 on Linear A, as pre-registered. Read as: not a
language signal.

### 1.0 sensitivity flags — 2026-09-11 · no protocol change; one confound found

`--secure-signs-only`, `--non-secure-only` and `--exclude-underdotted` were added to the
three protocol 1.0 scripts to restrict the word pool (A-001, A-004 sensitivities). Found
in use: a restricted pool also changes the null, because the frequency bands are
computed from the sampled words, so a restricted-pool z is not comparable with the
full-sample z (A-042, F-014). The valid sign-set sensitivity is
`scripts/subset_decomposition.py`, which draws the sample and the permuted maps once and
scores the same maps on word subsets, comparing per-word gaps. The flags are kept for
counting pools and as the record.

### 1.0 — 2026-09-11 · current, frozen

The first version frozen on Linear B before being applied to Linear A. Changing anything
in it means a new version, and the Linear A result must then be rerun rather than
reinterpreted.

- Expansion: known Mycenaean spelling rules, at most one omitted coda per word (l, r, m,
  n, s before a consonant), optional omitted final s, n, r.
- Statistic: mean over words of log(1 + mean lexicon count over the word's candidates).
- Null: sign-to-phoneme sets permuted within breadth class and corpus-frequency band,
  four bands.
- Sample: seeded random sample of 400 word types covered by every map in the run.
- Control: for every real lexicon, a synthetic twin with the same skeleton-length profile
  and consonant frequencies and random content, run under the same map.
- Calibration criterion, stated before running: on Linear B, real Greek must beat
  synthetic Greek clearly and Hebrew must not beat synthetic Hebrew.

Results, Linear B: Greek +2.78 vs synthetic +0.73; Hebrew +0.30 vs synthetic −1.01.
Criterion met. Linear A, run once at 400 permutations: Greek +3.10 vs synthetic −0.31;
Hebrew +2.44 (p = 0.010) vs synthetic −1.18.

Same day, same version, additional lexicons (`scripts/unrelated_controls.py`,
`scripts/extra_lexicons.py`). Ugaritic (Copenhagen Ugaritic Corpus, DULAT headwords) and
Akkadian (ORACC saao + rinap + ribo citation forms) added as loaders 2026-09-11; a
Unicode-decomposition bug in the first Akkadian skeleton function was caught before any
result was produced. Earlier the same day: Finnish, Turkish, Basque and Hungarian all beat their
synthetic twins on Linear B at z ≈ +2.5 and on Linear A at +0.9 to +2.1; LSJ Greek
+2.91 on Linear B and +2.81 on Linear A. Conclusion: the synthetic twin is a noise
control, not a wrong-language control, and the instrument cannot distinguish one real
language from another. Full reading in `docs/ai_context/hypothesis-harness.md`.

### 0.5 — 2026-09-11 · superseded by 1.0

Introduced the two changes that made the instrument work at all: expansion by the known
Mycenaean rules instead of blind insertion, and a frequency-weighted statistic instead of
set membership. Six Greek lexicons on Linear B clustered at z = +3.08 to +3.22, Hebrew at
+1.68.

Wrong with it: the word sample was `sorted(words)[:600]`, the alphabetically first 600,
which over-sampled vowel-initial words and inflated Hebrew on Linear B from +0.30 (1.0)
to +1.68. Results from this version are not comparable to 1.0 and should not be quoted.
The statistic was also chosen here as the best of four tried, which is legitimate on the
calibration corpus only because 1.0 then froze it.

### 0.4 — 2026-09-11 · superseded; conclusion withdrawn

First run on Linear B as a known-answer control, with the archaic Greek lexicon (Homer,
Hesiod, Hymns, early philosophy, Pindar, Bacchylides; 53,026 types) replacing Koine.
Under 0.3's set-membership statistic the true Greek reading scored +1.9% at p = 0.155 and
Hebrew +2.1% at p = 0.054 on Linear B. Blind insertion of up to two arbitrary consonants
raised true-reading recall from 13% to 78% without improving discrimination.

Conclusion drawn at the time: consonantal matching cannot work on a defectively spelled
syllabary. **Withdrawn** by 0.5: the failure was the blind-insertion expansion and the
set-membership statistic, not the method class. The diagnosis of *why* Linear B spelling
loses information (no coda consonants, so χαλκός is ka-ko) stands and is correct.

### 0.3 — 2026-09-11 · superseded

Hypothesis registry (`src/hypotheses/registry.yaml`), five prior scenarios, Greek added
as a known-false control on Linear A. Two nulls: breadth-matched (0.2) and a new
frequency-matched null with four bands. Found the breadth-matched null gave Greek
p = 0.001 on Linear A, where it is false; frequency matching cut Greek's excess from
+13.6% to +5.7% but not to zero. A band sweep showed the null degenerates above about
eight bands (fewer than six signs per band, permutation moves under half the signs), so
the residual could not be tightened away. Conclusion at the time: the instrument can
refute but not confirm. That conclusion survives, for reasons 1.0 makes clearer.

Wrong with it: Greek's residual was attributed to the transcription being Greek-derived,
which is true, but the set-membership statistic was the larger problem and was not yet
suspected.

### 0.2 — 2026-09-10 · superseded

Breadth-matched permutation null: values permuted only among signs with the same number
of phoneme options. Semitic on Linear A fell from p = 0.016 (0.1) to p = 0.153. Positive
control: 600 genuine Hebrew triliteral roots re-encoded through the syllabary, recovered
at 100% against a 78% null, z = +8.4.

Wrong with it: the positive control was too easy. Perfectly encoded roots are not how any
real language appears through a defective syllabary, so passing it did not show the
instrument could detect a real language. The Linear B control in 0.4 was the honest
version, and it failed.

### 0.1 — 2026-09-10 · superseded

First test of the Semitic reading (di Mino 2026). Strong's Hebrew as lexicon, 2,111
triliteral skeletons; Linear A words expanded to every consonant skeleton their signs
could write under Linear B values with sibilant and emphatic mergers; a word scored a hit
if any candidate was an attested root; null by free permutation of sign values. Result:
real 72.2% vs null 65.1%, p = 0.016.

Wrong with it: the free permutation let signs trade a four-option phoneme set for a
one-option one, so the real map reached 20.8 candidate roots per word against the null's
17.4, and candidate breadth correlated with hit rate at +0.65. The p-value was a
combinatorial artifact. This is the trap anyone running the obvious test falls into.

---

## Kober method (structure from sign patterns)

Does a corpus show stems recurring with different endings more than chance would give,
and on Linear B, are the recurring endings Greek grammar? Design: `docs/ai_context/kober-method.md`.
Code: `src/kober/` (planned). Assumptions A-033 to A-041.

### 0.1 — 2026-09-11 · designed, pre-registered, not yet built

Word types, CERTAIN only, normalised as for restoration. Stems of two or more signs,
endings of one or two; the mirror for prefixes. Two statistics, paradigm count and
alternation support, with their own nulls: N1 position-matched shuffle for the count, N2
ending shuffle for support, 200 draws each. The protocol 1.0 null (relabelling signs
within frequency bands) is explicitly rejected because relabelling preserves shared
prefixes exactly.

Criterion on Linear B, fixed before the build: paradigm count above the 99th percentile
of N1, maximum alternation support above the 99th percentile of N2, and at least seven
of the ten best-supported ending alternations in the reference list in the design page.

Disclosure. A read-only sizing count was run before the criterion was written. It showed
the paradigm counts (516 of 2,977 stems on Linear B, 51 of 547 on Linear A) and the
Linear B top alternations (-ja/-jo, -u/-we, -ta/-to, -u/-wo, -we/-wo, -ra/-ro,
-si-ja/-si-jo, -me-na/-me-no) with no null. The reference list was written from Mycenaean
grammar after that glimpse; it would contain those items regardless, but the "seven of
ten" part of the criterion is weaker pre-registration than the null-exceedance parts,
which were not glimpsed. The stage 2 grid check was not glimpsed at all.

Readings, written before the result exists:

- All three parts met: the instrument recovers suffixal grammar where it exists.
  Proceed to Linear A (TODO item 4) with the Linear A reading pre-registered separately,
  knowing from sizing that only the paradigm count and prefix channel can be read there.
- Null-exceedance met, alternation list not: the instrument finds structure but the
  structure it ranks first is not grammar (compound-name elements, chance overlap of
  frequent endings). The nulls or the ranking need a context constraint (same tablet
  series, same slot) before 0.2. Do not proceed to Linear A.
- Paradigm count at or below the null on Linear B: the corpus, nine times the size of
  Linear A, is below the method's floor at this granularity, and the Linear A run would
  be uninformative. Record that as the finding and stop the line.
- Prefix channel strong on Linear B: unexpected, since Greek is not prefixing. Would
  mean the channel picks up something other than grammar; explain before reading any
  prefix result on Linear A.

Built and run 2026-09-11 (FINDINGS F-016). All three parts met on both null seeds; 9 of
the top 10 alternations on the reference list. Found in the run: the prefix channel's
paradigm count under N1 measures shared suffixes, because its base is a word-final run,
so only its N2 support statistic is a prefix statistic (A-047). No protocol change; the
reading rule is recorded for the Linear A pre-registration.

### 0.1 stage 2, the grid — 2026-09-11 · pre-registered, gated open by F-016

`src/kober/grid.py`. For every stem with two or more endings, every unordered pair of
endings whose first signs differ yields a **bridging pair** (e1[0], e2[0]): in X-so /
X-si-jo the pair is (so, si); in X-ta / X-to it is (ta, to). A pair's support is the
number of stems yielding it. Under the known Linear B values each sign has a consonant
(its label minus the final vowel, trailing digits stripped; pure vowel signs share the
empty consonant; complex signs such as TWO, DWE, RA2 keep their full onset). The
statistic is the fraction of bridging pairs with support ≥ k that share a consonant, for
k = 2 and k = 3, and its value under N1 (same procedure on position-shuffled words),
200 draws. Also reported: the size-weighted grid, the sign classes the real pairs induce
by union-find, and how many of those classes are pure under the known values.

Criterion, written before the run: **at k = 2 and at k = 3, the shared-consonant
fraction exceeds the 99th percentile of its N1 distribution.** Readings: met, and the
grid is recovered without values, which is Kober's second inference reproduced and the
positive control the Linear A grid will be read against; not met, then bridging pairs at
this corpus size are dominated by chance overlap of frequent signs and the grid stage
does not run on Linear A. No value is used anywhere except in the final check.

Disclosure: the ending alternations in F-016 were seen before this was written; the
consonant-sharing fraction and its null were not computed.

Built and run 2026-09-11 (FINDINGS F-017). Criterion met at k = 2 and k = 3 on both
seeds; the grid was not recovered: union-find over all pairs at support ≥ 2 gives one
class of 64 signs. Cause recorded there: two thirds of the two-ending stems are at the
chance level, and their pairs swamp the paradigmatic ones.

### 0.2 — 2026-09-11 · pre-registered, not yet run · stage 2 anchored; stage 1 unchanged

Version note. This is Kober 0.2, one version line for the whole instrument. Stage 1
(paradigms, alternations, both nulls, the criterion, F-016) is byte-identical to 0.1 and
its results stay comparable, which is what a minor bump means under the rules at the top
of this file. Only stage 2, the grid, changes. And the change is a correction of our
instrument towards Kober's own practice, not a refinement of her method: she inferred the
grid from the few triplets whose paradigm status was certain, and 0.1 pooled every
chance overlap with them (F-017). Earlier text calling this "0.1 stage 2, version 0.2"
means 0.2.

Change from 0.1 stage 2: bridging pairs are taken only from stems that support one of
the **top ten ending alternations by support**, in the real corpus and, on each N1 draw,
in that draw's own top ten. Everything else is unchanged: same pair definition, same
consonant function consulted last, same N1, 200 draws, both seeds. Reported: pairs,
fraction sharing a consonant, the N1 distribution and percentile, and union-find classes
over the anchored pairs with purity under the known values.

Reason for the change, written after F-017: Kober used only the alternations whose
paradigm status was certain. Anchoring to the top ten is the mechanical form of that,
and ten is the number the stage 1 criterion already uses.

Criterion, written before the run: **the anchored fraction exceeds the 99th percentile
of its N1 distribution on both seeds, and union-find over the anchored pairs yields at
least three classes of size two or more that are pure under the known values.**
Readings: met, then the grid is recovered in the form Kober found it, a few solid
same-consonant pairs, and that is the positive control any Linear A grid is read
against; fraction met but classes not, then the consonant signal concentrates in the
paradigmatic pairs as expected but the top ten still admit chance pairs at this size;
neither, then the anchoring is wrong and stage 2 stops at F-017. Known in advance: the
eu-stem triangle contributes pairs (u, we), (u, wo) that do not share a consonant, so
the fraction cannot reach one; the expected same-consonant pairs are (ja, jo), (ta, to),
(ra, ro), (we, wo), (na, no).

Built and run 2026-09-11 (FINDINGS F-018). Fraction above the N1 99th percentile on
both seeds by 0.004 and 0.007; no pure class; the anchored fraction (0.090) is below
the pooled fraction at support ≥ 3 (0.127) and below chance (0.096). Anchoring by stem
readmits the chance endings the anchor stems carry.

### 0.3 — 2026-09-11 · pre-registered, not yet run · grid pairs from the anchoring alternations themselves

Change from 0.2, stage 2 only, stage 1 unchanged: bridging pairs are the first signs
of the two endings of each top-ten ending alternation itself, one pair per alternation
where the first signs differ, weighted by nothing. The null is the same procedure on
each N1 draw's own top ten. Statistic: the fraction of those pairs that share a
consonant under the known values, consulted last; union-find over the real pairs.

Disclosure: from the F-016 table, seven of the top ten alternations begin with
different signs and four share a consonant (-ja/-jo, -ta/-to, -ra/-ro, -we/-wo). This
was counted by hand before the entry was written, so the real value is known to be
about 0.57. What is not known is the null: how often a draw's own top ten, formed from
chance pairs of frequent endings, share consonants. The criterion is therefore the null
part alone: **the fraction exceeds the N1 99th percentile on both seeds.** Readings:
met, then the grid Kober drew, four same-consonant pairs from the strongest
alternations, is recovered without values, and the eu-stem triangle correctly does not
join it; not met, then frequent endings share consonants often enough by chance that
four of seven is unremarkable, and stage 2 closes at F-017. Expected union-find: three
or four pure classes of two and one impure class joining u, we and wo. On Linear A
every alternation ties at support two or below, so 0.3 has nothing to anchor there and
will not be run on it.

Built and run 2026-09-11 (FINDINGS F-021). Criterion met on both seeds: 4 of 7 pairs
share a consonant against a null 99th percentile of 0.25 to 0.27. Union-find gives one
pure class, not three or four, because the chance pair ro/to joins ra/ro to ta/to;
recorded as a limit of unweighted union-find at n = 10, not changed.

### Floor sweep under Kober 0.9.1, merged identities and reference list v3 — 2026-09-12 · pre-registered, run 2026-09-12 (FINDINGS F-046)

Question: F-022 measured the floor for the 0.3 instrument (tablet model 1,875 word
types, type model 2,750). Since then the answer key was rebuilt from Ventris and
Chadwick (0.8, v3) and the homophone merge (0.9) carried Greek at 988 word types to
eighteen of twenty on the strict top-three criterion (F-040). Those are different
criteria from the sweep's, so "the floor has moved" is not yet a like-for-like
statement. Where is the floor under the current instrument, on the sweep's own
criterion and on the strict top-three criterion, and is it at or below Linear A's size?

Design, fixed before the run. `scripts/kober_floor_sweep.py` gains `--merge-homophones`,
`--reference-version` and `--results-dir` (default behaviour unchanged, so the 2026-09-11
sweep reproduces); runs go to `results/kober-sweep-09/`.

- Instrument: Kober 0.9.1 stage 1, `--merge-homophones`, reference list v3, stem_min 2,
  200 draws, null seed 0. No medial block. Nothing in `src/` changes.
- Model: tablet model only (the floor the field is quoted; the type model is not swept).
  Sizes: 500, 750, 1,250, 1,500, 1,750 word types, twenty subsample seeds each; the 988
  cells are the twenty `results/kober-09-merged/kober-damos-docsK-sN.json` files already
  on disk, read, not rerun; 3,768 is the merged full-corpus run in the same folder.
- Two criteria, both reported at every size: (a) the sweep's three parts as in the
  2026-09-11 entry, with part three under v3 (top ten matched at least seven); (b) the
  strict top-three all grammar under v3 (`top_n_alternations_with_ties` strict variant,
  A-072), the criterion F-034 and F-040 quote. The bar is sixteen of twenty in both.
- Recorded per size: for each criterion, the count of twenty passing and each part's
  count; median and range of type count, of top-ten matched and of strict top-three
  matched.
- **The floor under each criterion is the smallest swept size at which at least sixteen
  of twenty pass**; if 988 passes and 750 does not, the floor is between them and is
  quoted as "at most 988".

Readings, written before the run. Both floors at or below 988: the current instrument
reads Greek at Linear A's size and below, and Linear A's null-level alternation support
(F-019, F-040) is a fact about the corpus's content, not its size; F-022's number is
recorded as the 0.3 floor and superseded for the current instrument. Criterion (b) at or
below 988 but (a) above it: the top-ten part of the sweep criterion is the harder one
at this size, which F-034 already showed at n=10; quote both. Neither at or below 988:
F-040's eighteen of twenty was a single-size result and the floor sentence stands as
F-022 wrote it. Whatever the outcome, the number describes Greek under Linear B spelling
with the spelling variants merged, and transfers to Linear A only under A-040 and A-144.

Outcome: criterion (a) floor 1,250; criterion (b) floor 750; second reading. Each size
ran in under a minute (20 to 64 seconds), against hours for the 2026-09-11 sweep. The
sweep script gained the three options with its default path reproducing the earlier
summary byte for byte; `top_10_matched_to_rule` in results files is always graded under
v1, so part 3 was recomputed from the stored top twenty at v3.

### Floor sweep on Linear B — 2026-09-11 · pre-registered, not yet run · Kober 0.3 stage 1, no protocol change

Question: at what corpus size does stage 1's criterion become readable on Greek text?
F-019 gives the two ends: at 988 word types the full criterion is met in none of ten
subsamples; at 3,768 it is met.

Design, fixed before the run.

- Sizes: 1,250, 1,500, 1,750, 2,000, 2,500, 3,000, 3,500 word types, plus the two ends
  already run. Then one bisection round between the two adjacent sizes where the pass
  rate crosses the bar, at their midpoint.
- Twenty subsamples per size, subsample seeds 0 to 19, null seed 0, 200 draws per
  null, stage 1 only (paradigm count against N1, maximum support against N2, seven of
  ten on the reference list). The grid is not swept.
- Two subsampling models, reported side by side. *Type model*: a random subset of
  word types, as in F-019 (`--subsample`). *Tablet model*: a random subset of documents
  (`--subsample-docs`), word types then extracted from those documents alone, with the
  document count chosen by bisection so that the resulting type count lands within 2%
  of the target. The tablet model is how a corpus is actually smaller: it keeps common
  words and loses rare ones.
- Recorded at each size and model: for each of the three parts, the number of twenty
  that meet it; the number meeting all three; the median and range of the top-10
  matched count.
- **The floor is the smallest size at which at least sixteen of twenty subsamples meet
  all three parts**, one floor per model.

Readings, written before the run. The two floors agree within one size step: quote the
tablet floor as the number and note the agreement. The tablet floor is lower: common
words carry the paradigms and hapax names carry noise, and the number the field needs is
the lower one. The tablet floor is higher: rare words carry endings the method needs,
and "more Linear A" would have to be more of the rare vocabulary. No floor below 3,768
in either model: the method is readable only at Linear B's full size and the sweep's
finding is that the floor is at or above it. Whatever the outcome, the number describes
Greek text under Linear B spelling; it transfers to Linear A only under A-040's limit,
that Minoan is assumed to inflect by suffix at least as visibly as Greek does.

### Segmentation sensitivity on Linear A — 2026-09-11 · pre-registered, not yet run · Kober 0.3 stage 1, no protocol change

Tests A-002, that GORILA's word dividers give the word boundaries, by running stage 1 on
the SigLA edition of Linear A (`aegean.load("sigla")`, CC BY-NC-SA), which carries its
own word division. Feasibility measured 2026-09-11, read-only: 697 of 802 SigLA
documents align with a GORILA document; 96 of those agree word for word and 508 differ,
of which 13 differ in divider placement alone, 137 in sign readings, and 365 in whole
words present in one edition and not the other, mostly line coverage. SigLA yields 692
word types under the Kober filter against GORILA's 988, with 577 shared. So this is a
test of the *edition*, readings and coverage included, and only weakly of dividers
alone; the entry says so.

Design. Stage 1 on SigLA, seeds 0 and 1, 200 draws. Beside it, GORILA subsampled to
692 word types by the type model, twenty subsample seeds, so SigLA's numbers are read
against GORILA at the same size rather than against GORILA at 988. The readable
statistic is the paradigm-count ratio to its N1 mean; alternation support is not
readable at either size (F-019). Also reported: the paradigm-count ratio on the 577
shared word types alone, computed once for each edition's own segmentation of them.

Readings, written before the run. SigLA's ratio above its N1 99th percentile and inside
the range of GORILA's twenty subsamples at 692: the one Linear A statement in F-019 does
not depend on which edition segments the words, and A-002 becomes a tested limit for
that statement. SigLA's ratio at or below its null: the statement depends on GORILA's
segmentation and readings, and A-002 is flagged as load-bearing. SigLA's ratio above the
null but outside GORILA's range at the same size: the editions differ in a way the
method sees; report which direction and explain nothing. No reading names a language.

Run 2026-09-11 (FINDINGS F-023). First reading: SigLA's ratio 1.58 is above its null and
inside GORILA's range at 692 (1.41 to 1.85); the shared 577 types give 1.55. The Linear A
statement does not depend on the edition. The a-/ja- prefix pair does not reappear under
SigLA.

### Null rate of the grammar match, and precision criteria — 2026-09-11 · pre-registered, not yet run · no protocol change

Prerequisites for Kober 0.4 (TODO item 8). Part 3 of the stage 1 criterion, at least
seven of the ten best-supported alternations on the reference list, has never had a
null: the reference rules are permissive (any same-consonant o/a pair matches "gender"),
so a shuffled corpus's own top ten will match some. Measured here, no protocol change.

Design. For every N2 draw, take that draw's own top-n alternations by support (ties as
A-053) and count how many `is_grammar` matches, for n in (3, 5, 10). Report the null
distribution of the matched count at each n (mean, sd, 95th, 99th percentile) and the
real value's percentile. Run on full Linear B (seeds 0 and 1) and on the twenty
tablet-model and twenty type-model subsamples at 988 from F-022. Then, for each
subsample, evaluate candidate precision criteria without choosing one: "real matched
count at top-n exceeds the null 99th percentile" for n in (3, 5, 10), and the raw
"k of top-n on the list" for (n, k) in ((3, 3), (3, 2), (5, 4), (10, 7)). Report, per
model, how many of twenty pass each. Also report, for the full corpus, the same.

Readings, written before the run. Full corpus: the real matched count at every n sits
above the null 99th percentile; if it does not at n = 10, F-016's part 3 was met partly
by chance and F-016 gains a dated note (the null-exceedance parts stand on their own).
At 988: the null matched count at n = 10 is expected in the range 2 to 5 given the
permissive rules; if the tablet-model real median of 6 lies inside that range, F-019 and
F-022 gain a dated note that part 3 pass counts at small sizes include chance matches,
and their floors are re-read as floors of null-exceeding grammar rather than of raw
counts. Whichever precision criterion is later chosen for 0.4 must be one whose pass
rate under the null is at or below one in twenty; the table produced here is what that
choice is made from, and the choice is then frozen before any Linear A run.

Run 2026-09-11 (FINDINGS F-025). Ties-included top-n found unusable at small sizes (tie
sets of hundreds); strict variant added (A-072) and read. Full corpus: real 9 against a
null 99th percentile of 2 to 3. At 988: real above the null in 17 of 20 (type) and 19
of 20 (tablet) at n = 10, but all top three right in only 5 and 6 of 20. Criterion for
0.4 frozen from the table: strict top three all on the list, sixteen of twenty,
tablet model.

### 0.4 — 2026-09-11 · pre-registered, not yet built · context-aware; stage 1 statistics unchanged in definition

Proposed by the prior-art session (TODO item 8). Purpose: close part of the gap between
the machine floor (F-022) and Kober's hand result by using tablet context and asking for
fewer, surer findings. Design in `kober-method.md`, "Version 0.4".

- *Context class* of a word token: (document support type from metadata, whether the
  token opens its line, the kind of the next token on the line: word, logogram,
  numeral, or none). Script-agnostic; identical for both corpora. A word *type* takes
  its dominant class, ties broken by sorted key (A-075).
- *Context-restricted support*: a stem counts toward an alternation only if its two
  words share a context class (A-076). Paradigm count and alternation support are
  otherwise as 0.1.
- *Nulls preserving context*: N1 shuffles signs by position within (length, class); N2
  shuffles endings within (length, class). Strata with fewer than two words pass through
  (A-077). The chance rate of the criterion is re-measured under these nulls, since the
  null has changed.
- *Criterion, frozen from F-025 before any build*: strict top three all on the reference
  list on at least sixteen of twenty tablet-model subsamples at 988, and the criterion's
  own rate under the stratified N2 at or below one in twenty per subsample. Type model
  reported beside it. Baseline to beat: 6 of 20 (tablet), 5 of 20 (type). Secondary,
  reported not gated: four of the top five.
- *Readings, written now.* Pass: tablet context makes the strongest alternations
  reliable at Linear A's size on Greek text; run Linear A once, same code, and report
  the top three and top ten context-supported alternations with support and null
  percentiles, and the candidate paradigms with their contexts, naming no language and
  grading nothing. Fail at or near baseline: context as encoded does not help at this
  size; record, do not run Linear A. Improves but below sixteen: record the count; the
  bar is the bar; do not run Linear A. Chance rate above one in twenty: the stratified
  null is too weak; stop and redesign before reading anything.
- *Known risks.* Context classes may be too coarse to matter or too fine to populate;
  Linear A's contexts (vessels, nodules, short tablets) differ from Linear B's, so a
  pass on Linear B transfers only under A-040 and A-078. Linear A's maximum support of 2
  means context can raise precision, not support.

Built and run 2026-09-11 (FINDINGS F-026). Failed: top three all grammar in 2 of 20
tablet-model subsamples against a bar of 16 and a 0.3 baseline of 6. Diagnostic on the
full corpus: the two forms of a real paradigm share a slot 21% of the time and show no
consistent slot pair, so the feature is uninformative and the filter removes evidence.
Linear A not run. 0.4 stays as an opt-in flag; no 0.5 on slots.

### Entry-role diagnostic on Linear B — 2026-09-11 · pre-registered, not yet run · read-only, no instrument

Question. Do the two forms of a real Linear B paradigm occupy the same *role* on
parallel tablets more often than chance? This is the finer-grained form of the question
F-026's slot diagnostic answered no to at the level of (support, line-initial, next
kind). It decides whether an entry-alignment instrument (TODO item 8, open question) has
anything to work with, and it runs before Kober 1946 is read because Linear B's answer
does not depend on what she did.

Role definition, fixed now. A tablet is a sequence of entries; an entry is a maximal run
of tokens on one line ending at a logogram or numeral or at the line's end. A word's
role is the tuple (series of the document, as `aegean.analysis.hands.series_of`; index
of its entry on the tablet, capped at 3; position of the word within its entry, first,
middle or last; the logogram that closes the entry, or "none"). A word type's roles are
the multiset of roles of its tokens.

Statistic. For each ending alternation with support of three or more in Kober 0.3 stage
1 (the same alternations as F-016), and for each stem supporting it, the two forms'
role sets are compared: (a) same-role rate, the fraction of stem pairs whose two forms
share at least one role; (b) same-series rate, sharing at least one series. Reported
per alternation for the top ten and pooled over all with support ≥ 3, with the real
value, and beside it the rate under a null that pairs each form with a random word type
of the same length and the same corpus frequency band (four bands), 200 draws, so that
frequent words' wide role sets do not pass as agreement.

Readings, written before the run. Pooled same-role rate above the null 99th percentile
and above 0.5: forms of one word do sit in the same role across tablets, entry alignment
is informative, and Kober 0.5 is worth pre-registering. Above the null but below 0.5:
informative but weak; report it and decide on the top-ten breakdown whether the
grammatical alternations (gender, genitive, eu-stem) carry it, since those are what
Linear A would be searched for. At the null: entry role, like slot, does not identify
forms of one word on Linear B; the entry-alignment line closes with F-026 and the
Kober line stops at F-027 on this corpus. Same-series rate is reported for information
and read only if same-role is above the null, because series is a property of
vocabulary as much as of grammar.

Run 2026-09-11 (FINDINGS F-028). Pooled same-role rate 0.087 against a null 99th
percentile of 0.024; grammar 0.159, not grammar 0.050. Second reading: informative but
weak, carried by the grammatical alternations. Filter designs closed; re-ranker
pre-registered as 0.5.

### 0.5 — 2026-09-11 · pre-registered, not yet built · entry-role tie-break; stage 1 unchanged

Change from 0.3: none to any statistic or null. Only the *ordering* of alternations for
the strict top-n changes: rank by support descending, then by the number of supporting
stems whose two forms share an entry role (F-028's role definition, computed by the
same code as `scripts/kober_entry_roles.py`, moved into `src/kober/roles.py`), then by
the existing lexicographic tie-break (A-072). The paradigm count, the support values,
N1 and N2 are byte-identical to 0.3; the regression pins must stay green. Under the N2
null the same ordering rule is applied to each draw, with roles staying attached to
words as endings shuffle, so the strict grammar-match null (A-072) is recomputed under
the new ordering and remains the chance rate.

Criterion, frozen from F-025 and F-027 and identical to 0.4's for comparability:
**strict top three all on the reference list in at least sixteen of twenty tablet-model
subsamples at 988 word types**, type model reported beside it, with the criterion's
chance rate under the re-ordered N2 at or below one in twenty per subsample. Baseline to
beat: 6 of 20 tablet, 5 of 20 type (F-025). Secondary, reported not gated: at least two
of the top three (F-027 baseline 20 of 20 tablet, 16 of 20 type), and top ten matched
against its null.

Readings, written before the build. Pass: role-sharing is enough to order the strongest
alternations at Linear A's size, and 0.5 runs on Linear A once, same code, reporting the
top three and top ten with support, role-sharing count and null percentiles, naming no
language. Improves on baseline but below sixteen: record the count; the bar is the bar;
Linear A is not run. At or below baseline: role-sharing is too rare at 988 to move the
order, which the F-028 caution predicts, and the Kober line stops at F-027 on this
corpus with entry alignment closed as well as slot context. Chance rate above one in
twenty: the ordering is picking up something the null does not preserve; stop and
diagnose before reading.

Built and run 2026-09-11 (FINDINGS F-029). Tablet model 9 of 20 against a bar of 16 and
a 0.3 baseline of 6; type model 6 of 20 against 5; chance rate 0 throughout. Middle
reading: improves, below the bar, Linear A not run. 0.5 stays as an opt-in flag.

### 0.6 — 2026-09-11 · pre-registered, not yet run · reference list revised; stage 1 and stage 2 untouched

Change from 0.5: one rule added to `reference.py`, and nothing else. Rule 11, *ethnic
derivation*: e2 == e1[:-1] + (Ci, JO) or (Ci, JA) where e1 ends in a sign Co, Ci has the
same consonant as Co and vowel i, Co has vowel o; that is, X-so / X-si-jo, X-so /
X-si-ja, X-to / X-ti-jo, X-to / X-ti-ja, the pattern Kober 1946 built Cases I to III on.
Source: kober1946 and Ventris and Chadwick 1973 on the ethnic adjectives in -ios.

Why a version: part 3 of the stage 1 criterion counts rules, so a rule added after the
runs changes what "seven of ten" and "top three all grammar" count, on every existing
file. Stage 1 statistics, both nulls and both grids are unchanged; the regression pins
must stay green. Every existing results file is rescored under the new list, not
rerun, into a `reference_v2` block beside the original counts, and every calibration
table (F-025, F-026, F-029) is reproduced with both columns.

Readings, written before the rescoring. Full corpus: the top ten is unchanged, so the
nine of ten stands; report how many of the top fifty gain a rule. At 988: the strict
top-three and top-ten matched counts can only rise or stay; report the rise, and the
null rate, which can also rise because the new rule admits more chance pairs. The bar
for any criterion stays where F-025 put it; if a calibration that failed under the old
list passes under the new, it is reported as passing under 0.6 and failing under the
list it was pre-registered with, both, and the Linear A gate opens only if 0.6's own
null rate is at or below one in twenty. Disclosure: the four alternations' supports and
ranks were seen before this was written; their rule status under the new rule is
known to be "matched" by construction, and that is the point of the revision.

Run 2026-09-11 (FINDINGS F-031). Full-corpus top ten unchanged; two of the top fifty
gain a rule (her triplets). Tablet-988 all-three rises 6 to 11 under the 0.3 ordering
and 9 to 12 under 0.5's; type-988 unchanged. Chance rate stays at or below one in
twenty. Corrected baselines for 0.7: 11 (no tie-break) and 12 (role tie-break).

### List homogeneity on Linear B — 2026-09-11 · pre-registered, not yet run · read-only, no instrument

Kober's Assumptions 4, 6 and 7 (kober1946): words listed on one tablet, each followed by
an ideogram and a number, share a case, so they share an ending, and a variant counts
only if it occurs in a list that is itself homogeneous. Neither slot (0.4) nor entry
role (0.5) encodes this. Before any instrument is built on it, measure it on Linear B.

Statistic. For each document with at least three eligible listed words (WORD, CERTAIN,
two or more signs, each followed on its line by a logogram or numeral), the
*homogeneity* is the fraction of its listed words whose final sign equals the document's
modal final sign. Report the distribution over documents (median, quartiles), pooled
over all listed words, and by tablet type (series prefix letter). Null: final signs
shuffled across all listed words in the corpus, holding each document's word count
fixed, 200 draws; report the null distribution of the pooled homogeneity and of the
count of documents at homogeneity ≥ 0.5. Second statistic, Kober's Assumption 7 as a
number: for each of the top twenty ending alternations by support, the fraction of
supporting stem pairs in which *each* form occurs in at least one document whose modal
final sign is that form's final sign, against the same null.

Readings, written before the run. Pooled homogeneity above the null 99th percentile:
co-listed words share endings beyond chance, Kober's Assumption 4 is a fact of the
corpus, and a list-anchored alternation statistic (Kober 0.7) is worth pre-registering,
with the F-025 bar. If in addition the Assumption 7 fraction is higher for the
grammatical top alternations than for the rest, the condition selects grammar, which is
what she used it for. At the null: co-listing carries no ending information on Linear
B, her Assumption 4 was a heuristic that happened to hold on the few tablets she chose,
and no list-anchored instrument is built.

Run 2026-09-11 (FINDINGS F-030). Pooled homogeneity 0.420 against a null 99th
percentile of 0.257: Assumption 4 holds. Assumption 7's fraction 0.056 against 0.020,
grammar 0.058 and not-grammar 0.049: real, unselective, one pair in eighteen. First
reading triggered on homogeneity, not on selectivity; 0.7 pre-registered as a tie-break.

### 0.7 — 2026-09-11 · pre-registered, not yet built · list-homogeneity tie-break after roles; stage 1 unchanged

Change from 0.5: a fourth ordering key. Alternations sort by support, then role-sharing
count (0.5), then the count of supporting stem pairs in which both forms satisfy
kober1946's Assumption 7 (each form occurs in a list whose modal final sign is that
form's final sign; `scripts/kober_list_homogeneity.py`'s definition, A-101), then the
lexicographic tie-break. Nothing else changes; the pins stay green; under N2 the same
ordering is applied per draw with lists computed on the draw's shuffled endings.

Criterion: identical to 0.4 and 0.5, strict top three all grammar in sixteen of twenty
tablet-model subsamples at 988, chance rate at or below one in twenty. Baselines: 0.3
six (eleven under the 0.6 list), 0.5 nine (twelve under 0.6). Reading, written now: the expectation is at or near nine, because
F-030's condition admits one stem pair in eighteen on the full corpus and fewer at 988;
at or near nine closes the context line with three measured encodings; sixteen or more
would mean the list condition carries information roles do not, and Linear A runs once.
The rescoring under 0.6's reference list is reported beside the v1 count.

Built and run 2026-09-11 (FINDINGS F-032). Tablet model 9 of 20 (v1) and 12 of 20 (v2),
identical to 0.5; type 6 of 20; chance rate 0. At the 0.5 count, as expected: the
context line closes with three measured encodings. No Kober version 0.4 to 0.7 ran on
Linear A. The Kober line is closed on this corpus; every version remains an opt-in flag
with its pins green.

### 0.7 on Linear A, EXPLORATORY — 2026-09-11 · pre-registered before the run; not a finding

At Ru's request, to see whether the context keys move anything on Linear A. Conditions
written first. (1) The run is labelled exploratory in its results file
(`results/exploratory/`) and in FINDINGS, where it enters as **exploratory**, never
current, and is quoted by no claim. (2) No alternation receives a rule name: the
reference list is Mycenaean Greek and its application to Linear A would be a category
error; `rule_v1` and `rule_v2` are reported as withheld. (3) The only statistics read
are structural: how many alternations tie at the top under 0.3's ordering, how many
positions the role key and the list key change, how many top-ten alternations carry any
role-sharing or list support, and the chance-rate machinery's output as a sanity check.
The top three are printed as sign pairs and not interpreted. Expectation, written now:
with every Linear A alternation at support two or below (F-019), 988 word types mostly
carrying one role each, and few Linear A documents with three or more listed words, the
keys will move little and no reading follows either way.

Run 2026-09-11 (FINDINGS F-033, exploratory). The keys moved ten of ten and eight of
ten positions, the opposite of the expectation, because 207 of Linear A's 209
alternations tie at support one and the keys select from that pool rather than order a
ranking. Recorded as the concrete form of the gate's rationale; no finding changes.

### 0.8 — 2026-09-12 · pre-registered, not yet built · reference list v3 from Documents in Mycenaean Greek; stage 1 and stage 2 untouched

Change from 0.7: `reference.py` gains `version=3`, a list derived from Ventris and
Chadwick 1973, chapter III §6 (Morphology) and Word-formation, read 2026-09-12
(docs/works/ventris_chadwick1973.md, V). Nothing else changes; versions 1 and 2 stay
byte-identical; pins stay green. Rules are stated on sign labels; C is a sign's consonant
(`values.consonant_of`), V its final vowel; "same consonant" means equal C.

Version 3 = versions 1 and 2, plus:

| rule | matches | source |
|---|---|---|
| 12 consonant-stem case | e1 and e2 differ only in their final sign, same consonant, vowels any two of a, e, o, i | pp. 85–86: -ne/-no, -te/-ta, -de/-do |
| 13 consonant-stem suffix | e2 == e1 + (S,) with S in {NE NO NA TE TO TA DE DO DA RE RO RA SE SO SA KE KO KA SI} | p. 85: wa-na-ka / wa-na-ka-te; dat. plur. -si |
| 14 s-stem set | after removing a final (O), (I), (A), (A2), (SI), (PI) or (E) from each ending, or nothing, the remainders are equal and end in a sign with vowel e | p. 86 |
| 15 u-stem | e2 == e1 + (WE,), (PI,) or (O,) with e1 ending in a sign with vowel u | p. 86 |
| 16 eu-stem plural | e2 == e1 + (SI,) or (PI,) with e1 ending in U | p. 86 |
| 17 -went- | e2 == e1 + (TO,) or (SA,) with e1 ending in WE | p. 86, note 1 |
| 18 participle plural | e2 == e1 + (TE,) with e1's final vowel o | p. 88: e-o / e-o-te |
| 19 infinitive | e2 == e1 + (E,) with e1's final vowel e | p. 88: e-ke / e-ke-e |
| 20 feminine of -eus | e1 ends in U and e2 == e1[:-1] + (JA,) | p. 89: i-je-re-u / i-je-re-ja |
| 21 material adjective | {e1, e2} ⊂ {(E,JO), (E,O), (I,JO)} after a common prefix | p. 89: wi-ri-ne-jo / wi-ri-ne-o / wi-ri-ni-jo |
| 22 spelling variant | endings equal after trailing digits are stripped from labels, or differ only as JA / A2 | pp. 46–47: pa-we-a / pa-we-a2, a-ke-ti-ra2 / a-ke-ti-ri-ja |

Rules 1 to 11 keep their names and order; a pair matches the first rule that fires. Rule
12 subsumes rule 1 (gender) for o/a; rule 1 is kept first so existing counts keep their
names. Tests must pass the chapter's own paradigm forms: ko-to-na / ko-to-na-o, te-o /
te-o-jo, po-me-ne / po-me-no, wa-na-ka / wa-na-ka-te, pa-we-a / pa-we-a2, ta-ra-nu /
ta-ra-nu-we, ka-ke-u / ka-ke-u-si, ko-ma-we / ko-ma-we-to, e-o / e-o-te, e-ke / e-ke-e,
i-je-re-u / i-je-re-ja, wi-ri-ne-jo / wi-ri-ni-jo, a-mi-ni-so / a-mi-ni-si-jo; and reject
ku / ma, se / ta, jo / qe.

Why a version. As 0.6: part 3 counts rules, so every existing file is rescored under v3
into a `reference_v3` block beside v1 and v2, and the strict grammar-match null is rerun
under v3 for the full corpus and the forty 988 subsamples, so the chance rate under the
broader list is measured, not assumed. Reading, written before the build. Full corpus:
top ten unchanged by construction; the count of the top fifty gaining a rule is
reported. At 988: matched counts can only rise; the null can also rise, and that is the
thing to watch: **if the v3 null's 99th percentile at n = 10 exceeds 3 on the full
corpus, or the "top three all grammar" chance rate at 988 exceeds one in twenty in more
than two subsamples, v3 is too permissive to serve as a criterion and is reported as
such, with the rules that fire most under the null named.** Otherwise v3 becomes the
default list for any future run and the F-025 and F-027 tables are re-read under it.
Disclosure: the rules were written after reading the chapter with the F-016 top twenty
in mind; no v3 number has been computed.

Built and run 2026-09-12 (FINDINGS F-034). Permissiveness check passed: full-corpus null
99th percentile at n = 10 is 3, at the bar; chance rate of top-three-all-grammar at 988
never above 0.005. Tablet-988 all-three: 13 of 20 under the 0.3 ordering, 14 under 0.5 and
0.7; type unchanged within one. v3 is the default reference list from here. Four of the
new rules are pre-empted by broader earlier rules and never surface (A-124).

### 0.9.1 — 2026-09-12 · current · reproducibility fix, no statistic changed

Spike S-013 found that null draws were not reproducible across processes: the length
groups (and the length-and-class strata of 0.4) were visited in the order the set
iteration first met them, which depends on Python's per-process hash seed, and the
draws consume one random stream group by group. Every statistic, every real value and
every null distribution are unchanged in definition; the null percentiles in results
files written before this fix were drawn under an unrecorded hash seed and reproduce in
distribution, not bit for bit. From 0.9.1 the groups are visited in sorted order and a
given seed gives the same draw in any process. No finding is affected; the regression
pins (real values) pass unchanged. A-057 amended.

### 0.9 — 2026-09-12 · pre-registered, built and run 2026-09-12 (FINDINGS F-040) · medial channel; homophone-merged identities as a sensitivity; stage 1 ending and prefix channels unchanged

Change from 0.8, additive. (a) A **medial channel**: for words of three or more signs,
an alternation is a pair of words identical except at one interior position (Packard's
third class, "first and third signs identical, second differs", generalised to any
interior position); its support is the number of word pairs so related, grouped by the
pair of differing signs. Null: N1 (position-matched shuffle) as for the paradigm count,
and, for the ranked pairs, a shuffle of the interior sign among words of the same length
holding the flanking signs fixed (N3, 200 draws). Answer key for Linear B: pairs whose
differing signs share a consonant under the known values (Ventris and Chadwick §13
homophones and §3 glides: a2 / ja, -i-jo / -e-jo material adjectives, e / i confusion
p. 76), scored after the ranking; the chance fraction of consonant sharing is reported
beside it as in stage 2. Criterion, written now: on Linear B the count of medial pairs
exceeds the N1 99th percentile, and the consonant-sharing fraction among the top twenty
medial pairs exceeds its N3 99th percentile. On Linear A, run once under this version,
report the count and the top ten pairs as sign pairs, no reading. (b) **Identity
sensitivity**: a `--merge-homophones` flag that maps a2→A, ai2→AI, pa2→PA, pu2→PU,
ra2→RA, ra3→RA, ro2→RO, ta2→TA (§13) and *118 and similar unidentified signs unchanged;
every stage 1 statistic rerun under it on Linear B and, once, on Linear A; reported
beside the unmerged numbers as a sensitivity, not a replacement. (c) No line-fragment
handling: F-035 found none to handle. (d) The reference list version used for part 3 is
whichever F-034 adopts.

Pins: a new regression file `tests/test_kober_regression_09.py` pins the 0.9 outputs on
both corpora beside the 0.1 pins, which stay untouched.

Readings, written before the build. Linear B medial count above its null and the
consonant fraction above N3: the medial channel is a real third channel and Linear A's
medial count is readable against the size-matched control, which is run first as in
F-019. Medial count above null but consonant fraction at null: the channel sees
spelling variation, not phonology; report and do not read Linear A's pairs. Both at
null on Linear B: Greek has too little medial alternation to calibrate the channel, and
Packard's 26 Linear A pairs stay a by-hand observation with no positive control. On the
homophone merge: a Linear A maximum support that rises above two under merging is
reported with its null; nothing more.

Built and run 2026-09-12 (FINDINGS F-040). Medial channel: Linear B pair count above
N1, consonant fraction at the N3 99th percentile (0.35 against 0.35), nothing at 988,
nothing on Linear A; second pre-registered reading. Homophone merge: Linear B 988
tablet-model all-three 13 to 18 of 20, past the context line's bar; Linear A paradigm
count and maximum support unchanged. Reported as a sensitivity as pre-registered; the
Linear A run under it was part of the version.

### 0.1 on Linear A — 2026-09-11 · pre-registered, run 2026-09-11 (FINDINGS F-019)

Same code, same parameters, same nulls, `--allow-lineara`. Nothing is tuned. What was
known before writing this: the sizing count in `kober-method.md` (988 unnormalised word
types; 51 of 547 two-sign stems with two or more one-sign endings; no ending
alternation supported by more than two stems) and the field's own structural findings
listed there. Nothing else about Linear A under this instrument has been computed.

**Size-matched control, run first.** Linear B has 3,768 word types; Linear A about a
quarter of that. Before Linear A runs, the Linear B instrument runs on ten random
subsamples of Linear B word types of Linear A's exact type count (seeds 0 to 9, each with
its own N1 and N2 at 200 draws), and the same is recorded for each: paradigm count
against its N1 99th percentile, maximum support against its N2 99th percentile, top-10
matched to the reference list. This says what the criterion looks like when Greek is the
answer and the corpus is Linear A's size. A Linear A result is read only against this.

Readings, written before either runs:

- *Ending channel, paradigm count.* Above its N1 99th percentile: Linear A word types
  share stems with varied endings more than positional sign frequencies produce. That is
  consistent with suffixal morphology and equally with compound names, transaction
  terms and formula words sharing elements; it identifies no language and does not
  separate inflection from derivation (A-030 in another form). At or below: no readable
  suffixal structure at this size. If the Linear B subsamples also fail the count at
  this size, the corpus is below the method's floor and the Linear A result is
  uninformative, not negative. If the subsamples pass and Linear A does not, that is a
  difference between the corpora worth recording, with the candidate explanations that
  Linear A's language suffixes less than Greek, that its word dividers cut differently
  (A-002), or that its vocabulary is names and formula words to a greater degree.
- *Ending channel, alternation support.* Not readable. Sizing shows a maximum of two
  stems per alternation; the N2 null maximum will be near that. Report the top ten with
  supports and the N2 percentile, attach no rule name and no language, and do not read
  it. If a support of four or more appears, say so and leave it.
- *Prefix channel.* Read by N2 support only (A-047). Report whether the pair (a-, ja-)
  or (a-, ja-…) appears among the top prefix alternations and at what support, because
  the field reports that alternation on the libation formula; its presence at support
  one or two is not evidence of anything and is recorded as agreement with what eyes
  found, no more. Above the N2 99th percentile on the maximum: prefixing structure
  exists beyond chance, which Linear B did not show; record it and explain nothing.
- *Grid on Linear A.* Runs only if F-017 meets its stage 2 criterion on Linear B. The
  check is the fraction of Linear A bridging pairs with support ≥ 2 that share a
  consonant *under the conventional (Linear B-derived) values*, against N1. This is the
  one place the value convention is tested rather than assumed: the grid comes from
  Linear A's internal structure alone, and the question is whether the transferred
  values respect it. Read only if at least ten pairs reach support 2; below that, report
  the count and stop. Above the N1 99th percentile: the value transfer is consistent
  with Linear A's own alternation structure for the signs involved, which bears on
  A-001 for those signs and on nothing else. At or below: either the pairs are too few
  or the transferred values do not respect the internal grid; the two are separated by
  the size-matched Linear B subsamples' grid fractions.

Whatever the outcome, no entry produced under this pre-registration names a language.

Outcomes (F-019). Size-matched control: at 988 word types Linear B meets the paradigm
count in ten of ten subsamples, the maximum support in three, the seven-of-ten in none,
so only "structure exists" survives at Linear A's size. Linear A: paradigm count above
the null at ratio 1.52 against Linear B's 1.53; alternation support at the null and
below every subsample; prefix maximum support at the null's 99th percentile with a-/ja-
at the top; grid below the ten-pair floor. Read as pre-registered: recurring stems with
varied endings beyond chance, nothing else readable, no language named.

## Value transfer (A-001): the toponym test

Does the convention that Linear A signs carry Linear B values have positive evidence
internal to the corpora? Packard 1974's Table 14 said yes through Knossos place names;
spike S-003b (F-038, exploratory) reproduced that under a proper null. This line
promotes it. Code: `scripts/toponym_test.py` (planned), importing the value-permutation
null from `src/hypotheses/run.py` and nothing from the Kober line.

### 1.0 — 2026-09-12 · pre-registered, run 2026-09-12 (FINDINGS F-041)

Frozen before the run. Lexicons: (a) Knossos toponyms, the S-003b list of 32 verified in
DĀMOS, re-derived in the script from Ventris and Chadwick 1973's place-name discussion
and Packard's Table 11, each entry cited; (b) wrong control 1, Knossos personal names,
the 32 most frequent non-toponym word types of the Knossos livestock series; (c) wrong
control 2, Pylos toponyms, the 16 Hither and Further Province place names and any others
attested in DĀMOS's Pylos documents, which are mainland places a Cretan archive should
not name; (d) wrong control 3, Knossos toponyms with their sign order reversed, a lexicon
of the same signs and lengths with no meaning. Corpora: GORILA and SigLA, Linear A word
types of three or more certain signs. Matches: Packard's 3= and 4=, literal label
identity at the fixed positions, shared consonant at the one free position. Null: label
permutation within frequency bands at every position, groups of ten and four bands, 400
draws, seeds 0 and 1. Reported: real count, null mean, sd, 95th, 99th percentile and the
real percentile for every lexicon, class, edition, banding and seed; the matched Linear
A words and toponyms as sign labels (place names are published readings, not corpus
text); and the set of sign labels whose values the matches involve.

Criterion: the toponym count exceeds the null's 99th percentile for both editions, both
bandings and both seeds, in the 3= class, and no wrong control does so anywhere.

Readings, written now. Met: A-001 gains a tested positive component, stated as "the
transferred values are supported for the signs occurring in the matched place names",
with the sign list; the register row is amended and F-038 is superseded by the main-line
entry. Toponyms clear but a wrong control also clears somewhere: the test does not
separate place names from any lexicon of the same shape, and A-001 stays untested; the
control that cleared is named. Toponyms fail on either edition: the spike's result was
edition- or seed-dependent and is recorded as such.

Assumptions: A-133 (the toponym list is the field's, not ours, and complete enough),
A-134 (Pylos toponyms are absent from Cretan Linear A by history, which is what makes
them a control), A-135 (label identity is the value transfer; a match under identity
tests the convention and nothing looser); construction decisions recorded at build time,
A-136 to A-139.

Outcome: criterion met in all eight cells; no wrong control clears anywhere (the Pylos
control sits at the 91st to 98th percentile without clearing). First pre-registered
reading applies: A-001 amended, F-038 superseded by F-041.

## Supplement sensitivity (F-047): the four new word types

Does adding what the 2024 GORILA supplement contributes to the loaded corpus change any
Linear A result? F-047 measured the contribution: 18 absent documents, 4 complete word
types. Code: a `--extra-word-types <path>` option on `scripts/toponym_test.py` and on
`scripts/kober_run.py`, reading a local JSONL of sign-label tuples (not committed), appended to the GORILA word-type set before anything
else runs; without the option nothing changes.

### 1.1 — 2026-09-12 · pre-registered, run 2026-09-12 (FINDINGS F-048) · the four division variants

The 1.0 run showed the four types from the absent documents are all attested elsewhere
in GORILA, so 1.0 appended nothing. The supplement's index holds exactly four complete
word types absent from the loaded set, and all four are word-division differences on
two loaded Petras documents: the supplement divides `U-KA-RE | A-SE-SI-NA` (PE 1) and
`A-KA-RA | KI-TA-NA-SI-JA-SE` (PE Zb 3) where the loader runs each pair together. Frozen
before the run: the same two runs as 1.0 with those four appended
(a local file, not committed), same draws, bandings and
seeds, results under `results/supplement-sensitivity/division/`. Same readings as 1.0;
in addition, a toponym match involving one of the four is a division-dependent match
and is reported as such under A-002, not as support for A-001.

Outcome: word-type count 992; every toponym real count and matched pair identical to
F-041, null means moved in the second decimal; paradigm count 101 and maximum support 2
unchanged. First reading.

### 1.0 — 2026-09-12 · pre-registered, run 2026-09-12 (FINDINGS F-048)

Outcome: every toponym cell identical to F-041; paradigm count 101 and maximum support 2
unchanged; the four appended types (I-DA-DA, DI-NA-U, TA-NA-MA-JE, TU-PI-TA) were
already in the loaded word-type set from other documents, so the word-type count stayed
988. First reading, trivially. The output file is `extension-check.md`.

Frozen before the run. Word types: the four complete groups from the supplement's index
belonging to the 18 absent documents, converted from sign numbers to loader labels by the
local number-to-label map; a group with an unmapped code is dropped and the drop
reported. Runs: (a) Value transfer 1.0 exactly as F-041 ran it, GORILA edition only, with
the four appended, 400 draws, both bandings, both seeds; (b) Kober 0.9.1 stage 1 on GORILA
with the four appended, unmerged, 200 draws, seeds 0 and 1, reporting paradigm count
against N1 and maximum support against N2 beside the F-019 and F-040 values.

Criterion: none; a sensitivity. Readings, written now. No cell of (a) changes and (b)'s
paradigm count moves by at most the number of new stems the four introduce (at most 4)
with maximum support unchanged: the supplement contributes nothing measurable, F-047
stands as written. A toponym count changes: the matched word is named as sign labels
and A-001's sign list is amended accordingly. Maximum support rises above 2: reported
with its null, and the pair named; nothing more, since four words cannot carry a
paradigm claim. Assumptions: A-003, A-129, A-133 to A-139, the number-to-label map
(A-147: the supplement's sign numbers are GORILA's, so the map from Unicode names holds).

## Linear B restoration benchmark

Can a published neural-network result on restoring damaged Linear B text be reproduced
from the source database, and what does a frequency floor and a seen/unseen split do to
it? Code: `src/linearb_restore/`. Write-up: `docs/ai_context/linearb-restoration.md`.

### 1.1 — 2026-09-10 · current

Extension to the 308 Knossos A&B tablets, the series whose published figures were fully
verified (ML4AL 2024: top-1 30.3%, top-20 66.2%). Same pipeline as 1.0. Results: prior
8.7 / 22.4 / 58.4; bigram 27.7 / 48.7 / 72.3; lexicon 31.5 / 46.4 / 68.9; backoff 34.8 /
52.3 / 74.9. Lexicon lookup matches the neural network at top-1; the frequency floor sits
eight points below the published top-20; the seen-versus-unseen split is 82.8% against
3.0%.

### 1.0 — 2026-09-10 · current

- Extraction: Knossos D family (1,016 documents), one physical line per sequence,
  `CERTAIN` tokens only, underdots stripped and flagged, one-sign syllabograms
  reclassified from `UNKNOWN` to `WORD` by signary membership.
- Masking: exhaustive leave-one-sign-out. No augmentation, no duplication.
- Split: document-grouped five-fold, sha256-seeded.
- Candidate set: frozen from training items only, maskable signs only.
- Rankers: frequency prior, Witten-Bell sign bigram (pyaegean's own), lexicon pattern
  lookup, backoff blend.
- Reporting: every figure with its frequency floor, bootstrap CI, and seen/unseen
  stratification.

Results: prior 7.7 / 26.5 / 63.2; bigram 41.2 / 64.9 / 85.8; lexicon 62.6 / 73.4 / 85.5;
backoff 64.3 / 77.5 / 89.8. The plan's gate expected the bigram at ≈ 50 / 78 / 91; the
gap was traced to single-split variance (42.5% to 52.9% across eight seeds under the
prototype protocol) and not tuned away.

---

## Catalogue and documentation structure

Not a test protocol, but versioned here because the survey's verification flags are
themselves a method.

- **3 — 2026-09-11.** One page per work under `docs/works/`, YAML frontmatter, queryable
  by `scripts/bib.py`, individually reviewable. 56 works.
- **2 — 2026-09-11.** `bibliography.yaml`, single structured file. Removed the same day
  in favour of 3.
- **1 — 2026-09-10.** `docs/ai_context/state-of-the-art.md`, ~100 works in markdown
  tables with per-row verification flags (Y primary fetched, P secondary, S snippet,
  M measured locally).
