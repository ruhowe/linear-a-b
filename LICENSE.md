# Licences

Copyright © 2026 Ru Howe. Two licences, by path.

| what | paths | licence |
|---|---|---|
| Code | `src/`, `scripts/`, `tests/`, `spikes/**/*.py`, `data/README.md` | MIT (below) |
| Everything else: findings, assumptions, changelog, journal, reports, guides, catalogue pages, the AI-context files including the HENGE index, and the results | `FINDINGS.md`, `ASSUMPTIONS.md`, `CHANGELOG.md`, `JOURNAL.md`, `TODO.md`, `README.md`, `docs/`, `results/`, `spikes/**/*.md`, `spikes/**/*.json` | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |

Reuse anything here in any project, commercial or not, with credit, and keep adaptations
under the same licence. Short quotations from published works in the prose are
attributed and used for criticism and review.

## Why the corpus terms do not reach the results

The source corpora below are licensed CC BY-NC-SA 4.0 (DĀMOS, SigLA) and are not
redistributed here. A Creative Commons licence conditions only what copyright covers:
its ShareAlike term applies to adapted material, meaning works that incorporate the
licensed text. The files under `results/` and the spike results hold counts,
percentiles, sign-label pairs with supports, and a few matched place names that are
published readings; those are measurements about the corpora, not copies or
adaptations of them, so they carry this repository's licence. What would bring the
corpus terms into play is storing corpus text or a substantial extract of it, which the
repository never does: pyaegean fetches the corpora to `~/.cache/pyaegean/` and this
project writes derived data to `~/.cache/linear-a-b/`.

## Sources, not included, and their terms

- **DĀMOS**, Database of Mycenaean at Oslo. CC BY-NC-SA 4.0. Aurora, F. (2015),
  "DAMOS (Database of Mycenaean at Oslo). Annotating a fragmentarily attested language",
  *Procedia, Social and Behavioral Sciences* 198, 21–31.
- **GORILA** transcriptions via mwenge/lineara.xyz. Corpus JSON Apache-2.0; facsimile
  imagery © École française d'Athènes, not redistributed. Godart, L. and Olivier, J.-P.
  (1976–1985), *Recueil des inscriptions en linéaire A*.
- **SigLA**, The Signs of Linear A. CC BY-NC-SA 4.0. Salgarella, E. and Castellan, S.
  (2020), https://sigla.phis.me.
- **pyaegean** 0.59.0, the toolkit that loads them; see its own licence.

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
