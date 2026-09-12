# Result Discipline — when a number becomes a finding

Files: `FINDINGS.md`, `CHANGELOG.md`, `scripts/controlled_comparison.py` (the model of a frozen protocol)

See also: [hypothesis-harness.md](hypothesis-harness.md) for the instrument these rules were learned on; [evaluation-harness.md](evaluation-harness.md) for the programme.

Written 2026-09-11 after three confident conclusions were withdrawn in two days (FINDINGS
F-003, F-006, F-007). Each was a result read before the control that would have caught it
existed. Each correction came from a design question, not from re-reading the numbers.

## The rule

A result is **exploration** until all of the following hold, and it enters `FINDINGS.md`
as **open** until they do:

| requirement | why |
|---|---|
| Success criterion written before the run | F-006 and F-007 were read after the fact against no stated bar |
| Protocol frozen, version ≥ 1.0, stamped into the results file | tuning on the calibration corpus is fine; tuning on the target is not, and the two must be distinguishable in the record |
| Target corpus (Linear A) run once under that version | a second run on Linear A without a version bump is tuning |
| At least three known-wrong real controls under the identical protocol | a synthetic or scrambled null shows structure exists; only a wrong real language shows whether it is *this* structure (F-008) |
| Positive control as hard as the real case | planted perfect roots passed at z = 8 (F-004) and proved nothing; the honest control encodes through the same defective spelling |
| Within-condition variance measured | six Greek lexicons had to agree within 0.15 before a Greek-vs-anything gap meant anything (F-007) |
| All compared numbers from one run: same words, seed, permutation count, map | F-007's Greek-vs-Hebrew gap was assembled from runs that were not comparable |
| p at the permutation floor rerun at ≥ 400 | 1/101 is not a p-value |
| At least two independent word samples before any between-lexicon comparison | the permutation se (~0.2) is null noise for one fixed sample; sample-to-sample spread on Linear A is 0.5 to 0.8 (F-011, seed 0 vs seed 1) and swamped a "separation" that had been called more than noise |
| Every finding's commit is tagged `F-nnn`; a change to instrument code keeps the regression pins green or bumps the version, reruns the affected findings and adds dated notes | later versions must be comparable with, and rollable back to, the code that produced each earlier finding (`git checkout F-016`); `tests/test_kober_regression.py` pins the stage 1 real values to the committed results files. Asked for by Ru 2026-09-11. The published branch is a squashed snapshot without the tags; version pins there are carried by the `protocol_version` fields in the results files and by CHANGELOG |
| A subset or restricted-pool comparison holds the null fixed and compares per-word gaps, never z | protocol 1.0's bands are computed from the sample, so a restricted pool changes the null too; the wrong languages scored near zero on each half of the pool and +2 on the union (F-014, A-042). Two seeds on a pool smaller than the sample size are one sample |

Only then does the entry become **current**. Superseded and withdrawn entries stay in
`FINDINGS.md` with the reason. They are the record of what a plausible wrong conclusion
looks like on this material, which is worth more than the right one.

## The four questions, asked before reading any result

1. What known facts is the instrument not using? (The Mycenaean spelling rules were
   known and unused in 0.4. The result was a straw man.)
2. What is the variance between two answers that are both right? (Without it, a gap
   between right and wrong is uninterpretable.)
3. What does the nearest wrong answer score? (Greek on Linear A, then Basque on Linear A,
   each in turn changed what the Hebrew number meant.)
4. What is the error bar that actually applies to the comparison being made? A
   permutation p-value is about one sample; a claim that one lexicon beats another needs
   the spread across samples.

These were the questions the review asked. They are cheaper before the result than after.

## Symmetry of surprise

The bar rises with the surprise **in both directions**. A result against the hypothesis
under test got immediate suspicion (Greek high on Linear A); a result for it got a moment
of interest first (Hebrew rising). Whatever would be checked if the result went the other
way is checked anyway.

## Why the answer key is the design

Every correction was possible because Linear B, a deciphered script in the same family,
was in the same repository. No instrument is pointed at Linear A that has not first been
shown to recognise Greek in Linear B, and shown to *fail* to recognise Finnish there. This
is the reason the two scripts share a repository (README) and it is not negotiable.

## Read the primary before building on it

Learned 2026-09-11 (kober1946, kober1948; JOURNAL phase 18). The Kober instrument was
designed, calibrated and taken through two context versions from secondary accounts of
her method. Her paper states the method as seven numbered assumptions, one of which,
list-level case homogeneity, neither context version encoded, and the canonical example
every summary quotes, a-mi-ni-so / a-mi-ni-si-jo, scored no rule on the instrument's
answer key. Hours went where a morning with the paper would have pointed. Three rules:

| rule | why |
|---|---|
| A replication reads the primary source before it builds. A catalogue page at verification P is a pointer to the paper, not a basis for encoding the method | secondary literature retells results and compresses procedures into the reteller's frame; the procedure is the thing a replication needs and the thing summaries drop |
| An answer key is checked against the canonical example before it scores anything | the reference list could not score the triplet Kober is famous for; the failure was visible in F-016's own output at rank 46 and nobody looked |
| When a method has stated assumptions, each is a row in ASSUMPTIONS.md from the day the instrument is designed, marked encoded, not encoded, or tested | "which of hers have we not encoded" becomes a query instead of a discovery |
| An answer key is a versioned artefact derived from a named primary source, and every revision rescores every existing result file with old and new counts side by side | three versions of the Kober reference list exist (0.1, 0.6, 0.8); a count that changes with the key is a fact about the key, and the record must show which key produced which count |
| The null varies the thing under test and nothing else; a null that holds the tested quantity fixed rates itself generously | spike S-003 fixed label identity between the scripts, which is the value transfer it was testing, and let only a third sign vary; the real count sat at the 87th percentile of a null that had been handed most of it. Companion to the F-014 rule: there the null moved with the sample, here it did not move with the hypothesis |
| A sign statistic on Linear A is checked for inventory dependence before it is read: Linear A attests about twice the signs of a same-sized slice of Linear B, and any measure that rises with the attested inventory (unigram entropy, smoothed conditional entropy, hapax share, inventory growth, positional entropy) will place Linear A with large-signary scripts for that reason alone | F-042 and F-044, the same night: the Indus-debate pair of numbers read Linear A as non-linguistic, and a pooled script-type distance read it as Egyptian-like; both effects vanished on the order-sensitive statistics |
| A spike is not a finding; a finding is not a spike | `spikes/` carries ideas under its own rules; a spike worth keeping is rebuilt under this table as a version, and the spike stays as the record of the idea |

## On speed

Fast iteration found every one of these problems within hours. It also produced three
write-ups that had to be withdrawn. The fix is not slower work. Confidence in the write-up
lags the result by at least one control, and FINDINGS entries default to **open**.
