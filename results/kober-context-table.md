# Kober 0.4 context calibration table

Kober 0.4, context-restricted statistics under stratified (length, class) nulls (CHANGELOG '0.4'); TODO item 8, 'Build and run'.

Source: `results/kober-context/`. 0.3 baseline quoted from `results/kober-precision-table.json`.

## 0.4 (context-restricted, stratified nulls)

| model | N | strict top 3 all matched | chance rate median (range) | 4 of top 5 | top-10 > null p99 | median class agreement fraction |
|---|---:|---:|---|---:|---:|---:|
| full | 2 | 2/2 | 0.000 (0.000 to 0.000) | 2/2 | 2/2 | 0.365 |
| type-988 | 20 | 0/20 | 0.000 (0.000 to 0.000) | 0/20 | 7/20 | 1.000 |
| tablet-988 | 20 | 2/20 | 0.000 (0.000 to 0.000) | 2/20 | 11/20 | 1.000 |

## 0.3 baseline (quoted from kober-precision-table.json, not recomputed)

| model | strict top 3 all matched | chance rate median (range) | 4 of top 5 | top-10 > null p99 | median class agreement fraction |
|---|---:|---|---:|---:|---:|
| full | 2/2 | n/a | 2/2 | 2/2 | n/a |
| type-988 | 5/20 | n/a | 2/20 | 17/20 | n/a |
| tablet-988 | 6/20 | n/a | 15/20 | 19/20 | n/a |
