# Kober 0.5 role-tiebreak calibration table

Kober 0.5, entry-role tie-break (CHANGELOG '0.5').

Source: `results/kober-role-tiebreak/`. 0.3 baseline quoted from `results/kober-precision-table.json`; 0.4 result quoted from `results/kober-context-table.json`.

## 0.5 (role-tiebreak ordering)

| model | N | strict top 3 all matched | chance rate median (range) | at least 2 of top 3 | top-10 > null p99 | positions changed vs 0.3 median (range) |
|---|---:|---:|---|---:|---:|---|
| full | 2 | 2/2 | 0.0 (0 to 0) | 2/2 | 2/2 | 3.0 (3 to 3) |
| type-988 | 20 | 6/20 | 0.0 (0 to 0) | 16/20 | 18/20 | 3.5 (0 to 8) |
| tablet-988 | 20 | 9/20 | 0.0 (0 to 0) | 20/20 | 20/20 | 4.5 (0 to 8) |

## 0.3 baseline (quoted from kober-precision-table.json, not recomputed)

| model | strict top 3 all matched | chance rate median (range) | at least 2 of top 3 | top-10 > null p99 |
|---|---:|---|---:|---:|
| full | 2/2 | n/a | 2/2 | 2/2 |
| type-988 | 5/20 | n/a | 16/20 | 17/20 |
| tablet-988 | 6/20 | n/a | 20/20 | 19/20 |

## 0.4 result (quoted from kober-context-table.json, not recomputed)

| model | strict top 3 all matched | chance rate median (range) | at least 2 of top 3 | top-10 > null p99 |
|---|---:|---|---:|---:|
| full | 2/2 | 0.0 (0 to 0) | n/a | 2/2 |
| type-988 | 0/20 | 0.0 (0 to 0) | n/a | 7/20 |
| tablet-988 | 2/20 | 0.0 (0 to 0) | n/a | 11/20 |
