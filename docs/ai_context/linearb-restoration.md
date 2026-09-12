# Linear B Restoration — extraction contract, protocol, measured baselines

Files: `src/linearb_restore/` (normalise, extract, mask, split, vocab, rankers, evaluate, report), `tests/test_extract.py`, `tests/test_mask_split.py`, `results/linearb_restoration.{md,json}`

See also: [state-of-the-art.md](state-of-the-art.md) for the published work this reproduces; [corpus-sources.md](corpus-sources.md) for DĀMOS licensing and the grouped-split invariant.

Measured 2026-09-10 against DĀMOS via pyaegean 0.59.0. Re-run: `.venv/bin/python -c "import sys;sys.path.insert(0,'src');from linearb_restore.report import run;run()"`

## What this is, and what it found

- Reproduces the only published Linear B restoration work (Papavassileiou/Kosmopoulos/Owens, JOCCH 2023 and ML4AL 2024) from DĀMOS directly rather than from their released Zenodo file.
- **The deliverable is a calibration, not a win.** A Witten-Bell sign bigram already in pyaegean lands in the same range as their BiRNN, and a 15-line lexicon lookup beats it on top-1. The neural model is not what is doing the work.
- **Three findings, each with bootstrap CIs and paired significance** (`results/linearb_restoration.json`).

## Headline results

2,684 items · 75 candidates · document-grouped 5-fold, seed 0 · exhaustive leave-one-sign-out. CIs are 999-resample bootstrap percentiles.

| Ranker | all items | word type seen in train | word type unseen | single-sign words |
|---|---|---|---|---|
| prior (floor) | 7.7 / 26.5 / **63.2** | 9.1 / 31.0 / 67.4 | 4.6 / 16.8 / 54.1 | 0.0 / 0.0 / 59.1 |
| bigram | 41.2 / 64.9 / 85.8 | 55.4 / 80.9 / 94.1 | **10.4** / 30.3 / 67.7 | 0.0 / 0.0 / 59.1 |
| lexicon | **62.6** / 73.4 / 85.5 | **89.3** / 99.5 / 100.0 | **4.3** / 16.7 / 53.8 | 44.6 / 95.2 / 98.9 |
| backoff | 64.3 / 77.5 / 89.8 | 89.3 / 99.5 / 100.0 | 9.8 / 29.6 / 67.6 | 44.6 / 95.2 / 98.9 |

Cells are top-1 / top-5 / top-20 as percentages. Full CIs in `results/linearb_restoration.md`.

| Comparison | top-1 difference | McNemar |
|---|---|---|
| bigram − prior | +33.6 pts (CI +31.6 to +35.5) | p = 1.4e-175 |
| lexicon − bigram | +21.3 pts (CI +19.5 to +23.2) | p = 6.1e-100 |
| backoff − lexicon | +1.8 pts (CI +1.1 to +2.4) | p = 6.1e-07 |

## Knossos A&B — the fully verified comparison (step 7, measured 2026-09-10)

The D-series comparison above is against JOCCH 2023 figures we could only partially verify (paywalled). **This one is against ML4AL 2024, whose PDF we read: top-1 30.3%, top-20 66.2%, 75 syllables.** Same pipeline, pointed at the 308 Knossos A&B documents (an exact match to the LREC 2020 count).

197 eligible sequences · 1,073 items · 68 candidates · document-grouped 5-fold, seed 0.

| Ranker | top-1 | top-5 | top-20 | seen top-1 | unseen top-1 |
|---|---|---|---|---|---|
| prior (floor) | 8.7 | 22.4 | **58.4** | 18.5 | 3.2 |
| bigram | 27.7 | 48.7 | 72.3 | 61.4 | 9.0 |
| lexicon | **31.5** | 46.4 | 68.9 | **82.8** | **3.0** |
| backoff | **34.8** | 52.3 | **74.9** | 82.8 | 8.1 |
| *published BiRNN (ML4AL 2024)* | *30.3* | *—* | *66.2* | *—* | *—* |

Three things follow, and they are firmer than the D-series versions because the target number is verified:

- **A 15-line lexicon lookup matches the BiRNN on top-1** (31.5 vs 30.3), and the backoff blend exceeds it (34.8). Neither uses a neural network, an embedding, or a GPU.
- **Their top-20 of 66.2% is only ~8 points above a frequency floor of 58.4%.** On a 68-candidate set, top-20 admits 29% of the inventory. The metric is close to uninformative at this scale.
- **A&B is 64% unseen word types** (690 of 1,073 items) against the D family's 31%, and the collapse is correspondingly worse: lexicon 82.8% → **3.0%**. The series the published paper found hardest is hardest for exactly the reason nobody reported.

Caveats belong in the same breath, per the comparison-framing rule below: our extraction is from DĀMOS rather than the printed editions, our eligibility excludes `UNCLEAR` and underdotted targets, our candidate set is 68 against their 75, and their masking protocol is unspecified. **The claim is that their reported numbers are reproduced and slightly exceeded by methods with no learned parameters, and that both sit near a frequency floor — not that a better model has been built.**

## The three findings

1. **Top-20 is close to uninformative on this vocabulary.** 20 of 75 candidates is 27% of the inventory, and the frequency prior alone reaches **63.2%** top-20. Published top-20 figures are 66.2% (A&B) and 78–80% (series D). Any top-20 number here must be printed next to its floor or it will be over-read.
2. **Memorisation beats modelling.** Lexicon lookup outscores the sign bigram by 21.3 points on top-1. The D tablets repeat a small gazetteer of place names (`ku-ta-to`, `ru-ki-to`, `e-ko-so`, `pa-i-to`) across dozens of documents.
3. **Nothing generalises to new material.** Between word types seen and unseen in training: lexicon 89.3% → **4.3%**, bigram 55.4% → **10.4%**. 845 of 2,684 items (31%) are unseen. The aggregate figure is therefore mostly a measurement of gazetteer recall. **Neither published paper appears to report this stratification**, which is the substantive contribution here.

## Protocol

| Decision | Value | Why |
|---|---|---|
| Sequence unit | one physical line (`Document.line_tokens`) | Only unit reproducing published sizes — see convergence table below |
| Scope | 1,016 Knossos D-family docs (`series_of` starts `D`, site Knossos, support tablet) | Their exact subseries filter is unconfirmed; narrower would be a guess dressed as replication |
| Ground truth | `CERTAIN` only, underdotted excluded as targets | `UNCLEAR` conflates partial restoration, lacuna-edge truncation and editorial query |
| Masking | exhaustive leave-one-sign-out | Deterministic, item-efficient, independently resamplable |
| Augmentation | **none** | JOCCH reached 2,565 from 513 via 725 augmented + 1,327 duplicates; duplication adds no information and risks crossing a split |
| Split | document-grouped 5-fold | corpus-sources.md invariant; joins are already one document id in DĀMOS |
| Candidate set | frozen from training items only, maskable signs only | A test-only sign must not be rankable; logograms/`<NUM>`/`<SEP>` are context, never targets |

Extraction convergence against published figures:

| Their figure | Ours | |
|---|---|---|
| LREC 2020: 308 KN tablets (A&B) | **308** | exact |
| LREC 2020: 651 sequences | 695 sign-bearing lines | close (surplus is apparatus-only lines) |
| JOCCH 2023: 513 complete D sequences | **536** (single-sign words excluded) / 596 (included) | close |

## The gate that did not reproduce, and why

The plan expected the bigram at ≈50/78/91. Five-fold gives **41.2/64.9/85.8**. Nothing was adjusted to close the gap; the cause was measured instead.

- The prototype used a **single 80/20 split** and **excluded single-sign words**. Under that exact protocol, top-1 across eight seeds ranges **42.5% – 52.9%**; the prototype's 49.7% was a favourable draw. Pooled 5-fold under the same protocol: **45.9%**.
- The remaining gap to 41.2% is the 269 single-sign-word items, which the bigram cannot score at all (`train_sign_bigram_model` skips words with no `-`), included in the headline set.

**A single 80/20 split on this corpus carries ±5 points of top-1 variance.** That is a reason to distrust single-number restoration figures on corpora this size, including the published ones.

## The three DĀMOS traps (measured, D family)

| Trap | Detail | Count |
|---|---|---|
| Underdots do not affect `ReadingStatus` | `loader._bracket_status` inspects only `[`, `]`, `?` — never U+0323. Damaged-but-legible signs arrive `CERTAIN`; leaving dots in inflates the vocabulary 75 → 118 | 770 tokens, 1,170 sign positions |
| One-sign syllabic tokens are typed `UNKNOWN` | `classify` needs `-` for `WORD`, and `_IDEOGRAM_RE` needs an initial capital, so `o`, `ki`, `pa`, `pe` fall through | 557 reclassified to `WORD` |
| `Token.form_state` is always `None` | The DĀMOS loader never builds one, so sub-token `FormSegment` damage handling is **inapplicable**, not deferred | all tokens |

Reclassification audit (counts-by-rule, safe to publish): 557 → `WORD`, 493 → `NUMERAL`, 207 → `LOGOGRAM`, 28 → `SEPARATOR`. Decided by membership in the 211-sign inventory, not a hand-rolled regex; the loader's own confident classifications are never overruled.

The 9 target signs absent from the inventory — `*18 *22 *34 *49 *56 *65 *82 *83 *86` — are Judson's (2020) undeciphered syllabograms: transliterated, but carrying no phonetic label. Correct, not residue.

## Why hand- and findspot-grouping are sensitivity only

| Field | Coverage | Concentration |
|---|---|---|
| `meta.scribe` | 943/1,016 | hand 117 writes **684 (67%)** |
| `meta.findspot` | 470/1,016 | `KN, J1` is **397 (85%** of those filled) |

Holding out hand 117 removes two thirds of the corpus; holding out the rest leaves a test set two thirds one scribe. Normalise `117?` → `117` before grouping or the same hand lands on both sides (`split.leave_one_hand_out` does this).

## Comparison framing — required wording

Any number quoted against Papavassileiou et al. must carry these differences **in the same sentence**, not a footnote:

- DĀMOS, not the printed editions — text their edition restored is our excluded `UNCLEAR`.
- Their exact D-subseries filter is unconfirmed.
- Underdotted targets excluded here; they do not discuss underdots.
- No augmentation or duplication.
- Their masking protocol is unspecified.
- The JOCCH 2023 figures are only partially verified (full text paywalled).

**The claim is: "the published numbers are reproduced by a sign bigram under a comparable protocol, and both sit close to a frequency floor."** Never "we beat them."

## Decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| Physical line as the sequence unit | 2026-09-10 | Reproduces 308 exactly and 513/651 closely; document-level gives 174 and 12 | Whole-document sequences; register-merged entries (kept behind `--unit entry`) |
| Whole D family, not a guessed subseries | 2026-09-10 | Their filter is unconfirmed | Narrowing to match 513 more tightly |
| `UNCLEAR` excluded from ground truth | 2026-09-10 | Conflates three different editorial situations, only one of which is a secure reading | Admitting 411 more word tokens |
| Single-sign words included by default, tracked as their own stratum | 2026-09-10 | They are real signs the scribe wrote; but they have no within-word context, so they are a different problem | Silently excluding them (the prototype's implicit choice) |
| No augmentation or duplication | 2026-09-10 | Duplication adds no information and risks crossing a split | Matching JOCCH's 2,565-sequence construction |
| Report every figure against the frequency floor and stratified seen/unseen | 2026-09-10 | Without both, a number here misleads | Bare aggregate accuracy |
| Gate failure documented, not tuned away | 2026-09-10 | Adjusting a pipeline until a target number appears produces results that look right and are not | Re-tuning eligibility or masking to recover 49.7% |

## Derived artifacts and licensing

- DĀMOS is **CC BY-NC-SA 4.0**. Sequences, masked items and split manifests are derivatives: they belong in `~/.cache/linear-a-b/` (override `LINEARB_RESTORE_CACHE`), never in the repo. See `data/README.md`.
- Safe in the repo: code, aggregate metrics, counts-by-rule, vocabulary **size**, per-subseries document counts. Not: token lists, reconstructed text.
- Cite Aurora, F. (2015), *Procedia — Social and Behavioral Sciences* 198, 21–31.

## Not done (deferred from the approved plan)

- **Step 5** log-linear model — the open question is whether context *outside* the masked word moves the unseen-word stratum. Nothing here tests that; both real baselines are word-internal.
- **Step 6** torch BiLSTM — gated on step 5 showing sequence context helps. torch 2.14.0 resolves against this cp314 interpreter, so it is a choice, not a blocker.
- **Step 7** extension to the 308 KN A&B documents — the only direct apples-to-apples comparison with the fully verified 30.3 / 66.2.
- Span and word-final masking regimes are implemented and tested but not yet scored.
