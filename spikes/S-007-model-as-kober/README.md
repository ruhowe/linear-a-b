# S-007 · how to run

Question and readings are in `BRIEF.md`. This file is how-to only; it carries no word
list and no model output, per `spikes/README.md` rule 6.

## Where the private files live

Everything corpus-derived for this spike lives outside the repo, under
`~/.cache/linear-a-b/s007/`, built by a one-off generation step (not committed; the
generator itself is scratch, not part of this repo — rebuild it from this README if it's
ever needed again):

- `corpus-A-lineara.txt` — GORILA's Linear A word types (`kober.words.extract_word_types`
  on `aegean.load("lineara")`), one hyphen-joined word per line, sorted. 988 words.
- `bijection-B.json` — every sign label appearing in corpus A, mapped to an opaque
  `S001`..`Snnn` label by a seeded random bijection (seed 7). Width is padded to the
  number of distinct signs (158 signs at the 2026-09-12 build, so three digits).
- `corpus-B-permuted.txt` — corpus A with every sign relabelled through the bijection.
  Same 988 words, opaque labels; nothing a model has read about Linear A applies to it.
- `corpus-C-shuffled.txt` — an N1 draw of corpus A (`kober.nulls.n1_draw`, seed 0),
  relabelled through the same bijection. N1 collapses some words to duplicates by
  construction (`docs/ai_context/kober-method.md`'s N1 description), so this corpus is
  smaller than A and B — 959 words at the 2026-09-12 build, not 988.
- `corpus-D-linearb.txt` — a Linear B (DĀMOS) tablet-model subsample at 988 word types,
  built the way `scripts/kober_floor_sweep.py` builds its tablet-model cells
  (`kober.words.subsample_document_ids` on the sorted document-id pool, bisected to the
  target word-type count, subsample seed 0). Real Linear B sign labels, not relabelled —
  this is the calibration corpus, and the point is to score it exactly like the other
  three while knowing the answer. 988 words at the 2026-09-12 build, via 1,042 documents.
- `PROMPT.md` — the single prompt template given to the model for every corpus, with a
  placeholder marking where that corpus's own word list is substituted in. Same wording
  regardless of which corpus is being run, including corpus D, so the model is never told
  which corpus (if any) is Linear B.

The model's own raw output (its proposals, per corpus per run) is equally private and
does not belong in this repo either — save it wherever the coordinating session keeps
run artifacts, as a JSON file in the form `score.py` expects (see `BRIEF.md`'s example
and below).

## Running the scorer

`score.py` takes a corpus word-list file and a JSON file of the model's proposals, and
scores them against that corpus's own Kober-method ending channel and N2 null. It holds
no word lists itself — everything corpus-shaped is a command-line argument.

```
.venv/bin/python spikes/S-007-model-as-kober/score.py \
    --corpus ~/.cache/linear-a-b/s007/corpus-A-lineara.txt \
    --proposals /path/to/model-proposals-A-run1.json \
    [--reference-version {1,2,3}] [--stem-min 2] [--draws 200] [--seed 0] \
    [--top-n 10] [--out /path/to/report.json]
```

Pass `--reference-version` (1, 2 or 3) only when scoring corpus D, the Linear B
calibration corpus: it additionally grades each proposed alternation against
`kober.reference.is_grammar` at that version. Grading GORILA sign labels or opaque
bijection/null labels against a Mycenaean Greek reference list is meaningless, so leave
it unset for corpora A, B and C.

The proposals file is a JSON list, one entry per paradigm, in the form `PROMPT.md` asks
the model for:

```json
[
  {
    "stem": ["S03", "S11"],
    "endings": [["S02"], ["S05", "S01"]],
    "words": [["S03", "S11", "S02"], ["S03", "S11", "S05", "S01"]]
  }
]
```

For each proposal, `score.py` checks that every word exists in the corpus and that
stem + ending reproduces it exactly; for every pair of the proposal's own distinct
endings it looks up the alternation support `kober.paradigms` defines (the number of
stems in the whole corpus carrying both endings) and compares it against the 99th
percentile of the N2 null's maximum-support distribution for that corpus (200 draws,
seed 0 by default — the same null `kober.report.build_report` runs via
`kober.nulls.run_n2`, and the same comparison `docs/ai_context/kober-method.md` uses to
read the top of a ranked list against the top of a null list). A proposal's own headline
`support` is the weakest of its pairs (a paradigm with more than two endings, one of
Kober's triplets, is only as strong as its worst-supported pair); `any_above`/`all_above`
are also reported per proposal for the more and less generous readings. `score.py` also
computes the instrument's own top-n alternations for the same corpus, scored the same
way, so a run's proposals can be read against the instrument's own ranking — the
comparison the brief's question turns on.

Output is a JSON report to stdout (and to `--out` if given): aggregate counts, plus the
already-small, already-disclosed proposal and top-n content — never the corpus's full
word list.

## Tests

`.venv/bin/python -m pytest tests/test_s007_score.py -q` — on a tiny synthetic corpus,
never real corpus data.
