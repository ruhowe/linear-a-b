# Kober 0.6 reference-list-revision calibration table

Kober 0.6, reference-list revision (CHANGELOG '0.6').

v1 source: `results/kober-grammar-null/`. v2 source: `results/kober-grammar-null-v2/`.

## Strict top three all grammar, v1 vs v2

| model | N | v1 | v2 |
|---|---:|---:|---:|
| full | 2 | 2/2 | 2/2 |
| type-988 | 20 | 5/20 | 5/20 |
| tablet-988 | 20 | 6/20 | 11/20 |

## At least two of top three, v1 vs v2

| model | N | v1 | v2 |
|---|---:|---:|---:|
| full | 2 | 2/2 | 2/2 |
| type-988 | 20 | 16/20 | 16/20 |
| tablet-988 | 20 | 20/20 | 20/20 |

## Top ten matched above its own v2 null 99th percentile (results/kober-grammar-null-v2/)

| model | N | pass |
|---|---:|---:|
| full | 2 | 2/2 |
| type-988 | 20 | 17/20 |
| tablet-988 | 20 | 20/20 |

## v2 null: mean matched by chance (median, range across the model's runs)

| model | n=3 | n=5 | n=10 |
|---|---|---|---|
| full | 0.49 (0.48 to 0.5) | 0.787 (0.745 to 0.83) | 1.29 (1.29 to 1.29) |
| type-988 | 0.19 (0.13 to 0.315) | 0.27 (0.2 to 0.395) | 0.398 (0.25 to 0.59) |
| tablet-988 | 0.278 (0.16 to 0.36) | 0.35 (0.22 to 0.5) | 0.53 (0.38 to 0.67) |

## v2 null: 99th percentile (median, range across the model's runs)

| model | n=3 | n=5 | n=10 |
|---|---|---|---|
| full | 2 (2 to 2) | 2 (2 to 2) | 2.5 (2 to 3) |
| type-988 | 1 (1 to 2) | 2 (1 to 2) | 2 (2 to 3) |
| tablet-988 | 1.01 (1 to 2) | 2 (1 to 2) | 2.01 (2 to 3) |

## Full corpus: top 50 alternations gaining a rule under v2

2 of 50.

| rank | ending pair | support | rule (v2) |
|---:|---|---:|---|
| 46 | SI-JA / SO | 6 | ethnic_derivation |
| 50 | TI-JA / TO | 6 | ethnic_derivation |
