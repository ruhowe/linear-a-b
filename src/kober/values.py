"""Consonant of a Linear B sign label under Ventris's known values (A-048).

This is the only place a sound value enters the Kober-method grid stage (protocol
0.1 stage 2, CHANGELOG). It runs *after* the grid is computed: ``grid.py`` builds
bridging pairs and sign classes from sign identity and position alone, with no
value anywhere in that computation; this module is consulted only afterwards, to
check what the value-free result recovers against Ventris's 1952 values.

A label's consonant: strip trailing digits (the subscript index, e.g. ``RA2`` ->
``RA``), then drop the final vowel letter (``A E I O U``). A remainder of zero
letters is a pure vowel sign, whose consonant is the empty string ``""``; every
pure vowel sign shares it with every other one, mechanically, because they have
no consonant to differ on. A remainder of more than one letter (``TWO`` ->
``TW``, ``DWE`` -> ``DW``, ``NWA`` -> ``NW``) is kept whole, not truncated to its
first letter, so ``TWO`` and ``TO`` do not count as sharing "T" alone.

A label is excluded (``consonant_of`` returns ``None``) if it contains GORILA's
or DAMOS's ``*`` unidentified-sign marker, or if it does not end in one of
``A E I O U`` after the digit strip. Callers must count and report exclusions
rather than silently drop them (CHANGELOG "0.1 stage 2, the grid").
"""

from __future__ import annotations

import re

__all__ = ["consonant_of"]

_VOWELS = "AEIOU"
_TRAILING_DIGITS = re.compile(r"\d+$")


def consonant_of(label: str) -> str | None:
    """The consonant of a Linear B sign label under the known values, or None.

    ``None`` means the label is excluded: it carries ``*`` (unidentified sign),
    or it does not end in a vowel letter once trailing digits are stripped.
    """
    if not label or "*" in label:
        return None
    stripped = _TRAILING_DIGITS.sub("", label)
    if not stripped or stripped[-1] not in _VOWELS:
        return None
    return stripped[:-1]
