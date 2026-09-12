#!/usr/bin/env python3
"""S-009: a document-by-document concordance of GORILA/SigLA disagreement.

Builds the resource the brief asks for (spikes/S-009-edition-concordance/BRIEF.md):
for every document present in both Linear A editions, the site, support type, word
token count in each edition, and the kind of disagreement between them. Then
aggregates by site, support, document length band and sign label, and separately
counts the documents each edition holds that the other does not.

**Alignment.** Reused, not invented: `docs/ai_context/corpus-sources.md` (Gotchas)
records that SigLA and GORILA document ids differ only in whitespace ("HT 1" against
"HT1") and that normalising before matching aligns 697 of SigLA's 802 documents with
a GORILA document. `_normalise_id` below (strip all whitespace, upper-case) reproduces
that count exactly (checked in `main`, not just asserted) — no tracked script from
F-023's feasibility check survives to import (it was a read-only, uncommitted check;
see CHANGELOG "Segmentation sensitivity on Linear A"), so this is the documented
*method* re-applied, not a new one.

**Word unit.** `Token.kind is TokenKind.WORD`, any `ReadingStatus` (coverage, not
reading confidence, is what a concordance measures), signs run through
`linearb_restore.normalise.normalise_text` then upper-cased — the same normalisation
`src/kober/words.py` uses for word types, so a sign is "the same sign" here exactly
when Kober analysis would treat it as one.

**Disagreement kind**, per aligned document, computed from the flat sequence of
normalised signs across all WORD tokens in document order (not per-word — a document
where GORILA groups five signs into two words and SigLA groups the same five signs
into three words differs in dividers, not readings, and only a flat comparison sees
that):

- `no_text_either_edition`: neither edition has a WORD token for this document. Not a
  disagreement (nothing to disagree about); reported separately from the four kinds
  below, which is why the four kinds' counts sum to fewer than 697.
- `identical`: the two editions' word sequences match exactly (same signs, same
  boundaries).
- `divider_placement_only`: the flat sign sequences match exactly but the word
  boundaries differ.
- `sign_readings_differ`: the flat sequences differ only by substitution (every
  position on one side has a corresponding position on the other; nothing is
  present in one edition and absent in the other).
- `line_coverage_differs`: the flat sequences differ by at least one insertion or
  deletion — some sign position exists in one edition's transcription and not the
  other's, which is what "different line coverage" (or a different word entirely)
  looks like in a flat sign stream.

`differing_sign_positions` is `difflib.SequenceMatcher`'s non-equal opcode span,
summed (replace spans by their longer side, insert/delete spans by their length) —
one number for all four kinds, not just the substitution one.

**Kind-tag diagnostic.** SigLA's provenance notes say it separates WORD and LOGOGRAM
tokens "as published by SigLA", same as GORILA — but spot-checks while building this
script found the two editions do not always agree on which class a given commodity
sign belongs to (GORILA's `TE`/`RO` as LOGOGRAM, SigLA's as WORD, on the same tablet).
Rather than silently pick a convention, `_kind_tag_diagnostic` reclassifies every
WORD-only `line_coverage_differs` document with LOGOGRAM tokens folded into the same
flat stream and reports how many change category. That number is the share of the
"line coverage differs" bucket attributable to the WORD/LOGOGRAM boundary rather than
to a word being transcribed or not; it is reported, not resolved, in RESULT.md.

Output: `results.json` (aggregate only — per `spikes/README.md` rule 6, no corpus
text anywhere; per-document rows carry id, site, support, token counts and
disagreement kind, never a reading; the sign-label table carries labels and counts,
never words) and `RESULT.md`.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import Document, TokenKind  # noqa: E402
from linearb_restore.normalise import normalise_text  # noqa: E402

EXPECTED_ALIGNED = 697  # F-023 / corpus-sources.md Gotchas, checked below, not assumed


def _normalise_id(doc_id: str) -> str:
    """Strip all whitespace and upper-case. Reproduces the 697-of-802 alignment
    corpus-sources.md records; checked against that number in main()."""
    return re.sub(r"\s+", "", doc_id).upper()


def _normalise_sign(label: str) -> str:
    normalised, _had_underdot, _had_span = normalise_text(label)
    return normalised.upper()


def _flat_signs(doc: Document, kinds: tuple[TokenKind, ...] = (TokenKind.WORD,)) -> tuple[str, ...]:
    """All signs from tokens of the given kind(s), in document order, normalised."""
    out: list[str] = []
    for tok in doc.tokens:
        if tok.kind not in kinds:
            continue
        out.extend(_normalise_sign(s) for s in tok.signs)
    return tuple(out)


def _word_seq(doc: Document) -> tuple[tuple[str, ...], ...]:
    """WORD tokens as normalised sign tuples, in document order."""
    return tuple(
        tuple(_normalise_sign(s) for s in tok.signs)
        for tok in doc.tokens
        if tok.kind is TokenKind.WORD
    )


def _diff_ops(flat_g: tuple[str, ...], flat_s: tuple[str, ...]):
    """SequenceMatcher opcodes, plus (n_replace, n_indel) summary counts."""
    ops = difflib.SequenceMatcher(None, flat_g, flat_s, autojunk=False).get_opcodes()
    n_replace = 0
    n_indel = 0
    for tag, i1, i2, j1, j2 in ops:
        if tag == "replace":
            n_replace += max(i2 - i1, j2 - j1)
        elif tag in ("insert", "delete"):
            n_indel += (i2 - i1) + (j2 - j1)
    return ops, n_replace, n_indel


def classify(doc_g: Document, doc_s: Document) -> dict:
    words_g = _word_seq(doc_g)
    words_s = _word_seq(doc_s)
    flat_g = tuple(s for w in words_g for s in w)
    flat_s = tuple(s for w in words_s for s in w)

    if not words_g and not words_s:
        return {
            "kind": "no_text_either_edition",
            "differing_sign_positions": 0,
            "tokens_gorila": 0,
            "tokens_sigla": 0,
            "replace_labels": [],
        }

    ops, n_replace, n_indel = _diff_ops(flat_g, flat_s)

    if n_replace == 0 and n_indel == 0:
        kind = "identical" if words_g == words_s else "divider_placement_only"
    elif n_indel == 0:
        kind = "sign_readings_differ"
    else:
        kind = "line_coverage_differs"

    replace_labels: list[str] = []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "replace":
            replace_labels.extend(flat_g[i1:i2])
            replace_labels.extend(flat_s[j1:j2])

    return {
        "kind": kind,
        "differing_sign_positions": n_replace + n_indel,
        "tokens_gorila": len(words_g),
        "tokens_sigla": len(words_s),
        "replace_labels": replace_labels,
    }


def _kind_tag_diagnostic(gmap: dict, smap: dict, rows: list[dict]) -> dict:
    """For every WORD-only `line_coverage_differs` document, recompute with LOGOGRAM
    tokens folded into the flat stream alongside WORD, and count how many change
    category. Quantifies how much of that bucket is the WORD/LOGOGRAM boundary
    rather than a genuinely missing word. See module docstring."""
    both_kinds = (TokenKind.WORD, TokenKind.LOGOGRAM)
    reclassified = Counter()
    checked = 0
    for row in rows:
        if row["kind"] != "line_coverage_differs":
            continue
        checked += 1
        doc_g = gmap[row["_key"]]
        doc_s = smap[row["_key"]]
        flat_g = _flat_signs(doc_g, both_kinds)
        flat_s = _flat_signs(doc_s, both_kinds)
        _ops, n_replace, n_indel = _diff_ops(flat_g, flat_s)
        if n_replace == 0 and n_indel == 0:
            new_kind = "identical_or_divider_only"
        elif n_indel == 0:
            new_kind = "sign_readings_differ"
        else:
            new_kind = "line_coverage_differs"
        reclassified[new_kind] += 1
    return {
        "line_coverage_differs_word_only": checked,
        "still_line_coverage_with_logograms": reclassified.get("line_coverage_differs", 0),
        "reclassified_with_logograms": checked - reclassified.get("line_coverage_differs", 0),
        "reclassified_breakdown": dict(reclassified),
    }


def _length_band(n: int) -> str:
    if n == 0:
        return "0"
    if n <= 2:
        return "1-2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    if n <= 20:
        return "11-20"
    return "21+"


def _group_counts(rows: list[dict], key: str) -> list[dict]:
    """Per distinct value of `key`: aligned-document count, count with text in at
    least one edition, count that disagrees (any kind but identical/no_text), rate."""
    by_key: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_key[row[key]].append(row)
    out = []
    for value, group in sorted(by_key.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        n_aligned = len(group)
        with_text = [r for r in group if r["kind"] != "no_text_either_edition"]
        n_with_text = len(with_text)
        n_differ = sum(1 for r in with_text if r["kind"] != "identical")
        out.append({
            key: value,
            "n_aligned": n_aligned,
            "n_with_text": n_with_text,
            "n_differ": n_differ,
            "disagreement_rate": (n_differ / n_with_text) if n_with_text else None,
        })
    return out


def _unaligned_breakdown(docs: list[Document], excluded_keys: set) -> dict:
    only = [d for d in docs if _normalise_id(d.id) not in excluded_keys]
    by_site = Counter((d.meta.site or "(unspecified)") for d in only)
    by_support = Counter((d.meta.support or "(unspecified)") for d in only)
    return {
        "count": len(only),
        "by_site": sorted(
            [{"site": k, "count": v} for k, v in by_site.items()],
            key=lambda r: (-r["count"], r["site"]),
        ),
        "by_support": sorted(
            [{"support": k, "count": v} for k, v in by_support.items()],
            key=lambda r: (-r["count"], r["support"]),
        ),
    }


def main() -> None:
    gorila = aegean.load("lineara")
    sigla = aegean.load("sigla")

    gmap = {_normalise_id(d.id): d for d in gorila.documents}
    smap = {_normalise_id(d.id): d for d in sigla.documents}
    aligned_keys = sorted(set(gmap) & set(smap))

    if len(aligned_keys) != EXPECTED_ALIGNED:
        print(
            f"WARNING: alignment gives {len(aligned_keys)} documents, "
            f"not the {EXPECTED_ALIGNED} corpus-sources.md records. "
            "Corpus data or normalisation has changed; investigate before trusting "
            "anything below.",
            file=sys.stderr,
        )

    rows = []
    sign_label_counts: Counter = Counter()
    for key in aligned_keys:
        doc_g = gmap[key]
        doc_s = smap[key]
        result = classify(doc_g, doc_s)
        row = {
            "_key": key,
            "gorila_id": doc_g.id,
            "sigla_id": doc_s.id,
            "site": doc_g.meta.site or "(unspecified)",
            "support": doc_g.meta.support or "(unspecified)",
            "sigla_site": doc_s.meta.site or "(unspecified)",
            "sigla_support": doc_s.meta.support or "(unspecified)",
            "tokens_gorila": result["tokens_gorila"],
            "tokens_sigla": result["tokens_sigla"],
            "kind": result["kind"],
            "differing_sign_positions": result["differing_sign_positions"],
            "length_band": _length_band(max(result["tokens_gorila"], result["tokens_sigla"])),
        }
        rows.append(row)
        if result["kind"] == "sign_readings_differ":
            sign_label_counts.update(result["replace_labels"])

    kind_tag = _kind_tag_diagnostic(gmap, smap, rows)

    by_kind = Counter(r["kind"] for r in rows)
    meta_site_mismatch = sum(1 for r in rows if r["site"] != r["sigla_site"])
    meta_support_mismatch = sum(1 for r in rows if r["support"] != r["sigla_support"])

    gorila_only = _unaligned_breakdown(gorila.documents, set(aligned_keys))
    sigla_only = _unaligned_breakdown(sigla.documents, set(aligned_keys))

    # Drop the internal join key before writing rows out.
    public_rows = [{k: v for k, v in r.items() if k != "_key"} for r in rows]

    output = {
        "meta": {
            "gorila_docs_total": len(gorila.documents),
            "sigla_docs_total": len(sigla.documents),
            "aligned_docs": len(aligned_keys),
            "expected_aligned_docs": EXPECTED_ALIGNED,
            "id_normalisation": "strip whitespace, upper-case (corpus-sources.md Gotchas)",
            "word_unit": "TokenKind.WORD, any ReadingStatus, normalise_text + upper-case",
            "gorila_provenance": {
                "source": gorila.provenance.source,
                "data_version": gorila.provenance.data_version,
            },
            "sigla_provenance": {
                "source": sigla.provenance.source,
                "data_version": sigla.provenance.data_version,
            },
            "meta_site_mismatch_count": meta_site_mismatch,
            "meta_support_mismatch_count": meta_support_mismatch,
        },
        "documents": public_rows,
        "by_kind": dict(by_kind),
        "disagreement_rate_by_site": _group_counts(rows, "site"),
        "disagreement_rate_by_support": _group_counts(rows, "support"),
        "disagreement_rate_by_length_band": _group_counts(rows, "length_band"),
        "sign_label_involvement_in_reading_differences": [
            {"label": label, "count": count}
            for label, count in sign_label_counts.most_common()
        ],
        "kind_tag_diagnostic": kind_tag,
        "gorila_only_documents": gorila_only,
        "sigla_only_documents": sigla_only,
    }

    out_path = Path(__file__).resolve().parent / "results.json"
    out_path.write_text(json.dumps(output, indent=2))

    print(f"aligned: {len(aligned_keys)} (expected {EXPECTED_ALIGNED})")
    print("by kind:", dict(by_kind))
    print("kind-tag diagnostic:", kind_tag)
    print("meta mismatches: site", meta_site_mismatch, "support", meta_support_mismatch)
    print(f"gorila-only: {gorila_only['count']}, sigla-only: {sigla_only['count']}")
    print(f"written {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
