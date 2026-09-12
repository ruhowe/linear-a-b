# S-007 result: the model finds the same stems Kober would, and they are single stems

Ran 2026-09-12. Twelve runs of a frontier model (claude-fable-5-1, as a subagent with
only a file-read and a file-write tool, no code), three per corpus, on the four private
word lists under `~/.cache/linear-a-b/s007/` (never in the repo): A, GORILA's 988 word
types as sign labels; B, the same words with every sign label renamed by a seeded
bijection to opaque codes; C, an N1 shuffle of A under the same opaque codes (959
types); D, one tablet-model Linear B subsample at 988 word types with real labels, the
calibration corpus. Prompt: `PROMPT.md` there, identical for all runs. Scoring:
`score.py` (committed), each proposal's alternation support as `kober.paradigms` counts
it (stems in the corpus carrying that ending pair) against the N2 null's 99th
percentile (200 draws, seed 0), and the instrument's own top ten on the same corpus;
on D, grammar under reference list v3.

## Counts

| corpus | runs | proposals | valid | above N2 99th pct | median support | N2 99th pct | instrument top ten above | proposals with a grammar pair (D) | instrument top ten grammar (D) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A, Linear A labelled | 3 | 30 | 30 | 0 | 1 | 3 | 0 | | |
| B, Linear A relabelled | 3 | 30 | 30 | 0 | 1 | 3 | 0 | | |
| C, shuffled, relabelled | 3 | 30 | 30 | 0 | 1 | 3 | 0 | | |
| D, Linear B calibration | 3 | 30 | 30 | 0 | 1 | 5 | 1 | 9, 10, 10 of 10 | 9 of 10 |

Every proposal on every corpus was valid (every word real, every stem-plus-ending equal
to its word). Every proposal had support 1: the proposed stem is the only stem in the
corpus carrying that set of endings, so no proposal exceeds the null anywhere, Greek
included.

## Recall or analysis

Distinct stems proposed across three runs: 16 on A, 14 on B mapped back through the
bijection, and 10 shared between the two. Run-to-run agreement: 5 to 8 stems on A, 7 to
8 on B, 9 to 10 on C. The model finds the same stems whether or not it can recognise
the labels, so the proposals are analysis of the list, not recall of the literature;
and among them, on both A and B, are the stems the field has long singled out. On the
shuffled corpus it proposes ten valid single-stem paradigms with equal confidence and
higher run-to-run agreement.

## Reading against the brief

**Nothing.** The brief's "interesting" required the model's proposals on the relabelled
corpus to exceed the N2 99th percentile more often than the instrument's top ten, with
the shuffled corpus below it. They never exceed it on any corpus. The reason is
structural: the model proposes paradigms the way a reader does, one stem with several
endings, whereas support in this instrument is the number of stems that share an
ending pair, which is what makes a paradigm a paradigm rather than a coincidence. A
single stem with three endings has support 1 by definition, on real text and on
shuffled text alike, and the model produced ten of those on the shuffle as readily as
on Linear A.

What is kept. On Greek the model's single-stem proposals are real grammar nine or ten
times in ten, the same rate as the instrument's top ten, so the reader is not worse
than the machine at finding true alternations; it is no better at telling them from
chance, which at this corpus size neither can do (F-022, F-046). And the model's
Linear A stems are found from the list, not remembered.

Must not be read as: a reading of any Linear A word. Nothing the model said beyond the
JSON was kept, and no stem is named here.
