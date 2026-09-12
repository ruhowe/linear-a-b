# Terminology

The two methods this project tests, with the shorthand names used everywhere in the
repository. Use these names and no others in FINDINGS, CHANGELOG, ASSUMPTIONS, HENGE
files, work pages and commit messages. Older documents that say "lexicon matching" or
"the matching instrument" mean the etymological method.

| Shorthand | What it is | Where it lives here |
|---|---|---|
| **Etymological method** | Assign sound values to the signs, then look the resulting words up in a candidate language's dictionary. A high match rate is taken as evidence of affiliation. The method behind almost every proposed Linear A decipherment. Duhoux and Davis use the name, usually critically; Packard's "fictitious decipherments" are its failure mode. Also called lexical or dictionary matching | `src/semitic_null/` (protocols 0.1 to 0.2), `src/hypotheses/` and `scripts/controlled_comparison.py` (0.3 onward); HENGE files `semitic-null-test.md`, `hypothesis-harness.md`; FINDINGS F-003 to F-015 |
| **Kober method** | Find grammatical structure from sign patterns alone, before any sound value is assigned: stems that recur with different endings, position rules, paradigms. Alice Kober did this on Linear B in the 1940s and Ventris built on it. Also called internal, structural, combinatory or morphological analysis; computationally, unsupervised morphology or paradigm induction | `src/kober/` and `scripts/kober_run.py`; HENGE file `kober-method.md`; FINDINGS F-016 to F-020 |

The two are not rivals for the same question. The etymological method asks *which
language*; the Kober method asks *what structure*, and only later whether that structure
matches a language. The project's finding so far (F-008, F-012, F-013) is that the
etymological method cannot answer its question on this corpus. The Kober method answers
its own on Linear B (F-016) and, on Linear A, gives one sentence and then runs out of
corpus (F-019, F-020).

Other terms used with a fixed meaning:

| Term | Meaning here |
|---|---|
| **Map** | A rule from each sign to the set of consonants it may write. Two exist: the Semitic map and the Greek map. z-scores are comparable only within one map (A-012) |
| **Wrong real language** | A lexicon of a language nobody proposes for Linear A (Finnish, Turkish, Basque, Hungarian, Sumerian), used as the bar a hypothesis has to clear. Not the same as a synthetic control |
| **Synthetic twin** | A random lexicon with the same length profile and consonant frequencies as a real one. A noise control only; every real language beats it (A-011) |
| **Positive control** | Linear B under the Greek map: the case where the answer is known. Shows recognition given the values, not discovery (A-032) |
| **Protocol version** | A frozen configuration of an instrument, numbered in CHANGELOG. Changing any component is a new version |
| **Answer key** | The list of known-correct structures a positive control is scored against: for the Kober method, the reference list of Mycenaean alternations, versioned (v1 from memory, v2 with the ethnic derivation from Kober 1946, v3 from Ventris and Chadwick 1973). Consulted after the ranking, never before |
| **Floor** | The corpus size at which an instrument's criterion is met in sixteen of twenty subsamples of the deciphered corpus (F-022). Measured, per model of subsampling; never assumed |
| **Edition** | A transcription of the Linear A corpus with its own word division and readings: GORILA (via pyaegean's `lineara`) and SigLA. A structural result is edition-independent only if both give it (F-023) |
| **Exploratory** | A FINDINGS status for a run made outside a pre-registered gate (F-033) or from `spikes/`. Never current; quoted by no claim |
| **Spike** | An experiment in `spikes/`, under that folder's rules: brief first, controls travel, never edits `src/`, promotion is a rebuild |
