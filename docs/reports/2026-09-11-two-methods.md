# Two methods for an undeciphered script, tested on a deciphered one

A report on what this repository found between 10 and 11 September 2026. Written for a
reader who knows the Aegean scripts and has an hour. Every number is quoted from a
FINDINGS entry (F-nnn); every assumption from ASSUMPTIONS (A-nnn); every protocol
version from CHANGELOG. Nothing here is asserted for the first time.

Status: one author working with an AI coding assistant, not peer reviewed. How to check
any claim: `scripts/findings.py --show F-nnn` prints the entry, and CHANGELOG pins the
protocol version behind it;
`tests/test_kober_regression.py` pins the structural instrument's real values to the
committed results files.

---

## Summary

The method behind nearly every proposed Linear A decipherment, assign sound values and
look the words up in a candidate language's dictionary, cannot choose a language on this
corpus. On Linear B, where the answer is Greek, it scores Sumerian and Finnish nearly as
high as Greek. The failure is not power: it is that dictionary shape matches dictionary
shape, and more corpus would not fix it.

Alice Kober's method, grammatical structure from sign patterns with no sound values,
works when a machine runs it with a null model. On Linear B it recovers Mycenaean
grammar and the consonant grid. Its corpus floor is measured: about 1,900 word types
under the realistic model. At Linear A's size, 988 word types, it does on Greek text
what Kober did by hand: a couple of sure paradigms. On Linear A it says one thing, that
words carry recurring stems with varied endings beyond chance, at or below the low end
of what Greek shows at the same size, in both editions of the text. Its strongest
alternations sit at chance. No encoding of tablet context available to the instrument
changes that.

Three rules for this kind of work came out of the day, stated first because they cost
the most to learn.

## Three rules

1. **Read the primary source before building on it.** The Kober instrument was designed
   from secondary accounts and taken through two context versions before her 1946 paper
   was read. Her method is seven numbered assumptions; the strongest, that words listed
   together on a tablet share a case, was in neither version. A morning with the paper
   would have redirected hours. (F-030, F-031; result-discipline.md.)
2. **Check the answer key against the canonical example before it scores anything.**
   The reference list of Mycenaean grammar could not score a-mi-ni-so against
   a-mi-ni-si-jo, the triplet every summary quotes. The instrument's own output had
   shown the alternation at rank 46 since the first run; nobody looked. Correcting it
   moved the small-corpus baseline by five subsamples in twenty. (F-031.)
3. **Register a method's stated assumptions as atoms on day one**, marked encoded, not
   encoded, or tested, so that "which of hers have we not encoded" is a query. Kober's
   seven are A-109 to A-115.

Two older rules, from the etymological work, sit behind these: a wrong real language is
the only control that shows *which* structure a match detects (F-008), and a
restricted-pool comparison must hold the null fixed, because a null computed from the
sample moves with it (F-014, A-042).

## 1. The material and the control

Linear B, 5,932 documents and 54,476 tokens in DĀMOS, deciphered in 1952 as Greek.
Linear A, 1,721 documents and 6,406 tokens through pyaegean's transcription of GORILA,
undeciphered, transcribed by convention with Linear B sound values, which is the
circularity every phonetic argument about it must control for (A-001). After
normalisation and the two-sign filter the structural instrument sees 3,768 Linear B word
types and 988 Linear A.

The design principle of the repository is that Linear B is the answer key. Every instrument
pointed at Linear A has first been shown to recognise Greek in Linear B and to fail to
recognise Finnish there. Every result below was produced that way, with
the criterion and the reading written into the CHANGELOG before the run.

A third line, Linear B text restoration, is not covered here beyond one sentence: the
published neural benchmark is matched by a lookup of training word types, its top-20
metric sits near a sign-frequency floor, and accuracy falls from about 90% on word types
seen in training to under 10% on unseen ones (F-001, F-002). The paper's own Table 2
already carried a near-equivalent n-gram baseline (F-024).

## 2. The etymological method

**Instrument.** Map each sign to the set of consonants it may write under a hypothesis
(a Semitic map reconstructed from di Mino 2026, a Greek map from the decipherment with
voicing and aspiration folded); expand each word by the known Mycenaean spelling rules
(omitted codas, final s/n/r); score a word by the log of the mean dictionary count over
its candidate skeletons; compare with a null that permutes sign values within candidate
breadth and corpus-frequency band, four bands, which is Packard's 1974 design read
strictly (F-003 to F-005, protocol 1.0). Frozen on Linear B before Linear A was run
once.

**Calibration on Linear B, Greek the answer** (F-008, F-013; z against the null, 400
words, seeded sample):

| lexicon | map | z |
|---|---|---:|
| Greek, archaic (53,026 types) | Greek | +2.78 |
| Greek, LSJ (80,435) | Greek | +2.91 |
| Sumerian (ePSD2, 2,428) | Greek | +2.31 |
| Finnish (37,305) | Greek | +2.25 |
| Basque | Semitic | +2.68 |
| Turkish | Semitic | +2.62 |
| Hebrew, Strong's | Semitic | +0.30 |

Every real language beats the synthetic control with matched letter frequencies, so
"beats random" detects that a lexicon is a language, not which one (A-011). Greek's lead
over the best wrong real language under its own map is about one sample standard error
(F-013).

**Linear A** (F-008, F-012): Greek +3.10, where Greek is not the language, because the
transcription's values are Greek; Hebrew +2.44 inside the range of Finnish, Turkish,
Basque and Hungarian; Ugaritic's lead over Basque about one standard error across three
word samples once the laryngeal channel is closed. The same language scored two units
apart depending on dictionary type (Strong's +2.44, a Modern Hebrew frequency list
+0.59). Under the laryngeal-stripped variant Hebrew and Arabic fit Mycenaean Greek text
better than Linear A.

**Verdict.** A false-positive instrument. It returns a result for every language at the
strength of the right one, on the corpus where the right one is known. Its failure
mechanisms are named: dictionary shape, the laryngeal channel, sample-to-sample variance
three to four times the permutation error, and a null that moves with any restriction of
the pool. Restricting Linear A to the 25 signs whose values Meißner and Steele show to
be secure changes nothing the instrument can say (F-014). Kober said the same of
sign-shape matching in 1948, in one sentence about thirty signs in a hundred and twenty
against thirty in three hundred.

## 3. The Kober method

**Instrument** (kober-method.md, protocol 0.1). Word types. A stem is a word-initial
run of two or more signs; an ending the remaining one or two. A paradigm is a stem with
two or more endings; an alternation is a pair of endings; its support is the number of
stems carrying both. Two statistics, two nulls: the paradigm count against a
position-matched shuffle of signs that preserves length and positional frequencies; the
maximum alternation support against a shuffle of endings among words of the same length
that preserves which stems exist. Two hundred draws each. A reference list of Mycenaean
grammatical alternations, from Ventris and Chadwick, is consulted only after the ranking,
as the answer key. The pre-registered criterion: paradigm count above its null's 99th
percentile, maximum support above its null's 99th percentile, and at least seven of the
ten best-supported alternations on the reference list.

**Linear B, full corpus** (F-016): 932 paradigms against a null ceiling of 634; the top
alternation, -ja/-jo, on 57 stems against a null maximum of 19; nine of the top ten
grammatical, with the eu-stem triangle and the -jo genitive at the top. The grammar
match has its own null: a shuffled corpus's own strict top ten matches 1.3 rules on
average, 99th percentile 2 to 3 (F-025). Stage 2, the grid: bridging pairs from the ten
strongest alternations share a consonant under the known values four times in seven
against one in ten by chance (F-021); pooling every pair instead drowns the signal
(F-017, F-018), which is the narrowing Kober did by hand.

**The floor** (F-022). Linear B cut to smaller sizes twenty times each, two models. By
removing documents, the realistic model, the full criterion is met in sixteen of twenty
subsamples from about 1,875 word types (about 2,300 of 5,932 documents); by removing
random word types, from about 2,750. The part that fails below the floor is always the
grammar match; the paradigm count never fails; the support ranking clears its null from
about 1,500 types, or from 988 under the tablet model.

**At Linear A's size, on Greek** (F-025, F-027, F-031). At 988 word types the strict
top ten beats its grammar null in 19 of 20 tablet-model subsamples; two of the top three
are grammar in 20 of 20; all three in 6 of 20 under the original reference list and 11
of 20 once the ethnic-derivation rule from Kober 1946 is added. Kober's own corpus was
under 750 word types and her bar was two words sharing a variant rule. The instrument at
988 does what she published: a couple of sure paradigms.

**Linear A** (F-019, F-022, F-023). Paradigm count 101 against a null mean of 66.4,
six standard deviations, ratio 1.52. Linear B at the same size under the tablet model
gives 1.63 to 2.06. Maximum alternation support 2, at its null, where Greek at the same
size clears its null eighteen times in twenty. The prefix channel's top pair is a-/ja-,
the alternation the field reports on the libation formula, at the level chance produces.
SigLA's edition, 692 word types, gives the same paradigm statement (ratio 1.58; the 577
shared word types 1.55). The corrected sentence: **Linear A words carry recurring stems
with varied endings beyond chance, at or below the low end of what Greek shows at the
same corpus size, in both editions.** Nothing further is readable at this size.

**Context** (F-026, F-028, F-029, F-030, F-032). Three encodings of where a word sits on
the tablet were calibrated on Linear B at 988 against a fixed bar of sixteen in twenty
with the top three all grammar. A word-level slot class, used as a filter, fell to 2 of
20: the two forms of a real paradigm share a slot one time in five, so the filter
discards evidence. An entry role, used only to order ties, reached 9 (12 under the
corrected list): forms of one word share a role six times more often than chance, but
only one pair in eleven shares one at all. Kober's own condition, that words listed
together share an ending, holds on the corpus (homogeneity 0.42 against 0.25 by chance)
but admits one stem pair in eighteen and grammar and non-grammar alike; as a final
ordering key it changed nothing at the top. Net: the answer-key correction moved the
count by five; three context encodings moved it by one; what lies between twelve and
sixteen is the corpus.

## 4. The two methods side by side

From F-020, with the later corrections noted there.

| | Etymological | Kober |
|---|---|---|
| Question | Which language? | What structure? |
| What enters from outside | a sign map and a dictionary | nothing, until the answer key is read after the ranking |
| Linear B, answer known | Greek +2.8 to +3.2; Sumerian and Finnish +2.3 under the same map | criterion met; nine of ten grammar; grid pairs four of seven against one in ten |
| Linear A | every language beats the synthetic control; no real language separated from a wrong one beyond sample variance | one sentence: recurring stems with varied endings beyond chance, at or below Greek's low end at matched size |
| Why it stops | shape matches shape; more corpus would not help | power; the floor is measured, and Linear B shows where it is passed |

## 5. What can be said about Linear A

Only this. Its words show suffixal stem-sharing beyond chance, less than Greek does at
the same size, in two independent editions. That excludes a language with no visible
suffixal alternation at all and excludes almost none of the proposed candidates. It does
not separate inflection from derivation, names or formula words (A-030). Its strongest
alternations are at chance, so the grid check that would test the borrowed sound values
from Linear A's own structure has eight pairs to work with, below the pre-registered
floor of ten, and stays closed (F-019). Kober wrote in 1948 that inflection of Linear
B's type does not seem to exist in Linear A; these measurements say the same with a null
attached.

Testing candidate languages against this profile now would produce exactly the kind of
result the repository exists to stop.

## 6. Limits

- Every Linear A result uses sign identities from a volunteer transcription chain of
  GORILA (A-003), and every phonetic result uses Linear B values by convention (A-001).
- The Kober instrument presupposes suffixal inflection visible at the word's end (A-040);
  its prefix channel has no positive control, since Greek prefixes little.
- Linear A's documents are shorter than Linear B's and include vessels and nodules; the
  size-matched Linear B subsamples are the nearest available control, not a match
  (A-078).
- The reference list of Mycenaean grammar is from a source at verification P (Ventris
  and Chadwick 1973) and was shown incomplete once; it may be incomplete elsewhere
  (A-037).
- Kober's 1946 and 1948 papers were read; her 1945 AJA paper and her working notes were
  not.

## 7. What would change the picture

More Linear A. The floor is measured on Greek text and transfers under A-040; roughly
doubling Linear A's word types is what the tablet-model floor implies, and new
inscriptions do appear. A representation of tablets richer than sign sequences with
dividers, which this repository does not have and which the context line suggests would
have to be considerably richer than roles and lists to matter. Or a candidate-language
test that separates a right real language from a wrong one on Linear B by more than the
sample spread, which no version of dictionary matching here has done.

---

## Appendix: reproducing the numbers

```bash
.venv/bin/python scripts/findings.py --status current          # the entries that stand (24 of 33 at 2026-09-11)
.venv/bin/python scripts/findings.py --show F-032               # one entry
.venv/bin/python -m pytest tests/ -q                            # 105 tests, including the pins
.venv/bin/python scripts/kober_run.py --corpus damos --perms 200 --seed 0 --grid --grid-alternations
.venv/bin/python scripts/controlled_comparison.py --corpus damos --perms 100 --seed 0
git tag -l 'F-*'                                                # the commit behind each finding
```

Files: FINDINGS.md (results), CHANGELOG.md (protocol versions and pre-registrations),
ASSUMPTIONS.md (A-001 to A-122), JOURNAL.md (twenty-two phases, why each followed the
last), docs/ai_context/ (instrument descriptions), docs/works/ (one page per source,
verification flag on each), results/README.md (which file feeds which finding).

---

## Addendum, 2026-09-12

Three primary texts arrived after this report was written and changed two prior-art
grades, not any result. Barber 1974, read in full, states on p. 212 that Linear A "shows
no systematic and almost no suspectable inflection, although a Linear B corpus of not much
larger size gives ample evidence for suffixation": the size-matched comparison of section
3 was stated in prose in 1974 without a null, so it is a measurement of a stated view, not
a new observation. Her theoretical figures for the text a decipherment needs (about 225
signs for a 100-sign syllabary) come with the statement that the practical minimum is
"undetermined" and needs measuring on samples of different sizes, which is what the floor
sweep does. Packard's Tables 13 and 14, legible at last, show the "2 to 1" was his weakest
class of evidence and that his case for the borrowed values rested on toponyms, outside
the structural line. The claims register carries the regrades.
