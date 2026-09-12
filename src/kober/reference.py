"""The Linear B reference alternation list and grammar matcher (A-037).

``REFERENCE_ALTERNATIONS`` is the table from ``docs/ai_context/kober-method.md``,
quoted verbatim as data — drawn from Ventris and Chadwick 1973 (verification P),
written from Mycenaean grammar after the sizing glimpse (see the CHANGELOG entry
for the disclosure). It is documentation, reproduced for the report; it is not
what ``is_grammar`` matches against.

``is_grammar`` implements the rules from that table algorithmically, over
**decomposed sign labels**, so it works on any ending pair the paradigm code
produces rather than on a fixed literal list. A sign label decomposes to
``(consonant, vowel)`` by its final letter: ``TO`` -> ``("T", "O")``, ``U`` ->
``("", "U")``. A label that does not end in one of ``A E I O U``, or that contains
``*`` (GORILA's unidentified-sign marker), does not decompose and cannot match any
rule.

Rules are tried in the fixed order below and the **first** match is returned.
Rule 1 (gender) subsumes some cases nominally described by rule 2 (adjective) and
by rule 8 (participle) — an ending pair like ``-no``/``-na`` fits the generic
same-consonant, o/a-vowel pattern of rule 1 whether or not it is also literally a
participle. This is expected, not a bug: the rules are not mutually exclusive, and
reporting the first match is the pre-registered tie-break.

**Rule 11, ethnic derivation (Kober 0.6, CHANGELOG "0.6", A-037).** Added after
rules 1 to 10, gated behind ``is_grammar``'s ``version`` parameter so every
existing result stays reproducible: ``version=1`` (the default) runs only rules 1
to 10, byte-identical to the pre-0.6 behaviour; ``version=2`` also tries rule 11,
last, after the first ten have all failed to match. The rule is the pattern
kober1946 built Cases I to III on: X-so / X-si-jo, X-so / X-si-ja, X-to / X-ti-jo,
X-to / X-ti-ja, i.e. ``e2 == e1[:-1] + (Ci, "JO")`` or ``e1[:-1] + (Ci, "JA")``,
where e1's final sign ``Co`` has vowel o, and ``Ci`` has the same consonant as
``Co`` (``values.consonant_of``, not this module's own ``decompose``) and vowel i.

**Rules 12 to 22 (Kober 0.8, CHANGELOG "0.8", A-037), reference list version 3.**
Drawn from Ventris and Chadwick 1973, chapter III §6 (Morphology) and
Word-formation (``docs/works/ventris_chadwick1973.md``, verification V), read
2026-09-12 -- the consonant-stem case and suffix endings, the s-stem set, the
u- and eu-stems, the -went- adjectives, the -o/-o-te participle, the infinitive,
the feminine of -eus, the material-adjective triplet and the -a2/ja spelling
variants the v1/v2 list lacked. Appended after rule 11, tried only under
``version=3``, in fixed order, first match wins as always; rule 12 subsumes
rule 1 (gender) for the o/a case, but rule 1 is kept first so a pair already
named "gender" keeps that name. Each rule's consonant is ``values.consonant_of``
(strips a trailing digit first); each rule's vowel is the label's own final
letter (this module's ``decompose``/``_vowel_of``, no digit stripping) -- a
digit-suffixed label (``RA2``) is excluded from every rule's vowel test except
rule 22, which is the only rule that strips digits.
"""

from __future__ import annotations

from typing import Callable, NamedTuple

from .paradigms import Word
from .values import consonant_of

__all__ = [
    "ReferenceRow",
    "REFERENCE_ALTERNATIONS",
    "decompose",
    "is_grammar",
    "RULE_NAMES",
    "RULE_NAMES_V2",
    "RULE_NAMES_V3",
]


class ReferenceRow(NamedTuple):
    alternation: str
    grammar: str


# Verbatim from the table in docs/ai_context/kober-method.md.
REFERENCE_ALTERNATIONS: tuple[ReferenceRow, ...] = (
    ReferenceRow(
        "-o / -a on the same consonant (e.g. -to/-ta, -ro/-ra, -no/-na)",
        "masculine and feminine of o/ā-stem nouns and adjectives",
    ),
    ReferenceRow(
        "-jo / -ja, -i-jo / -i-ja, -si-jo / -si-ja, -wi-jo / -wi-ja",
        "adjective and ethnic suffix, masculine and feminine",
    ),
    ReferenceRow("-o / -o-jo", "nominative and genitive singular, o-stems"),
    ReferenceRow("-o / -o-i, -a / -a-i", "singular and dative plural"),
    ReferenceRow("-a / -a-o", "feminine and masculine ā-stem genitive"),
    ReferenceRow(
        "-u / -we / -wo, -e-u / -e-we / -e-wo",
        "nominative, dative and genitive of eu-stems",
    ),
    ReferenceRow("-e / -e-i, -e / -e-o", "consonant and s-stem case forms"),
    ReferenceRow("-me-no / -me-na", "middle participle, masculine and feminine"),
    ReferenceRow("-e / -si", "third person singular and plural of verbs"),
    ReferenceRow(
        "X / X-qe, X / X-de, X / X-te, X / X-pi",
        'enclitic "and", allative, ablative and instrumental particles',
    ),
)

_VOWELS = set("AEIOU")


def decompose(label: str) -> tuple[str, str] | None:
    """``(consonant, vowel)`` from a sign label's final letter, or None if unusable.

    None when the label is empty, carries GORILA's ``*`` unidentified-sign marker,
    or does not end in a vowel letter (subscripted signs like ``RA2`` end in a
    digit and are deliberately excluded here).
    """
    if not label or "*" in label:
        return None
    last = label[-1]
    if last not in _VOWELS:
        return None
    return label[:-1], last


def _rule1_gender(e1: Word, e2: Word) -> bool:
    if len(e1) != len(e2) or e1[:-1] != e2[:-1]:
        return False
    d1, d2 = decompose(e1[-1]), decompose(e2[-1])
    if d1 is None or d2 is None:
        return False
    (c1, v1), (c2, v2) = d1, d2
    return c1 == c2 and {v1, v2} == {"O", "A"}


def _rule2_adjective(e1: Word, e2: Word) -> bool:
    if len(e1) != len(e2) or len(e1) not in (1, 2) or e1[:-1] != e2[:-1]:
        return False
    return {e1[-1], e2[-1]} == {"JO", "JA"}


def _rule3_genitive(e1: Word, e2: Word) -> bool:
    def check(base: Word, derived: Word) -> bool:
        if not base or derived != base + ("JO",):
            return False
        d = decompose(base[-1])
        return d is not None and d[1] == "O"

    return check(e1, e2) or check(e2, e1)


def _rule4_dative_plural(e1: Word, e2: Word) -> bool:
    def check(base: Word, derived: Word) -> bool:
        if not base or derived != base + ("I",):
            return False
        d = decompose(base[-1])
        return d is not None and d[1] in ("O", "A")

    return check(e1, e2) or check(e2, e1)


def _rule5_a_stem_genitive(e1: Word, e2: Word) -> bool:
    def check(base: Word, derived: Word) -> bool:
        if not base or derived != base + ("O",):
            return False
        d = decompose(base[-1])
        return d is not None and d[1] == "A"

    return check(e1, e2) or check(e2, e1)


def _rule6_eu_stem(e1: Word, e2: Word) -> bool:
    eu_signs = {"U", "WE", "WO"}
    if len(e1) != len(e2) or e1[:-1] != e2[:-1]:
        return False
    return e1[-1] in eu_signs and e2[-1] in eu_signs and e1[-1] != e2[-1]


def _rule7_consonant_s_stem(e1: Word, e2: Word) -> bool:
    def check(base: Word, derived: Word) -> bool:
        if not base:
            return False
        d = decompose(base[-1])
        if d is None or d[1] != "E":
            return False
        return derived in (base + ("I",), base + ("O",))

    return check(e1, e2) or check(e2, e1)


def _rule8_participle(e1: Word, e2: Word) -> bool:
    if len(e1) != len(e2) or len(e1) < 2 or e1[:-2] != e2[:-2]:
        return False
    return {e1[-2:], e2[-2:]} == {("ME", "NO"), ("ME", "NA")}


def _rule9_verb(e1: Word, e2: Word) -> bool:
    def check(a: Word, b: Word) -> bool:
        if len(a) != 1 or len(b) != 2:
            return False
        da = decompose(a[0])
        if da is None or da[1] != "E":
            return False
        db0 = decompose(b[0])
        if db0 is None or db0[1] != "O" or db0[0] != da[0]:
            return False
        return b[1] == "SI"

    return check(e1, e2) or check(e2, e1)


def _rule10_particle(e1: Word, e2: Word) -> bool:
    particles = {"QE", "DE", "TE", "PI"}

    def check(base: Word, derived: Word) -> bool:
        return len(derived) == len(base) + 1 and derived[:-1] == base and derived[-1] in particles

    return check(e1, e2) or check(e2, e1)


def _vowel_of(label: str) -> str | None:
    """The final letter of ``label`` if it is a vowel, else None. ``*`` (GORILA's
    unidentified-sign marker) never matches, matching ``decompose``'s exclusion."""
    if not label or "*" in label:
        return None
    last = label[-1]
    return last if last in _VOWELS else None


def _rule11_ethnic_derivation(e1: Word, e2: Word) -> bool:
    """Rule 11, ethnic derivation (Kober 0.6): ``derived == base[:-1] + (Ci, "JO")``
    or ``base[:-1] + (Ci, "JA")``, where ``base``'s final sign ``Co`` has vowel o
    and ``Ci`` has the same consonant as ``Co`` (``values.consonant_of``) and
    vowel i. X-so / X-si-jo, X-to / X-ti-jo and their -ja counterparts."""

    def check(base: Word, derived: Word) -> bool:
        if not base or len(derived) != len(base) + 1:
            return False
        if derived[:-2] != base[:-1] or derived[-1] not in ("JO", "JA"):
            return False
        co, ci = base[-1], derived[-2]
        if _vowel_of(co) != "O" or _vowel_of(ci) != "I":
            return False
        cons_o, cons_i = consonant_of(co), consonant_of(ci)
        return cons_o is not None and cons_o == cons_i

    return check(e1, e2) or check(e2, e1)


_CONSONANT_CASE_VOWELS = frozenset({"A", "E", "O", "I"})


def _rule12_consonant_stem_case(e1: Word, e2: Word) -> bool:
    """Rule 12 (Kober 0.8): e1 and e2 differ only in their final sign, same
    consonant (``values.consonant_of``), vowels any two of a, e, o, i (not u).
    -ne/-no, -te/-ta, -de/-do (pp. 85-86). Subsumes rule 1 (o/a gender) but is
    tried after it, so a gender pair keeps that name."""
    if len(e1) != len(e2) or e1[:-1] != e2[:-1]:
        return False
    c1, c2 = consonant_of(e1[-1]), consonant_of(e2[-1])
    if c1 is None or c1 != c2:
        return False
    v1, v2 = _vowel_of(e1[-1]), _vowel_of(e2[-1])
    if v1 is None or v2 is None or v1 == v2:
        return False
    return v1 in _CONSONANT_CASE_VOWELS and v2 in _CONSONANT_CASE_VOWELS


_RULE13_SUFFIXES = frozenset(
    {
        "NE", "NO", "NA", "TE", "TO", "TA", "DE", "DO", "DA",
        "RE", "RO", "RA", "SE", "SO", "SA", "KE", "KO", "KA", "SI",
    }
)


def _rule13_consonant_stem_suffix(e1: Word, e2: Word) -> bool:
    """Rule 13 (Kober 0.8): e2 == e1 + (S,) with S a consonant-stem case
    suffix. wa-na-ka / wa-na-ka-te; dative plural -si (p. 85)."""

    def check(base: Word, derived: Word) -> bool:
        return len(derived) == len(base) + 1 and derived[:-1] == base and derived[-1] in _RULE13_SUFFIXES

    return check(e1, e2) or check(e2, e1)


# Rule 14's strip set (p. 86): a final (O), (I), (A), (A2), (SI), (PI) or (E)
# may be removed from each ending, or nothing, before the two are compared.
_S_STEM_STRIP = frozenset({"O", "I", "A", "A2", "SI", "PI", "E"})


def _strip_candidates(e: Word) -> set[Word]:
    candidates = {e}
    if e and e[-1] in _S_STEM_STRIP:
        candidates.add(e[:-1])
    return candidates


def _rule14_s_stem(e1: Word, e2: Word) -> bool:
    """Rule 14 (Kober 0.8): after removing a final (O), (I), (A), (A2), (SI),
    (PI) or (E) from each ending, or nothing, the remainders are equal and end
    in a sign with vowel e (p. 86: the s-stem set -e, -e-o, -e-i, -e-e, -e-a,
    -e-a2, -e-si, -e-pi)."""
    for r1 in _strip_candidates(e1):
        for r2 in _strip_candidates(e2):
            if r1 and r1 == r2 and _vowel_of(r1[-1]) == "E":
                return True
    return False


def _rule15_u_stem(e1: Word, e2: Word) -> bool:
    """Rule 15 (Kober 0.8): e2 == e1 + (WE,), (PI,) or (O,) with e1 ending in
    a sign with vowel u (p. 86: ta-ra-nu / ta-ra-nu-we)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or _vowel_of(base[-1]) != "U":
            return False
        return derived in (base + ("WE",), base + ("PI",), base + ("O",))

    return check(e1, e2) or check(e2, e1)


def _rule16_eu_stem_plural(e1: Word, e2: Word) -> bool:
    """Rule 16 (Kober 0.8): e2 == e1 + (SI,) or (PI,) with e1 ending in the
    bare sign U, not merely a sign with vowel u (p. 86: ka-ke-u / ka-ke-u-si)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or base[-1] != "U":
            return False
        return derived in (base + ("SI",), base + ("PI",))

    return check(e1, e2) or check(e2, e1)


def _rule17_went(e1: Word, e2: Word) -> bool:
    """Rule 17 (Kober 0.8): e2 == e1 + (TO,) or (SA,) with e1 ending in the
    bare sign WE (p. 86 note 1: ko-ma-we / ko-ma-we-to)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or base[-1] != "WE":
            return False
        return derived in (base + ("TO",), base + ("SA",))

    return check(e1, e2) or check(e2, e1)


def _rule18_participle_plural(e1: Word, e2: Word) -> bool:
    """Rule 18 (Kober 0.8): e2 == e1 + (TE,) with e1's final vowel o
    (p. 88: e-o / e-o-te)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or _vowel_of(base[-1]) != "O":
            return False
        return derived == base + ("TE",)

    return check(e1, e2) or check(e2, e1)


def _rule19_infinitive(e1: Word, e2: Word) -> bool:
    """Rule 19 (Kober 0.8): e2 == e1 + (E,) with e1's final vowel e
    (p. 88: e-ke / e-ke-e)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or _vowel_of(base[-1]) != "E":
            return False
        return derived == base + ("E",)

    return check(e1, e2) or check(e2, e1)


def _rule20_feminine_of_eus(e1: Word, e2: Word) -> bool:
    """Rule 20 (Kober 0.8): e1 ends in the bare sign U and e2 == e1[:-1] +
    (JA,) (p. 89: i-je-re-u / i-je-re-ja)."""

    def check(base: Word, derived: Word) -> bool:
        if not base or base[-1] != "U":
            return False
        return derived == base[:-1] + ("JA",)

    return check(e1, e2) or check(e2, e1)


# Rule 21's target set (p. 89): the abstracted (vowel-of-penultimate-sign,
# final-sign) pair of each of wi-ri-ne-jo (E, JO), wi-ri-ne-o (E, O) and
# wi-ri-ni-jo (I, JO), sharing the common prefix wi-ri-.
_MATERIAL_ADJECTIVE_SET = frozenset({("E", "JO"), ("E", "O"), ("I", "JO")})


def _rule21_material_adjective(e1: Word, e2: Word) -> bool:
    """Rule 21 (Kober 0.8): after a common prefix (everything but the last two
    signs), each ending's last two signs abstract to (vowel of the
    second-to-last sign, the final sign); both abstractions must be in
    ``_MATERIAL_ADJECTIVE_SET``. wi-ri-ne-jo / wi-ri-ne-o / wi-ri-ni-jo."""
    if len(e1) != len(e2) or len(e1) < 2 or e1[:-2] != e2[:-2]:
        return False

    def abstract(e: Word) -> tuple[str, str] | None:
        v = _vowel_of(e[-2])
        return (v, e[-1]) if v is not None else None

    a1, a2 = abstract(e1), abstract(e2)
    return a1 in _MATERIAL_ADJECTIVE_SET and a2 in _MATERIAL_ADJECTIVE_SET


def _strip_trailing_digits(label: str) -> str:
    return label.rstrip("0123456789")


def _rule22_spelling_variant(e1: Word, e2: Word) -> bool:
    """Rule 22 (Kober 0.8): endings equal after trailing digits are stripped
    from each label (pa-we-a / pa-we-a2), or, at the same length, differ at
    exactly one position and only as JA / A2 there (pp. 46-47).

    Read literally, both clauses require ``e1`` and ``e2`` to be the same
    length: this does not reach a-ke-ti-ra2 / a-ke-ti-ri-ja (4 signs against
    5), where a single sign (RA2) alternates with a two-sign spelling (RI,
    JA) -- a stated limit (ASSUMPTIONS A-123), not a case this rule bends for.
    """
    if len(e1) != len(e2):
        return False
    if tuple(_strip_trailing_digits(s) for s in e1) == tuple(_strip_trailing_digits(s) for s in e2):
        return True
    diffs = [(a, b) for a, b in zip(e1, e2) if a != b]
    return len(diffs) == 1 and {diffs[0][0], diffs[0][1]} == {"JA", "A2"}


_RULES: tuple[tuple[str, Callable[[Word, Word], bool]], ...] = (
    ("gender", _rule1_gender),
    ("adjective", _rule2_adjective),
    ("genitive", _rule3_genitive),
    ("dative_plural", _rule4_dative_plural),
    ("a_stem_genitive", _rule5_a_stem_genitive),
    ("eu_stem", _rule6_eu_stem),
    ("consonant_s_stem", _rule7_consonant_s_stem),
    ("participle", _rule8_participle),
    ("verb", _rule9_verb),
    ("particle", _rule10_particle),
)

# Kober 0.6 (CHANGELOG "0.6"): rules 1 to 10 plus rule 11, appended, never
# reordered, so it is tried last -- only after all ten pre-0.6 rules have
# failed to match.
_RULES_V2: tuple[tuple[str, Callable[[Word, Word], bool]], ...] = _RULES + (
    ("ethnic_derivation", _rule11_ethnic_derivation),
)

# Kober 0.8 (CHANGELOG "0.8"): rules 1 to 11 plus rules 12 to 22, appended in
# order, never reordered -- tried only after every earlier rule has failed.
_RULES_V3: tuple[tuple[str, Callable[[Word, Word], bool]], ...] = _RULES_V2 + (
    ("consonant_stem_case", _rule12_consonant_stem_case),
    ("consonant_stem_suffix", _rule13_consonant_stem_suffix),
    ("s_stem", _rule14_s_stem),
    ("u_stem", _rule15_u_stem),
    ("eu_stem_plural", _rule16_eu_stem_plural),
    ("went", _rule17_went),
    ("participle_plural", _rule18_participle_plural),
    ("infinitive", _rule19_infinitive),
    ("feminine_of_eus", _rule20_feminine_of_eus),
    ("material_adjective", _rule21_material_adjective),
    ("spelling_variant", _rule22_spelling_variant),
)

RULE_NAMES: tuple[str, ...] = tuple(name for name, _ in _RULES)
RULE_NAMES_V2: tuple[str, ...] = tuple(name for name, _ in _RULES_V2)
RULE_NAMES_V3: tuple[str, ...] = tuple(name for name, _ in _RULES_V3)


def is_grammar(e1: Word, e2: Word, version: int = 1) -> str | None:
    """The first rule name that matches this unordered ending pair.

    ``version=1`` (default) tries rules 1 to 10 only, exactly as before Kober
    0.6 -- every existing call site, result and regression pin is unaffected.
    ``version=2`` also tries rule 11 (ethnic derivation), after the first ten,
    so a v1 match is always also a v2 match at the same rule name.
    ``version=3`` (Kober 0.8) also tries rules 12 to 22, after rule 11, so a
    v2 match is always also a v3 match at the same rule name.
    """
    if version >= 3:
        rules = _RULES_V3
    elif version == 2:
        rules = _RULES_V2
    else:
        rules = _RULES
    for name, fn in rules:
        if fn(e1, e2):
            return name
    return None
