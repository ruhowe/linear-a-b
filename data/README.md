# data/

**This directory holds nothing derived from either corpus, by design.**

DĀMOS (Linear B) is CC BY-NC-SA 4.0 — NonCommercial, ShareAlike, attribution required.
The Linear A transcription chain has an unresolved licence (GORILA → Douros → mwenge →
pyaegean; see [corpus-sources.md](../docs/ai_context/corpus-sources.md)). Committing
corpus content, or a dataset derived from it, would redistribute licensed material
under this repository's terms.

So:

| What | Where it lives |
|---|---|
| Fetched corpora | `~/.cache/pyaegean/` (pyaegean's own cache; never bundled in the wheel) |
| Sequences, masked datasets, split manifests, model artifacts | `~/.cache/linear-a-b/` (override with `LINEARB_RESTORE_CACHE`) |
| Downloaded reference data and working copies | `~/.cache/linear-a-b/reference/` |
| Local working files | `private/` at the repo root, gitignored |
| Code, aggregate metrics, counts-by-rule, results tables | this repository |

[REPRODUCING.md](../REPRODUCING.md) says which of these a clean download builds on its
own; `scripts/fetch_reference.py` fetches the open reference data.

Aggregate figures are safe to publish: corpus sizes, vocabulary counts, per-subseries
document counts, accuracy tables. Token lists and reconstructed text are not.

Cite DĀMOS as: Aurora, F. (2015), *Procedia — Social and Behavioral Sciences* 198,
21–31. `Corpus.cite()` returns the current citation string.
