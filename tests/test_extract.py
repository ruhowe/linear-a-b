"""Gates for the Linear B restoration extraction.

Run: ``.venv/bin/python -m pytest tests/ -q`` (or ``.venv/bin/python tests/test_extract.py``).

These are calibration gates, not unit tests in the usual sense: they pin the extraction
against externally published corpus sizes, so a silent change in normalisation or
eligibility shows up as a failed count rather than as a slightly different accuracy
figure three steps downstream.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import aegean  # noqa: E402

from linearb_restore.extract import (  # noqa: E402
    corpus_summary,
    d_family,
    extract_sequences,
)
from linearb_restore.normalise import (  # noqa: E402
    UNDERDOT,
    normalise_text,
    sign_label_set,
)

_CORPUS = None


def corpus():
    global _CORPUS
    if _CORPUS is None:
        _CORPUS = aegean.load("damos")
    return _CORPUS


# --------------------------------------------------------------------------- #
# Normalisation golden cases
# --------------------------------------------------------------------------- #


def test_underdot_stripped_and_flagged():
    """U+0323 is removed and reported. DĀMOS leaves status CERTAIN on these."""
    text = unicodedata.normalize("NFC", "o" + UNDERDOT)
    out, had_dot, had_span = normalise_text(text)
    assert out == "o"
    assert had_dot is True
    assert had_span is False


def test_underdot_inside_a_word():
    out, had_dot, _ = normalise_text("a-ṇọ-qo-ta-o")
    assert out == "a-no-qo-ta-o"
    assert had_dot is True


def test_span_brackets_stripped_but_lacuna_brackets_kept():
    """Span brackets delimit text the edition gives; lacuna brackets carry status."""
    out, _, had_span = normalise_text("ra⌞")
    assert out == "ra" and had_span is True
    kept, _, _ = normalise_text("pa-]i-to")
    assert "]" in kept, "lacuna brackets must survive — they encode the reading status"


def test_underdotted_logogram_normalises_to_its_plain_form():
    out, had_dot, _ = normalise_text("ỌṾỊṢ:ṃ")
    assert out == "OVIS:m"
    assert had_dot is True


# --------------------------------------------------------------------------- #
# Extraction gates
# --------------------------------------------------------------------------- #


def test_d_family_document_count():
    """The Knossos D family is 1,016 documents across subseries Da–Dv."""
    assert len(d_family(corpus())) == 1016


def test_knossos_a_and_b_reproduces_lrec_figure():
    """LREC 2020 reports 308 KN tablets for series A&B. Exact match validates the filter."""
    from aegean.analysis.hands import series_of

    docs = [
        d
        for d in corpus().documents
        if d.meta.site == "Knossos" and (series_of(d) or "")[:1] in ("A", "B")
    ]
    assert len(docs) == 308


def test_eligible_sequence_counts_both_conventions():
    """536 without single-sign words (closest to the published 513); 596 with them."""
    c = corpus()
    docs = d_family(c)
    with_singles = corpus_summary(extract_sequences(c, docs)).eligible_sequences
    without = corpus_summary(
        extract_sequences(c, docs, include_single_sign_words=False)
    ).eligible_sequences
    assert without == 536
    assert with_singles == 596


def test_every_target_sign_is_a_real_sign():
    """No bracket residue or mis-split may enter the target vocabulary.

    Signs are either inventory syllabograms or the ``*NNN`` undeciphered series
    (Judson 2020) — which is transliterated but carries no phonetic label, so it is
    absent from the 211-sign inventory by design.
    """
    c = corpus()
    labels = sign_label_set(c)
    signs = {
        sign
        for rec in extract_sequences(c, d_family(c))
        for _, _, sign in rec.maskable_positions()
    }
    unknown = {s for s in signs if s.upper() not in labels}
    assert unknown == {"*18", "*22", "*34", "*49", "*56", "*65", "*82", "*83", "*86"}
    assert all(s.islower() or s.startswith("*") for s in signs)


def test_target_vocabulary_size():
    c = corpus()
    summary = corpus_summary(extract_sequences(c, d_family(c)))
    assert summary.sign_vocabulary == 77


def test_no_uncertain_word_survives_into_targets():
    """Eligibility must exclude every non-CERTAIN and every underdotted target."""
    from aegean.core.model import ReadingStatus

    for rec in extract_sequences(corpus(), d_family(corpus())):
        for ti, _, _ in rec.maskable_positions():
            tok = rec.tokens[ti]
            assert tok.status is ReadingStatus.CERTAIN
            assert not tok.damaged_but_read


def test_apparatus_tokens_never_reach_the_content_stream():
    for rec in extract_sequences(corpus(), d_family(corpus())):
        assert all(not t.is_apparatus for t in rec.tokens)


def test_document_lines_align_with_transcription():
    """Register merging later depends on this 1:1 alignment, so assert it now."""
    mismatches = []
    for doc in d_family(corpus()):
        if not doc.transcription or not doc.lines:
            continue
        printed = [ln for ln in doc.transcription.splitlines() if ln.strip()]
        if len(printed) != len(doc.lines):
            mismatches.append(doc.id)
    assert not mismatches, f"{len(mismatches)} documents mis-align, e.g. {mismatches[:5]}"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{failures} failure(s)")
    sys.exit(1 if failures else 0)
