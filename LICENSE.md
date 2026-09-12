# Licences

Copyright © 2026 Ru Howe. Two licences, by path.

| what | paths | licence |
|---|---|---|
| Code | every `.py` file: `src/`, `scripts/`, `tests/`, `spikes/**/*.py` | MIT (below) |
| Everything else | every other file, including `README.md`, `START-HERE.md`, `REPRODUCING.md`, `CONTRIBUTING.md`, `CLAUDE.md`, `CITATION.cff`, `FINDINGS.md`, `ASSUMPTIONS.md`, `CHANGELOG.md`, `JOURNAL.md`, `TODO.md`, the requirements files, `data/README.md`, `docs/` (findings, reports, guides, catalogue pages and the HENGE files), `results/`, and the non-code files in `spikes/` | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |

A file the first row does not cover falls under the second. Reuse anything here in any
project, commercial or not, with credit, and keep adaptations under the same licence.
Short quotations from published works in the prose are attributed and used for criticism
and review.

## Results released under a commercial-permitting licence: the decision and its one exception

Three sources used here are NonCommercial: DĀMOS and SigLA (CC BY-NC-SA 4.0) and the
Copenhagen Ugaritic Corpus (CC BY-NC). The results in this repository are released under
CC BY-SA 4.0, which permits commercial reuse. That is a deliberate decision, taken on
2026-09-12, and this is the reasoning.

A Creative Commons licence conditions what copyright covers: copies of the licensed
material and adaptations that incorporate it. The files under `results/` and the spike
results hold measurements about the corpora (counts, percentiles, z-scores, null
distributions, and sign-label pairs such as JA/JO with the number of stems supporting
them). Measurements are facts about a text and carry this repository's licence. Apart
from the exception below, the repository stores no corpus text: pyaegean fetches the corpora to `~/.cache/pyaegean/`,
and every dataset built from them (sequences, samples, word lists) is written to
`~/.cache/linear-a-b/`. This is the author's reading of the licences; no rights holder
has been asked.

**The one exception.** The value-transfer test (FINDINGS F-041) stores the word forms it
tested and the words that matched, so that the test can be checked by hand. They are in
the `toponym_test*` files under `results/` and `results/supplement-sensitivity/` and in
the lexicon inside `scripts/toponym_test.py`; the S-003 and S-003b spike write-ups quote
some of them. Counted from the files:

- 54 place-name readings from the Linear B tablets, 33 at Knossos and 21 at Pylos (for
  example `pa-i-to`, `ko-no-so`), including three recorded as dropped from the test with
  the reason, each cited to Ventris and Chadwick 1973 or Packard 1974;
- 32 frequent Knossos personal names, stored as sign sequences with their DĀMOS
  frequencies, used as a wrong-lexicon control;
- 10 Linear A sign sequences, the words on the Linear A side of each match as the GORILA
  chain and SigLA transcribe them: seven that match Knossos place names (DA-TA-RA,
  DA-TA-RE, PA-I-TO, SE-TO-I-JA, SU-KI-RI-TA, SU-KI-RI-TE-I-JA, and SigLA's SU-KI-RA-TA),
  two that match the Pylos control (A-SI-JA-KA, SA-MA-RO), and one undivided sixteen-sign
  group that matches a personal name. The identities pa-i-to, se-to-i-ja and su-ki-ri-ta
  are the standard published readings (Packard 1974).

These are a few dozen items from corpora of 54,476 and 6,406 words, included for
verification and criticism. They are the only word forms in the repository's data
files; the prose documents quote some of the same readings when discussing them.
`tests/test_word_forms.py` fails if a word-shaped field appears in any other results or
spike file, or if these counts stop matching the files. If a rights holder objects, the
forms will be replaced by index numbers.

## Sources, not included, and their terms

- **DĀMOS**, Database of Mycenaean at Oslo. CC BY-NC-SA 4.0. Aurora, F. (2015),
  "DAMOS (Database of Mycenaean at Oslo). Annotating a fragmentarily attested language",
  *Procedia, Social and Behavioral Sciences* 198, 21–31.
- **GORILA**, through a volunteer transcription chain. Godart, L. and Olivier, J.-P.
  (1976–1985), *Recueil des inscriptions en linéaire A*, © École française d'Athènes. The
  texts reach this project as GORILA → George Douros's tabulation → mwenge/lineara.xyz →
  pyaegean. pyaegean's metadata asserts Apache-2.0 over its corpus JSON; the mwenge
  repository states no licence; whether an open licence can attach to a transcription of
  the edition is an open question, recorded in
  [docs/ai_context/corpus-sources.md](docs/ai_context/corpus-sources.md). Accordingly
  nothing from this chain is redistributed here beyond the ten matched Linear A sign
  sequences named in the exception above, and no facsimile imagery is used.
- **SigLA**, The Signs of Linear A. CC BY-NC-SA 4.0. Salgarella, E. and Castellan, S.
  (2020), https://sigla.phis.me.
- **Reference lexicons**, fetched by `scripts/fetch_reference.py` to
  `~/.cache/linear-a-b/reference/`: Strong's Hebrew (1894, public domain); Perseus
  canonical Greek and LSJ (CC BY-SA); ORACC Akkadian (CC BY-SA 3.0) and ePSD2 Sumerian
  (CC0); the Copenhagen Ugaritic Corpus (CC BY-NC); the kaikki.org Wiktionary extract for
  Hittite (CC BY-SA); FrequencyWords 2018 by Hermit Dave, whose code is MIT and whose word
  lists are CC BY-SA 4.0, built from OpenSubtitles subtitle files.
- **pyaegean** 0.59.0 by Ryan Pavlicek, the toolkit that loads the corpora. Code
  Apache-2.0.

## MIT licence (code)

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
