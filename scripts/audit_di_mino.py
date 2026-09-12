"""Audit di Mino (2026) *Ya Diktu* against the loaded Linear A corpus.

Two questions, kept separate because they have different answers:

1. **Are his inscription references accurate?** He cites specific documents for
   specific sign-groups and gives attestation counts. Cheapest possible check on a
   decipherment claim, and the one most likely to fail on a careless paper. His pass.

2. **Does he accept the edition's word division?** Not always. Where he does not, his
   readings spend a degree of freedom that `src/semitic_null/` does not price, because
   that test holds segmentation fixed at GORILA's `𐄁` divisions.

Both results are recorded in `docs/ai_context/semitic-null-test.md` and
`docs/ai_context/state-of-the-art.md`. This script is what regenerates them.

Run: `.venv/bin/python scripts/audit_di_mino.py`

Note on glyphs: `Document.transcription` is unreliable for tablets — HT 31's is
truncated — so sign strings are rebuilt from `Token.signs` through the inventory.
"""

from __future__ import annotations

import sys
from collections import Counter

import aegean
from aegean.scripts.lineara.inventory import linear_a_inventory


def sign_glyph_map() -> dict[str, str]:
    """label → glyph, the only reliable transliteration↔glyph bridge (corpus-sources.md)."""
    return {s.label: s.glyph for s in linear_a_inventory()}


def word_types_containing(corpus, sign: str) -> dict[str, list[str]]:
    """Distinct word types whose sign sequence includes `sign`, with the docs they sit in."""
    found: dict[str, list[str]] = {}
    for doc in corpus.documents:
        for tok in doc.tokens:
            if tok.kind.name == "WORD" and sign in (tok.signs or ()):
                found.setdefault(tok.text, []).append(doc.id)
    return found


def tokens_containing(corpus, needle: str) -> list[tuple[str, str, str]]:
    """(doc id, site, token text) for every token whose text contains `needle`."""
    return [
        (doc.id, doc.meta.site, tok.text)
        for doc in corpus.documents
        for tok in doc.tokens
        if needle in (tok.text or "")
    ]


def check(label: str, claimed, measured, exact: bool = True) -> bool:
    verdict = "EXACT" if measured == claimed else ("NEAR" if not exact else "MISMATCH")
    ok = measured == claimed or not exact
    print(f"  [{verdict:8s}] {label}")
    print(f"             claimed {claimed!r} | measured {measured!r}")
    return ok


def audit_citations(la, lb) -> None:
    print("\n1. CITATION AUDIT — do the inscriptions say what he says they say?\n")

    # n.30: *314 attested 6x at Hagia Triada, Kophinas, Phaistos, Arkhalokhori
    t314 = tokens_containing(la, "*314")
    sites = sorted({site for _, site, _ in t314})
    check("*314 attestation count (n.30)", 6, len(t314))
    check(
        "*314 sites (n.30)",
        ["Arkhalkhori", "Haghia Triada", "Kophinas", "Phaistos"],
        sites,
    )
    for doc_id, site, text in t314:
        print(f"             {doc_id:12s} {site:16s} {text}")

    # Appendix A: AB79 in 25 LA word-forms; 7 LB attestations across 4 forms.
    # The corpus transliterates AB79 as ZU; he transliterates it TH (/ṯ/). Same sign.
    zu = word_types_containing(la, "ZU")
    check("AB79 in distinct LA word-forms (App. A)", 25, len(zu), exact=False)
    print("             (his corpus is 1,780 docs against this load's 1,721)")

    lb_forms: dict[str, list[str]] = {}
    for doc in lb.documents:
        for tok in doc.tokens:
            if tok.kind.name == "WORD" and any(
                s in ("*79", "zu", "ZU", "wo2", "zo2") for s in (tok.signs or ())
            ):
                lb_forms.setdefault(tok.text, []).append(doc.id)
    n_att = sum(len(v) for v in lb_forms.values())
    check("AB79 Linear B forms (App. A)", 4, len(lb_forms))
    check("AB79 Linear B attestations (App. A)", 7, n_att, exact=False)
    for form in sorted(lb_forms):
        print(f"             {form}")

    # Appendix B spot-checks: sign-group → the document he cites for it.
    # Appendix B cites *a* reference per sign-group, not an exhaustive attestation list,
    # so the right test is "is the cited document among the attestations", not set equality.
    spot = {
        "ZU-DU": {"HT51b", "HT99b"},      # ṯudu "breast"
        "MA-ZU": {"HT102"},                # MA-*79, maṯu "man"
        "ZU-RI-NI-MA": {"KNZb52"},         # Ṯawrinima, a bull name
        "I-ZU-RI-NI-TA": {"PH6"},          # feminine counterpart
        "KI-DA-RO": {"HT117a"},            # qәdērāh "pot"
        "KU-MI-NA-QE": {"HTWc3014"},       # kamōn "cumin"
    }
    print()
    for form, cited in spot.items():
        got = {
            doc.id
            for doc in la.documents
            for tok in doc.tokens
            if tok.text == form
        }
        held = cited <= got
        extra = sorted(got - cited)
        verdict = "EXACT" if held and not extra else ("HOLDS" if held else "MISMATCH")
        print(f"  [{verdict:8s}] Appendix B: {form}")
        print(f"             cited {sorted(cited)} | attested {sorted(got)}")
        if extra:
            print(f"             (also attested at {extra} — he cites one reference, not all)")

    # §8: formula spread. He says >=15 across 7 sites, 28 vessels / 11 sites w/ fragments.
    verb = [
        doc.id
        for doc in la.documents
        if any(
            any(p in (tok.text or "") for p in ("301-WA", "301-U", "301-DE", "301-TI"))
            for tok in doc.tokens
        )
    ]
    sasara = [
        (doc.id, doc.meta.site)
        for doc in la.documents
        if any("SA-SA-RA" in (tok.text or "") for tok in doc.tokens)
    ]
    print()
    print(f"  formula verb forms: {len(verb)} docs — {verb}")
    print(
        f"  *-SA-SA-RA-*: {len(sasara)} docs across "
        f"{len({s for _, s in sasara})} sites — {sasara}"
    )


def audit_segmentation(la) -> None:
    print("\n2. SEGMENTATION — does he accept the edition's word division?\n")

    glyphs = sign_glyph_map()
    by_id = {doc.id: doc for doc in la.documents}

    # His Appendix A reads KN Zc 7 as seven lexemes. GORILA divides it into five.
    claimed = ["A-KA-NU", "ZA-TI", "DU-RA-RE", "A-*79-RA", "JA-SA-RA", "A-NA-NE", "WI-PI"]
    doc = by_id["KNZc7"]
    edition = [t.text for t in doc.tokens if t.kind.name == "WORD"]

    print(f"  KN Zc 7 — GORILA divides into {len(edition)}:")
    for w in edition:
        signs = next(t.signs for t in doc.tokens if t.text == w)
        print(f"             {w:22s} {''.join(glyphs.get(s, '?') for s in signs)}")
    print(f"  KN Zc 7 — di Mino reads {len(claimed)}:")
    for w in claimed:
        print(f"             {w}")
    print(
        f"\n  => splits {len(claimed) - len(edition)} word-group(s) the edition does not divide."
    )
    print("     A-KA-NU-ZA-TI     -> A-KA-NU + ZA-TI")
    print("     JA-SA-RA-A-NA-NE  -> JA-SA-RA + A-NA-NE")
    print("     (A-ZU-RA vs A-*79-RA is NOT a divergence: same signs, his TH for AB79)")

    # Same pattern at PE Zb 3.
    pe = by_id["PEZb3"]
    pe_words = [t.text for t in pe.tokens if t.kind.name == "WORD"]
    print(f"\n  PE Zb 3 — edition: {pe_words}")
    print("  PE Zb 3 — he cites KI-TA-NA-SI-JA-SE as a unit out of that string.")

    print(
        "\n  Consequence for src/semitic_null/: it scores GORILA's 648 word types for real\n"
        "  and null alike, so segmentation does not differentially favour the real map\n"
        "  there. But it is freedom his method spends and the test does not price.\n"
        "  Direction is conservative — re-division shortens words, and short words sit\n"
        "  where the Hebrew root space is densest (2-sign: 89.9% real vs 88.6% null)."
    )


def corpus_shape(la) -> None:
    print("\n3. CORPUS SHAPE — what a 'sample' can be\n")
    supports = Counter(doc.meta.support for doc in la.documents)
    for support, n in supports.most_common(6):
        words = [
            len([t for t in doc.tokens if t.kind.name == "WORD"])
            for doc in la.documents
            if doc.meta.support == support
        ]
        mean = sum(words) / len(words) if words else 0.0
        print(f"  {support:28s} {n:5d} docs   mean {mean:5.2f} words   max {max(words):3d}")


def main() -> int:
    la = aegean.load("lineara")
    lb = aegean.load("damos")
    print(f"Linear A: {len(la.documents)} docs | DAMOS: {len(lb.documents)} docs")
    audit_citations(la, lb)
    audit_segmentation(la)
    corpus_shape(la)
    print("\nSee docs/ai_context/semitic-null-test.md and state-of-the-art.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
