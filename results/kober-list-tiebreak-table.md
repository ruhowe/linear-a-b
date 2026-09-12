# Kober 0.7 list-tiebreak calibration table

Kober 0.7, list-support tie-break (CHANGELOG '0.7').

Source: `results/kober-list-tiebreak/`. 0.3 baseline quoted from `results/kober-precision-table.json`; 0.5 result quoted from `results/kober-tiebreak-table.json`; 0.6 result quoted from `results/kober-reference-v2-table.json`.

## 0.7 (list-tiebreak ordering: support, role-sharing, list-support, lexicographic)

| model | N | top3 all grammar v1 | v2 | >=2 of 3 v1 | v2 | top10 > null p99 v1 | v2 | chance rate v1 (range) | v2 (range) | positions changed vs 0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| full | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 0 (0 to 0) | 0 (0 to 0) | 0 (0 to 0) |
| type-988 | 20 | 6/20 | 6/20 | 15/20 | 15/20 | 18/20 | 18/20 | 0 (0 to 0) | 0 (0 to 0) | 4 (0 to 9) |
| tablet-988 | 20 | 9/20 | 12/20 | 20/20 | 20/20 | 20/20 | 20/20 | 0 (0 to 0) | 0 (0 to 0) | 0 (0 to 4) |

## 0.3 baseline (quoted from kober-precision-table.json, version 1 only, not recomputed)

| model | strict top 3 all grammar | at least 2 of 3 | top-10 > null p99 |
|---|---:|---:|---:|
| full | 2/2 | 2/2 | 2/2 |
| type-988 | 5/20 | 16/20 | 17/20 |
| tablet-988 | 6/20 | 20/20 | 19/20 |

## 0.5 result (quoted from kober-tiebreak-table.json, version 1 only, not recomputed)

| model | strict top 3 all grammar | at least 2 of 3 | top-10 > null p99 | chance rate median (range) |
|---|---:|---:|---:|---|
| full | 2/2 | 2/2 | 2/2 | 0 (0 to 0) |
| type-988 | 6/20 | 16/20 | 18/20 | 0 (0 to 0) |
| tablet-988 | 9/20 | 20/20 | 20/20 | 0 (0 to 0) |

## 0.6 result (quoted from kober-reference-v2-table.json, plain 0.3 ordering scored at v1 vs v2, not recomputed)

| model | top3 all grammar v1 | v2 | >=2 of 3 v1 | v2 | top10 > null p99 (v2 null) |
|---|---:|---:|---:|---:|---:|
| full | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| type-988 | 5/20 | 5/20 | 16/20 | 16/20 | 17/20 |
| tablet-988 | 6/20 | 11/20 | 20/20 | 20/20 | 20/20 |
