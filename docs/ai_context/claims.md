# Claims — what this project says is new, and the prior-art test for each

Files: `tests/test_claims.py` (guards the register below), `FINDINGS.md` (the only source of
every number here), `docs/works/*.md` (every prior work graded in the ledger has a page).

See also: [result-discipline.md](result-discipline.md) for when a number is a finding;
[state-of-the-art.md](state-of-the-art.md) for the survey the leads come from;
[terminology.md](terminology.md) for the two method names; [writing-style.md](writing-style.md)
before turning any claim into prose for a person.

Written 2026-09-11, after the plain-English "five things" summary was corrected twice in
one session (F-022 changed two of the five). This file exists so the summary is written
once, precisely, and can be retested instead of re-derived.

## Rules

- Numbers here are quotations of FINDINGS. A claim with no current FINDINGS entry behind it
  is not a claim. `tests/test_claims.py` fails if any F-id in the Register's "rests on"
  column is missing or not **current**.
- A claim changes only when a FINDINGS entry changes. Edit this file in the same commit
  (HENGE rule 5), and re-run the prior-art check for the atoms that moved.
- The word "new" is allowed only for an atom graded **Not found** after the search protocol
  below has been completed, and only as "as far as we found, on [date]".
- Plain statements are for people; precise statements are what a prior work is tested
  against. Never grade a prior work against the plain statement.
- Framing (evaluation-harness Decisions): tool-assisted measurement, never "AI discovered".
- The people-facing version is `docs/guides/what-we-found.md`. Update it in the same commit as
  any claim change; `tests/test_claims.py` fails if an atom is not referenced there.
- Awareness is read from git by `scripts/prior_art.py`, never set from memory. "We got there
  independently" is the claim a reader will doubt, so the history has to carry it.

## Register

| id | short name | plain statement | rests on | priority |
|---|---|---|---|---|
| C-1 | Dictionary matching cannot choose a language | The dictionary-matching method nearly every decipherment uses matches wrong languages about as well as the right one, even on Linear B where the answer is known | F-008, F-013 | 1 |
| C-2 | The Semitic signal is dictionary shape | The best-looking language match for Linear A, Northwest Semitic, came from how the dictionaries were built and how sounds were mapped, not from the language | F-012 | 3 |
| C-3 | Kober's method works by machine | Alice Kober's method, run by machine with no sound values, recovers Greek grammar and the sign pairs she used from Linear B | F-016, F-021 | 2 |
| C-4 | Linear A has stem-and-ending structure | Linear A words share stems with varied endings beyond chance, a little more weakly than Greek does at the same size, in both editions of the corpus | F-019, F-022, F-023 | 2 |
| C-5 | The corpus-size floor, measured | By machine, the amount of text at which Greek's grammar comes through reliably depends on the instrument: about twice Linear A's size with the first answer key, about a quarter more than Linear A's size with the key rebuilt from the handbook and its spelling variants merged, and less than Linear A's size on the weaker top-three bar; Kober found it by hand from less | F-022, F-046 | 1 |
| C-6 | Linear B restoration sits near a floor | A published neural result on restoring damaged Linear B is matched by a word-list lookup, and its headline metric sits close to a sign-frequency floor | F-001, F-002 | 3 |
| C-8 | The borrowed sounds have positive evidence, for a few signs | Cretan place names known from the Knossos tablets recur on Linear A tablets under the borrowed sounds more often than chance allows, in both editions, and three wrong word lists do not; this supports the sounds of the dozen signs in those names and no others | F-041 | 1 |
| C-7 | Measurements on di Mino 2026 | A third of the central inscription in the most serious recent Semitic reading rests on sign values not shown to carry over from Linear B, and two of its words exist only under a re-division the edition does not make | F-010 | 4 |

Priority: 1 = the claims a reader will take as the headline, check first; 4 = narrow, check last.

## Prior-art grades

Grade each **atom** (C-1a, C-1b, ...) separately, against its precise statement. One work can
carry different grades for different atoms. Highest applicable grade wins.

| grade | means | consequence for the atom |
|---|---|---|
| **Shown** | An earlier work reached the same conclusion from a measurement on Aegean material, with a control that could have failed | Not new. Ours is a replication or extension; cite it first |
| **Precursor** | An earlier measurement on Aegean material with a weaker or different control, or the same method by hand | Not new as an idea. Ours is new only in the named "makes it ours" component |
| **Shown elsewhere** | The same conclusion measured on another script or language, or a theoretical bound that yields a number for this setting | The transfer to the Aegean may be new; the idea is not. Cite it as the lineage |
| **Stated** | Asserted or argued without a measurement: by eye, in a review, in a critique, in a blog | Ours supplies the measurement. Say "confirms by measurement what X argued" |
| **Contradicted** | An earlier work reports or argues the opposite | Must be answered in any write-up, whatever else is found |
| **Not found** | Search protocol completed, no work above | May be called new, "as far as we found, on [date]" |

Two more columns per Ledger row. The grade says what the earlier work established; these
say what our result does to it, and whether we knew it at the time.

| relation (ours, to theirs) | means |
|---|---|
| **replicates** | Same test, same result |
| **confirms** | Same conclusion by a different method |
| **measures** | Turns their argued or by-eye conclusion into a measurement |
| **extends** | Same direction, adds a control, a corpus or a comparison they lacked |
| **transfers** | Ours is the Aegean counterpart of their result from another script, language or field (whether we knew it is the awareness column's job) |
| **complements** | A different result that fits with ours or with its stated limit |
| **qualifies** | Ours narrows what their result can be taken to show |
| **is qualified by** | Theirs narrows what ours can be taken to show |
| **contradicts** | The two readings cannot both stand; must be answered |
| **unresolved** | Their content has not been read; the row holds the atom open |

| awareness | means | git test (`scripts/prior_art.py`) |
|---|---|---|
| **built on** | We knew the work and used it | First mentioned before the finding's commit, and named in the FINDINGS entry, CHANGELOG, ASSUMPTIONS or the method's HENGE file at that commit |
| **known** | In our survey before the finding, not drawn on by it | First mentioned before the finding's commit |
| **independent** | We did not know it when we got the result | First mentioned after the finding's commit |

The script fails a row git contradicts. It lets judgement mark "known" where git would
allow "built on" (a mention is not always use), never the reverse.

## Search protocol

Deterministic order; the same inputs give the same ledger.

1. **Catalogue.** `scripts/bib.py --grep <term>` for each query term, then the leads named
   under the claim. Grade from the work page only if it is verification Y; otherwise go to
   the source.
2. **Named leads.** Every lead listed under the claim, catalogued or not. Fetch the primary
   source where reachable. Record which were unreachable.
3. **Queries.** The fixed query list under the claim, each run against: general web and
   Google Scholar; ACL Anthology; arXiv; De Gruyter (Kadmos); Minos (Salamanca, open);
   Pasiphae; SMEA; BMCR; Language Log. Add a query only if a hit suggests a term the list
   lacks, and record it.
4. **Citation chase, one level.** For every hit graded Stated or above: its reference list
   for earlier work on the atom, and "cited by" for later work.
5. **Stop.** An atom closes when a **Shown** hit is verified from the primary source, or when
   steps 1 to 4 are done and the last five queries produced no new hit graded Stated or above.
6. **Record.** One Ledger row per (atom, work), with grade, relation and awareness. The
   evidence cell quotes the sentence or gives the page or table that earns the grade, in
   under 30 words; the work page carries the rest. Every work in the Ledger has a
   `docs/works/<key>.md` page (the test enforces it); new pages use verification Y/P/S as
   state-of-the-art.md defines them. Then `scripts/prior_art.py --suggest` for awareness,
   update Atom status, and `--write-view`.

Retrieval is Sonnet; grading a hit and writing the Ledger is the session model (TODO.md
model rule). An agent returns rows; it does not edit the repo.

## Claims

### C-1 · Dictionary matching cannot choose a language

- **C-1a.** On Linear B, whose language is known, dictionary matching under a sign-to-consonant
  map scores wrong real languages close to the right one: Greek lexicons +2.8 to +3.2,
  Sumerian +2.31, Finnish +2.25, Basque +1.98, under the same Greek map; Greek's lead is
  about one sample standard error (F-008, F-013).
- **C-1b.** Every real lexicon beats a shape-matched synthetic lexicon, so beating a random
  or synthetic control is not evidence for a language (F-008, F-013; A-011 falsified).
- **C-1c.** On Linear A, Greek, which is not its language, scores +3.10, as high as on
  Linear B (F-008). Stated as a measurement only; the cause is not asserted (F-014 withdrew
  the first explanation).
- **Makes it ours:** the calibration corpus is the deciphered sister script, and the bar is
  wrong real languages, not random sign values.
- **Limit, always quoted with it:** this is dictionary matching under a sign-to-consonant map
  at Aegean corpus size. Character n-gram models identify the language of known texts at 97%
  over 380 languages given about 1,800 words each (hauer2016), so "matching cannot choose a
  language" is false as a general statement.
- **Shown would need:** a dictionary-matching score for at least one wrong real language on
  Linear B, or on another deciphered script, compared with the right language's.
- **Does not count as Shown:** random-value nulls on Linear A alone (Precursor at most);
  critiques that dictionary matching is loose (Stated); chance-resemblance theory in
  historical linguistics (Shown elsewhere at most).
- **Leads, catalogued:** packard1974, peronocacciafoco_programme, nepal2024, raghavendra2026,
  hauer2016, luo2021, tamburini2025, sproat2014, shannon1949, steele2017, dimino2026.
- **Leads, not catalogued:** Ringe 1992 (chance in language comparison); Kessler 2001 (*The
  Significance of Word Lists*); Barber 1974 (*Archaeological Decipherment*); Pope 1975/1999;
  Robinson 2002; Duhoux's critiques of Linear A decipherments; Chadwick 1958 on false
  decipherments; Mair 2026 (Language Log); Adkins 2026 (The Conversation).
- **Queries:** "fictitious decipherment" Linear A · decipherment control "wrong language" ·
  "Linear B" control dictionary matching decipherment · chance resemblance lexical
  comparison probability · "false positive" decipherment evaluation · Linear A etymological
  method critique · "Linear B" "known answer" decipherment method test.

### C-2 · The Semitic signal is dictionary shape

- **C-2a.** Ugaritic and Strong's Hebrew rank first and second on Linear A across three word
  samples (means 2.73 and 2.16), but the lead over the best wrong language falls from about
  two standard errors (0.78) to about one (0.57) when the map's laryngeal options are
  removed (F-012).
- **C-2b.** With the language held fixed, dictionary format moves the score by about two
  units: Strong's Hebrew +2.44, a Modern Hebrew frequency list +0.59, on the same Linear A
  words (F-012).
- **Makes it ours:** same-language, different-format control; laryngeal ablation.
- **Shown would need:** a measurement that a Semitic match on Linear A, or dictionary
  matching on any script, changes with lexicon format or with the vowel-to-laryngeal rule.
- **Leads, catalogued:** peronocacciafoco_programme (Eu, Perono Cacciafoco & Cavallaro 2019,
  "very little" Semitic), dimino2026, hauer2016 (Hebrew top for Voynich, self-hedged as
  combinatorial artefact), strongs_hebrew.
- **Leads, not catalogued:** Gordon 1966 and its reviews; Best; Rendsburg 1996; Kessler 2001;
  Ringe 1992; Mair 2026.
- **Queries:** Linear A Semitic reading critique · Gordon Minoan Semitic review · laryngeal
  vowel matching decipherment · lexicon choice bias cognate matching · Hebrew dictionary
  matching artefact undeciphered.

### C-3 · Kober's method works by machine

- **C-3a.** An unsupervised stem-and-ending analysis of Linear B word types, using sign
  identity and position only, ranks alternations so that 9 of the top 10 are known
  Mycenaean inflection; the top, -ja/-jo, has 57 supporting stems against a null 99th
  percentile of 19 (F-016).
- **C-3b.** The first signs of the top alternations share a consonant 4 of 7 times against a
  positional null mean of about 0.1 (99th percentile 0.25 to 0.27): Kober's grid pairs,
  recovered without values (F-021). Pooling every pair does not recover the grid (F-017,
  F-018).
- **C-3c.** At Linear A's corpus size (988 word types, Linear B shrunk by removing tablets,
  twenty subsamples) the instrument's two best alternations are Greek grammar in 20 of 20
  and all of its top three in 13 of 20 under the reference list rebuilt from Ventris and
  Chadwick's morphology (v3), 18 of 20 with the spelling-variant signs merged; Kober's own
  corpus was under 750 word types and her bar was two words (F-027, F-031, F-034, F-040;
  kober1946).
- **C-3d.** Kober's stated condition that words listed together on one tablet share a case
  (kober1946, Assumptions 4, 6, 7) holds on Linear B as a corpus fact, homogeneity 0.42
  against 0.25 by chance, and as a condition for admitting a paradigm variant admits one
  stem pair in eighteen, grammar and non-grammar alike; added to the instrument as an
  ordering key it changes nothing at the top (F-030, F-032). Three encodings of tablet
  context moved the small-corpus count by one subsample net (F-026, F-029, F-032).
- **Makes it ours:** by machine, null-tested, answer key consulted only after the ranking;
  the list condition measured as a statistic.
- **Correction, not a claim:** the reference list lacked the ethnic-adjective derivation
  Kober's triplets are made of until her paper was read; adding it moved the small-corpus
  count from 6 to 11 of 20 (F-031), and rebuilding the list from Ventris and Chadwick's
  morphology moved it to 13 (F-034). Reported as an instrument correction wherever C-3c is.
  Search 2026-09-11: DĀMOS itself carries a per-word morphological annotation of the whole
  corpus (aurora2015) that pyaegean's loader does not fetch, and UniMorph's Ancient Greek
  paradigms are already a dependency of the toolkit; no machine-readable list of Mycenaean
  alternation pairs was found. The hand-built list should be replaced by one derived from
  DĀMOS's annotation (TODO, blocked 2026-09-12: the annotation is unexported and
  unfinished for nominal forms, per Aurora 2024 and Aurora et al. 2025; a request to its
  curator is the only route).
- **Shown would need:** a computational or statistical recovery of Linear B inflectional
  alternations or grid pairs from sign patterns, scored against the known values; for
  C-3d, any prior test of within-tablet ending homogeneity on Linear B against a null.
- **Does not count as Shown:** Kober's and Ventris's hand work (Precursor, the method's
  origin); unsupervised morphology on other languages (Shown elsewhere).
- **Leads, catalogued:** kober1948, ventris_chadwick1973, packard1974, davis2026 (syllabotactics
  with a Linear B control), luo2019, snyder2010, pyaegean (`morphology.py`, unpublished).
- **Leads, not catalogued:** Ventris, *Work Notes on Minoan Language Research* (Sacconi
  1988); Chadwick 1958; Fox 2013; Goldsmith 2001 (Linguistica); Harris 1955 (successor
  variety); Knight & Yamada 1999.
- **Queries:** Kober triplets computational · automatic grid Linear B · "unsupervised
  morphology" "Linear B" · Linear B inflection statistical analysis · "combinatory analysis"
  Linear B computer · Ventris grid computer reconstruction · paradigm induction undeciphered
  syllabary.

### C-4 · Linear A has stem-and-ending structure

- **C-4a.** Linear A word types (GORILA, 988) share stems carrying two or more endings more
  often than a positional-frequency null produces: 101 against a null mean of 66.4, ratio
  1.52. No sound value is used; sign identities are (F-019).
- **C-4b.** (Stated in prose by Barber 1974, p. 212, without a null.) That ratio is at or below the low end of Greek's at the same size: 1.63 to 2.06
  when Linear B is shrunk by tablets, 1.41 to 1.70 by word types. Linear A's maximum
  alternation support sits at its null, where Greek at the same size clears its null 18
  times in 20 (tablet model) (F-022).
- **C-4c.** The result holds in the SigLA edition, which divides and reads words
  differently: ratio 1.58 (F-023).
- **C-4d.** The grid route cannot test the transferred Linear B values on Linear A at this
  size: eight bridging pairs at support two, below the pre-registered floor of ten (F-019).
  On all 146 pairs the consonant-sharing fraction is 0.103 against a null mean of 0.075, a
  ratio of 1.4 at the 85th percentile: the same direction as Packard's 7 against 3.9 on 34 hand-collected
  pairs (about 1.8), which he himself read as largely fortuitous (pp. 75 to 80, read from the
  primary 2026-09-11); not significant either way (F-019 notes). The values are neither supported nor
  contradicted by Linear A's alternations. The values' positive evidence is C-8.
- **Limit, always quoted with it:** it does not separate inflection from compound names,
  transaction terms or formula words (F-019).
- **Makes it ours:** a null, a size-matched deciphered control, and two editions.
- **Shown would need:** a statistical test of stem or affix recurrence in Linear A against a
  null or a control corpus.
- **Does not count as Shown:** by-eye identification of particular affixes (Stated).
- **Contradiction watch:** any work arguing Linear A's vocabulary is mostly names or
  unanalysable, or that it shows no morphology.
- **Leads, catalogued:** packard1974, younger_texts, thomas2020, monti2022, davis2013,
  davis2014, davis2026, salgarella2025, meissner_steele_preprint, karajgikar2021, pyaegean.
- **Leads, not catalogued:** Duhoux 1978 and later (Linear A linguistic analysis, affixes);
  Facchetti 1999–2003 (possible statistical morphology); Schrijver; Valério; Brown 1992
  (distributional sign classes).
- **Queries:** "Linear A" morphology statistical · "Linear A" suffixes prefixes quantitative
  · Duhoux linéaire A analyse affixes · Facchetti Linear A statistical morphematic ·
  "Linear A" inflection evidence · Linear A agglutinative evidence.

### C-5 · The corpus-size floor, measured

- **C-5a.** A minimum corpus size for one structural decipherment step has been measured by
  subsampling a deciphered corpus (F-022).
- **C-5b.** The number: Kober stage 1 recovers Greek grammar from Linear B in at least 16 of
  20 subsamples from about 1,875 word types when tablets are removed (about 2,300 of 5,932
  documents), and 2,750 when word types are removed: 1.9 to 2.8 times Linear A's 988. At 988,
  Greek meets the full three-part criterion in 7 of 20 (tablet model) and 0 of 10 (type
  model) (F-022); by the weaker bar Kober herself published, two sure paradigms, it passes
  in 20 of 20 (F-027). Under the current instrument (answer key rebuilt from Ventris and
  Chadwick, spelling-variant signs merged) the same sweep gives 1,250 on the three-part
  criterion and 750 on the strict top three, with 15 of 20 meeting the full criterion at
  988 (F-046): the key and the merge moved the floor by a third, no new text did.
- **Limit, always quoted with it:** it transfers to Linear A only if Minoan inflects by
  suffix at least as visibly as Greek (A-040), and even above the floor Linear A's ranking
  could not be graded, having no answer key (F-022). It is the floor of this instrument's
  three-part criterion, not of the method: Kober found the triplets from under 750 word
  types with a two-word bar (kober1946, read), and the instrument does the same at 988
  (F-027). The merge uses knowledge that exists only because Linear B is read, so the
  1,250 describes Greek with that knowledge (F-046). The plain statement must say "by
  machine", "reliably", and which instrument.
- **Makes it ours:** measured on the deciphered sister script, one method, a stated bar.
- **Shown would need:** a measured minimum corpus size, for any decipherment or structural
  step on any script, from subsampling a deciphered corpus or an equivalent learning curve.
- **Does not count as Shown:** statements that Linear A is too small (Stated). Shannon's
  unicity distance counts as Shown elsewhere only if someone derived a number for a
  syllabary of this kind; otherwise Stated.
- **Leads, catalogued:** shannon1949, braovic2024, sommerschield2023, luo2021, tamburini2025,
  raghavendra2026, rao2009, sproat2014, born2019, davis2026, packard1974.
- **Leads, not catalogued:** Barber 1974 (the "provability threshold" cited via Language
  Log); Knight & Yamada 1999 ("how much data"); Knight et al. 2006; learning-curve
  results in computational decipherment.
- **Queries:** "minimum corpus size" decipherment · unicity distance undeciphered script ·
  Barber provability threshold decipherment · how much text decipherment Linear A ·
  decipherment data size learning curve · subsampling deciphered corpus decipherment.
- **Survey note:** state-of-the-art.md already records "No paper quantifies a minimum corpus
  size for decipherment" from the 2026-09-10 survey. That was not a targeted search; this
  protocol is.

### C-6 · Linear B restoration sits near a floor

- **C-6a.** On Knossos A&B, a 15-line lexicon lookup scores 31.5% top-1 against the published
  BiRNN's 30.3%, and a sign-frequency prior reaches 58.4% top-20 against the published 66.2%
  (F-002). On series D, frequency prior top-20 63.2% against published 78–80% (F-001).
- **C-6b.** Accuracy collapses on unseen word types: lexicon top-1 82.8% seen, 3.0% unseen
  (F-002); 64% of test items are unseen types.
- **Makes it ours:** the frequency floor, the lexicon lookup, baselines on A&B (where none
  was published), and the seen/unseen stratification. Not the near-match itself on series
  D: the JOCCH 2023 paper's own Table 2 reports a bidirectional 3-gram at 44.64% top-1
  against its BRNN's 48.34% (papavassileiou2023), which F-001 did not know when written.
- **Shown would need:** a non-neural baseline, frequency floor or seen/unseen split reported
  for Linear B restoration.
- **Leads, catalogued:** papavassiliou2020, papavassileiou2023, papavassileiou2024,
  zenodo7404653, sommerschield2023, braovic2024, assael2022.
- **Queries:** Linear B restoration baseline · Linear B infilling n-gram baseline ·
  Papavassileiou restoration citing works · Mycenaean text restoration evaluation.
- **Outreach:** a draft exists locally and is held; contact-the-claimant rule applies.

### C-8 · The transferred values have internal positive evidence, for a few signs

- **C-8a.** Under a null that permutes sign labels within frequency bands at every
  position, Linear A words match Knossos place names in Packard's 3= class beyond the
  99th percentile on both editions (GORILA 6 against a 99th percentile of 4 to 5; SigLA 5
  against 3), and three wrong lexicons of the same script and size (Knossos personal
  names, Pylos toponyms, the toponyms reversed) do not clear anywhere (F-041).
- **Limit, always quoted with it:** five Linear A words, three place names, thirteen sign
  labels, all in Meißner and Steele's demonstrably shared set; the Pylos control sits at
  the 91st to 98th percentile without clearing.
- **Makes it ours:** a null of 400 draws that varies the thing under test at every
  position, two editions, two bandings, three wrong controls; Packard's Table 14 used
  nine hand-built rotations, one edition and no wrong lexicon.
- **Shown would need:** a published test of Linear A place-name matches under the
  transferred values against a permutation null with a wrong-lexicon control.
- **Leads, catalogued:** packard1974, ventris_chadwick1973, meissner_steele_preprint.
- **Leads, catalogued (search 2026-09-12):** raison_pope1978. **Not catalogued:** Younger's
  place-name list; Duhoux on Linear A toponyms; Schoep 2002 on the Hagia Triada place names.
- **Queries:** "Linear A" toponyms Linear B place names statistical · Packard 1974 Table 14
  replication · Minoan place names Phaistos su-ki-ri-ta.

### C-7 · Measurements on di Mino 2026

- **C-7a.** In IO Za 2, 14 of 22 distinct signs and 22 of 33 sign positions (67%) rest on
  values Meißner and Steele list as demonstrably shared (F-010).
- **C-7b.** On KN Zc 7 GORILA writes 5 word-groups and di Mino reads 7; same at PE Zb 3
  (F-010).
- **Shown would need:** a published measurement of di Mino's sign-value security or
  segmentation.
- **Leads, catalogued:** dimino2026, meissner_steele_preprint.
- **Leads, not catalogued:** Mair 2026 (Language Log); Adkins 2026 (The Conversation); the
  HN thread (item 48600107); any 2026 response by Rendsburg or Aegeanists.
- **Queries:** di Mino Linear A Semitic response · "Ya Diktu" review · Tinitic Minoan critique.

## Atom status

First search completed 2026-09-11 (five Sonnet agents, one per claim cluster; graded by the
session model). Best earlier grade ignores Contradicted rows, which are flagged in status.

| atom | best earlier grade | what is ours | status |
|---|---|---|---|
| C-1a | Precursor | Wrong real languages scored on the deciphered sister script | closed, stop rule |
| C-1b | Precursor | Real lexicons against synthetic twins, for every language | closed, stop rule |
| C-1c | Precursor | Greek measured on Linear A under the transferred values | closed, stop rule |
| C-2a | Precursor | Laryngeal ablation on Linear A; Packard 1974 p. 90 states the consonant-only inflation for name matching | closed, stop rule |
| C-2b | Shown elsewhere | One language, two dictionary formats, on Linear A | closed, stop rule |
| C-3a | Precursor | By machine, against a null, answer key consulted after ranking | closed, stop rule |
| C-3b | Precursor | Grid pairs by machine against a positional null | closed, stop rule |
| C-3c | Precursor | The instrument at her corpus size, against her bar, on Greek text | closed; kober1946 read |
| C-3d | Precursor | Her list condition as a statistic with a null; three context encodings calibrated | closed, stop rule (search 2026-09-11: no statistical test of co-listed-word ending agreement found on Linear B or on Ugaritic, Cypriot or Maya material; Chadwick 1958, Fox 2013, Robinson 2002 restate her by hand; Pope 1975/1999 unreached) |
| C-4a | Precursor | A null, and two editions | **open**: facchetti1999 (the statistical paper, pp. 1 to 11) unread; its companion (pp. 121 to 136) read 2026-09-11 and graded Stated |
| C-4b | Stated | Greek at matched size as the comparison, with a null and twenty subsamples; Barber 1974 p. 212 stated the comparison in prose | closed, stop rule; regraded 2026-09-12 from Not found on reading Barber |
| C-4c | Not found | A structural result checked across editions | closed, stop rule |
| C-4d | Precursor | A positional null, and a size-matched Linear B control showing why alternations cannot decide at this size | closed on the primary (Packard pp. 73 to 80 and Tables 13, 14 read from the full PDF 2026-09-12) |
| C-5a | Shown elsewhere | Subsampling a deciphered corpus, one method, a stated bar | closed; Barber 1974 read 2026-09-12: theoretical unicity numbers, practical minimum "undetermined", the measurement she asks for on p. 237 is ours |
| C-5b | Precursor | The number, for this instrument's criterion | closed; kober1946 read (under 750 word types, two-word bar) |
| C-6a | Precursor | Frequency floor, lexicon lookup, A&B baselines | closed, stop rule |
| C-6b | Shown elsewhere | The seen/unseen split on Linear B | closed, stop rule |
| C-7a | Stated | The count | closed, stop rule |
| C-7b | Not found | The segmentation comparison | closed, stop rule |
| C-8a | Precursor | A permutation null at every position, two editions, three wrong controls | closed, stop rule (search 2026-09-12: Raison and Pope 1978 read place names by eye, seen through a 1983 review; Ventris and Chadwick's overlap caution noted; no permutation or wrong-lexicon test found) |

## Open leads

Each blocks one status above. Reading it may change a grade; nothing else in the Ledger
depends on it. Fetched copies go to `~/.cache/linear-a-b/reference/` with their terms,
never into git.

| lead | decides | how to get it |
|---|---|---|
| Facchetti 1999, "Statistical data and morphematic elements in Linear A", *Kadmos* 38:1–11 | C-4a: whether anyone tested Linear A morphology statistically before. Its companion paper's corrigenda show it carried percentages | De Gruyter, paywalled, DOI 10.1515/kadm.1999.38.1-2.1. The companion (pp. 121–136) is read |
| Davis 2026, *The Undeciphered Aegean Scripts*, ch. 11 | C-4b: confirms it compares syllabotactics, not morphological strength | Library |

## Relation to earlier work

Generated from the Ledger by `scripts/prior_art.py --write-view`; do not edit by hand.

<!-- view:start -->
**Built on: we knew the work and used it in the design or reading of the finding.** 13 rows.

| atom | work | their grade | ours |
|---|---|---|---|
| C-1a | packard1974 | Precursor | extends |
| C-1a | raghavendra2026 | Shown elsewhere | transfers |
| C-1b | packard1974 | Precursor | complements |
| C-1c | packard1974 | Precursor | confirms |
| C-2a | gordon1966 | Stated | measures |
| C-2a | packard1974 | Precursor | confirms |
| C-3b | kober1948 | Precursor | replicates |
| C-3b | ventris_chadwick1973 | Precursor | replicates |
| C-4a | monti2022 | Stated | measures |
| C-4a | thomas2020 | Stated | measures |
| C-6a | papavassileiou2023 | Precursor | extends |
| C-8a | packard1974 | Precursor | extends |
| C-8a | ventris_chadwick1973 | Stated | complements |

**Known, not used: in our survey before the finding, not drawn on by it.** 28 rows.

| atom | work | their grade | ours |
|---|---|---|---|
| C-1a | adkins2026 | Stated | measures |
| C-1a | barber1974 | Stated | measures |
| C-1a | hauer2016 | Shown elsewhere | is qualified by |
| C-1a | luo2021 | Shown elsewhere | confirms |
| C-1a | nepal2024 | Precursor | extends |
| C-1a | peronocacciafoco_programme | Precursor | extends |
| C-1c | owens1999 | Precursor | measures |
| C-1c | steele2017 | Stated | measures |
| C-2a | hauer2016 | Shown elsewhere | transfers |
| C-2a | peronocacciafoco_programme | Stated | measures |
| C-3a | kober1946 | Precursor | replicates |
| C-3a | snyder2010 | Shown elsewhere | transfers |
| C-4a | barber1974 | Stated | measures |
| C-4a | facchetti1999 | Stated | unresolved |
| C-4a | facchetti1999b | Stated | measures |
| C-4a | packard1974 | Precursor | extends |
| C-4a | salgarella2025 | Stated | measures |
| C-4b | barber1974 | Stated | measures |
| C-4d | packard1974 | Precursor | confirms |
| C-5a | barber1974 | Shown elsewhere | measures |
| C-5a | braovic2024 | Stated | measures |
| C-5a | knight_yamada1999 | Shown elsewhere | transfers |
| C-5a | shannon1949 | Stated | measures |
| C-5b | kober1946 | Precursor | is qualified by |
| C-6a | assael2022 | Shown elsewhere | transfers |
| C-6b | assael2022 | Shown elsewhere | transfers |
| C-7a | adkins2026 | Stated | measures |
| C-7a | hn48600107 | Stated | measures |

**Reached independently: first mentioned in the repo after the finding.** 12 rows.

| atom | work | their grade | ours |
|---|---|---|---|
| C-1a | ringe1992 | Shown elsewhere | transfers |
| C-1c | wyatt1976 | Stated | confirms |
| C-2b | kessler2001 | Shown elsewhere | transfers |
| C-3a | goldsmith2001 | Shown elsewhere | transfers |
| C-3b | kim_snyder2013 | Shown elsewhere | transfers |
| C-4a | duhoux1978 | Stated | measures |
| C-5a | ravi_knight2008 | Shown elsewhere | transfers |
| C-5a | taylor1976 | Stated | measures |
| C-5a | wyatt1976 | Stated | measures |
| C-6a | fetaya2020 | Shown elsewhere | transfers |
| C-7a | braindetox2026 | Stated | measures |
| C-8a | raison_pope1978 | Stated | measures |
<!-- view:end -->

## Ledger

One row per (atom, work). Grades, relations and awareness from the tables above only.

| atom | work | grade | relation | awareness | evidence | V |
|---|---|---|---|---|---|---|
| C-1a | packard1974 | Precursor | extends | built on | Nine fictitious decipherments rotate Linear B values within frequency bands (p. 74) and estimate chance matches (p. 73); scored on Linear A only, no wrong real language | Y |
| C-1a | peronocacciafoco_programme | Precursor | extends | known | Several real languages tried on Linear A, "inconclusive" by their own account; no deciphered-script control | Y |
| C-1a | nepal2024 | Precursor | extends | known | "Some possible word matches" for each of five languages on Linear A; no known-answer control | P |
| C-1a | hauer2016 | Shown elsewhere | is qualified by | known | Character n-grams identify the language of known texts at 97% over 380 languages | Y |
| C-1a | luo2021 | Shown elsewhere | confirms | known | Iberian against Basque, "no strong evidence", at about Linear A's scale | Y |
| C-1a | raghavendra2026 | Shown elsewhere | transfers | built on | Indus dictionary matching falls from in-sample to grouped held-out coverage | Y |
| C-1a | ringe1992 | Shown elsewhere | transfers | independent | Probability of chance lexical matches between unrelated word lists | P |
| C-1a | adkins2026 | Stated | measures | known | "Statistical pattern matching can't manufacture meaning out of nothing. It needs an anchor" | Y |
| C-1b | packard1974 | Precursor | complements | built on | Weights each class of evidence by how well it beats random values, and dismisses Pylos matches as "nearly worthless" (p. 91); we add wrong real languages | Y |
| C-1c | packard1974 | Precursor | confirms | built on | Linear B values match Knossos names more than any random set: "at least some of the Linear B phonetic values are valid for Linear A" (p. 93) | Y |
| C-1c | wyatt1976 | Stated | confirms | independent | Review of Packard: "significantly more matches if Linear B values are assigned than with any of the random decipherments. I find his results convincing" | Y |
| C-1c | owens1999 | Precursor | measures | known | Reads apparently Greek or Indo-European words in Linear A under Linear B values, by eye | S |
| C-1c | steele2017 | Stated | complements | known | Projecting Linear B values onto Linear A is legitimate in principle, and reading Linear A with them leaves its language unknown (pp. 93-110); the word circular is this repo's | Y |
| C-2a | hauer2016 | Shown elsewhere | transfers | known | Hebrew tops their Voynich ranking; hedged as an artefact of anagramming's combinatorial power | Y |
| C-2a | peronocacciafoco_programme | Stated | measures | known | Semitic has "very little in common" with the libation-table words | Y |
| C-2a | gordon1966 | Stated | measures | built on | Reviewers: his matches are drawn across several Semitic languages, not one | S |
| C-2a | packard1974 | Precursor | confirms | built on | "If vowels are ignored, the random decipherments produce hundreds of matches ... The Linear B values produce more but not by an impressive margin" (p. 90): the consonant-only channel inflates matches for wrong values | Y |
| C-2b | kessler2001 | Shown elsewhere | transfers | independent | Word-list and procedure choices change significance in lexical comparison | P |
| C-3a | kober1946 | Precursor | replicates | known | Three cases for two noun types from under 750 sign groups, seven stated assumptions, bar "two or more" (fn. 7); no count against chance | V |
| C-3a | goldsmith2001 | Shown elsewhere | transfers | independent | Unsupervised stem and suffix induction by minimum description length | Y |
| C-3a | snyder2010 | Shown elsewhere | transfers | known | Prefix-stem-suffix model recovers Ugaritic given Hebrew | Y |
| C-3b | kober1948 | Precursor | replicates | built on | Tentative ten-sign grid without values, AJA 52:97–98 | P |
| C-3b | ventris_chadwick1973 | Precursor | replicates | built on | Full grid by combinatory analysis, checked by reading place names | Y |
| C-3b | kim_snyder2013 | Shown elsewhere | transfers | independent | Consonant or vowel predicted from distribution at 99% over 503 languages, with cross-language priors | Y |
| C-4a | packard1974 | Precursor | extends | known | Appendix A: Linear A alternation pairs chosen "mechanically, with no attempt to segregate the plausible from the merely coincidental" | Y |
| C-4a | thomas2020 | Stated | measures | built on | Root i-*301 with four prefixes and seven suffixes, "necessarily tentative" | Y |
| C-4a | monti2022 | Stated | measures | built on | a-/ja- read as an article-like prefix on the verbal root | P |
| C-4a | duhoux1978 | Stated | measures | independent | Linear A uses prefixes and suffixes heavily in word formation (secondary paraphrase) | S |
| C-4a | facchetti1999 | Stated | unresolved | known | Title only: "Statistical data and morphematic elements in Linear A"; content unread. The survey named a Facchetti 1999, for the Tyrsenian hypothesis, not this paper | S |
| C-4a | facchetti1999b | Stated | measures | known | Formula variants read by slot across about thirty inscriptions (pp. 128 to 135): ja-/a- "attested in securely connected context" (n. 73), -si/-ti, -ja/-e; no count against chance | V |
| C-4a | barber1974 | Stated | measures | known | "Linear A ... shows no systematic and almost no suspectable inflection" (p. 212), from internal analysis, no null | V |
| C-4b | barber1974 | Stated | measures | known | "although a Linear B corpus of not much larger size gives ample evidence for suffixation" (p. 212): the size-matched comparison stated in prose, not measured | V |
| C-1a | barber1974 | Stated | measures | known | "Vocabulary ... is a very risky indication of genetic relation, especially in a small sample and even more in a sample of unknown contents" (p. 209) | V |
| C-4a | salgarella2025 | Stated | measures | known | Synthesis: agglutinative-looking, prefixing and suffixing | P |
| C-4d | packard1974 | Precursor | confirms | known | Table 13: final alternations sharing two signs, 7 under Linear B values against a random mean of 3.9 (ratio 1.8, his weight 2); three-sign classes 3 against 0.33 on a few pairs; his strong evidence is toponyms (Table 14) | Y |
| C-8a | packard1974 | Precursor | extends | built on | Table 14: 13 place-name matches under Linear B values against about 3 by his nine rotations; his rotation scheme reproduced gives 0.2 to 0.7, not 3 (F-041); no wrong lexicon, one edition | Y |
| C-8a | ventris_chadwick1973 | Stated | complements | built on | Names the lexicon source F-041 uses; states by eye that only one or two full Linear A words under Linear B signs recur in Linear B | Y |
| C-8a | raison_pope1978 | Stated | measures | independent | By-eye toponym and personal-name readings under the transferred values; no count against chance, no wrong lexicon; seen through a 1983 review | P |
| C-5a | knight_yamada1999 | Shown elsewhere | transfers | known | Kana decipherment accuracy against text size: 5 sentences 48.5%, 100 sentences 97.5% | Y |
| C-5a | ravi_knight2008 | Shown elsewhere | transfers | independent | Cipher decipherment error against cipher length, 2 to 256 characters | Y |
| C-5a | barber1974 | Shown elsewhere | measures | known | Unicity about 225 signs for a 100-sign syllabary treated as a substitution cipher (p. 204); "the practical minimum is much higher, and higher by an as yet undetermined amount" (p. 238); calls for "statistical analysis of different-sized language samples" (p. 237) | V |
| C-5a | shannon1949 | Stated | measures | known | Unicity distance: the text length past which a cipher's solution is unique | Y |
| C-5a | taylor1976 | Stated | measures | independent | Review of Packard: "In view of the paucity of Linear A material an independent decipherment, such as was possible with Linear B, is unlikely" | Y |
| C-5a | wyatt1976 | Stated | measures | independent | Classification needs "a large corpus", a condition that does not apply "with Linear A" | Y |
| C-5a | braovic2024 | Stated | measures | known | Small dataset size is a challenge that "might be impossible" to overcome | Y |
| C-5b | kober1946 | Precursor | is qualified by | known | "less than 750 in all" different sign groups; three cases set up; "there is not enough material to work with" (p. 276) | V |
| C-6a | papavassileiou2023 | Precursor | extends | built on | Their Table 2: bidirectional 3-gram top-1 44.64% against their BRNN's 48.34% on series D | Y |
| C-6a | assael2022 | Shown elsewhere | transfers | known | Ithaca reports Pythia and a human onomastics baseline | Y |
| C-6a | fetaya2020 | Shown elsewhere | transfers | independent | Akkadian restoration RNN reported against a 2-gram baseline | Y |
| C-6b | assael2022 | Shown elsewhere | transfers | known | Per-word accuracy plotted against training frequency, not a seen/unseen split | Y |
| C-7a | adkins2026 | Stated | measures | known | Argues AI readings need an anchor; no count of secured values | Y |
| C-7a | hn48600107 | Stated | measures | known | "Keep only W-J and assume *301 starts with N, then you get a claimed Semitic root" | Y |
| C-7a | braindetox2026 | Stated | measures | independent | Methodology unpublished; "matching one-fifth of one word" is not a demonstration | Y |

## Decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| Claims are split into atoms and graded per atom | 2026-09-11 | A work that states C-4a by eye says nothing about C-4b or C-4c; one grade per claim would let a partial precedent erase or inflate the whole | One novelty verdict per claim |
| C-1c is stated as a measurement with no cause | 2026-09-11 | F-008 attributed it to transferred Greek values; F-014's fixed-null decomposition withdrew the related sign-set explanation | Keeping "because the values are Greek" in the plain statement |
| C-4 carries C-4b in the plain statement | 2026-09-11 | F-022 corrected "as strongly as Greek" to "at or below the low end"; the uncorrected sentence had already gone into a draft message | Quoting the type-model comparison alone |
| C-4d regraded Contradicted to Precursor | 2026-09-11 | Packard pp. 6, 72-109 and Appendix D read (read in full; archive.org text as a check). His alternation test is ours with rotated values; his 7 against 3.9 is the "2:1", and he reads it as weak, as F-019 does. The snippet had dropped his conclusion | Keeping the snippet's framing |
| C-6 and C-7 added to the user's five | 2026-09-11 | Both are current, independent of the Kober and etymological lines, and cheap to check; C-6 is the result with an outreach draft already written | Leaving them to be rediscovered |
