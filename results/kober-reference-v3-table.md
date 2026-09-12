# Kober 0.8 reference-list-v3 calibration table

Kober 0.8, reference-list v3 revision (CHANGELOG '0.8').

v1 source: `results/kober-grammar-null/`. v3 source: `results/kober-grammar-null-v3/`.

## Strict top three all grammar, v1 vs v2 vs v3

| model | N | v1 | v2 | v3 |
|---|---:|---:|---:|---:|
| full | 2 | 2/2 | 2/2 | 2/2 |
| type-988 | 20 | 5/20 | 5/20 | 6/20 |
| tablet-988 | 20 | 6/20 | 11/20 | 13/20 |

## At least two of top three, v1 vs v2 vs v3

| model | N | v1 | v2 | v3 |
|---|---:|---:|---:|---:|
| full | 2 | 2/2 | 2/2 | 2/2 |
| type-988 | 20 | 16/20 | 16/20 | 17/20 |
| tablet-988 | 20 | 20/20 | 20/20 | 20/20 |

## Top ten matched above its own v3 null 99th percentile (results/kober-grammar-null-v3/)

| model | N | pass |
|---|---:|---:|
| full | 2 | 2/2 |
| type-988 | 20 | 17/20 |
| tablet-988 | 20 | 19/20 |

## v3 null: 99th percentile (median, range across the model's runs)

| model | n=3 | n=5 | n=10 |
|---|---|---|---|
| full | 1.5 (1.01 to 2) | 2 (2 to 2) | 3 (3 to 3) |
| type-988 | 1.01 (1 to 2) | 2 (1 to 2) | 2.01 (2 to 3) |
| tablet-988 | 2 (1 to 2) | 2 (1 to 2.01) | 3 (2 to 3.01) |

## Real strict matched count under v3 (median, range across the model's runs)

| model | n=3 | n=5 | n=10 |
|---|---|---|---|
| full | 3 (3 to 3) | 5 (5 to 5) | 9 (9 to 9) |
| type-988 | 2 (0 to 3) | 3 (1 to 4) | 4 (2 to 8) |
| tablet-988 | 3 (2 to 3) | 4 (3 to 5) | 7 (3 to 9) |

## Chance rate of "strict top three all matched" under v3 (median, range; count exceeding 0.05)

| model | N | median | range | count > bar |
|---|---:|---:|---|---:|
| full | 2 | 0 | 0 to 0 | 0/2 |
| type-988 | 20 | 0 | 0 to 0.005 | 0/20 |
| tablet-988 | 20 | 0 | 0 to 0.005 | 0/20 |

## Rule-firing counts under the null, v3, summed over all draws and runs per model

### full

| rule | count |
|---|---:|
| gender | 485 |
| feminine_of_eus | 10 |
| eu_stem | 3 |
| ethnic_derivation | 2 |
| consonant_stem_case | 1 |

### type-988

| rule | count |
|---|---:|
| gender | 1185 |
| ethnic_derivation | 271 |
| consonant_stem_case | 178 |
| material_adjective | 132 |
| eu_stem | 113 |
| feminine_of_eus | 69 |
| genitive | 36 |
| spelling_variant | 32 |
| consonant_stem_suffix | 25 |
| particle | 21 |
| a_stem_genitive | 10 |
| dative_plural | 8 |
| verb | 2 |

### tablet-988

| rule | count |
|---|---:|
| gender | 1717 |
| ethnic_derivation | 281 |
| consonant_stem_case | 144 |
| material_adjective | 137 |
| eu_stem | 116 |
| feminine_of_eus | 114 |
| genitive | 57 |
| spelling_variant | 38 |
| consonant_stem_suffix | 28 |
| particle | 24 |
| a_stem_genitive | 10 |
| dative_plural | 4 |
| s_stem | 1 |

## Full corpus: top 50 alternations gaining a rule under v3 that they did not have under v2

4 of 50.

| rank | ending pair | support | rule (v3) |
|---:|---|---:|---|
| 15 | TA / TE | 10 | consonant_stem_case |
| 28 | JA / U | 7 | feminine_of_eus |
| 32 | WA / WE | 7 | consonant_stem_case |
| 42 | NO / NO-RE | 6 | consonant_stem_suffix |

## Full corpus: top 50 alternations gaining a rule under v3 that they did not have under v1

6 of 50 (includes the 0.6/v2 gains, rules 11's ethnic derivation, plus rules 12 to 22's own).

| rank | ending pair | support | rule (v3) |
|---:|---|---:|---|
| 15 | TA / TE | 10 | consonant_stem_case |
| 28 | JA / U | 7 | feminine_of_eus |
| 32 | WA / WE | 7 | consonant_stem_case |
| 42 | NO / NO-RE | 6 | consonant_stem_suffix |
| 46 | SI-JA / SO | 6 | ethnic_derivation |
| 50 | TI-JA / TO | 6 | ethnic_derivation |
