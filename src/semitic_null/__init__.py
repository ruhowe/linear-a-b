"""How much does a Semitic reading of Linear A actually constrain?

This package tests a specific, public, falsifiable claim: Di Mino (2026), *Ya Diktu*
(Zenodo 10.5281/zenodo.22129502, CC BY 4.0), which reads Linear A as an archaic Semitic
language and supplies Semitic comparanda for the Linear A sign-groups listed in Davis
(2026). The question asked here is **not** "is Minoan Semitic?" — which no statistic can
answer — but the prior question the field requires before any such reading counts as
evidence:

    Given the phonological freedom the method allows, how often would an
    *arbitrary* sign-value assignment produce comparably good Semitic matches?

This is Packard's (1974) instrument, applied to Linear A fifty years ago and since
dropped: score the proposed decipherment against **fictitious decipherments** built by
randomly reassigning sound values, and see whether the real one stands out. It is the
same logic as Raghavendra's SIGIL (2026) for the Indus script, and the same objection
Sproat (2014) raised and Rao conceded for entropy measures.

**The test can exonerate.** If the real assignment matches Semitic roots far more often
than permuted assignments do, that is evidence *for* the hypothesis, and it would be the
first such evidence anyone has produced — including its author, who released no code.

**What this cannot do.** It says nothing about whether the individual readings are good
Semitic philology: whether a tG-stem parse is sound, whether an energic nun is plausible
in this position. That needs a Semitist. This measures only the size of the haystack.

Resources, both openly licensed:

- Strong's *Concise Dictionary of the Words in the Hebrew Bible* (1894), public domain;
  JSON edition CC BY-SA by Open Scriptures. 8,674 entries → consonantal skeletons.
- Linear A corpus via pyaegean (GORILA transcription chain — see corpus-sources.md).

Hebrew is the right comparison lexicon because it is what the claim itself leans on most
heavily: the paper cites Biblical Hebrew throughout, by BHS page number.
"""

from __future__ import annotations

__all__ = ["lexicon", "phonology", "experiment"]
