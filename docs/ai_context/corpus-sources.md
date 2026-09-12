# Corpus Sources — Linear A and Linear B

Files: `.venv/` (pyaegean 0.59.0), `~/.cache/pyaegean/` (fetched corpora, not in repo), `data/` (local exports)

See also: [state-of-the-art.md](state-of-the-art.md) for what has been published against these corpora and what the field requires of a claim.

All rows verified live on 2026-09-10 unless marked otherwise. Re-verify before trusting a licence claim in anything published.

## Source landscape

| Source | Script | Holds | Licence / terms | Access route | Status |
|---|---|---|---|---|---|
| DĀMOS (damos.hf.uio.no) | B | All published Mycenaean docs; transliteration + epigraphic/morphological annotation | Content CC BY-NC-SA 4.0; software GPL-3.0 | `aegean.load("damos")` | **Canonical for B** |
| GORILA (via pyaegean) | A | GORILA transcription, bundled in the wheel. **Not the edition itself**: chain is GORILA → George Douros's spreadsheet → mwenge/lineara.xyz (volunteer, + Younger commentary) → Linear A Research Workbench → pyaegean | `Corpus.provenance.license` asserts Apache-2.0 on the corpus JSON; mwenge repo states **no licence**; GORILA volumes + facsimiles © École française d'Athènes, not redistributed | `aegean.load("lineara")` | **Canonical for A**, with the caveat that it is edition-derived |
| SigLA (sigla.phis.me) | A | Second Linear A edition, sign-level palaeographic focus (Salgarella & Castellan) | **CC BY-NC-SA 4.0** — "Dataset and drawings", verified on site 2026-09-10 | `aegean.load("sigla")` | Cross-check against GORILA |
| pyaegean (PyPI 0.59.0) | A, B, Cypriot, Cypro-Minoan | Toolkit + typed model + exports; cross-script phonetic comparison | Apache-2.0 (code only — data keeps its own licence) | `pip install "pyaegean[all]"` | **Primary access layer** |
| j-luo93/NeuroDecipher | B | `linear_b-greek.cog` — 919 Linear B↔Greek pairs (general lexicon, not only names; Greek diacritics stripped) | **No LICENSE file** (GitHub API `license: null`, checked 2026-09-10). Pairs were extracted from Tselentis, *Linear B Lexicon* (2011), **CC BY-ND 3.0** — a derivative of an ND work | GitHub clone | Benchmark only. Reused byte-identical by Tamburini 2025 (`ftamburin/CSA_OptMatcher`, GPL-3.0). Regenerate from DĀMOS before redistributing anything |
| Papavassiliou/Owens/Kosmopoulos, LREC 2020 | B | Mycenaean word+ideogram "sequences" from printed editions (KT, Ruipérez & Melena, Hooker, V&C); 19-sheet spreadsheet | Unstated | Full corpus **not public**; paper says ~⅓ complete | Only the series D derivative is released (next row). Ask the Patras authors for the rest |
| Papavassileiou/Kosmopoulos/Owens, Zenodo 7404653 | B | `Samples.txt` (103 kB): 2,565 KN series D sequences = 513 real + 725 augmented + 1,327 duplicates, for BiRNN infilling (JOCCH 2023) | **CC BY 4.0**, verified 2026-09-10 | zenodo.org/record/7404653 | The one public LB restoration baseline; reproduce it from DĀMOS directly rather than train on the augmented file |
| LiBER v.2 (liber.cnr.it; Del Freo, Di Filippo, Rougemont, CNR Edizioni 2024) | B | 5,638 docs, all sites except Ayios Vasileios and Thebes; transcriptions, apparatus, photos, RTI refs, WebGIS | Texts reusable per academic practice; **images personal/non-profit only, Greek Law 3028/2002** | Browse UI | No bulk export, no API |
| InsiderPhD/Linear-B-Dataset | B | Scraped CSVs from minoan.deaditerranean.com | **None stated** | GitHub | Unofficial; prototype only |
| CaLiBRA (Cambridge; Judson, Meißner, Thompson) | B | B&W photographs, Pylos tablets (1969 Seraphis set, © Univ. Cincinnati); joins and hand attributions | No download terms stated (site read 2026-09-10) | Search UI | Browse-only |
| Ashmolean / Sir Arthur Evans Archive | B | ~40 Knossos tablets, RTI (2012) | No licence stated | RTIViewer by URL | Browse-only |
| pa-i-to Epigraphic Project (paitoproject.it; Greco, Flouda, Notti) | B | ~90 Knossos tablets naming pa-i-to; 3D laser 0.034–0.118 mm + RTI | View-only, non-profit, reproduction prohibited | Web viewer | Browse-only |
| Pylos Tablets Digital Project (Nakassis, Pluta) | B | RTI, structured-light 3D, XRF of Pylos docs → *Palace of Nestor IV* (2025) | Print publication; no 3D or RTI files released | — | Not obtainable |
| INSCRIBE 3D models (Ferrara et al. 2023; Lastilla, Ravanelli, Ferrara 2019) | A, CH | 3D models of Cretan Hieroglyphic and Linear A objects, online | Unverified | INVESTIGATE | Not verified |
| Greco/Flouda/Notti 2023; Hogan 2022/23 | A, B | Listed as digital resources by Braović et al. 2024 (Comp. Ling. 50(2)); contents unknown | Unverified | INVESTIGATE | Not verified |

## Corpus facts (measured via pyaegean, not cited)

| Corpus | Script | Docs | Tokens | Words | Sign inventory |
|---|---|---|---|---|---|
| DĀMOS | B | 5,932 | 54,476 | 14,491 | 211 |
| GORILA | A | 1,721 | 6,406 | 1,381 | 342 |
| SigLA | A | 802 | 2,616 | 1,895 | — |

- DĀMOS data version: `damos-corpus-v2@2026-06-11`.
- **Linear A is ~6.4k tokens.** An order of magnitude smaller than Linear B, which is itself tiny. This is the single hardest constraint on the whole project and rules out most data-hungry methods outright.
- **The two Linear A chains label some signs differently.** GORILA's chain writes `*56`
  and `*79` where SigLA's writes `PA₃` and `ZU` (AB56, AB79); the same sign counts as two
  labels in any cross-edition comparison until reconciled (F-045). The chains also draw
  the word-versus-logogram boundary differently, which is most of what F-023 counted as
  "line coverage differs". And the ten ARKH tablets are sited at Arkalochori in one chain
  and Arkhanes in the other; the identifiers match, the site metadata does not.
- **The loaded chain is not 1985-only.** Checked 2026-09-12 against the 2024 supplement's Concordance générale (transcribed locally): 89 of its 107 documents are already loaded under matching identifiers and 18 are absent, carrying 4 complete word types (F-047). The earlier index-only check gave 79 of 114 references (Petras, Syme, Kythera, Miletos, Thera, Iouktas, Khania above 91, and more), and 20 of its 24 complete word types are already word types here. The supplement adds a few dozen documents and a handful of word types to this corpus, not 107 documents. Identifier forms differ for some (`GO 2a` is loaded as `GO2R`/`GO2V`; `KN Zb 27`, `PE 6`, `SA We 3` are not loaded). F-035's item 2 carries the correction.
- **The Anetaki ring has no published transliteration yet.** Kanta, Nakassis, Palaima and Perna 2025 (Ariadne Suppl. 5, CC BY-NC-SA 4.0) is a narrative overview naming individual signs; the sign-by-sign edition of KN Zg 57 (the ring, about 119 signs) and KN Zg 58 (the handle, an accounting text) is reserved for *Anetaki II*, forthcoming. Nothing from it can enter a word-type set (checked 2026-09-12). The corpus's one known addition stays outside it until that volume appears.
- **The supplement prints its texts as glyph copies, not Latin values.** Every entry gives a normalised copy and a tabular copy in a Linear A font with French apparatus; only the Index des signes carries the text as GORILA sign numbers. So the index is the text source and the entry pages are context (site, findspot, date, museum, apparatus, earlier publication). All of it is transcribed locally (not committed): `index-des-signes.jsonl`, `concordance-generale.jsonl` and the three other concordances, `concordance-douteuses.jsonl`, `introduction.md`, `inscriptions-tablets.jsonl` and `inscriptions-other.jsonl` (entries with apparatus, no readings), `ab-number-to-corpus-label.json`, `extra-word-types.jsonl`. Never commit any of it.
- **The edition's own count differs from the loaded count.** GORILA + *RILA Supplément 1* (Del Freo & Zurbach 2024, Études Crétoises 21.6; finds 1985–2023, +107 docs, +427 signs) = **1,534 inscriptions / 7,574 signs**, plus a *dubitanda* section. pyaegean's 1,721 "documents" is mwenge's tagged-entry count over the pre-supplement GORILA (faces/sides split, Younger's readings), and its 6,406 tokens are word-level, not signs. Quote the edition figure in anything academic; the 2024 supplement material is **not** in the loaded corpus.
- SigLA and GORILA both report `script_id="lineara"` but are different editions with different document counts. They are not interchangeable — decide which is authoritative per task and record it.
- Read `Corpus.provenance` for source/licence/citation/`data_version` rather than hardcoding any of them.

## Cross-script relationship

- Linear B was adapted from Linear A. Shared graphic inventory is the reason comparative work is possible at all, and the reason both scripts belong in one repo.
- Naive overlap of sign **labels** between the two loaded inventories: **56 shared**, 155 B-only, 286 A-only.
- **That 56 is a transliteration-label match, not a scholarly homomorphy judgement.** Linear A signs are conventionally transliterated using Linear B sound values for the signs judged graphically equivalent, so this measure partly reflects that convention rather than independent evidence. Do not quote it as "the sign correspondence figure". See Open questions.
- Three different "shared" counts exist and none is the palaeographic answer. Measured 2026-09-10 on the loaded inventory: **81** signs carry `attrs["sharedWithLinearB"]`; **50** carry a `phonetic` value; **56** labels overlap naively with the B inventory; pyaegean's `analysis.procrustes` docstring works from **53** "AB chart-shared by transliteration value". Record which basis you used whenever you quote one.
- pyaegean's own leave-one-out Procrustes test (`aegean/analysis/procrustes.py` docstring, run 2026-07-11) found **no recoverable A→B sign correspondence from distributional embeddings at this corpus scale**: top-1 recovery 0.000, top-5 0.094 vs chance 0.068, median rank 26/73, while self-alignment recovers 90.1%. Treat it as a measured negative baseline for any distribution-only cross-script method. Evidence JSON is in the pyaegean source repo, not the wheel.
- `Sign` carries `label`, `glyph`, `codepoint`, `phonetic`, `script_id`, `attrs` — the join key for cross-script work.

## Data model contract

`Corpus` → `Document` → `Token` → `Sign` (pyaegean `aegean.core`), identical across scripts:

| Object | Fields |
|---|---|
| `Document` | `id, script_id, tokens, lines, glyphs, transcription, translations, meta, source_text` |
| `DocumentMeta` | `site, support, scribe, findspot, period, name, images, notes` |
| `Token` | `text, kind, signs, glyphs, line_no, position, status, alt, annotations, alignment, form_state` |
| `Sign` | `label, glyph, codepoint, phonetic, script_id, attrs` |

- One model across both scripts is what makes comparative code cheap. Don't fork per-script structures.
- `DocumentMeta.scribe` is DĀMOS-curated scribal hand (B), `findspot` the find context, `support` the object class.
- `Token.status` / `Token.alt` carry reading confidence and alternative readings. **Filter on these before any training run** — damaged and conjectural readings are in the corpus by design.
- **`Document.translations` on Linear A is a token-aligned gloss layer, and it is not GORILA.** Measured 2026-09-10: 1,711 of 1,721 docs carry it, but it is mostly a passthrough of the transliteration; only **344 docs carry an actual gloss**, drawn from **72 distinct strings**. Composition: commodity logograms (`olive oil` 165, `grain` 104, `cyperus` 85, `figs` 75, `wine` 67), transaction terms in quotes (`"total"` 37, `"owed"` 16, `"assessment"?` 10), and a residue of ~10 contested word glosses on the libation formula (`gives`, `this dedication`, `requesting`, `a favour`, `divine`, `name?`). GORILA is a transcription edition with no translations; the field is a mwenge `parityFields` mirror (`manifest.json`, `sourceCommit 568f452`), tracing to Younger's commentary, which itself encodes tier-2 proposals — `gives` is Duhoux 1992, 80 / Davis 2013; `requesting … divine favour` is Davis 2013 verbatim; `dedication` is Finkelberg 1993, 54–55. **Consequence: quoting a `translations` value as "the reading" silently cites a contested proposal as if it were the edition.** Separate the logogram/transaction glosses (value-free, safe) from the formula glosses (tier 3 by proxy) before using either.

## Unicode mapping rules

Block range ≠ assigned range. Verified against `unicodedata` 16.0.0:

| Block | Script | Block range | Actually assigned | Count |
|---|---|---|---|---|
| Linear B Syllabary | B | U+10000–U+1007F | U+10000–U+1005D | 88 |
| Linear B Ideograms | B | U+10080–U+100FF | U+10080–U+100FA | 123 |
| Aegean Numbers | A + B | U+10100–U+1013F | U+10100–U+1013F | 57 |
| Linear A | A | U+10600–U+1077F | INVESTIGATE — not yet verified locally | — |

- **Aegean Numbers is shared by both scripts and is not optional.** It holds `AEGEAN WORD SEPARATOR LINE` (U+10100) plus numeric and metrological signs. Both corpora are administrative accounts; omitting this block loses the quantities, which is most of what the documents are *for*.
- Transliteration → codepoint goes through `Sign.codepoint` / `Sign.phonetic`. Don't hand-roll a table.
- B sign inventory is 211 vs. 268 assigned B codepoints — the inventory is what DĀMOS attests, not what Unicode encodes.
- All blocks are astral-plane. Check any regex/tokeniser is not operating on UTF-16 surrogate halves.

## Decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| One repo for both scripts | 2026-09-10 | Shared sign inventory, one toolkit, one data model; the comparative question is the research question | Separate repos — would duplicate the corpus/licence/Unicode layer and put the interesting work across a repo boundary |
| DĀMOS canonical for B; GORILA canonical for A | 2026-09-10 | Both are the standard published editions and both load through one API | Hand-parsing EpiDoc XML, or scraping either site |
| SigLA kept as cross-check, not primary | 2026-09-10 | Different doc count and edition basis from GORILA; useful for disagreement analysis | Merging A editions into one corpus, which would hide edition-level disagreement |
| InsiderPhD CSV demoted to prototype-only | 2026-09-10 | No licence stated, 2 commits, scraped from a secondary site | Using it as the working corpus because it is fastest to `read_csv` |
| Text-first, images deferred | 2026-09-10 | Every image archive is browse-only with restrictive terms | Starting with computer vision on tablet photos |
| ~~No `git init` for now~~ → **git initialised** | 2026-09-10 (reversed same day) | Reversed once real code started accumulating and an unattended multi-step build began: `.backups/` does not scale to iterative code work, and an overnight run needs a reviewable diff. Committing publishes nothing | Staying on manual snapshots |
| NeuroDecipher's 919-pair LB↔Greek set is a benchmark to compare against, never training or published data | 2026-09-10 | No licence file; derived from Tselentis's CC BY-ND lexicon, so redistributing it or a close derivative breaks that licence. See [state-of-the-art.md](state-of-the-art.md) Decisions | Reusing it as the project's parallel corpus |

## Invariants

- **DĀMOS is NonCommercial (CC BY-NC-SA 4.0).** Commercial use, or a derivative under a non-ShareAlike licence, breaks the terms. Consequence: unpublishable results and a licence conversation with UiO.
- **Never commit fetched corpus data into this repo.** pyaegean fetches rather than bundles deliberately. Committing redistributes licensed content under this repo's terms.
- **Anything derived from a corpus inherits its licence.** Extracted sequences, masked datasets, split manifests and model artifacts are derivatives of CC BY-NC-SA content, so they live in `~/.cache/linear-a-b/` (override `LINEARB_RESTORE_CACHE`), never in `data/`, and are gitignored either way. Safe to commit: code, aggregate metrics, counts-by-rule, vocabulary sizes, per-subseries document counts. Not safe: token lists, reconstructed text. See `data/README.md`.
- **The repository's own licences** are in `LICENSE.md` at the root: code MIT, everything else CC BY-SA 4.0, results included: the corpora's NC-SA terms reach copies and adaptations of their text, not measurements about them, and no text is stored here. Decided 2026-09-12. One stated exception (added 2026-09-12 after an outside review): the value-transfer test stores 54 published place-name readings (33 Knossos, 21 Pylos, dropped entries included), 32 Knossos personal-name sign sequences and the 10 Linear A sign sequences that matched, so the test can be checked; LICENSE.md names the files and `tests/test_word_forms.py` pins both the boundary and the counts. Corrected the same day after a second review found the first count missed the matched Linear A words. LICENSE.md describes the GORILA chain's licence as open, matching the Open questions section below; keep the two in step.
- **Cite DĀMOS.** Aurora, F. (2015), *Procedia — Social and Behavioral Sciences* 198, 21–31. Available from `Corpus.cite()`.
- **LiBER images are personal/non-profit only** under Greek Law 3028/2002 — heritage law, not merely licensing.
- **Never treat Linear A transliterations as evidence about the Minoan language.** They are Linear B sound values applied by convention to graphically similar signs. Using them as input and then concluding something about Minoan phonology is circular. Consequence: the single most common way Linear A work is dismissed by reviewers. **Concrete case, not a hypothetical**: Di Mino 2026 built exactly this circle with an AI coding tool — B values, free reassignment of the rest, then Semitic-root matching to a "Tinitic" language — and it is already being dismissed by the field (see [state-of-the-art.md](state-of-the-art.md) Fringe and hype register). Treat this as the failure mode this repo's own AI-assisted tooling has to actively avoid, not just an invariant to state.
- Any train/test split must be grouped by document, and probably by scribal hand and findspot. Consequence of a random token-level split: leakage across joins of the same tablet and a meaningless accuracy figure.

## Gotchas

- pyaegean under `[all]` installs ~90 transitive deps including cloud SDKs. Use a narrower extra if footprint matters.
- Installs and runs clean on Python 3.14.7 — no wheel gap.
- **`.venv` hardcodes the absolute project path in 33 files under `.venv/bin/`** plus `pyvenv.cfg`. Renaming or moving the repo folder breaks pip and console scripts. Rewrite the path in those 34 files rather than rebuilding (done for the 2026-09-10 rename; see the Environment note in `CLAUDE.md`).
- **The value-transfer caution in the primary.** Ventris and Chadwick 1973, p. 32: similarities
  between Linear A and Linear B signs "should not be taken to argue an identical sound-value;
  such an identity could only be proved by a cogent decipherment"; Bennett 1953, quoted there
  p. 37: "where the same sign is used in both Linear A and B there is no guarantee that the same
  value is assigned to it." Barber 1974, p. 98, says the same with the Cypriot precedent.
- **Linear A coverage and edition gotchas, measured 2026-09-12 (FINDINGS F-035).** 1,162 of
  1,721 `lineara` documents have no word token (858 are uninscribed HT roundels). The 2024
  GORILA supplement and the Knossos Anetaki ring (Kanta 2025) are absent from `lineara` and
  `sigla`. No line-continuation marks exist in either chain, so split words, if any, were
  rejoined upstream. `sigla`'s `doc.lines` holds one token per line: never run a line- or
  entry-based statistic on SigLA. Neither edition reads do, we or so anywhere in Linear A;
  Packard 1974's sign-groups using them are readings the editions have abandoned, and 67 of
  his 175 Appendix A sign-groups do not exist under GORILA's labels.
- **Nothing in copyright is committed.** Working copies of reference material live in
  `~/.cache/linear-a-b/reference/`, outside the repo (added 2026-09-12).
- **SigLA and GORILA document ids differ in spacing** (`"HT 1"` against `"HT1"`); normalise
  before aligning. 697 of SigLA's 802 documents align with a GORILA document; 96 agree word
  for word, 508 differ (13 in divider placement alone, 137 in readings, 365 in line
  coverage). SigLA yields 692 Kober word types to GORILA's 988, 577 shared. Measured
  2026-09-11 (FINDINGS F-023).
- **Leiden underdots do not affect `Token.status` in either script.** `scripts/linearb/loader._bracket_status` inspects only `[`, `]` and `?`, never U+0323 COMBINING DOT BELOW. So a damaged-but-legible sign (`ọ`, `a-ṇọ-qo-ta-o`, `ỌṾỊṢ:ṃ`) arrives as `CERTAIN`. Filtering on `status == CERTAIN` therefore does **not** give you securely-read text, and leaving the dots in place inflates a sign vocabulary with phantom variants (measured on the Linear B D family: 75 signs → 118). `ReadingStatus` has four members, not three: `CERTAIN`, `UNCLEAR`, `RESTORED`, `LOST`.
- Linear A `Token.status` is coarse: measured 2026-09-10, 5,734 certain / 552 lost / 120 unclear tokens. The pyaegean wiki states the full Leiden apparatus was dropped upstream (mwenge), so absence of an `unclear` flag is not evidence of a secure reading. SigLA is the place to check a doubtful sign.
- **A-004, measured 2026-09-11 (`scripts/lineara_underdots.py`):** the DAMOS underdot problem above does not recur in `lineara` in that form — no token, of any status, carries U+0323 anywhere in the corpus; the upstream mwenge chain drops the Leiden apparatus before pyaegean loads it. What does survive into `CERTAIN` WORD tokens of 2 to 4 signs is GORILA's asterisk-numbered unidentified-sign convention (`*301`, or ligatured as `VIR+*307`): 246 of 3,336 sampled sign positions (7.4%), 224 of 1,257 tokens, 167 of 893 word types. That mark is unstripped in `Token.signs`/`Sign.label`, but every `ConsonantMap` used by `scripts/controlled_comparison.py` only covers signs with an assigned phonetic value, so `word_pool`'s coverage filter already excludes these word types regardless of status — confirmed by a bit-identical rerun under `--exclude-underdotted`. See ASSUMPTIONS A-004.
- Corpus name is `lineara`, not `linear_a`. The KeyError does suggest the right name.
- The DĀMOS `/statistics/` URL 404s. Get counts from the loaded corpus.
- Search engines still index pyaegean at 0.15.1; current is 0.59.0 (2026-08-12). Check PyPI, not search results.
- Fetched corpora live outside the repo at `~/.cache/pyaegean/`. A clean clone has no data until something calls `aegean.load()`.
- Word boundaries follow each edition's conventions (DĀMOS: comma/slash dividers), not whitespace.

## Open questions

- ~~Whether to `git init`~~ — **resolved 2026-09-10: initialised**, reversing the earlier same-day decision. See the Decisions table and HENGE Repo status.
- INVESTIGATE: the real Linear A↔B sign correspondence set, from the palaeographic literature rather than label matching. Needed before any transfer or cross-script model. The 56-label figure above is a placeholder.
- INVESTIGATE: Linear A Unicode block U+10600–U+1077F — assigned range and count, verified locally the way the B blocks were.
- ~~GORILA licence~~ — partially resolved 2026-09-10: the loaded corpus is not GORILA but a transcription chain ending at mwenge/lineara.xyz (see Source landscape). Still open: whether Douros's spreadsheet / mwenge's JSON carry any licence at all (mwenge states none), and whether pyaegean's Apache-2.0 assertion over that JSON would survive a challenge from the École française d'Athènes. Do not publish derived corpus data until this is answered.
- ~~SigLA licence~~ — resolved 2026-09-10: CC BY-NC-SA 4.0, same NC/SA obligations as DĀMOS.
- INVESTIGATE: how GORILA and SigLA disagree — document overlap, sign readings. Disagreement between editions is itself a signal worth measuring.
- ~~NeuroDecipher licence~~ — resolved 2026-09-10: none, and the pairs derive from a CC BY-ND lexicon. Use as a benchmark to compare against; regenerate a clean pair list from DĀMOS + an open Greek lexicon before publishing anything derived.
- ~~LREC 2020 dataset~~ — resolved 2026-09-10: full corpus not public; the series D derivative is on Zenodo under CC BY 4.0 (see Source landscape). Ask the Patras authors for the rest.
- INVESTIGATE: `DocumentMeta.images` contents — whether it cross-references LiBER/CaLiBRA identifiers. If so, it is the bridge from text to image work.
- ~~Current state of the art~~ — surveyed 2026-09-10, both scripts: see [state-of-the-art.md](state-of-the-art.md). Its own INVESTIGATE list supersedes the three starting points that used to sit here.
- INVESTIGATE: the "real Linear A↔B sign correspondence set" question above now has a literature answer to start from — Meißner & Steele's Table 1 (25 core signs) and Table 2 (~60 assumed), in state-of-the-art.md. Encode both tables as data and compare with the 81 / 56 / 53 loader-derived figures.
