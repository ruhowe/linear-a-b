# Hypothesis Harness — every claim through the same test

## Read this first

This file describes the etymological method's instrument (see `terminology.md`; older
text says "lexicon matching"): what it is, what it holds fixed,
how to run it, and what a reader must know before trusting a number from it. **It states
no results.** Results and verdicts live in [FINDINGS.md](../../FINDINGS.md), dated and
tied to protocol versions; the versions themselves are in
[CHANGELOG.md](../../CHANGELOG.md). Current entries: F-008, F-012 to F-015; the
head-to-head with the Kober method is F-020. **The line is closed on this corpus**
(F-020, 2026-09-11): the instrument returns a result for every real language at the
strength of the right one on Linear B, where the right one is known, and the cause is
dictionary shape, not power. Everything from "The headline result" onward is the record
of versions 0.1 to 0.5 being built and broken and is kept as history; none of it is a
current conclusion.

**What the primaries say about it (read 2026-09-11 and 2026-09-12).** Packard 1974 built
nine fictitious value sets by rotating values within frequency bands (pp. 73 to 74),
which is protocol 1.0's null; predicted about five chance name matches and one twelfth of
alternations sharing a consonant by chance (p. 73); and observed that "if vowels are
ignored, the random decipherments produce hundreds of matches ... the Linear B values
produce more but not by an impressive margin" (p. 90), which is the consonant-skeleton
channel F-006 and F-012 measured. Barber 1974, p. 209: vocabulary "is a very risky
indication of genetic relation, especially in a small sample and even more in a sample
of unknown contents." Kober 1948, p. 100, on sign-shape matching to Cypriot: "when we say
30/120 of Cypriote is equal to 30/300 of Minoan, we are saying very little." The
instrument measures what all three stated.

**Expansion checked against Ventris and Chadwick 1973 §§8 to 10 (A-005).** The coda rule
matches §8. §9, initial s- before a consonant omitted (pe-ma = sperma), was never
expanded; a stated limit, and a small one for a closed line.

### The frozen instrument (protocol 1.0)

`scripts/controlled_comparison.py`, stamped `PROTOCOL_VERSION`. Any change that could
move a result is a new version and a CHANGELOG entry, and Linear A is then rerun rather
than reinterpreted.

| component | setting | why |
|---|---|---|
| expansion | Mycenaean rules: at most one omitted l/r/m/n/s before a consonant; optional omitted final s/n/r | blind insertion (0.4) had no power; the real rules recover 90% of known readings |
| statistic | mean over words of log(1 + mean lexicon count over candidates) | chosen best-of-four on Linear B, then frozen; set membership (0.1 to 0.4) had no power |
| null | `frequency_matched_permute`, four bands | breadth-only (0.2) let frequent signs trade with rare; above ~8 bands the null cannot move |
| sample | seeded random 400 word types covered by every map in the run | `sorted()[:n]` (0.5) over-sampled vowel-initial words and inflated Hebrew |
| control | synthetic twin per lexicon: same length profile and consonant unigrams, random content, same map | a z-score is comparable only within a map |
| calibration | stated before running: on Linear B real Greek beats synthetic Greek and Hebrew does not beat synthetic Hebrew | Linear B is the corpus whose answer is known |

Companion scripts under the same version: `scripts/unrelated_controls.py` (Finnish,
Turkish, Basque, Hungarian through the Semitic map) and `scripts/extra_lexicons.py`
(any `loader:map` pair, real and synthetic).

### What a reader must know

- The synthetic twin is a **noise** control. Every real lexicon beats it, on both corpora,
  because every real language has phonotactics and a random-string lexicon does not. The
  wrong-language controls are the unrelated real languages. See F-008.
- A z-score is comparable only with another z-score under the same map. Never compare
  Greek-map z to Semitic-map z directly.
- Greek on Linear A is contaminated: the conventional transcription uses Linear B values,
  which are Greek. No lexicon choice removes this (archaic, Koine and LSJ agree).
- Linear B's values are Ventris's decipherment, so the positive control shows the
  instrument recognises the right language *given* the right values, not that it could
  find them.
- With 100 permutations the smallest reportable p is 0.0099. Anything at the floor is
  rerun at 400 before it is quoted.
- Do not tune on Linear A. If a better statistic is wanted, choose it on Linear B, bump
  the version, and rerun.

Files: `src/hypotheses/` (registry.yaml, scenarios.yaml, harness.py, lexicons.py, phonologies.py, run.py), `results/hypotheses.json`

See also: [semitic-null-test.md](semitic-null-test.md) for the single-hypothesis version this replaces; [evaluation-harness.md](evaluation-harness.md) for why results rather than tools.

Run: `.venv/bin/python -c "import sys;sys.path.insert(0,'src');from hypotheses.run import main;main()"` (~60 s)

## History begins here (protocol 0.3, 2026-09-11 morning)

## The headline result

A hypothesis we are confident is **false** scores better than the hypothesis under test.

| Hypothesis | real | breadth null | freq null | excess | z | p |
|---|---:|---:|---:|---:|---:|---:|
| Greek (known-false control) | 83.2% | 69.6% | 77.5% | **+5.7%** | +2.67 | **0.005** |
| Semitic (under test) | 72.2% | 69.8% | 69.9% | +2.3% | +1.59 | 0.054 |

679 Linear A word types, 999 permutations, seed 0.

**What this licenses saying.** Greek reaches p = 0.005 on this instrument, and Linear A is
not Greek by strong consensus (Davis 2026, Duhoux), with Linear B available to show what
Greek in this script actually looks like. So a p-value below 0.01 here does not indicate
language affiliation. It indicates how much artifact the test still carries. Semitic, at
p = 0.054, does not reach the level a known-wrong answer reaches.

That is a stronger and fairer statement than the single-hypothesis version, which could
only report "not significant". It also could not have been produced without running a
control hypothesis, which is the argument for the registry.

## Why Greek scores at all, measured

Two causes, both artifacts, neither evidence about Minoan.

| | Greek | Semitic |
|---|---:|---:|
| Skeletons of length 2 | 42% | 15% |
| Lexicon density at length 2 | **86.1%** | 42.6% |
| Lexicon density at length 3 | 38.3% | 19.8% |
| Correlation, sign-implied phoneme frequency against lexicon phoneme frequency | **+0.69** | +0.15 |
| Mean candidate skeletons per word | 2.3 | 20.8 |

Greek writes vowels, so a Linear A vowel sign contributes no consonant and readings
collapse to short skeletons. 86% of all two-consonant skeletons are attested Greek words,
so short skeletons almost always hit.

The second cause is worse and is specific to this corpus. **Linear A's conventional sign
values are Linear B values, and Linear B values are Greek.** The phoneme frequencies the
signs imply therefore align with Greek phoneme frequencies by construction, at +0.69
against +0.15 for Hebrew. Greek is a contaminated control rather than a clean one, and it
cannot be decontaminated without abandoning the conventional transcription entirely.

That contamination is a fact about Linear A scholarship, not a flaw in the experiment. It
means Greek sets an upper bound on artifact magnitude, which is the use we put it to.

## Three generations of null

Each caught something the previous one missed. The progression is the transferable part.

| Null | What it holds fixed | What it misses | Greek | Semitic |
|---|---|---|---:|---:|
| Naive permutation | nothing but the sign set | candidate breadth, frequency | not run | p = 0.016 |
| Breadth-matched | number of options per sign | which signs are common | p = 0.001 | p = 0.153 |
| **Frequency-matched** | options per sign, and corpus-frequency band | remaining skeleton-length effects | p = 0.005 | p = 0.054 |

The naive null returns a false positive on Semitic. The breadth-matched null returns a
worse false positive on Greek. Only the frequency-matched null brings the known-false
control down toward its real rate, and it still does not bring it to chance.

`frequency_matched_permute` is Packard 1974 read strictly. He reassigned values **within
frequency bands**, and that detail is easy to skip when reading the method second-hand.
It is the difference between a null that works and one that flatters every hypothesis.

## The null cannot be tightened further, and that is the finding

Two questions were put to the null on 2026-09-11. The first closed cleanly. The second
established a limit on the whole instrument.

**Skeleton length is already preserved, so a length-stratified null is unnecessary.**
Measured over 30 permutations: Greek's length profile drifts by 0.000 and Semitic's by
0.006. Breadth stratification already holds length fixed, because signs contributing the
same number of consonants carry the same number of options. The length hypothesis for
Greek's residual is wrong.

**Frequency banding has a narrow valid window, and Greek clears the bar throughout it.**
Sweeping the number of bands, 399 permutations each:

| bands | signs per band | % of signs a permutation moves | Greek excess | Greek p | Semitic excess | Semitic p |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 50.0 | 63% | +13.4% | 0.003 | +2.5% | 0.122 |
| 2 | 25.0 | 60% | +7.0% | 0.003 | +2.7% | 0.033 |
| 4 | 12.5 | 57% | +5.6% | 0.005 | +2.3% | 0.062 |
| 8 | 6.2 | 46% | +5.9% | 0.003 | +1.1% | 0.195 |
| 16 | 3.1 | 28% | +3.0% | 0.005 | +0.7% | 0.265 |
| 32 | 1.6 | **10%** | +0.3% | 0.302 | +0.2% | 0.393 |
| 50 | 1.0 | **0%** | 0.0% | 1.000 | −0.0% | 1.000 |

The last two rows are degenerate rather than reassuring. Only 50 Linear A signs carry a
conventional value, so 32 bands leaves 1.6 signs per band and a permutation moves 10% of
them. At 50 bands it moves nothing at all. **A null that cannot move cannot be beaten**,
and p = 1.000 there is arithmetic, not evidence. Any band count above about 8 is measuring
its own degeneracy.

Inside the valid window, bands 2 to 8, the pattern is stable and unwelcome. Greek sits
between +5.6% and +7.0% at p ≤ 0.005 every time. Semitic wanders between +1.1% and +2.7%
and crosses 0.05 depending on the setting, which is its own warning: a result that depends
on a tuning parameter is not a result.

**So Greek's excess is not an artifact of frequency alignment after all.** Frequency
banding removes about half of it and nothing removes the rest. A known-false hypothesis
retains a significant excess under every non-degenerate null we can construct.

### What that licenses, and what it forbids

The instrument can **refute** and cannot **confirm**.

A hypothesis scoring at or below the Greek benchmark has failed to show anything, and that
conclusion is safe because a false hypothesis reaches the same level. Semitic is in that
position.

A hypothesis scoring above Greek would be interesting and would still not be evidence of
affiliation, because we cannot say what the ceiling on artifact is. We only know it is at
least as high as Greek reaches.

This is the honest statement of the limit, and it should appear in anything written from
this work. It also puts a floor under how much a better lexicon or a cleverer null could
buy: the residual survives frequency matching, length is already controlled, and the
corpus is 679 word types. Shannon's unicity argument is the likely reason, and if so no
refinement of this method will fix it.

## The method fails on Linear B, and that invalidates the method class

Measured 2026-09-11, and this supersedes the readings above. Running the harness on Linear
B, where the answer is known, shows it cannot find it.

| Corpus | Hypothesis | Truth | n | real | null | excess | p |
|---|---|---|---:|---:|---:|---:|---:|
| Linear B | Greek (archaic) | **true** | 3,138 | 66.2% | 64.2% | +1.9% | 0.155 |
| Linear B | Semitic (Hebrew) | **false** | 3,138 | 60.8% | 58.7% | +2.1% | 0.054 |
| Linear A | Greek (archaic) | false | 679 | 89.7% | 85.1% | +4.6% | 0.006 |
| Linear A | Semitic (Hebrew) | unknown | 679 | 72.2% | 69.9% | +2.3% | 0.054 |

Three things follow, and the third is the important one.

**The instrument cannot detect Greek in a Greek corpus.** On Linear B it returns p = 0.155
for the correct answer, and ranks the wrong answer marginally higher.

**Greek scores higher on Linear A, where it is false, than on Linear B, where it is true.**
+4.6% against +1.9%. Whatever the score measures, it is not language affiliation.

**The cause is defective spelling, and it is structural.** Only **3 of 23** undisputed
Linear B readings can be reached by consonant-skeleton matching at all:

| Linear B | Greek | true skeleton | reachable |
|---|---|---|---|
| ko-no-so | Κνωσός | knss | kns only, geminate and final s unwritten |
| ka-ko | χαλκός | klks | kk only, the lambda in the cluster unwritten |
| wa-na-ka | ϝάναξ | nks | wnk, the xi written as plain k |
| i-qo | ἵππος | pps | k, geminate and final s gone |
| qa-si-re-u | βασιλεύς | bsls | bsl, final s unwritten |

Linear B does not write consonants in coda position, before another consonant or word
finally. The consonant skeleton of a Linear B word is therefore systematically shorter
than, and different from, the skeleton of the Greek word it records. No amount of
statistical care bridges that, because the information is not in the text.

### The trap, quantified

The obvious fix is to allow unwritten consonants. Doing so does not help:

| unwritten allowed | true readings recovered | candidates per word | excess over null |
|---:|---:|---:|---:|
| 0 | 13% | 3 | +5.3% |
| 1 | 70% | 88 | +4.4% |
| 2 | 78% | 819 | +4.4% |

Strict matching is blind to the truth. Loose matching can see it, at 70% recall, but
candidates per word rise twenty-nine-fold and **the discrimination does not improve**. The
added freedom lifts the null exactly as much as it lifts the signal. There is no setting
at which the method both sees the right answer and distinguishes it from a wrong one.

### Compensating for the spelling rules does not rescue it

The obvious objection is that Mycenaean orthography is known, so the omissions can be
reversed rather than guessed. That is right, and it was tested on 2026-09-11 by expanding
each Linear B word under the actual rules: an omitted liquid, nasal or /s/ before a
consonant, an omitted final /s/, /n/ or /r/, and stop-plus-liquid clusters written with an
echo vowel.

It works, for recall.

| Max omitted codas | True readings recovered | Candidates per word | real | null | excess |
|---:|---:|---:|---:|---:|---:|
| 0 | 70% | 9 | 77.8% | 77.9% | −0.0% |
| 1 | **90%** | 100 | 78.6% | 79.2% | −0.6% |
| 2 | 90% | 289 | 78.6% | 79.2% | −0.7% |

Recall rises from 70% to 90%, so the rules do what they should. **The discrimination is
zero or negative at every setting.** Correct Greek sign values match archaic Greek no
better than scrambled values do, on genuine Greek text.

Restricting to long skeletons, where the lexicon is sparse, does not help either:

| minimum skeleton length | lexicon density | real | null | excess | z |
|---:|---:|---:|---:|---:|---:|
| 2 | 95.8% | 72.9% | 72.9% | −0.0% | −0.01 |
| 3 | 51.0% | 72.9% | 72.9% | −0.0% | −0.01 |
| 4 | 13.5% | 70.3% | 70.8% | −0.5% | −0.25 |
| 5 | **1.7%** | 61.5% | 59.3% | +2.2% | +0.83 |

Even where only one skeleton in sixty is an attested Greek word, the correct assignment
carries no significant advantage.

So the failure is not defective spelling alone, and not lexicon density alone. **Matching
consonant skeletons against a large lexicon has almost no statistical power, full stop.** A
lexicon of 53,000 word types covers so much of the plausible consonant-string space that a
wrong assignment lands on real words nearly as often as a right one. Nothing recoverable
from the orthography changes that.

### What this means for everything above, and for the field

**Our Semitic result is a statement about the method, not about Minoan.** We cannot say
Linear A does not look Semitic. We can say this method cannot tell, and we can now prove
it cannot, because it fails to identify Greek in Greek. That is a narrower claim and the
only one the evidence supports.

**It generalises to the whole matching literature.** Consonantal-skeleton matching against
a candidate lexicon is the shared method of di Mino 2026, the Perono Cacciafoco programme,
Gordon 1966 and the Revesz line. All of them run it on a script from the same family as
Linear B, with the same defective spelling. The Linear B control says the method cannot
work, whoever runs it and whichever language they propose.

Linear A is very likely worse than Linear B here, not better. It is the parent script, its
orthographic rules are unknown rather than merely defective, and nobody can correct for
rules they have not established.

This is the strongest result this repository has produced, and it exists only because a
deciphered script sat in the same repository as an undeciphered one.

## What is registered and what is blocked

`registry.yaml` holds seven entries. Three run; one runs but cannot inform.

| Key | Status | Note |
|---|---|---|
| `semitic_hebrew` | runnable | Strong's Hebrew, 2,111 triliteral skeletons |
| `greek_mycenaean` | runnable, control | Nestle 1904 NT via pyaegean, 25,187 word types |
| `anatolian_luwian` | proxy, uninformative | Hittite via Wiktionary, 67 headwords: z near zero on Linear B, so it cannot be read on Linear A (F-013). Purer sources located: TLHdig, eDiAna |
| `sumerian_control` | control | ePSD2-literary, 2,428 headwords. The typology-matched wrong real language for the Greek-style map |
| `tyrsenian_etruscan` | blocked | Corpus small, glosses contested |
| `uralic` | blocked | Revesz builds his own dictionary, which is the objection. Needs an independent Uralic root list |
| `isolate_null` | control, no lexicon | The mainstream position. Every null result is a point in its favour, and that asymmetry is stated rather than hidden |

Blocked hypotheses are listed in the output rather than silently omitted. A survey that
reports only what it could run misrepresents itself.

## Weighting and scenarios

`scenarios.yaml` holds five named prior weightings: `mainstream`, `uniform`,
`semitic_advocate`, `indo_european_advocate`, `sceptical`. `posterior_ordering` combines a
prior with `1 - p` as a blunt monotone stand-in for a likelihood ratio.

**This is a sensitivity device and must never be reported as a calibrated posterior.** Its
only purpose is to show whether the evidence moves the ordering. Currently it does not
move it anywhere: under every scenario the ordering reproduces the prior, because neither
runnable hypothesis produces evidence strong enough to shift anything. Saying that plainly
is the honest output.

## Design decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| Each hypothesis scored against its own null | 2026-09-11 | Lexicon density varies by an order of magnitude, so raw match rates measure dictionary shape rather than fit | A shared null, which would rank by lexicon size |
| Frequency-matched permutation is the headline | 2026-09-11 | The breadth-matched null gives the known-false control p = 0.001 | Keeping breadth-matching, which flatters every hypothesis |
| Greek included despite being contaminated | 2026-09-11 | It bounds the artifact, which is exactly what a control is for. A clean Greek control is impossible while the transcription uses Linear B values | Omitting it and reporting Semitic alone |
| Fringe hypotheses registered | 2026-09-11 | A harness pointed only at claims we respect is rhetoric. A fringe claim clearing the bar would be the most interesting result available | Registering only serious proposals |
| Blocked hypotheses reported in output | 2026-09-11 | Silence about an untestable hypothesis misrepresents the survey's coverage | Listing only what ran |

## Limits

- **Two of six hypotheses run.** Any statement about the relative standing of Anatolian,
  Etruscan or Uralic is unsupported until their lexicons exist.
- **Koine Greek is a thousand years later than Linear A** and has lost the digamma, so
  Linear A words containing the w-series can never match. This makes the control
  conservative, which is the right direction, but it is not Mycenaean Greek.
- **The residual is unexplained, and probably irreducible.** Length is already controlled
  and frequency matching removes only half of Greek's excess. What remains survives every
  non-degenerate null we can build, so the instrument has a floor. See the section on why
  the null cannot be tightened further.
- **The test measures root and word-shape matching only.** It says nothing about
  morphology or syntax, which is where the stronger arguments in the claims under test
  actually live.
- **Nothing here identifies a language.** A hypothesis clearing every bar would earn a
  closer look from specialists, not a decipherment.
