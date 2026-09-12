"""Hebrew consonantal roots from Strong's, and the density of the root space.

Semitic lexical roots are consonantal skeletons, canonically triliteral. The single most
important number for judging any Semitic reading of an undeciphered script is therefore
**what fraction of possible skeletons are attested roots**, because that is the base rate
a match has to beat.

Measured from Strong's 8,674 entries: 2,111 distinct triliteral skeletons over a
22-consonant inventory. 22³ = 10,648 possible, so **19.8% of the space is occupied**
before any phonological allowance is made. A skeleton drawn at random is a real Hebrew
root about one time in five.

Source: Strong's *Concise Dictionary of the Words in the Hebrew Bible* (1894), public
domain; JSON edition by Open Scriptures, CC BY-SA. Cached outside the repo.
"""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

__all__ = ["HEBREW_CONSONANTS", "Lexicon", "load_lexicon", "skeleton"]

# Hebrew consonant → an ASCII-safe transliteration key. Final forms fold to their base.
# Multi-character symbols are avoided so a skeleton is one character per consonant.
HEBREW_CONSONANTS: dict[str, str] = {
    "א": "ʾ",  # alef
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "ה": "h",
    "ו": "w",
    "ז": "z",
    "ח": "H",  # het
    "ט": "T",  # tet (emphatic)
    "י": "y",
    "כ": "k", "ך": "k",
    "ל": "l",
    "מ": "m", "ם": "m",
    "נ": "n", "ן": "n",
    "ס": "s",  # samekh
    "ע": "O",  # ayin
    "פ": "p", "ף": "p",
    "צ": "S", "ץ": "S",  # tsade (emphatic)
    "ק": "q",
    "ר": "r",
    "ש": "C",  # shin/sin — Strong's lemmas do not reliably distinguish them
    "ת": "t",
}


def skeleton(hebrew_word: str) -> str:
    """Strip vowel points, cantillation and punctuation; return the consonant skeleton."""
    decomposed = unicodedata.normalize("NFD", hebrew_word)
    return "".join(HEBREW_CONSONANTS[c] for c in decomposed if c in HEBREW_CONSONANTS)


@dataclass(frozen=True, slots=True)
class Lexicon:
    """Attested Hebrew consonantal skeletons, indexed by length."""

    by_length: dict[int, frozenset[str]]
    counts: dict[str, int]
    inventory: frozenset[str]
    n_entries: int

    def attested(self, skel: str) -> bool:
        return skel in self.by_length.get(len(skel), frozenset())

    def density(self, length: int = 3) -> float:
        """Fraction of the possible skeleton space of this length that is attested.

        The base rate any Semitic match has to beat. ~0.198 at length 3.
        """
        possible = len(self.inventory) ** length
        return len(self.by_length.get(length, ())) / possible if possible else 0.0

    def summary(self) -> dict:
        return {
            "entries": self.n_entries,
            "consonant_inventory": len(self.inventory),
            **{
                f"skeletons_len{n}": len(self.by_length.get(n, ()))
                for n in sorted(self.by_length)
                if 2 <= n <= 4
            },
            "density_len3": self.density(3),
            "density_len2": self.density(2),
            "density_len4": self.density(4),
        }


def load_lexicon(path: str | Path | None = None, *, min_len: int = 2, max_len: int = 5) -> Lexicon:
    """Parse the Open Scriptures Strong's Hebrew JSON into a skeleton index.

    The file is a JS module wrapping a JSON object, so the object is sliced out by brace
    position rather than by executing anything.
    """
    if path is None:
        path = Path.home() / ".cache" / "linear-a-b" / "reference" / "strongs-hebrew.json"
    raw = Path(path).read_text(encoding="utf-8")
    obj = raw[raw.index("{") : raw.rindex("}") + 1]
    data = json.loads(obj)

    counts: Counter[str] = Counter()
    for entry in data.values():
        lemma = entry.get("lemma") or ""
        skel = skeleton(lemma)
        if min_len <= len(skel) <= max_len:
            counts[skel] += 1

    by_length: dict[int, set[str]] = {}
    for skel in counts:
        by_length.setdefault(len(skel), set()).add(skel)

    inventory = frozenset("".join(counts))
    return Lexicon(
        by_length={k: frozenset(v) for k, v in by_length.items()},
        counts=dict(counts),
        inventory=inventory,
        n_entries=len(data),
    )
