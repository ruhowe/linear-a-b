# A brief for a specialist reader

Written 2026-09-12 for whoever in the field first reads this repository. Not peer reviewed.
It says what the repository claims, where each claim can be checked, and what a
specialist can see that its authors cannot. Every number below is quoted from a
FINDINGS entry; nothing here is new.

## What the repository is

A statistical review of two methods for reading Linear A, run on the corpus as it
can currently be loaded (GORILA through the pyaegean transcription chain, which carries 89
of the 2024 supplement's 107 documents and lacks the 2025 Anetaki ring, A-003 and F-047;
and SigLA as a second edition) with Linear B as the
control script where the answer is known. Results are dated, versioned and tagged
(`FINDINGS.md`, F-nnn); each protocol version is pre-registered in `CHANGELOG.md` before it
runs, and where the design changed after results were in, the change is a new version
with its reason recorded (the Kober answer key was rebuilt twice, F-031 and F-034; spikes
are exploratory and run under their own rules); every assumption is a numbered row in `ASSUMPTIONS.md`. The eight claims and the
prior-art ledger are in `docs/ai_context/claims.md`; the plain-English version is
`docs/guides/what-we-found.md`.

## The claims, and what to check in each

1. **Dictionary matching cannot choose a language (C-1, F-008, F-013).** Wrong real
   languages match Linear A, and Linear B, about as well as any candidate. *Check:* the
   consonant-skeleton matching rules and the Mycenaean spelling expansion (protocol 1.0,
   `docs/ai_context/hypothesis-harness.md`); whether the wrong-language lexicons are
   fair; whether the value-permutation null (Packard's) is the right null.
2. **The Semitic signal is dictionary shape (C-2, F-012).** *Check:* the laryngeal
   ablation and the two dictionary formats.
3. **Kober's method works by machine (C-3, F-016, F-021, F-030, F-032).** *Check:* the
   reference list of Mycenaean alternations in `src/kober/reference.py`, rebuilt from
   Ventris and Chadwick 1973's morphology chapter (v3). It is hand-built and it is the
   biggest lever in the calibration (F-034, F-046). A specialist will find errors and
   omissions in it in an hour; each one changes a count.
4. **Linear A has stem-and-ending structure, weaker than Greek's at the same size (C-4,
   F-019, F-022, F-023).** *Check:* whether "word type" and "ending of one or two signs"
   are the right units for Linear A; whether the divider is the word boundary (A-002).
5. **The corpus-size floor depends on the instrument (C-5, F-022, F-046).** *Check:*
   the bar (sixteen of twenty), the tablet-model subsampling, and the homophone merge
   (a2, ra2 and the rest folded to base signs), which uses knowledge from the
   decipherment.
6. **Linear B restoration sits near a floor (C-6, F-001, F-002).** *Check:* the
   comparison framing against the published neural results.
7. **Measurements on di Mino 2026 (C-7, F-010).** *Check:* the count of signs resting on
   values Meißner and Steele list as demonstrably shared.
8. **The transferred values have positive evidence for a dozen signs (C-8, F-041).**
   Knossos place names match Linear A words beyond a permutation null on both editions,
   and three wrong lexicons do not. *Check:* the toponym list (32 names cited to Ventris
   and Chadwick and Packard's Table 11), the Pylos control list, and whether label
   identity is the right definition of the transfer (A-135). This is the one positive
   result and it rests on five words.

## What a specialist can see that we cannot

- Whether the answer key (item 3) is right. It was written from a handbook by a
  non-specialist and corrected twice.
- Whether the toponym lists (item 8) are complete and correctly read.
- Whether the loader's edition of Linear A is trustworthy. It is a volunteer
  transcription chain (`docs/ai_context/corpus-sources.md`); F-045 measures its
  disagreement with SigLA and F-047 its coverage against the 2024 supplement.
- Whether any of the eight claims is already in print. The prior-art ledger was searched
  by machine and graded by the authors; `claims.md` says what "ours" means for each atom
  and lists the leads not yet read.

## What the repository does not claim

The claims stop short of any reading of a Linear A word, any language, and any sound
value beyond the thirteen signs in item 8, all of which the field already held secure. The etymological method is
closed here as a false-positive instrument (F-020), and the Kober method on Linear A
finds structure at or below Greek's low end with alternation support at the null. The
honest summary is in `docs/guides/what-we-found.md`.

## How to check a number

```
.venv/bin/python scripts/findings.py --show F-041      # one finding, with its protocol
.venv/bin/python scripts/findings.py --assumption A-001 # everything resting on one assumption
.venv/bin/python -m pytest -q                            # the regression pins
```

Results files under `results/` carry aggregate numbers only; the corpora are fetched by
pyaegean under their own licences and never stored here.
