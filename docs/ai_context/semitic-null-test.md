# Semitic Null Test — does Linear A root-matching beat a fictitious decipherment?

Files: `src/semitic_null/` (lexicon, phonology, experiment, run), `results/semitic_null.json`

See also: [state-of-the-art.md](state-of-the-art.md) for the claim tested and its standing; [evaluation-harness.md](evaluation-harness.md) for why this is the shape of contribution this repo makes.

Run: `.venv/bin/python -c "import sys;sys.path.insert(0,'src');from semitic_null.run import main;main()"` (~30 s)

## The question, stated precisely

**Not** "is Minoan Semitic?" — no statistic answers that. The prior question the field requires before a reading counts as evidence:

> Given the phonological freedom the method allows, how often would an *arbitrary* sign-value assignment produce comparably good Semitic matches?

Target: Di Mino (2026), *Ya Diktu* (Zenodo `10.5281/zenodo.22129502`, CC BY 4.0, not peer reviewed) — 42 sign readings, a 508-entry lexicon, Semitic comparanda for the ~66 Linear A sign-groups in Davis 2026's appendix. Chosen because it is the most falsifiable claim in circulation and **nobody had tested it**, including its author, who released no code.

Instrument: Packard (1974), who ran random-reassignment nulls on Linear A fifty years ago and whose method the field dropped. Same logic as Sproat (2014) on entropy and Raghavendra (2026) on the Indus script.

## Result

| Test | real | null | z | p |
|---|---|---|---|---|
| Naive permutation | 72.2% | 65.1% (sd 3.3) | +2.14 | **0.016** |
| **Breadth-matched permutation** | 72.2% | 69.8% (sd 2.4) | **+1.00** | **0.153** |
| Positive control (planted Hebrew roots) | 100.0% | 78.4% (sd 2.6) | **+8.38** | 0.001 |

648 distinct Linear A word types · 999 permutations · seed 0 · mean 20.8 candidate skeletons per word.

**Headline: under a correctly matched null, a Semitic reading of Linear A is not distinguishable from a fictitious decipherment.** Root-matching, on its own, carries no evidential weight.

Three things make that statement safe to make:

1. **The base rate is enormous.** 2,111 of 10,648 possible triliteral skeletons are attested Hebrew roots — **19.8% of the space**, rising to **42.6%** at length 2. A random three-consonant skeleton is a real Hebrew root about one time in five, before any phonological allowance.
2. **The freedom multiplies it.** Aegean syllabograms neutralise Semitic contrasts: the r-series writes both /r/ and /l/ (a fact about the script), vowel signs may carry any laryngeal, and the reading itself invokes sibilant merger and emphatic neutralisation. So a word does not propose one skeleton but the cross-product of its per-sign options — **20.8 candidate roots on average**, any one of which counts as a hit.
3. **The instrument works.** Genuine Hebrew roots re-encoded through the same syllabary are recovered at 100% against a 78.4% null, z = +8.38. A null result on real Linear A is therefore a fact about Linear A, not a broken test.

## Superseded: the method itself fails a known-answer control

**Read [hypothesis-harness.md](hypothesis-harness.md) first.** Running this same procedure
on Linear B, where the language is Greek and is not in doubt, shows it cannot identify the
correct answer: p = 0.155 for Greek, with Semitic ranking marginally higher on the same
corpus. Only 3 of 23 undisputed Linear B readings are even reachable by consonant-skeleton
matching, because Mycenaean does not write coda consonants.

So the negative result below is **a fact about the method, not about Minoan**. The correct
statement is that consonantal matching cannot decide the question, demonstrated on a script
we can read. It is not that Linear A fails to look Semitic.

Everything below stands as the record of how that conclusion was reached, and the null
design in it is still the right design. What changed is what a null result licenses.

## Superseded in part: a control changed the reading

**Read [hypothesis-harness.md](hypothesis-harness.md) alongside this file.** Running the
same test against a known-false control (Greek) after this write-up changed what the
numbers mean.

Two corrections. The breadth-matched null used here is not the strongest available: it
holds each sign's number of options fixed but lets a frequent sign trade phonemes with a
rare one, and Linear A's conventional values are Greek values, so frequency alignment is
worth real points. Under a frequency-matched null the Semitic figure moves from p = 0.153
to p = 0.054.

More importantly, Greek reaches **p = 0.005** on that same stronger null, and Linear A is
not Greek. So p-values on this instrument are not calibrated as evidence of affiliation,
and Semitic at 0.054 does not reach the level a known-wrong answer reaches. That is a
firmer conclusion than "not significant", and it was unavailable until a second hypothesis
was run.

The negative result stands. The reasoning behind it is stronger.

## The naive test returns a false positive — and that is a finding

The obvious null (shuffle all sign values freely) gives **p = 0.016**, which reads as significant.

It is confounded. A free shuffle lets a sign trade a 4-option consonant set for a 1-option one, changing how many roots the corpus can reach at all. Measured: the real map reaches **20.8** candidate roots per word against the naive null's **17.4**, and across permutations **candidate breadth correlates with hit rate at +0.65**. The real assignment was being rewarded for combinatorial reach, not Semitic fit.

Holding each sign's *number* of options fixed and permuting only *which* consonants it writes (`run.stratified_permute`) equalises breadth at 20.8 vs 20.7 — and the effect collapses to p = 0.153.

**Anyone running this test naively will conclude they have evidence.** That is the trap, and it is the most transferable part of this work.

## The length curve

Hit rate against a breadth-matched null, by word length in signs:

| signs | n | real | null | delta |
|---|---:|---:|---:|---:|
| 2 | 257 | 89.9% | 88.6% | +1.3 |
| 3 | 245 | 75.1% | 70.5% | +4.6 |
| 4 | 123 | 40.7% | 35.8% | +4.8 |
| 5 | 20 | 15.0% | 27.1% | −12.1 |
| 6 | 3 | 0.0% | 17.3% | −17.3 |

The matching succeeds where the root space is dense and freedom is greatest, and **fails on exactly the words that would be most probative**. If Linear A were Semitic, long words should match *better* — they are more constrained, so a correct reading is less likely to be luck. Instead they match worse than chance. The n at lengths 5–6 is small (23 words) and this is a diagnostic, not a proof.

## What this does and does not establish

**Does:** the specific evidential move "these Linear A words correspond to Semitic roots" is uninformative at this corpus scale, because fictitious decipherments do it about as well. Any future Semitic reading must clear a breadth-matched null before its matches count.

**Does not:**
- Disprove that Minoan is Semitic. A true hypothesis can be supported by bad evidence.
- Assess the philology. Whether a tG-stem parse is sound, or an energic nun plausible in position 7, needs a Semitist. This measures the size of the haystack, nothing else.
- Test his morphological or syntactic arguments, which are separate from root-matching and are where the paper's real substance lies.
- Cover his readings of undeciphered signs. `*301` = /na/ is excluded here, along with all `*NNN` signs, because they carry no conventional value. That exclusion is **conservative**: admitting them adds freedom, so including them would lower the real map's advantage further, not raise it.
- **Price segmentation freedom — the test holds word division fixed, and his method does not.** The word set is GORILA's word-groups as divided by `𐄁`. Real and permuted maps score on that same list, so segmentation does not differentially favour the real map *inside* this test. But it is a second free parameter the test never prices, and measured 2026-09-11 he spends it: on **KN Zc 7**, his one fully-translated inscription, GORILA writes **5** word-groups and he reads **7**, splitting `A-KA-NU-ZA-TI` → `A-KA-NU` + `ZA-TI` and `JA-SA-RA-A-NA-NE` → `JA-SA-RA` + `A-NA-NE` where the edition marks no divider — 2 of his 7 lexemes there exist only under that re-division. Same at **PE Zb 3**, where he cites `KI-TA-NA-SI-JA-SE` out of the edition's unbroken `A-KA-RA-KI-TA-NA-SI-JA-SE-VIR+[?]-ZA`. **Direction is conservative, like the `*NNN` exclusion**: re-division yields shorter words, and the length curve puts short words where the root space is densest (2-sign, 89.9% real vs 88.6% null, delta +1.3). Admitting it would raise real and null together and push the comparison into the band where discrimination is worst. See [state-of-the-art.md](state-of-the-art.md) INVESTIGATE.

## Method

| Step | Choice | Why |
|---|---|---|
| Lexicon | Strong's Hebrew (1894), 8,674 entries → 2,111 triliteral skeletons | Public domain; and it is what the tested claim leans on most, citing BHS throughout |
| Word set | 648 distinct multi-sign `CERTAIN` Linear A word types, **divided as GORILA divides them** (`𐄁`) | Types not tokens, so recurring words do not dominate. Segmentation is held fixed for real and null alike — see the scope limit above, and note the tested claim does not always accept this division |
| Sign map | 50 of 342 signs carrying a conventional Linear B value | The rest have no value to permute |
| Per-sign options | Consonant series → Hebrew set (`phonology.SERIES_TO_HEBREW`) | Encodes the mergers the reading itself invokes |
| Hit | any skeleton in the cross-product is an attested root | The method's own success criterion |
| Null | permute within consonant-set-size classes | Preserves breadth; isolates the assignment |
| p | one-sided, add-one smoothed over 999 permutations | No distributional assumption |

## Decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| Breadth-matched null is the headline | 2026-09-10 | The free permutation is confounded by candidate reach (+0.65 correlation) and returns a false positive | Reporting the naive p = 0.016 |
| Report the naive result anyway | 2026-09-10 | The trap is the most useful transferable finding; hiding it would let the next person fall in | Reporting only the correct test |
| Positive control is mandatory | 2026-09-10 | Without it a null is indistinguishable from a broken instrument — the lesson from pyaegean's Procrustes self-alignment check | Reporting the negative alone |
| Undeciphered `*NNN` signs excluded | 2026-09-10 | They carry no conventional value to permute; excluding them is conservative | Assigning them the paper's proposed values |
| Hebrew alone, not a pan-Semitic lexicon | 2026-09-10 | Openly licensed, and the claim's own primary comparison language | Assembling Ugaritic + Akkadian, which widens the target and weakens the claim further |

## Open

- ~~**Widen the lexicon.**~~ Done 2026-09-11 under protocol 1.0: Ugaritic and Akkadian. See FINDINGS F-011. The original expectation below was wrong in direction for Ugaritic.
- **Widen the lexicon (original note).** Adding Ugaritic (the Copenhagen corpus, Zenodo `10.5281/zenodo.20022023`, open) and Akkadian would *raise* the null, since more roots means more chance matches. The current single-language test is the version most favourable to the claim.
- **Test the morphology instead.** The paper's stronger material is the claim of consistent Semitic morphology across attestations — prefix conjugation, N-stem, mimation. That is a distributional claim and might be testable; root-matching is not the strongest form of the argument.
- **Send this to the author before publishing**, per the contact rule in [evaluation-harness.md](evaluation-harness.md). He released no code, so he cannot check this himself, and the naive-versus-matched distinction is exactly the kind of thing a author should get to respond to first.
- Whether the same test applied to Revesz's Uralic readings, or to Gordon 1966, gives the same answer. If every hypothesis clears the naive test and fails the matched one, that is a stronger and fairer statement than singling out one claim.
- **A segmentation-free variant.** Re-run scoring over every division of each inscription's sign string rather than GORILA's word-groups, for real and null alike. Predicted from the length curve: both rise, the gap narrows. If it narrows to nothing, the headline gets stronger — the method's freedom is larger than the phonology alone suggests. Requires the raw sign strings, not `Token.text`; `Document.transcription` is unreliable for tablets (HT 31's is truncated), so build them from `Token.signs` via `linear_a_inventory()`, as `scripts/audit_di_mino.py` does.
- Note when citing the target: **his inscription references are accurate.** Audited 2026-09-10/11 against the load — `*314` at 6 tokens across exactly the four sites he names, AB79's four Linear B forms exactly, `ZU-DU` / `MA-*79` / `ZU-RI-NI-MA` / `I-ZU-RI-NI-TA` all at the documents he cites. The negative result here is about evidential weight, not about sloppiness, and should be worded so it cannot be read as the latter.
