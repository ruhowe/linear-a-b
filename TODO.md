# To do

Ordered. Each item names the model to run it on and why. "Go ahead" means start at the
first unticked item and work down, committing per item, without asking between items
unless an item says to stop.

Model rule: Sonnet for corpus checks, folding, plumbing and retrieval. Fable for
designing a test, choosing a null, or reading a result. Opus is not needed for anything
listed. Subagents doing retrieval or bulk runs are Sonnet regardless of the session model.

## Night plan 2026-09-12 (unattended overnight run; instruction: carry on until morning; a 05:03 reminder is set in this session)

If a different session picks this up (session ended), read the last few
hundred lines of the transcript of the session that wrote this plan for where it got to,
and its scratchpad reports (agent reports named kober-08-report.md, fresh-look-checks.md, assumptions-refresh-draft.md,
what-we-missed-draft.md). Agents spawned by that session: Kober 0.8 build, fresh-look
checks, spikes S-002 and S-003; each commits its own files; if a commit is missing, its
working-tree files are the state to continue from.

Work down in order; each step commits; nothing is pushed. If a step's agent output is on
disk but unread, read it first. If the session ended overnight, resume from the first
unticked step.

- [x] N1. (Done: F-034.) Read the Kober 0.8 report (answer key v3); write F-034; record the outcome in
      CHANGELOG 0.8; apply the pre-registered permissiveness check.
- [x] N2. (Done: F-035.) Read the fresh-look checks (line fragments, corpus coverage, Packard Appendix A
      recall); write F-035 (exploratory or current per what they are).
- [x] N3. (Done: A-001 etc. amended; section H A-125 to A-132.) Apply the ASSUMPTIONS refresh from the scratch draft: status updates and new
      section H (inherited from precedent, A-123 onward, renumbered after any rows the
      0.8 agent added).
- [x] N4. (Done.) Write docs/reports/2026-09-12-fresh-look.md: the three parts (assumptions
      refreshed, methodology refreshed, what we missed by following precedent) with
      the checks' numbers; link from README and HENGE.
- [x] N5. (Done: F-040.) Pre-register Kober 0.9 in CHANGELOG: medial channel, homophone-merged sign
      identities as a sensitivity, line-fragment handling if N2 found any; readings first.
      Sonnet builds; new pinned regression file for 0.9 beside the 0.1 pins; run Linear B
      full and size-matched controls; then Linear A once; Fable writes F-036.
- [x] N6a. Spikes S-001 (F-037), S-002 (F-036), S-003 withdrawn and S-003b (F-038) done.
- [x] N6b. (Done: F-041, criterion met, A-001 amended.) **Value transfer 1.0**, the promotion of S-003b under the main line
      (pre-registered in CHANGELOG): Sonnet runs; Fable writes the next F-number when it lands (F-039 went to S-011).
- [x] N6c. (Closed 2026-09-12; S-005 to S-007 get briefs today.) S-011 done (F-039, nothing); S-012 done (F-042, nothing but a diagnosis kept); S-013 done (nothing, note on F-037, and it found the 0.9.1 reproducibility bug); S-014 done (F-043, nothing); S-010 done (F-044: 'nearest Egyptian' is signary size; one-sign-per-word excluded); S-009 done (F-045: edition disagreement is mostly tagging and labelling; label aliases *56/PA₃, *79/ZU); S-008 done (nothing: the proxy cannot test Assumption 3; A-111 annotated) (Ru: keep going until usage runs out, resume after 05:03); S-005 to S-007 have index rows and no briefs yet; S-010, S-008, S-009, S-013, S-014 have briefs.
- [x] N6. (superseded by N6a to N6c) Spikes S-001 (mirror Linear B), S-002 (etymological floor), S-003 (Packard
      toponyms under a modern null): Sonnet runs each from its brief; Fable writes
      RESULT.md and an exploratory FINDINGS entry where warranted; INDEX.md updated.
- [x] N6d. (Done: F-046, floors 1,250 and 750; C-5 and the guide updated.) **Floor sweep under Kober 0.9.1** (merged identities, v3), pre-registered in CHANGELOG 2026-09-12 and launched 01:58 on Sonnet, tablet model, sizes 500 to 1,750; Fable writes the finding (supersedes F-022's floor for the current instrument if the reading is the first one). Emerged from Ru's point that discovery adds about 11 signs a year, so the floor has to move with the instrument or not at all.
- [x] N7. (Done through phase 40.) Journal phases for each; refresh kober-method.md with 0.8 and 0.9; HENGE index;
      README scope line; regenerate the report addendum if a finding it quotes changed.
- [x] N8. (Done 05:25, bundle through f278d8c; summary left as the session's last message.) Fresh dated backup bundle. Then stop and leave a morning summary
      as the last message.

## 1. Corpus hygiene (Sonnet)

- [x] **Linear A underdots (A-004).** Check whether sign labels in `aegean.load("lineara")`
      carry U+0323 or other damage marks that the `CERTAIN` status ignores, as DĀMOS does.
      Count affected tokens. If any, the `word_sample()` in
      `scripts/controlled_comparison.py` has been sampling damaged signs as certain;
      record the count in ASSUMPTIONS A-004 and, if above 1% of sampled signs, rerun
      protocol 1.0 seed 0 on Linear A with them excluded and add the delta to F-012.
- [x] **Secure-sign sensitivity (A-001).** Restrict the Linear A word sample to words
      written entirely with the 25 signs in Meißner and Steele's Table 1 (list is in
      `docs/works/` under their page; if the table is not transcribed there, transcribe it
      first and cite it). Run protocol 1.0 seed 0 with the frozen lexicon set. Report the
      sample size that survives and the z-scores beside the full-sample ones. Record in
      FINDINGS as F-014 and update A-001 to tested. If fewer than 100 words survive, say
      the test is underpowered and stop there.
- [x] **Test runner.** Install pytest into `.venv` so the command in the test docstrings
      works, and confirm 28 tests pass. Note the change in `docs/ai_context/HENGE.md`
      under environment. Done 2026-09-11, 28 passed.

## 2. Kober-method design (Fable, session model, no subagents)

This is the new direction. Design before code. Nothing here runs against Linear A.

- [x] **Write `docs/ai_context/kober-method.md`.** (Done 2026-09-11; A-033 to A-041; CHANGELOG Kober 0.1.) State in plain English what the Kober
      method is (structure from sign patterns, no sound values), what Kober found on
      Linear B (the triplets), and what the computational version has to do. Define:
      what counts as a candidate stem and suffix; what a paradigm is (a stem attested with
      two or more suffixes, at minimum); what the null is (the same procedure on Linear B
      with sign identities shuffled within frequency bands, as in protocol 1.0); what
      "recovers Greek grammar on Linear B" means as a pre-registered criterion, for
      example that the top-ranked suffix alternations correspond to known Mycenaean case
      or number endings at a stated rate. List every assumption as A-033 onward in
      ASSUMPTIONS.md. Enter the design in CHANGELOG.md as Kober protocol 0.1 with the
      reading written before any result exists.
- [x] **Stop and show Ru the design** before any code is written. Plain English, under
      300 words, with the pre-registered criterion in one sentence. Shown 2026-09-11;
      approved by Ru 2026-09-11 as written.

## 3. Kober-method on Linear B (Sonnet builds, Fable reads)

Only after item 2 is approved.

- [x] **Build `src/kober/`** (done 2026-09-11, 39 tests pass) to the design: extraction of word types from DĀMOS with the
      same normalisation as `src/linearb_restore/normalise.py`, stem and suffix
      candidate generation, paradigm scoring, the N1 and N2 nulls from the design (the
      frequency-banded null was rejected in the design), and a report.
      Tests pin the word-type count and check the null cannot see sign identity.
- [x] **Run on Linear B** and write F-016 (done 2026-09-11: criterion met, 9 of 10) (Fable reads the result). The only question is
      whether the criterion in the design was met. If not, the method is not ready for
      Linear A and the entry says so, and items 4 and 5 wait.

- [x] **Stage 2, the grid, on Linear B.** (Done 2026-09-11, F-017: fraction met, grid
      not recovered.) Build `src/kober/grid.py` to the stage 2 pre-registration in
      CHANGELOG (Kober 0.1 stage 2), run on Linear B, seeds 0 and 1. Sonnet builds and
      runs; Fable applies the criterion and writes F-017.
- [x] **Kober 0.2, anchored grid pairs, on Linear B.** (Done 2026-09-11, F-018: fraction
      marginally met, no pure class.) Per the CHANGELOG pre-registration; stage 1 unchanged.
- [x] **Kober 0.3, grid pairs from the anchoring alternations themselves, on Linear B.**
      (Done 2026-09-11, F-021: met, 4 of 7 against a null of about 0.1.)
      Per the CHANGELOG pre-registration. Sonnet builds and runs; Fable reads. Not on the
      critical path: it sharpens the Linear B positive control only. Sonnet builds and runs; Fable reads, F-018.

## 4. Kober method on Linear A (Sonnet runs, Fable reads)

Only if F-016 met its criterion (it did). The grid on Linear A is included only if F-017 meets its criterion.

- [x] **Pre-register the Linear A reading** in CHANGELOG before running (done
      2026-09-11, "0.1 on Linear A"): what a paradigm count above its null would and
      would not mean, given A-001 (sign values are not needed here, but sign
      *identities* are, and the transcription chain supplies them). Fable.
- [x] **Size-matched Linear B control.** (Done 2026-09-11, in F-019.) Add `--subsample N --subsample-seed S` to
      `scripts/kober_run.py` (random subset of word types, no other change) and run ten
      subsamples of Linear B at Linear A's normalised type count, with the grid if F-017
      passed. Sonnet. Report per subsample the three criterion parts and the grid
      fraction; no verdict.
- [x] **Run on Linear A**, same protocol version, same null, `--allow-lineara`, and write
      F-019 against the size-matched control. (Done 2026-09-11.) Report
      paradigms found, their size, and the null distribution. Do not attach any language
      to any paradigm in this entry. Sonnet runs, Fable writes.

## 5. Compare the two methods (Fable)

- [x] **Write F-020, the head-to-head.** (Done 2026-09-11.) Same corpora, same date. For each method: what
      question it asks, what it found on Linear B where the answer is known, what it
      found on Linear A, and what its best wrong control scored. State plainly which
      method can say anything about Linear A at this corpus size and which cannot. Update
      `docs/ai_context/terminology.md` if the comparison changes how either name should
      be read. Update the state-of-the-art Decisions table.

## 6. Next line of work (proposed, not started)

- [x] **Locate the Kober floor.** (Done 2026-09-11, F-022: tablet floor 1,875 types, type floor 2,750; F-019 corrected.) Pre-registered 2026-09-11 in CHANGELOG ("Floor sweep
      on Linear B"): seven sizes plus bisection, twenty subsamples each, two subsampling
      models (types, tablets), stage 1 only, floor = sixteen of twenty meet all three
      parts. Sonnet builds `--subsample-docs` and the sweep script and runs it; Fable
      writes F-022.
- [x] **Linear A word dividers (A-002).** (Done 2026-09-11, F-023: statement survives the change of edition.) Feasibility checked 2026-09-11 (SigLA carries
      its own division; 692 types against 988). Pre-registered in CHANGELOG
      ("Segmentation sensitivity on Linear A"). Sonnet adds `sigla` to `kober_run.py`
      behind a gate and runs the design after the floor sweep has committed, since both
      edit the runner; Fable writes F-023.

## 7. Prior art for the claims register (taken over by the findings session 2026-09-11; the prior-art session is closed and the two-session file rule no longer applies)

- [x] **Bank the claims.** (Done 2026-09-11.) `docs/ai_context/claims.md`: seven claims
      in atoms, each resting on current FINDINGS entries, guarded by `tests/test_claims.py`.
      Opus (session model).
- [x] (All atoms closed; C-8a searched 2026-09-12, best earlier grade Precursor.) **Prior-art search.** Run the search protocol in `claims.md` for every atom, in
      priority order. Sonnet agents retrieve and return rows, one agent per claim cluster
      (C-1 with C-2, C-3, C-4, C-5, C-6 with C-7); the session model grades each hit, writes
      the Ledger and a `docs/works/` page for every graded work. Stop and show Ru the
      ledger before any claim is called new anywhere.

- [x] **`docs/guides/what-we-found.md` items 5, 6, 8 and claims C-3, C-5b updated** (done 2026-09-11 by the findings session; C-3c and C-3d added). Original note: (noted by the findings session 2026-09-11). F-025 and F-027 change
      the reading: at Linear A's size the machine's two best alternations are grammar in
      every tablet-model subsample and its top three beat chance in 16 of 20, so "finds
      Greek's grammar about one time in three" and "the limit is the machine's, not the
      method's" no longer hold as written; 1,875 is the floor for a *mostly* grammatical
      top ten. The "about 200 tablets" is now verified from Kober 1944 as about 200
      published inscriptions (docs/works/kober1944.md). F-026 closes the slot-context line.

## 8a. Read Kober 1946 and 1948 (Fable) — done 2026-09-11

- [x] Both read in full; pages at V; dated notes on F-016,
      F-019, F-026, F-027; A-037 annotated. Three consequences queued below.
- [x] **List-homogeneity diagnostic on Linear B** (done 2026-09-11, F-030: Assumption 4 holds, Assumption 7 unselective).
- [x] **Kober 0.6, reference list v2** (done 2026-09-11, F-031: tablet baseline 6 → 11; with roles 9 → 12; type unchanged).
- [x] **Kober 0.7, list-homogeneity tie-break** (done 2026-09-11, F-032: 9 and 12 of 20, identical to 0.5; context line closed; Kober line closed on this corpus).

## 8c. Close-out (2026-09-11)

- [x] **Specialist write-up**: `docs/reports/2026-09-11-two-methods.md`, quoting FINDINGS
      only, three rules first. Fable.
- [x] **Two new atoms graded** (C-3c, C-3d; done 2026-09-11, both Precursor via kober1946; ledger shown to Ru). (a) Kober's list condition (kober1946 Assumptions 4, 6, 7) measured as a
      statistic with a null, F-030: search for any prior test of within-tablet ending
      homogeneity on Linear B. (b) The ethnic-derivation gap in a Mycenaean-grammar
      answer key, F-031: this is a correction to our instrument, not a claim; grade as
      such. Also re-read `docs/guides/what-we-found.md` items 5, 6 and 8 against F-025
      to F-032 and the note already left under item 7.

## 8b. (was 8a) Original reading task

- [x] (Read in full 2026-09-11; banked in docs/works/kober1946.md.) **Kober 1946, JSTOR 499054** (`docs/works/kober1946.md`) and **Kober 1948, JSTOR 500555**. Read for the three questions on the 1946
      page: which tablets, whether context was used, how many triplets and how hedged.
      Update both pages to V, add dated notes to F-024 and F-027, and only then decide
      whether the entry-alignment diagnostic (item 8, open question) is worth running.

## 8. Context-aware Kober instrument (proposed by the prior-art session 2026-09-11; accepted with two prerequisites; not started)

Why. F-022 puts the machine floor at about 1,875 word types, Kober found inflection by
hand from about 200 tablets (secondary account, unverified; claims.md C-5b). She asked
for a few sure findings, used tablet context, and assumed inflection. F-021 showed that
narrowing to the strongest alternations recovers what pooling loses.

- [x] **Prerequisite 1: the null rate of the grammar match (Fable designs, Sonnet runs).**
      Part 3 of the stage 1 criterion, "seven of the top ten on the reference list", has
      never been measured under a null. The gender rule accepts any same-consonant o/a
      pair, so frequent endings pairing by chance can match it. Add to `kober_run.py`:
      for each N2 draw, the matched count of that draw's own top ten; report its
      distribution and the real value's percentile. Run on full Linear B and on the
      twenty tablet-model subsamples at 988 (F-022). Reading, to pre-register: at full
      size the real 9 of 10 is expected far above the null; at 988 the real median of 6
      may sit inside the null's range, in which case F-019 and F-022 gain a dated note
      that the part 3 pass counts at small sizes include chance matches, and any
      precision criterion must be stated as "above the null rate", not as a raw count.
      Done 2026-09-11 per CHANGELOG "Null rate of the grammar match, and precision
      criteria": `nulls.py::grammar_matched_count` reuses the existing N2 ending draws
      (`run_n2`'s `track_grammar_match`, no extra randomness), for n in (3, 5, 10) with
      ties at the n-th place included (A-053); reported under `ending_channel.grammar_match_null`
      in every report. Run on full Linear B (seeds 0, 1) and the forty 988 subsamples
      from F-022 (twenty type-model, twenty tablet-model at the sweep's own document
      counts), written to `results/kober-grammar-null/`.
- [x] **Prerequisite 2: the no-context precision baseline (Sonnet).** Re-score the
      existing 988 subsample results (both models) under candidate precision criteria,
      for example "the top 3 are all grammar and each above its N2 support null", with
      the false-positive rate from prerequisite 1. This is the bar the context-aware
      version has to beat; without it a pass could be the criterion, not the context.
      Done 2026-09-11: `scripts/kober_precision_table.py` scores, per model (full,
      type-988, tablet-988), "real matched at top-n above the null p99" (n in 3, 5, 10)
      and raw "k of top-n on the list" ((n, k) in (3,3), (3,2), (5,4), (10,7)), plus the
      per-model null p99 and real matched spread, in `results/kober-precision-table.json`
      and `.md`.
- [x] **Kober 0.4 design (Fable).** (Done 2026-09-11: CHANGELOG 0.4, kober-method.md, A-075 to A-078.) Pre-register in CHANGELOG. (a) Stem-ending pairs
      weighted or restricted by shared tablet context: position in the document,
      adjacent logogram or numeral, document type via pyaegean's `structure.py` and
      `commodity.py`. (b) A precision criterion fixed before the run. (c) A null that
      preserves the context features: N2 stratified so endings shuffle only among words
      sharing the same context class. Calibrate on Linear B at 988 under both subsampling
      models, twenty each, bar sixteen of twenty as in F-022. Only if it passes, run Linear
      A once. Assumptions from A-069.
- [x] **Build and run (Sonnet), read (Fable).** (Done 2026-09-11, F-026: failed, 2 of 20 against a bar of 16; Linear A not run; the slot line is closed.) On Linear A the honest payoff is a
      null-calibrated list of candidate paradigms with their tablet contexts, which the
      field does not have, and a possible reopening of the grid test (C-4d) if support
      rises above two. It is not a decipherment; the language-anchor step is still
      missing. Risk: Linear A is thinner than Kober's material (84% of word types occur
      once, maximum alternation support 2, F-019), so context can raise precision, not
      support.

- [x] **Entry-role diagnostic on Linear B** (done 2026-09-11, F-028: above the null,
      weak, grammar carries it; filter designs closed, re-ranker opened).
- [x] **Kober 0.5, entry-role tie-break (Sonnet builds and calibrates, Fable reads,
      F-029).** (Done 2026-09-11: 9 of 20 against 16; improves, below the bar; Linear A not run.) Per the CHANGELOG 0.5 pre-registration. Stage 1 unchanged; regression
      pins must stay green. Linear A only if the bar is met.

## 9. Spikes (see spikes/INDEX.md; run only on "go ahead" naming the spike)

- [x] (All run; superseded by the spikes index.) S-001 mirror Linear B; S-002 etymological floor; S-003 Packard toponyms under a
      modern null. Briefs written 2026-09-12. Sonnet runs; Fable reads. Each lands as an
      exploratory FINDINGS entry or as nothing.

## 10. Parked, run only if asked

- [x] **The 2024 GORILA supplement, bought 2026-09-12** (closed 2026-09-12, F-047, F-048) (Del Freo and Zurbach 2024; the
      publisher's PDF is not machine-readable). Next: transcribe the transliteration pages
      and the siglum concordance locally; a Sonnet agent builds a local supplementary
      corpus file in the loader's document shape (never committed), and reports the
      document and word-type counts; then every Linear A run repeats under a new version
      (Kober 1.0 and Value transfer 1.1), pre-registered first, with the 1985-corpus
      results kept beside the enlarged-corpus results. The Anetaki ring's edition is
      forthcoming.
      Progress 2026-09-12, 01:30: the table of contents, the 22 sign plates and 12
      spreads of the *Index des signes* (pages 183 to 205) are in hand; a Sonnet agent is
      transcribing the index to a local file with a per-word consistency check.
      The index lists every sign group with its inscription reference, so the word-type
      list can be built from it alone. Still wanted: index pages 181 to 182 and 206;
      Introduction V (XXII to XXIV) for the conventions (asterisk, dotted underline,
      column letters); the Concordance générale (XXVI to XXXV) to separate new documents
      from re-editions already in the loader; Introduction I (XVII to XVIII). Expected
      gain: about 50 to 100 word types (427 signs at the corpus's rate of 0.24 word types
      per sign in words), against a Kober floor of 1,875; so the reruns are for the
      toponym test and edition-independence, not for the floor. Pre-register Kober 1.0
      and Value transfer 1.1 only once the concordance is in hand.
      Transcription done 05:15 (619 rows, 281 sign-group/reference pairs, 257 groups, 24
      complete word types of two or more signs, one code unmapped). Joined to the loaded
      corpus: 79 of 114 referenced inscriptions already load, 20 of 24 word types already
      present, 4 new (2 sharing a stem with an existing type, all 4 eligible for the
      toponym test). The loaded chain is not 1985-only (F-035 corrected). The reruns
      shrink to: add the 4 new types and the unmatched documents once the concordance
      confirms identifiers, then Value transfer 1.1 as a sensitivity. Kober 1.0 on the
      enlarged corpus would change nothing measurable and is dropped unless the
      concordance shows more.
      09:30: the rest of the book (front matter, concordances, map, all inscription
      pages 5 to 179) is in hand; index pages 181, 182 and 206 are blank. A
      Haiku agent is cataloguing every file (page numbers, sections, entry layout, the
      conventions page); then Sonnet transcribes the Introduction and Concordance
      générale, and the inscription entries' PRINTED transliterations (never glyphs from
      photos or drawings) into a local corpus file in the loader's shape; Fable reads
      the reports, reconciles identifiers with the loaded chain, and pre-registers Value
      transfer 1.1 and any Kober rerun.
      10:40: front matter and tablets transcribed (Introduction, all four concordances,
      the doubtful concordance; 27 tablet entries, which the book prints as glyph copies,
      not Latin values). Joined on the Concordance générale: 89 of 107 documents loaded,
      18 absent, 4 word types new (F-047). Pre-registered "Supplement sensitivity 1.0"
      in CHANGELOG; Sonnet builds `--extra-word-types` and runs it; Fable writes the
      finding. Pages 57 to 179 transcribed 11:20 (107 entries, no printed Latin values
      anywhere; apparatus banked). The whole book has now been read.
      12:10: sensitivities 1.0 and 1.1 run and banked (F-048): the supplement adds no word
      type the loader lacks; four division variants on Petras change nothing. F-047
      corrected. The supplement item is closed; the Anetaki ring stays open.
- [ ] **Comprehensive Linear A bibliography.** The catalogue is targeted (README, "Scope
      and coverage"). If it is to become a full review of Linear A research, seed it from
      Younger's online bibliography and Davis 2026's, one page per work with a
      verification flag, Sonnet for retrieval and page drafting, a few hundred items. Not
      needed for any finding; needed only if the repo is to be read as a survey.
- [x] (Done, F-034.) **Kober 0.8, reference list v3 from Ventris and Chadwick 1973** (pre-registered
      2026-09-12 in CHANGELOG; the book arrived). Sonnet builds, rescores every file, reruns
      the null; Fable reads, F-034. The DĀMOS-annotation route remains the later option.
- [ ] **BLOCKED (2026-09-12).** The annotation exists in DĀMOS's database (`ling_words`) but is not exported anywhere: Aurora 2024 (Ariadne Suppl. 5) says the nominal and participial annotation, ninety percent of occurrences, is unfinished, and Aurora et al. 2025 (DHNB) say linguistic analysis is in neither the online search nor the EpiDoc export; a future bulk release would be CC BY-NC-SA 4.0, no date. The only route is a request to Federico Aurora (University of Oslo Library), which is Ru's decision, not the session's. Even then the annotation is a set of competing readings per word, so a disambiguation policy would need pre-registering first. **Reference list v4 from DĀMOS's morphological annotation.** DĀMOS annotates case
      and number per word (aurora2015); pyaegean fetches transliteration only. Extend the
      loader or fetch the annotation directly, derive the alternation list from it, and
      rescore as Kober 0.8 with old and new beside each other. Replaces the hand-built list
      and its known gap (A-037). Sonnet fetches; Fable pre-registers the readings.

- [x] (Not pursued: the etymological line is closed, F-020 and F-036; recorded as a limit on A-024.) **TLHdig fold (A-024).** Download the TLHdig XML dataset from the Hethitologie
      Portal, extract lemmatised headwords, replace `hittite_kaikki`. Sonnet.
- [x] (Not pursued: the etymological line is closed, F-020 and F-036; recorded as a limit on A-023.) **Alif and matres folding (A-023).** Treat word-internal alif, waw and yod as vowel
      letters in the Arabic and Modern Hebrew folds, rerun protocols 1.0 and 1.1 on both
      corpora, update F-012. Sonnet.

## Standing rules for whoever works this list

- The two methods are called the **etymological method** and the **Kober method**, as
  defined in `docs/ai_context/terminology.md`. No other names in new writing.
- Results go in FINDINGS.md only, dated and versioned. README and HENGE describe.
- When a phase closes (a finding written, a direction changed, a correction made), append
  one concise entry to JOURNAL.md saying what was done, what it found, and why the next
  step follows. The journal is the narrative; it quotes, never asserts.
- A new instrument or lexicon is not done until its assumptions are in ASSUMPTIONS.md.
- Every "detects" or "recognises" claim quotes the best wrong real language under the
  same map on the same sample beside it.
- Nothing derived from the corpora is committed. Aggregate numbers only.
- No external communication of any kind.
- Two sessions write to this repo. This one owns FINDINGS.md, CHANGELOG.md,
  ASSUMPTIONS.md, TODO.md and the instrument pages in `docs/ai_context/`. The prior-art
  session owns `docs/ai_context/claims.md` and the prior-art additions to
  `docs/works/`. Neither edits the other's files; each re-reads any shared file
  immediately before editing and commits its own files only. `scripts/findings.py
  --check-claims` reports any claim that cites a superseded or withdrawn finding.

## After the supplement (2026-09-12, afternoon)

- [ ] **A specialist reader.** `docs/reports/2026-09-12-reviewer-brief.md` says what to
      check and where. Ru decides whom to show it to; nothing leaves the repo without
      that decision.
- [x] **Anetaki ring** (2026-09-12): Kanta et al. 2025 fetched (CC BY-NC-SA), read, banked;
      it prints no transliteration, the edition is *Anetaki II*, forthcoming. Nothing to
      run. Watch for that volume.
- [x] **S-005 (structural profiles)** run 2026-09-12 (F-049, exploratory): Linear A sits with running text of inflecting languages and away from lemma lists; the axis is genre, not language.
- [x] **S-007 (a model as Kober)** run 2026-09-12 (twelve runs): nothing; the model finds the same stems with opaque labels (analysis, not recall) and its single-stem paradigms never exceed the null, on Greek either.
- [x] S-006 done (nothing; note on F-019); v4 blocked; Anetaki closed until Anetaki II; C-8a search closed. 2026-09-12 13:40.

