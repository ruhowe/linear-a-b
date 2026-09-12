# S-003 result: Packard's Knossos toponym test under a 200-draw null

Ran 2026-09-12. Protocol version: n/a (spike, not main line). Code: `run.py`. Raw
numbers: `results.json`. Lexicon sources and per-entry provenance:
`~/.cache/linear-a-b/reference/s003-knossos-lexicons.json` (corpus-derived, outside the
repo per corpus-sources.md).

## Lexicons

32 of 33 candidate Knossos toponyms (the Ventris and Chadwick 1973 well-known set,
cross-checked against Packard 1974 Table 11) are attested as WORD/CERTAIN types in
DĀMOS. `di-ka-ta` is not attested in that bare form (only `di-ka-ta-de` and
`di-ka-ta-jo` are) and was dropped rather than substituted.

The personal-name control is the 32 most frequent non-toponym WORD/CERTAIN types on the
770 Knossos Da-Dv sheep-series documents, after excluding the toponyms themselves, any
word type with a toponym as an exact sign-prefix, and `da-mi-ni-jo` (Packard's Table 11
tags it "(place)"). Same script, same site, same size as the toponym lexicon: a
wrong-real-lexicon control.

## Match counts

**GORILA** (607 Linear A word types of 3+ signs):

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile |
|---|---|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 5 | 3.17 | 1.56 | 6.0 | 8.0 | 87.2 |
| toponyms | 4= | 3 | 2.35 | 0.48 | 3.0 | 3.0 | 82.5 |
| personal names (control) | 3= | 1 | 0.52 | 0.50 | 1.0 | 1.0 | 74.2 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 |

**SigLA** (443 Linear A word types of 3+ signs):

| lexicon | class | real | null mean | null sd | null p95 | null p99 | real percentile |
|---|---|---:|---:|---:|---:|---:|---:|
| toponyms | 3= | 5 | 3.95 | 1.15 | 6.0 | 7.0 | 81.2 |
| toponyms | 4= | 1 | 0.28 | 0.45 | 1.0 | 1.0 | 86.0 |
| personal names (control) | 3= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 |
| personal names (control) | 4= | 0 | 0.00 | 0.00 | 0.0 | 0.0 | 50.0 |

**Packard 1974, Table 14, p.98** (nine random decipherments, Knossos names only, for
comparison, not recomputed here):

| class | Linear B values | mean of his 9 random |
|---|---:|---:|
| 3 equal | 13 | 3.0 |
| 4 signs equal | 2 | 0.0 |

## Reading against the brief

**Nothing.** On both editions and both match classes, the real toponym count sits inside
the null distribution, at its 81st to 87th percentile, below even the 95th percentile,
let alone the 99th. The brief's "interesting" reading required clearing the null's 99th
percentile on both editions; it does not clear the 95th on either. The personal-name
control, as expected for a control, sits near its own null's median throughout (50th to
74th percentile) and never separates from noise either, so the toponym lexicon is not
failing to register a real effect that the control also lacks.

This does not fall in either of the brief's readings as an unambiguous confirmation of
"interesting", but it lands squarely in "nothing": Packard's nine rotations were too few
to characterise the null's spread, and once 200 draws map that spread properly, the
toponym match count he reported as decisive (13 against 3.0, a match Packard himself
never subjected to a proper null distribution, only nine points) is unremarkable against
it. The gap between Packard's own numbers (13 vs. 3.0, a ratio of 4.3) and this run's
(5 vs. 3.17 on GORILA, a ratio of 1.6) is itself informative: it is not fully explained
by corpus differences (GORILA already gives Packard's own scale of Linear A word types)
and points at his hand-collected matches including looser parallels than this run's
literal "identical label" criterion admits, or at his nine-draw null having understated
its own spread by chance. Either way, the toponym argument for transferred values does
not hold up under a properly characterised null on the current corpus, on either
edition. Must not be read as evidence against any specific transferred value, or against
the toponym argument's underlying mechanism (place-name persistence): only as a failure
of this match count, at this definition, to clear this null.

## Review, 2026-09-12 (session): the null is too weak, the verdict is withdrawn

The match definition takes "first two sign labels identical" as a corpus fact and lets
only the third sign's consonant vary under the null. But label identity between a Linear
A sign and a Linear B sign *is* the value transfer under test: under Packard's own null
every position's value is rotated, so a chance match must get all three positions by
luck, and under the real assignment (identity) they come free. Fixing positions one and
two hands the null most of the real count (3.17 of 5 on GORILA), which is why the real
sits at the 87th percentile of a null it should tower over or not. "Nothing" is therefore
not established. Redone as S-003b with values permuted at every position, which is
Packard's construction with 200 draws instead of nine; this run stays as the record.
