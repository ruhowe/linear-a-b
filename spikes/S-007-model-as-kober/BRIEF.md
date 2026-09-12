# S-007 · A model as Kober: paradigm hypotheses from a frontier model, scored by the nulls

**Question.** Kober found her triplets by eye from under 750 word types. A frontier
language model given Linear A word types as sign labels, with no sound values and no
Linear B, proposes paradigms the way she did. Scored by the instrument's nulls, are its
proposals better than the instrument's own ranking, and better than the same model's
proposals on a shuffled corpus?

**Why a spike.** It tests a reader, not a corpus. The model has read the literature on
Linear A, so its proposals may be recall rather than analysis; the shuffled-corpus
control and a label-permuted corpus (the same words with sign labels renamed by a
random bijection, so nothing it has read applies) are what separate the two. If the
label-permuted run still finds structure the instrument misses, that is a method
result about human-style pattern finding at small sizes, and would deserve a rebuild.

**Method.** Three corpora: GORILA's 988 word types as labels; the same labels permuted
by a seeded bijection; a column-shuffled null corpus (N1 draw). Same prompt to a
frontier model (claude-fable-5-1) three times per corpus: propose up to ten stem-plus-
ending paradigms with their supporting words. Score each proposal by its support in
the corpus and by the N2 null (`kober.nulls`), and by the strict grammar-match rule
where Linear B is used as a fourth, calibration corpus (988-type tablet subsample, v3
key). The model's outputs are private (they contain word lists); the repo gets counts.

**Interesting.** On the label-permuted Linear A the model's top proposals have supports
above the N2 99th percentile more often than the instrument's top ten do, and on the
shuffled corpus they do not. **Nothing.** The model's proposals are at the null on the
permuted corpus and above it only on the labelled one, which is recall; or they are
never above it.

**Must not be read as.** A reading of Linear A. Anything the model says about meaning or
language is discarded unscored.
