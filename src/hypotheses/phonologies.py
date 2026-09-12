"""Sign-to-phoneme maps, one per hypothesis.

Each hypothesis implies a different answer to the same question: if this Linear A sign
were read aloud, which sounds in the candidate language could it stand for? The answer
differs because languages contrast different things, and the Aegean syllabary neutralises
many of those contrasts.

The width of these sets is the hypothesis's degrees of freedom, and it is the quantity
the null model exists to price. A hypothesis whose signs each stand for four possible
consonants reaches far more dictionary entries than one whose signs stand for one, and
will match more often whether or not it is correct.

Measured widths, on the 50 Linear A signs carrying a conventional value:

- Semitic: mean 2.7 options per sign, because the script cannot write the sibilant,
  emphatic and laryngeal contrasts Semitic treats as phonemic.
- Greek: mean 1.5, because Linear B was designed for Greek and writes it adequately.

That gap is the point. Greek is the harder hypothesis to satisfy by luck, which is
exactly what makes it the control worth running.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from semitic_null.phonology import (  # noqa: E402
    SERIES_TO_HEBREW,
    ConsonantMap,
    consonant_series,
)

__all__ = ["SERIES_TO_GREEK", "PHONOLOGIES", "build_map"]

# Linear B was built to write Greek, so these correspondences are the deciphered values
# rather than a proposal. Aspirates fold to their plain stop because the syllabary does
# not write aspiration; voicing folds for the same reason, except that Linear B keeps a
# separate d-series.
#
# A vowel-only sign maps to the empty set: Greek has no laryngeal or pharyngeal
# consonants, so a word-initial vowel contributes nothing to a consonant skeleton. This
# is the structural reason Greek is more constrained than Semitic here, and it is a fact
# about Greek rather than a handicap imposed on it.
SERIES_TO_GREEK: dict[str, frozenset[str]] = {
    "": frozenset(),
    "d": frozenset({"d"}),
    "t": frozenset({"t"}),           # τ and θ both fold to t
    "k": frozenset({"k", "g"}),      # κ, γ, χ
    "q": frozenset({"k", "g", "p", "b"}),  # labiovelar, resolves several ways
    "p": frozenset({"p", "b"}),      # π, β, φ
    "s": frozenset({"s"}),
    "z": frozenset({"z", "s"}),
    "m": frozenset({"m"}),
    "n": frozenset({"n"}),
    "r": frozenset({"r", "l"}),      # the syllabary has no l-series
    "l": frozenset({"l", "r"}),
    "w": frozenset({"w"}),           # digamma, absent from Koine — see lexicons.greek_nt
    "j": frozenset(),                # glide, not in the Greek consonant skeleton
    "y": frozenset(),
}

PHONOLOGIES = {
    "semitic_consonantal": SERIES_TO_HEBREW,
    "greek_syllabic": SERIES_TO_GREEK,
}


def build_map(inventory, phonology: str) -> ConsonantMap:
    """Build the sign-to-phoneme map for one hypothesis from a pyaegean sign inventory.

    Only signs carrying a conventional phonetic value are included, which is 50 of the
    342 Linear A signs. Undeciphered ``*NNN`` signs are excluded throughout: they have no
    value to permute, and admitting the values a proposal assigns them would hand the
    hypothesis freedom the null could not match.

    Signs mapping to an empty phoneme set are kept, since contributing nothing to a
    skeleton is a real prediction rather than a gap.
    """
    series_map = PHONOLOGIES.get(phonology)
    if series_map is None:
        raise KeyError(f"No phonology registered for {phonology!r}")

    mapping: dict[str, frozenset[str]] = {}
    for sign in inventory.signs:
        series = consonant_series(getattr(sign, "phonetic", "") or "")
        if series is None:
            continue
        options = series_map.get(series)
        if options is not None:
            mapping[sign.label] = options
    return ConsonantMap(mapping)
