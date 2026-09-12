# Kober grammar-match null: precision-criterion table

Kober 0.3 stage 1, grammar-match null (CHANGELOG 'Null rate of the grammar match, and precision criteria'); TODO item 8, prerequisite 1.

## Criterion (a): real matched count at top-n exceeds the null 99th percentile

### Ties-included top-n (A-053)

| model | N | n=3 pass | n=5 pass | n=10 pass |
|---|---:|---:|---:|---:|
| full | 2 | 2/2 | 2/2 | 2/2 |
| type-988 | 20 | 10/20 | 5/20 | 6/20 |
| tablet-988 | 20 | 10/20 | 16/20 | 12/20 |

### Strict top-n (A-072)

| model | N | n=3 pass | n=5 pass | n=10 pass |
|---|---:|---:|---:|---:|
| full | 2 | 2/2 | 2/2 | 2/2 |
| type-988 | 20 | 15/20 | 15/20 | 17/20 |
| tablet-988 | 20 | 16/20 | 18/20 | 19/20 |

## Criterion (b): raw k of top-n on the reference list

| model | N | (3,3) | (3,2) | (5,4) | (10,7) |
|---|---:|---:|---:|---:|---:|
| full | 2 | 2/2 | 2/2 | 2/2 | 2/2 |
| type-988 | 20 | 5/20 | 16/20 | 2/20 | 0/20 |
| tablet-988 | 20 | 6/20 | 20/20 | 15/20 | 8/20 |

## Null 99th percentile and real matched count, ties-included top-n (median, range)

| model | n | null p99 median | null p99 range | real matched median | real matched range |
|---|---:|---:|---|---:|---|
| full | 3 | 2.0 | [2.0, 2.0] | 3.0 | [3, 3] |
| full | 5 | 2.0049999999999955 | [2.0, 2.009999999999991] | 6.0 | [6, 6] |
| full | 10 | 3.0 | [3.0, 3.0] | 9.0 | [9, 9] |
| type-988 | 3 | 4.014999999999986 | [2.0, 6.009999999999991] | 3.5 | [2, 10] |
| type-988 | 5 | 6.009999999999991 | [5.0, 8.0] | 5.0 | [2, 10] |
| type-988 | 10 | 8.0 | [7.0, 10.0] | 6.0 | [3, 33] |
| tablet-988 | 3 | 2.009999999999991 | [2.0, 3.0] | 3.0 | [2, 6] |
| tablet-988 | 5 | 3.009999999999991 | [2.0, 6.0] | 5.0 | [3, 8] |
| tablet-988 | 10 | 8.009999999999991 | [5.009999999999991, 10.0] | 10.0 | [4, 12] |

## Null 99th percentile and real matched count, strict top-n (median, range)

| model | n | null p99 median | null p99 range | real matched median | real matched range |
|---|---:|---:|---|---:|---|
| full | 3 | 1.5 | [1.0, 2.0] | 3.0 | [3, 3] |
| full | 5 | 2.0 | [2.0, 2.0] | 5.0 | [5, 5] |
| full | 10 | 2.5049999999999955 | [2.009999999999991, 3.0] | 9.0 | [9, 9] |
| type-988 | 3 | 1.0 | [1.0, 2.0] | 2.0 | [0, 3] |
| type-988 | 5 | 1.009999999999991 | [1.0, 2.0] | 2.0 | [1, 4] |
| type-988 | 10 | 2.0 | [1.0, 2.009999999999991] | 3.0 | [2, 6] |
| tablet-988 | 3 | 1.0 | [1.0, 2.0] | 2.0 | [2, 3] |
| tablet-988 | 5 | 2.0 | [1.0, 2.0] | 4.0 | [2, 5] |
| tablet-988 | 10 | 2.0 | [2.0, 3.0] | 6.0 | [2, 8] |

## Ties-included top-10 set size (median across runs, A-072)

| model | real median | null mean median |
|---|---:|---:|
| full | 10.0 | 12.3475 |
| type-988 | 14.0 | 349.39250000000004 |
| tablet-988 | 21.5 | 193.1775 |
