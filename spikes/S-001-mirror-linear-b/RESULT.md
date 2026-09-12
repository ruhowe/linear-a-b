# S-001 result: mirroring Linear B as a positive control for the prefix channel

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json`. Corpus `damos`, stem_min
2, 200 draws, seed 0 throughout. Grammar matching at `reference.is_grammar` version 3
(Kober 0.8's full rule list) on both sides of each comparison, so the two sides are
graded identically; F-016's own "9 of 10" and "1 of 10" figures used version 1 and are
not recomputed here.

An exact-match check precedes both comparisons: every alternation in the mirrored
ending channel, with its two endings reversed back to real orientation, is looked up
against the real prefix channel's own alternation support, and vice versa for the
mirrored prefix channel against the real ending channel. Both checks came back
identical — 7,052 alternations matching value-for-value for the first pair, 5,250 for
the second, zero mismatches — which is what the bijection argument in `run.py`'s
docstring predicts: reversal maps one channel's splits onto the other's exactly, so
only the two nulls' Monte Carlo draws can differ.

## Comparison 1: mirrored ending channel vs real prefix channel

| statistic | mirrored ending (real-orientation) | real prefix |
|---|---:|---:|
| paradigm count | 707 | 707 |
| N1 null mean (sd) | 621.4 (12.3) | 622.7 (12.6) |
| N1 null p99 | 652.0 | 647.0 |
| N1 real percentile | 100.0 | 100.0 |
| maximum alternation support | 10 | 10 |
| N2 null mean (sd) | 13.1 (2.5) | 13.2 (2.6) |
| N2 null p99 | 19.0 | 20.0 |
| N2 real percentile | 17.0 | 15.5 |
| strict top-10 grammar count (v3) | 4 | 4 |

Top ten alternations (identical set, identical order, both sides): A/E 10, A/KA 9,
A/A3 8, A/PA 8, E/O 8, A/PE 7, A/PO 7, E/PA 7, KA/KO 7, A/KE 6. Four of the ten match a
version-3 rule on both sides: A/E and E/O (`consonant_stem_case`), A/A3
(`spelling_variant`), KA/KO (`gender`).

## Comparison 2: mirrored prefix channel vs real ending channel

| statistic | mirrored prefix (real-orientation) | real ending |
|---|---:|---:|
| paradigm count | 932 | 932 |
| N1 null mean (sd) | 609.0 (13.4) | 608.3 (12.3) |
| N1 null p99 | 639.0 | 638.0 |
| N1 real percentile | 100.0 | 100.0 |
| maximum alternation support | 57 | 57 |
| N2 null mean (sd) | 13.5 (2.0) | 13.5 (2.0) |
| N2 null p99 | 20.0 | 18.0 |
| N2 real percentile | 100.0 | 100.0 |
| strict top-10 grammar count (v3) | 9 | 9 |

Top ten alternations (identical set, both sides; the only order difference is a tie at
support 13 between JA/JA-O and RA/RO, which the two sides' tie-breaks resolve in
opposite order): JA/JO 57, U/WE 29, JO/JO-JO 22, TA/TO 19, U/WO 17, WE/WO 17, JA/JA-O
13, RA/RO 13, TA/TA-O 13, RO/TO 12. This is F-016's own ending-channel top ten,
reproduced exactly, both by paradigm count and maximum support and by the alternation
list itself.

## Reading against the brief

**Interesting**, in the brief's own terms: the mirrored ending channel and the real
prefix channel agree in paradigm count (707 = 707), maximum alternation support
(10 = 10), the full top-ten alternation list, and the strict top-ten grammar count
(4 = 4); the mirrored prefix channel and the real ending channel agree the same way
(932 = 932, 57 = 57, top ten identical, 9 = 9), reproducing F-016's ending-channel
figures exactly. The two real-value comparisons are not merely close, they are exact,
which the bijection argument predicts and the exact-match check confirms directly. The
only place any difference appears at all is inside the two nulls' own Monte Carlo
estimates, and it is small: N1's null mean differs by 1.2 of 621 (comparison 1) and 0.7
of 609 (comparison 2), well under one standard deviation (12 to 13) in both cases; N2's
null mean differs by 0.1 to 0.3 against a standard deviation of 2 to 2.6. So the prefix
channel works: A-047's fix (read prefixes by N2 support alone, not by N1 paradigm count)
is validated by an independent construction, not merely by the argument that motivated
it. F-019's prefix null on Linear A (maximum support 3 against a null mean 1.9, at but
not above the 99th percentile) is accordingly a fact about Linear A not prefixing
visibly at this corpus size, not a property of a channel that cannot see prefixes.

One number needs flagging so it is not over-read: the real prefix channel's strict
top-10 grammar count is 4 of 10 at reference version 3, well above F-016's own 1 of 10
at version 1. This is not new evidence of prefixal grammar — it is exactly matched by
the mirrored-ending side (4 = 4), which computes the identical real corpus fact by a
different route, so the increase is a property of version 3's broader, more permissive
rule set (added for suffix morphology, in `docs/ai_context/kober-method.md`'s "Version
0.8") firing more often on short one- and two-sign pairs generally, not a property of
prefixation. F-016's own version-1 reading of the prefix channel as weak stands.

Must not be read as anything about Linear A: this spike touches only Linear B, by
design, and its subject is the instrument, not either corpus's grammar.
