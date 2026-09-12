# results/

Aggregate numbers only, one JSON per run, each stamped with the protocol version that
produced it. Nothing here is corpus text. The finding each file feeds is listed below;
the finding, not the file, is where a number is read.

| file pattern | protocol | finding |
|---|---|---|
| `linearb_restoration*.md`, `restoration-*.json` | restoration 1.0, 1.1 | F-001, F-002 |
| `controlled_comparison-{corpus}[-seedN][-secure25|-nonsecure|-exunderdot].json` | etymological 1.0 | F-008, F-012, F-014, F-015 |
| `unrelated_controls-*.json`, `extra_lexicons-*.json` | etymological 1.0 (`--map greek` variants: `-greekmap`) | F-008, F-011, F-012, F-013, F-014 |
| `laryngeal_test-*.json` | etymological 1.1 | F-012 |
| `subset_decomposition-lineara-seedN.json` | etymological 1.0, one null held fixed | F-014 |
| `lineara_underdots.json` | measurement | F-015 |
| `kober-damos-seedN.json` | Kober 0.1 to 0.3 (blocks `grid`, `grid_anchored`, `grid_alternations`) | F-016, F-017, F-018, F-021 |
| `kober-damos-seed0-sub988-sN.json` | Kober, type-model subsample | F-019 |
| `kober-lineara-seedN.json` | Kober on Linear A (GORILA) | F-019 |
| `kober-sweep/`, `kober-sweep-summary.json` | Kober floor sweep, both models | F-022 |
| `kober-sigla-seedN.json`, `kober-lineara-seed0-sub692-sN.json`, `kober-lineara-seed0-sharedwithsigla.json` | Kober on SigLA and the size-matched GORILA control | F-023 |
| `kober-grammar-null/kober-damos-seedN.json` (full corpus), `-sub988-sN.json` (type model), `-docsK-sN.json` (tablet model) | Kober 0.3 stage 1, grammar-match null (`ending_channel.grammar_match_null`, `nulls.py::grammar_matched_count`); same stage 1 real values as the `kober-damos-*` and `kober-sweep/*size988*` files they parallel, written under `kober-grammar-null/` (`--results-dir`) so the rerun does not overwrite those | TODO item 8, prerequisite 1 |
| `kober-precision-table.json`, `kober-precision-table.md` | precision-criterion scoring (`scripts/kober_precision_table.py`) over the `kober-grammar-null/` files, no criterion chosen | TODO item 8, prerequisite 2 |
| `reference_v2` block, added by `scripts/kober_rescore_reference.py` to every Kober results file under `results/` (top-level `kober-*.json`, `kober-sweep/`, `kober-grammar-null/`, `kober-context/`, `kober-role-tiebreak/`) that has an `ending_channel` | Kober 0.6, reference-list revision (CHANGELOG "0.6"); rescored in place, stage 1 untouched | none new; feeds the tables below |
| `kober-grammar-null-v2/` (same filenames as `kober-grammar-null/`) | Kober 0.6's own strict grammar-match null, `--reference-version 2`; stage 1 bit-identical to the `kober-grammar-null/` counterpart | CHANGELOG "0.6" |
| `kober-reference-v2-table.json`, `kober-reference-v2-table.md` | Kober 0.6 calibration (`scripts/kober_reference_v2_table.py`): v1-vs-v2 strict top-three and at-least-two-of-three per model, v2 null-exceedance, v2 chance rate, and the full corpus's top fifty alternations gaining a rule under v2; no criterion chosen | CHANGELOG "0.6" |
| `kober-list-tiebreak/kober-damos-seedN.json` (full corpus), `-sub988-sN.json` (type model), `-docsK-sN.json` (tablet model) | Kober 0.7, list-support tie-break (`--list-tiebreak`, implies `--role-tiebreak`): `list_tiebreak` block, both reference versions | CHANGELOG "0.7" |
| `kober-list-tiebreak-table.json`, `kober-list-tiebreak-table.md` | Kober 0.7 calibration (`scripts/kober_list_tiebreak_table.py`): strict top-three, at-least-two-of-three and top-ten-exceeds-null-p99 per model at both reference versions, chance rate median/range both versions, positions changed vs 0.5, beside the 0.3, 0.5 and 0.6 figures; no criterion chosen | CHANGELOG "0.7" |
| `kober-09/kober-damos-seed{0,1}.json` (full corpus), `-docsK-sN.json` (tablet-model subsamples at 988 word types, N the subsample seed 0-19, K from `kober-sweep/kober-sweep-tablet-size988-seedN.json`), `kober-09/kober-lineara-seed{0,1}.json` | Kober 0.9: medial channel (`medial` block, `--medial`), stage 1 unmerged | CHANGELOG "0.9" |
| `kober-09-merged/` (same filenames as `kober-09/`) | Kober 0.9's identity sensitivity, `--merge-homophones`, same runs | CHANGELOG "0.9" |
| `kober-sweep-09/kober-sweep-tablet-size{500,750,1250,1500,1750}-seedN.json` (N 0-19), `kober-sweep-09-summary.json`, `kober-sweep-09-summary.md` | Kober 0.9.1 stage 1, `--merge-homophones --reference-version 3`, tablet model only; the 988 and 3,768 cells are read from `kober-09-merged/` (not rerun) | CHANGELOG "Floor sweep under Kober 0.9.1, merged identities and reference list v3" |
| `toponym_test.md`, `toponym_test-{gorila,sigla}-seed{0,1}.json` | Value transfer 1.0 (`scripts/toponym_test.py`). The one file set that stores word forms: 51 published place-name readings and 32 Knossos personal-name sign sequences, kept so the test can be checked (LICENSE.md, the one exception) | F-041 |
| `kober-09/`, `kober-09-merged/`, `kober-context/` | Three different runs that share filenames because they cover the same corpus, seeds and subsamples: 0.9 unmerged, 0.9 with `--merge-homophones`, and 0.4's context channels. Contents differ; each is cited by its own finding or CHANGELOG entry, so none is a copy of another | see the rows above and FINDINGS |
| `supplement-sensitivity/division/` (`toponym_test.md`, `toponym_test-gorila-seed{0,1}.json`, `kober-lineara-seed{0,1}.json`) | Supplement sensitivity 1.1, the four division variants appended | F-048 |
| `toponym_test.md`, `toponym_test-{gorila,sigla}-seed{0,1}.json` | Value transfer 1.0 (`scripts/toponym_test.py`): four lexicons, two bandings, 400 draws, matched pairs as sign labels | F-041 |
| `supplement-sensitivity/toponym_test-gorila-seed{0,1}.json`, `supplement-sensitivity/toponym_test.md` (`--extra-word-types`, `--edition gorila`, `--results-dir`), `supplement-sensitivity/kober-lineara-seed{0,1}.json` (`--extra-word-types`, unmerged), `supplement-sensitivity/extension-check.md` | Supplement sensitivity 1.0: the four F-047 word types appended to the GORILA word-type set before Value transfer 1.0 and Kober 0.9.1 stage 1; no criterion, beside F-041's and `kober-09/kober-lineara-seed{0,1}.json`'s values | F-047 |

Seeds: `seedN` is the null seed; `sN` after `sub` is the subsample seed. A file without
a seed tag is seed 0 at 100 permutations for the etymological scripts and 200 draws for
the Kober scripts.
