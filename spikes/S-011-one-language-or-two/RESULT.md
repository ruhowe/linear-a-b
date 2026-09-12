# S-011 result: one language in Linear A, or two?

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json`. `stem_min` 2, 100 N1 draws per paradigm ratio, 20 seeded draws each for the size-matched control and the random-halves noise floor. Distances are Jensen-Shannon divergence (log base 2, bounded in [0, 1]) on word tokens, plus the absolute difference of stage 1 paradigm ratios on word types.

## Linear A: tablets vs every other support type pooled

`tablets`: 848 word tokens, 610 types, paradigm ratio 1.491 (count 51, N1 mean 34.21). `non-tablets`: 525 word tokens, 407 types, paradigm ratio 2.526 (count 37, N1 mean 14.65).

| distance | real | size-matched median [range] | noise floor median | noise floor p95 | real > p95 | real / p95 |
|---|---:|---:|---:|---:|:---:|---:|
| sign unigram JS | 0.095 | 0.100 [0.093, 0.107] | 0.034 | 0.037 | yes | 2.550 |
| first-sign JS | 0.198 | 0.208 [0.191, 0.222] | 0.073 | 0.081 | yes | 2.440 |
| last-sign JS | 0.152 | 0.162 [0.149, 0.179] | 0.067 | 0.075 | yes | 2.023 |
| word-length JS | 0.055 | 0.055 [0.047, 0.065] | 0.006 | 0.008 | yes | 6.799 |
| paradigm ratio abs diff | 1.035 | 0.806 [0.534, 1.117] | 0.236 | 0.492 | yes | 2.102 |

## Linear A: Hagia Triada vs everything else

`HT`: 700 word tokens, 455 types, paradigm ratio 1.600 (count 28, N1 mean 17.5). `non-HT`: 673 word tokens, 564 types, paradigm ratio 1.966 (count 56, N1 mean 28.49).

| distance | real | size-matched median [range] | noise floor median | noise floor p95 | real > p95 | real / p95 |
|---|---:|---:|---:|---:|:---:|---:|
| sign unigram JS | 0.105 | 0.105 [0.103, 0.110] | 0.034 | 0.037 | yes | 2.805 |
| first-sign JS | 0.228 | 0.229 [0.225, 0.237] | 0.074 | 0.090 | yes | 2.544 |
| last-sign JS | 0.169 | 0.169 [0.167, 0.173] | 0.066 | 0.076 | yes | 2.225 |
| word-length JS | 0.051 | 0.051 [0.049, 0.053] | 0.006 | 0.008 | yes | 6.172 |
| paradigm ratio abs diff | 0.366 | 0.406 [0.327, 0.547] | 0.198 | 0.639 | no | 0.572 |

## Linear B: Knossos vs Pylos

`Knossos`: 3457 word tokens, 1617 types, paradigm ratio 1.557 (count 340, N1 mean 218.36). `Pylos`: 5830 word tokens, 2024 types, paradigm ratio 1.860 (count 531, N1 mean 285.54).

| distance | real | size-matched median [range] | noise floor median | noise floor p95 | real > p95 | real / p95 |
|---|---:|---:|---:|---:|:---:|---:|
| sign unigram JS | 0.054 | 0.055 [0.052, 0.058] | 0.002 | 0.003 | yes | 17.162 |
| first-sign JS | 0.089 | 0.091 [0.086, 0.093] | 0.007 | 0.007 | yes | 12.042 |
| last-sign JS | 0.094 | 0.097 [0.090, 0.101] | 0.007 | 0.009 | yes | 11.068 |
| word-length JS | 0.005 | 0.005 [0.003, 0.006] | 0.000 | 0.001 | yes | 4.716 |
| paradigm ratio abs diff | 0.303 | 0.319 [0.258, 0.401] | 0.044 | 0.109 | yes | 2.765 |

## Linear B: Knossos D-series (livestock) vs A-series (personnel)

`D-series`: 995 word tokens, 376 types, paradigm ratio 2.095 (count 51, N1 mean 24.34). `A-series`: 504 word tokens, 285 types, paradigm ratio 2.118 (count 32, N1 mean 15.11).

| distance | real | size-matched median [range] | noise floor median | noise floor p95 | real > p95 | real / p95 |
|---|---:|---:|---:|---:|:---:|---:|
| sign unigram JS | 0.124 | 0.128 [0.114, 0.138] | 0.014 | 0.016 | yes | 7.546 |
| first-sign JS | 0.286 | 0.296 [0.280, 0.313] | 0.034 | 0.043 | yes | 6.711 |
| last-sign JS | 0.239 | 0.245 [0.232, 0.263] | 0.034 | 0.043 | yes | 5.505 |
| word-length JS | 0.050 | 0.047 [0.040, 0.062] | 0.002 | 0.005 | yes | 9.266 |
| paradigm ratio abs diff | 0.022 | 0.246 [0.002, 0.502] | 0.211 | 0.665 | no | 0.034 |

## Linear A: tablets vs stone vessels alone

`tablets`: 848 word tokens, 610 types, paradigm ratio 1.523 (count 51, N1 mean 33.49). `stone vessels`: 259 word tokens, 211 types, paradigm ratio 4.167 (count 21, N1 mean 5.04).

| distance | real | size-matched median [range] | noise floor median | noise floor p95 | real > p95 | real / p95 |
|---|---:|---:|---:|---:|:---:|---:|
| sign unigram JS | 0.116 | 0.128 [0.111, 0.138] | 0.036 | 0.041 | yes | 2.817 |
| first-sign JS | 0.203 | 0.232 [0.188, 0.255] | 0.077 | 0.089 | yes | 2.280 |
| last-sign JS | 0.203 | 0.229 [0.183, 0.256] | 0.072 | 0.077 | yes | 2.633 |
| word-length JS | 0.087 | 0.091 [0.073, 0.118] | 0.004 | 0.007 | yes | 12.975 |
| paradigm ratio abs diff | 2.644 | 2.364 [1.700, 2.927] | 0.153 | 0.935 | yes | 2.827 |

Stone vessels alone clear the 100-word-token threshold the brief sets for reporting this group on its own; the tablets-vs-non-tablets split above already pools them into "non-tablets".

## Headline: each split's real distance in units of its own noise floor

| split | sign unigram JS | first-sign JS | last-sign JS | word-length JS | paradigm ratio abs diff |
|---|---:|---:|---:|---:|---:|
| Linear A: tablets vs every other support type pooled | 2.550 | 2.440 | 2.023 | 6.799 | 2.102 |
| Linear A: Hagia Triada vs everything else | 2.805 | 2.544 | 2.225 | 6.172 | 0.572 |
| Linear B: Knossos vs Pylos | 17.162 | 12.042 | 11.068 | 4.716 | 2.765 |
| Linear B: Knossos D-series (livestock) vs A-series (personnel) | 7.546 | 6.711 | 5.505 | 9.266 | 0.034 |

## Reading against the brief

**Nothing** applies. Linear A's largest tablets-versus-rest or HT-versus-rest ratio to its own noise floor is 6.80, against Linear B's largest genre-or-site ratio of 17.16. Linear A's split sits inside the spread one language produces across genre and site in Linear B, once each distance is read in units of its own random-halves noise.

This must not be read as evidence for any particular language in either Linear A set, per the brief. Nothing here is a finding (spikes/README.md rule 1).
