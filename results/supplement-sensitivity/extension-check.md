# Supplement sensitivity (F-047): the four new word types

Protocol: CHANGELOG "Supplement sensitivity (F-047): the four new word types", entry
1.0, pre-registered, run 2026-09-12. `--extra-word-types <local file>`
on `scripts/toponym_test.py` and `scripts/kober_run.py` (never committed; the four
labels are sign labels, not corpus text). Criterion: none; a sensitivity.

## (a) Value transfer 1.0, GORILA only, extra types appended

400 draws, both bandings, seeds 0 and 1. F-041 columns read from
`results/toponym_test-gorila-seed{0,1}.json`; sensitivity columns from
`results/supplement-sensitivity/toponym_test-gorila-seed{0,1}.json`.

| seed | banding | lexicon | class | F-041 real | F-041 null mean | F-041 p99 | F-041 pct | sensitivity real | sensitivity null mean | sensitivity p99 | sensitivity pct |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | groups of ten | Knossos toponyms | 3= | 6 | 0.85 | 5.0 | 99.6 | 6 | 0.85 | 5.0 | 99.6 |
| 0 | groups of ten | Knossos toponyms | 4= | 3 | 0.00 | 0.0 | 100.0 | 3 | 0.00 | 0.0 | 100.0 |
| 0 | groups of ten | Knossos personal names (control) | 3= | 1 | 0.61 | 4.0 | 73.4 | 1 | 0.61 | 4.0 | 73.4 |
| 0 | groups of ten | Knossos personal names (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |
| 0 | groups of ten | Pylos toponyms (control) | 3= | 2 | 0.64 | 4.0 | 91.0 | 2 | 0.64 | 4.0 | 91.0 |
| 0 | groups of ten | Pylos toponyms (control) | 4= | 0 | 0.01 | 0.0 | 49.8 | 0 | 0.01 | 0.0 | 49.8 |
| 0 | groups of ten | Knossos toponyms, reversed (control) | 3= | 0 | 0.34 | 3.0 | 36.4 | 0 | 0.34 | 3.0 | 36.4 |
| 0 | groups of ten | Knossos toponyms, reversed (control) | 4= | 0 | 0.00 | 0.0 | 49.9 | 0 | 0.00 | 0.0 | 49.9 |
| 0 | four bands | Knossos toponyms | 3= | 6 | 0.73 | 4.0 | 99.6 | 6 | 0.73 | 4.0 | 99.6 |
| 0 | four bands | Knossos toponyms | 4= | 3 | 0.01 | 0.0 | 100.0 | 3 | 0.01 | 0.0 | 100.0 |
| 0 | four bands | Knossos personal names (control) | 3= | 1 | 0.42 | 4.0 | 81.4 | 1 | 0.42 | 4.0 | 81.4 |
| 0 | four bands | Knossos personal names (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |
| 0 | four bands | Pylos toponyms (control) | 3= | 2 | 0.46 | 3.0 | 94.2 | 2 | 0.46 | 3.0 | 94.2 |
| 0 | four bands | Pylos toponyms (control) | 4= | 0 | 0.01 | 0.0 | 49.8 | 0 | 0.01 | 0.0 | 49.8 |
| 0 | four bands | Knossos toponyms, reversed (control) | 3= | 0 | 0.34 | 3.0 | 36.8 | 0 | 0.34 | 3.0 | 36.8 |
| 0 | four bands | Knossos toponyms, reversed (control) | 4= | 0 | 0.00 | 0.0 | 49.9 | 0 | 0.00 | 0.0 | 49.9 |
| 1 | groups of ten | Knossos toponyms | 3= | 6 | 1.03 | 5.0 | 99.6 | 6 | 1.03 | 5.0 | 99.6 |
| 1 | groups of ten | Knossos toponyms | 4= | 3 | 0.01 | 0.0 | 100.0 | 3 | 0.01 | 0.0 | 100.0 |
| 1 | groups of ten | Knossos personal names (control) | 3= | 1 | 0.55 | 4.0 | 75.2 | 1 | 0.55 | 4.0 | 75.2 |
| 1 | groups of ten | Knossos personal names (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |
| 1 | groups of ten | Pylos toponyms (control) | 3= | 2 | 0.56 | 3.0 | 91.9 | 2 | 0.56 | 3.0 | 91.9 |
| 1 | groups of ten | Pylos toponyms (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |
| 1 | groups of ten | Knossos toponyms, reversed (control) | 3= | 0 | 0.43 | 3.0 | 33.8 | 0 | 0.43 | 3.0 | 33.8 |
| 1 | groups of ten | Knossos toponyms, reversed (control) | 4= | 0 | 0.00 | 0.0 | 49.9 | 0 | 0.00 | 0.0 | 49.9 |
| 1 | four bands | Knossos toponyms | 3= | 6 | 0.74 | 4.0 | 100.0 | 6 | 0.74 | 4.0 | 100.0 |
| 1 | four bands | Knossos toponyms | 4= | 3 | 0.00 | 0.0 | 100.0 | 3 | 0.00 | 0.0 | 100.0 |
| 1 | four bands | Knossos personal names (control) | 3= | 1 | 0.45 | 4.0 | 79.8 | 1 | 0.45 | 4.0 | 79.8 |
| 1 | four bands | Knossos personal names (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |
| 1 | four bands | Pylos toponyms (control) | 3= | 2 | 0.43 | 3.0 | 95.0 | 2 | 0.43 | 3.0 | 95.0 |
| 1 | four bands | Pylos toponyms (control) | 4= | 0 | 0.00 | 0.0 | 49.9 | 0 | 0.00 | 0.0 | 49.9 |
| 1 | four bands | Knossos toponyms, reversed (control) | 3= | 0 | 0.37 | 2.0 | 35.0 | 0 | 0.37 | 2.0 | 35.0 |
| 1 | four bands | Knossos toponyms, reversed (control) | 4= | 0 | 0.00 | 0.0 | 50.0 | 0 | 0.00 | 0.0 | 50.0 |

No cell changes: none of the four extra word types is a toponym match under any
lexicon, class, banding or seed. `extra_word_types_count` in each sensitivity file is
4, `extra_word_types_file` is `extra-word-types.jsonl`.

## (b) Kober 0.9.1 stage 1, GORILA, extra types appended

`--corpus lineara --allow-lineara --stem-min 2 --perms 200`, unmerged (no
`--merge-homophones`), seeds 0 and 1. Baseline columns read from
`results/kober-09/kober-lineara-seed{0,1}.json` (stage 1 is unaffected by that file's
`--medial` block, CHANGELOG "0.9": "stage 1 ... is untouched"); sensitivity columns
from `results/supplement-sensitivity/kober-lineara-seed{0,1}.json`.

| seed | statistic | baseline (kober-09) | sensitivity |
|---|---|---:|---:|
| 0 | word types | 988 | 988 |
| 0 | paradigm count (real) | 101 | 101 |
| 0 | N1 mean | 66.72 | 66.84 |
| 0 | N1 p99 | 79.01 | 80.00 |
| 0 | maximum support (real) | 2 | 2 |
| 0 | N2 mean | 2.02 | 2.02 |
| 0 | N2 p99 | 3.00 | 3.00 |
| 1 | word types | 988 | 988 |
| 1 | paradigm count (real) | 101 | 101 |
| 1 | N1 mean | 65.78 | 66.53 |
| 1 | N1 p99 | 77.02 | 78.01 |
| 1 | maximum support (real) | 2 | 2 |
| 1 | N2 mean | 2.00 | 2.00 |
| 1 | N2 p99 | 3.00 | 3.00 |

`extra_word_types_count` is 4 (`extra_word_types_file`: `extra-word-types.jsonl`) in
both sensitivity files. The word-type count does not move: all four extra word types
(sign sequences, not surface transliterations) coincide with word types already
attested elsewhere in the loaded GORILA corpus (one, DI-NA-U, is the well-attested
Haghia Triada word occurring on HT9a, HT9b, HT16 and HT25a). Paradigm count and maximum
support are therefore unchanged (101 and 2, matching the CHANGELOG entry's own "at
most 4" ceiling realised at its floor of zero); the small N1 p99 movement (<= 1 point at
200 draws) is null-draw noise from a fresh process's frozen-set iteration order
(A-057's pattern), not a content change, and does not move the maximum-support N2 p99.

## Reading

CHANGELOG "Supplement sensitivity" 1.0, pre-registered: "no reading of them is
expected to change a cell, and that expectation is written down before the run" and,
for the run itself: "No cell of (a) changes and (b)'s paradigm count moves by at most
the number of new stems the four introduce (at most 4) with maximum support unchanged:
the supplement contributes nothing measurable, F-047 stands as written."

Both runs land in that reading exactly: every cell of (a) is unchanged, and (b)'s
paradigm count and maximum support are unchanged (the four introduce zero new stems,
the floor of the entry's own "at most 4"). No toponym count changes, so A-001's sign
list gains nothing from this sensitivity, and no alternation's support rises above 2.
F-047 stands as written.
