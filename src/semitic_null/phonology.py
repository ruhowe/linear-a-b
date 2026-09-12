"""Linear A syllabograms → the Hebrew consonants a Semitic reading may map them to.

The Aegean syllabary is a poor fit for Semitic phonology, and the mismatch is the whole
issue. Each Linear A/B syllabogram writes a consonant-vowel pair, but the consonant
series **neutralise distinctions Semitic treats as contrastive**. Under the reading being
tested, and following its own stated conventions, one sign therefore stands for a *set*
of possible Hebrew consonants:

===========  ===============================  ==================================
Series       May write                        Why
===========  ===============================  ==================================
vowel-only   ʾ, ʿ, h, ḥ                       The script writes no laryngeals or
                                              pharyngeals; a vowel sign carries any
d-           d, ḏ, ṭ                          No voicing or emphasis contrast
t-           t, ṭ, ṯ, d, ṣ                    Emphatic neutralisation is invoked
                                              explicitly (e.g. ṣ → t in the T-series)
k-, q-       k, g, q, ḥ                       Velar/uvular series conflated
p-           p, b                             No voicing contrast
s-, z-       s, š, ś, ṣ, z                    Three-way sibilant merger, invoked
                                              explicitly (SA-SA for /š/)
r-           r, l                             Linear B r- writes both; a fact about
                                              the script, not an allowance
m-, n-       m / n                            Clean
w-, j-       w / y                            Clean
===========  ===============================  ==================================

The r/l merger is not a concession by the author: the Aegean syllabary genuinely has no
l-series. The sibilant and emphatic mergers are argued for in the paper. Either way they
are load-bearing, because they multiply the number of Hebrew roots any given Linear A
word can reach.

Consequence, and the reason this module exists: a three-sign Linear A word does not
propose one Semitic skeleton. It proposes the **cross-product** of its per-sign consonant
sets — routinely dozens of candidate roots — and the reading succeeds if *any* of them is
attested. Against a root space that is already ~20% occupied, that is a very low bar, and
this package measures how low.

Consonant keys match ``lexicon.HEBREW_CONSONANTS``: H=ḥet, T=ṭet, O=ayin, S=tsade,
C=shin/sin, ʾ=alef.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SERIES_TO_HEBREW", "consonant_series", "ConsonantMap", "default_map"]

# Linear B/A consonant series → Hebrew consonants it could plausibly write, under the
# conventions the tested reading itself adopts.
SERIES_TO_HEBREW: dict[str, frozenset[str]] = {
    "": frozenset({"ʾ", "O", "h", "H"}),   # vowel-initial sign: any laryngeal/pharyngeal
    "d": frozenset({"d", "T"}),
    "t": frozenset({"t", "T", "d", "S"}),
    "k": frozenset({"k", "g", "q"}),
    "q": frozenset({"k", "g", "q"}),
    "p": frozenset({"p", "b"}),
    "s": frozenset({"s", "C", "S", "z"}),
    "z": frozenset({"z", "S", "s"}),
    "m": frozenset({"m"}),
    "n": frozenset({"n"}),
    "r": frozenset({"r", "l"}),            # the syllabary has no l-series
    "l": frozenset({"l", "r"}),
    "w": frozenset({"w"}),
    "j": frozenset({"y"}),
    "y": frozenset({"y"}),
}

_VOWELS = set("aeiou")


def consonant_series(phonetic: str) -> str | None:
    """The consonant series of a syllabogram's conventional value (``ka`` → ``k``).

    Returns ``""`` for a pure-vowel sign (``a``, ``i``), which is meaningful rather than
    empty: such a sign may stand for a laryngeal. Returns ``None`` when the value is
    unusable — an undeciphered ``*301``-type label, or anything unparseable.
    """
    if not phonetic:
        return None
    value = phonetic.strip().lower()
    if not value or value.startswith("*") or not value.isalpha():
        return None
    # Strip the vowel nucleus; the remainder (possibly empty) is the onset.
    onset = "".join(ch for ch in value if ch not in _VOWELS)
    if onset == "":
        return ""
    if len(onset) > 2:
        return None
    # Digraph onsets (e.g. "nwa") are not part of the tested system; take the first.
    return onset[0]


@dataclass(frozen=True, slots=True)
class ConsonantMap:
    """Sign label → the set of Hebrew consonants it may write.

    ``permute`` produces a *fictitious decipherment* in Packard's (1974) sense: the same
    multiset of consonant sets, redealt among the same signs. Word structure, sign
    frequencies and the size of every candidate set are all preserved; only which sound
    goes with which sign is destroyed. That is precisely the assumption under test.
    """

    mapping: dict[str, frozenset[str]]

    def get(self, sign: str) -> frozenset[str] | None:
        return self.mapping.get(sign)

    def covered(self, signs) -> bool:
        return all(s in self.mapping for s in signs)

    def permute(self, rng) -> "ConsonantMap":
        keys = sorted(self.mapping)
        values = [self.mapping[k] for k in keys]
        rng.shuffle(values)
        return ConsonantMap(dict(zip(keys, values)))


def default_map(inventory) -> ConsonantMap:
    """Build the sign→consonant-set map from a pyaegean sign inventory.

    Only signs carrying a conventional phonetic value are included — the ~50 Linear A
    signs read with Linear B values. Undeciphered ``*NNN`` signs are excluded, which is
    conservative: the tested reading assigns values to several of them (``*301`` = /na/
    being the load-bearing case), and admitting those would add freedom, not remove it.
    """
    mapping: dict[str, frozenset[str]] = {}
    for sign in inventory.signs:
        series = consonant_series(getattr(sign, "phonetic", "") or "")
        if series is None:
            continue
        options = SERIES_TO_HEBREW.get(series)
        if options:
            mapping[sign.label] = options
    return ConsonantMap(mapping)
