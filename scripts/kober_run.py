#!/usr/bin/env python3
"""Run the Kober method (protocol 0.1) and write results/kober-{corpus}-seed{seed}.json.

    .venv/bin/python scripts/kober_run.py --corpus damos --perms 200 --seed 0

Refuses ``--corpus lineara`` or ``--corpus sigla`` unless ``--allow-lineara`` is also
passed: TODO item 4 runs Linear A only after item 3's Linear B criterion is read, and
that reading is not this script's job (see ``docs/ai_context/result-discipline.md``
and ``kober.report`` — no verdict is computed here, only numbers). ``--allow-lineara``
gates both Linear A editions pyaegean exposes (GORILA via ``lineara`` and SigLA via
``sigla``, CHANGELOG "Segmentation sensitivity on Linear A"); the flag name is kept
as-is rather than renamed.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

import kober.report as kober_report  # noqa: E402
from kober.context import extract_word_contexts  # noqa: E402
from kober.grid import (  # noqa: E402
    build_alternation_grid_report,
    build_anchored_grid_report,
    build_grid_report,
)
from kober.lists import extract_listed_words  # noqa: E402
from kober.report import (  # noqa: E402
    build_context_report,
    build_list_tiebreak_report,
    build_medial_report,
    build_report,
    build_role_tiebreak_report,
    render_markdown,
    write_report,
)
from kober.roles import word_roles  # noqa: E402
from kober.words import (  # noqa: E402
    WordTypes,
    extract_word_types,
    subsample_document_ids,
)

_LINEAR_A_CORPORA = {"lineara", "sigla"}

_LINEAR_A_REFUSAL = (
    "Refusing --corpus {corpus} without --allow-lineara. TODO item 4 (Kober method on "
    "Linear A) runs only after item 3's Linear B criterion has been read; see "
    "docs/ai_context/kober-method.md and TODO.md item 4. --allow-lineara gates both "
    "Linear A editions (lineara, sigla)."
)


def load_extra_word_types(path: str | Path) -> list[tuple[str, ...]]:
    """CHANGELOG "Supplement sensitivity" (F-047): read a private JSONL of extra
    Linear A sign-label-tuple word types. One JSON list of labels per line; lines
    starting with ``#`` (the required source header) are ignored. Labels are
    upper-cased to match ``kober.words``' own normalised-label form."""
    types: list[tuple[str, ...]] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        labels = json.loads(line)
        types.append(tuple(str(s).upper() for s in labels))
    return types


def extract_word_types_with_extra(base_extract_word_types, extra_word_types):
    """Wrap ``kober.words.extract_word_types`` (or any callable with the same
    signature) so its returned ``WordTypes.words`` also contains
    ``extra_word_types`` -- F-047's supplement-sensitivity word types, appended
    before any statistic runs. ``labels_changed``/``labels_seen`` are carried
    through unchanged: they describe what normalisation did to the real
    corpus's signary, not this addition (the same carry-through pattern
    ``kober.words.subsample_word_types``/``restrict_to_shared`` already use,
    unedited here). An empty ``extra_word_types`` returns ``base_extract_word_types``'s
    own result unchanged, object included."""
    extra_frozen = frozenset(extra_word_types)

    def wrapped(documents, merge_homophones: bool = False):
        wt = base_extract_word_types(documents, merge_homophones=merge_homophones)
        if not extra_frozen:
            return wt
        return WordTypes(
            words=frozenset(wt.words | extra_frozen),
            labels_changed=wt.labels_changed,
            labels_seen=wt.labels_seen,
        )

    return wrapped


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", choices=["damos", "lineara", "sigla"], required=True)
    ap.add_argument("--stem-min", type=int, default=2)
    ap.add_argument("--perms", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--allow-lineara",
        action="store_true",
        help="required to run --corpus lineara or --corpus sigla, and required "
        "whenever --restrict-to-shared-with names either; see TODO item 4",
    )
    ap.add_argument(
        "--grid",
        action="store_true",
        help="also run stage 2, the grid (bridging pairs and consonant check; CHANGELOG "
        "'0.1 stage 2, the grid'); appends a grid block to the same results JSON",
    )
    ap.add_argument(
        "--grid-anchored",
        action="store_true",
        help="also run stage 2 version 0.2, anchored bridging pairs (CHANGELOG '0.1 "
        "stage 2, version 0.2, anchored bridging pairs'); appends a grid_anchored "
        "block to the same results JSON, independent of --grid",
    )
    ap.add_argument(
        "--grid-alternations",
        action="store_true",
        help="also run stage 2 version 0.3, bridging pairs from the top-ten ending "
        "alternations' own first signs (CHANGELOG '0.3'); appends a "
        "grid_alternations block to the same results JSON, independent of --grid "
        "and --grid-anchored",
    )
    ap.add_argument(
        "--subsample",
        type=int,
        default=None,
        help="seeded random subset of N word types after normalisation, no other "
        "change; tags the results filename -sub{N}-s{subsample-seed} so nothing "
        "existing is overwritten (CHANGELOG '0.1 on Linear A', size-matched control)",
    )
    ap.add_argument(
        "--subsample-seed",
        type=int,
        default=0,
        help="seed for --subsample or --subsample-docs",
    )
    ap.add_argument(
        "--subsample-docs",
        type=int,
        default=None,
        help="seeded random subset of K documents, drawn before word-type "
        "extraction so word types come from those documents alone (the 'tablet "
        "model', CHANGELOG 'Floor sweep on Linear B'); tags the results filename "
        "-docs{K}-s{subsample-seed}. Mutually exclusive with --subsample.",
    )
    ap.add_argument(
        "--results-dir",
        type=str,
        default=None,
        help="write the results JSON under this directory instead of results/ "
        "(e.g. results/kober-grammar-null/ for TODO item 8 prerequisite 1's "
        "reruns), so a rerun for a different purpose does not overwrite the "
        "original file for the same corpus/seed/tag; filename unchanged",
    )
    ap.add_argument(
        "--context",
        action="store_true",
        help="also run Kober 0.4, the context-restricted statistics under stratified "
        "(length, class) nulls (CHANGELOG '0.4', docs/ai_context/kober-method.md "
        "'Version 0.4'); appends a context block to the same results JSON",
    )
    ap.add_argument(
        "--role-tiebreak",
        action="store_true",
        help="also run Kober 0.5, the entry-role tie-break ordering for the strict "
        "top-n (CHANGELOG '0.5', docs/ai_context/kober-method.md); appends a "
        "role_tiebreak block to the same results JSON and raises the file-level "
        "protocol_version to 0.5. Roles are computed on `documents` (already "
        "doc-subsampled for --subsample-docs, else the full/--subsample-restricted "
        "corpus), then restricted to this run's own word set (A-098)",
    )
    ap.add_argument(
        "--list-tiebreak",
        action="store_true",
        help="also run Kober 0.7, the list-support tie-break ordering (support, "
        "role-sharing, list-support, lexicographic; CHANGELOG '0.7', "
        "docs/ai_context/kober-method.md); appends a list_tiebreak block to the "
        "same results JSON and raises the file-level protocol_version to 0.7. "
        "Implies --role-tiebreak (the ordering is defined on top of it). "
        "Listed words are computed on `documents` (already doc-subsampled for "
        "--subsample-docs, else the full/--subsample-restricted corpus), then "
        "restricted to this run's own word set for the real top-ten/top-three "
        "(A-116)",
    )
    ap.add_argument(
        "--reference-version",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="reference-list version the grammar-match null "
        "(ending_channel.grammar_match_null/grammar_match_null_strict/"
        "rule_firing_counts_null) is graded under (Kober 0.6, CHANGELOG '0.6'; "
        "Kober 0.8, CHANGELOG '0.8'); 2 also tries rule 11, ethnic derivation; "
        "3 also tries rules 12 to 22 (consonant-stem case and suffix, s-stem, "
        "u-stem, eu-stem plural, -went-, participle plural, infinitive, "
        "feminine of -eus, material adjective, spelling variant). Default 1 "
        "leaves stage 1 (paradigm count, alternation support, each top-20 "
        "alternation's own 'rule' field) bit-identical to every existing file "
        "-- only the grammar-match null block changes.",
    )
    ap.add_argument(
        "--medial",
        action="store_true",
        help="also run Kober 0.9's medial channel, word pairs identical except "
        "at one interior sign (CHANGELOG '0.9', docs/ai_context/kober-method.md "
        "'Version 0.9'); appends a medial block to the same results JSON and "
        "raises the file-level protocol_version to 0.9",
    )
    ap.add_argument(
        "--merge-homophones",
        action="store_true",
        help="Kober 0.9's identity sensitivity: merge homophone-index sign "
        "labels (a2->A, ai2->AI, pa2->PA, pu2->PU, ra2->RA, ra3->RA, ro2->RO, "
        "ta2->TA) at word-type extraction, before every other statistic "
        "(CHANGELOG '0.9'); raises the file-level protocol_version to 0.9",
    )
    ap.add_argument(
        "--extra-word-types",
        type=str,
        default=None,
        help="path to a private JSONL of extra Linear A sign-label-tuple word "
        "types (CHANGELOG 'Supplement sensitivity (F-047)'); appended to "
        "kober.words.extract_word_types's returned word-type set before any "
        "statistic runs, via a scoped monkeypatch of kober.report.extract_word_types "
        "restored after this run (src/ itself is never edited). Without this "
        "option, behaviour and output are byte-identical to before the option "
        "existed. Records extra_word_types_count and extra_word_types_file in "
        "the results JSON.",
    )
    ap.add_argument(
        "--restrict-to-shared-with",
        choices=["lineara", "sigla"],
        default=None,
        help="restrict the primary corpus's word types to their intersection with "
        "the named corpus's own extracted word-type set (identical normalised sign "
        "tuple in both) before any channel or null is built; for the A-002 "
        "GORILA/SigLA shared-types comparison (CHANGELOG 'Segmentation sensitivity "
        "on Linear A'). Tags the results filename -sharedwith{corpus}. Mutually "
        "exclusive with --subsample and --subsample-docs. No word list is written "
        "anywhere by this flag, only the resulting counts.",
    )
    args = ap.parse_args()

    if args.list_tiebreak:
        args.role_tiebreak = True  # 0.7 is defined on top of the 0.5 ordering

    if args.corpus in _LINEAR_A_CORPORA and not args.allow_lineara:
        print(_LINEAR_A_REFUSAL.format(corpus=args.corpus), file=sys.stderr)
        raise SystemExit(2)

    if args.restrict_to_shared_with is not None:
        if args.restrict_to_shared_with == args.corpus:
            print("--restrict-to-shared-with must name a different corpus from --corpus", file=sys.stderr)
            raise SystemExit(2)
        if not args.allow_lineara:
            print(_LINEAR_A_REFUSAL.format(corpus=args.restrict_to_shared_with), file=sys.stderr)
            raise SystemExit(2)

    _exclusive = [
        name
        for name, val in (
            ("--subsample", args.subsample),
            ("--subsample-docs", args.subsample_docs),
            ("--restrict-to-shared-with", args.restrict_to_shared_with),
        )
        if val is not None
    ]
    if len(_exclusive) > 1:
        print(f"{' and '.join(_exclusive)} are mutually exclusive", file=sys.stderr)
        raise SystemExit(2)

    t0 = time.time()
    corpus = aegean.load(args.corpus)
    documents = corpus.documents
    subsample_docs_meta = None
    if args.subsample_docs is not None:
        doc_ids = [d.id for d in corpus.documents]
        chosen = subsample_document_ids(doc_ids, args.subsample_docs, args.subsample_seed)
        documents = corpus.subset(chosen).documents
        subsample_docs_meta = {
            "requested": args.subsample_docs,
            "seed": args.subsample_seed,
            "documents_used": len(documents),
        }

    restrict_to_shared_words = None
    if args.restrict_to_shared_with is not None:
        other_corpus = aegean.load(args.restrict_to_shared_with)
        restrict_to_shared_words = extract_word_types(other_corpus.documents).words

    # A-098: roles computed on `documents` (already doc-subsampled for the
    # tablet model, else the full or --restrict-to-shared-with-restricted
    # corpus), i.e. before any word-type-level (--subsample) restriction --
    # the same "compute on documents, restrict to the final word set inside
    # build_report" pattern --context already follows for full_contexts.
    full_word_roles = word_roles(documents) if args.role_tiebreak else None
    # A-116: listed words computed on `documents`, the same "compute on
    # documents, restrict to the final word set inside build_report" pattern
    # as roles (A-098) and contexts (A-089).
    full_listings = extract_listed_words(documents) if args.list_tiebreak else None

    # CHANGELOG "Supplement sensitivity" (F-047): --extra-word-types is applied
    # by a scoped monkeypatch of kober.report.extract_word_types (the name
    # build_report's own module resolves at call time), restored in the
    # finally block below regardless of outcome; src/ itself is never edited.
    # Absent the option, the patch is never installed and every code path
    # below is byte-identical to before this option existed.
    extra_word_types: list[tuple[str, ...]] = []
    original_extract_word_types = kober_report.extract_word_types
    if args.extra_word_types:
        extra_word_types = load_extra_word_types(args.extra_word_types)
        kober_report.extract_word_types = extract_word_types_with_extra(
            original_extract_word_types, extra_word_types
        )

    try:
        report = build_report(
            documents,
            corpus=args.corpus,
            stem_min=args.stem_min,
            perms=args.perms,
            seed=args.seed,
            subsample_n=args.subsample,
            subsample_seed=args.subsample_seed,
            restrict_to_shared_words=restrict_to_shared_words,
            word_roles=full_word_roles,
            reference_version=args.reference_version,
            listings=full_listings,
            merge_homophones=args.merge_homophones,
        )
        grid_report = None
        if args.grid:
            grid_report = build_grid_report(
                report.word_types.words,
                report.ending,
                stem_min=args.stem_min,
                perms=args.perms,
                seed=args.seed,
            )
        anchored_grid_report = None
        if args.grid_anchored:
            anchored_grid_report = build_anchored_grid_report(
                report.word_types.words,
                report.ending,
                stem_min=args.stem_min,
                perms=args.perms,
                seed=args.seed,
            )
        alternation_grid_report = None
        if args.grid_alternations:
            alternation_grid_report = build_alternation_grid_report(
                report.word_types.words,
                report.ending,
                stem_min=args.stem_min,
                perms=args.perms,
                seed=args.seed,
            )
        context_report = None
        if args.context:
            # A-089: contexts are extracted from `documents` (already doc-subsampled
            # for the tablet model, unchanged for the type model or full corpus),
            # i.e. before any word-type-level (--subsample) restriction; build_context_report
            # restricts word_class down to report.word_types.words itself.
            full_contexts = extract_word_contexts(documents)
            context_report = build_context_report(
                report.word_types,
                full_contexts,
                report.ending,
                stem_min=args.stem_min,
                perms=args.perms,
                seed=args.seed,
            )
        role_tiebreak_report = None
        if args.role_tiebreak:
            role_tiebreak_report = build_role_tiebreak_report(report, full_word_roles)
        list_tiebreak_report = None
        if args.list_tiebreak:
            list_tiebreak_report = build_list_tiebreak_report(report, full_word_roles, full_listings)
        medial_report = None
        if args.medial:
            medial_report = build_medial_report(report.word_types.words, perms=args.perms, seed=args.seed)
        elapsed = time.time() - t0

        if args.subsample is not None:
            tag = f"-sub{args.subsample}-s{args.subsample_seed}"
        elif args.subsample_docs is not None:
            tag = f"-docs{args.subsample_docs}-s{args.subsample_seed}"
        elif args.restrict_to_shared_with is not None:
            tag = f"-sharedwith{args.restrict_to_shared_with}"
        else:
            tag = ""
        results_dir = Path(args.results_dir) if args.results_dir is not None else None
        path = write_report(
            report,
            grid_report,
            anchored_grid_report,
            alternation_grid_report,
            tag=tag,
            subsample_docs=subsample_docs_meta,
            results_dir=results_dir,
            context_report=context_report,
            role_tiebreak_report=role_tiebreak_report,
            list_tiebreak_report=list_tiebreak_report,
            medial_report=medial_report,
        )
    finally:
        kober_report.extract_word_types = original_extract_word_types

    if extra_word_types:
        data = json.loads(path.read_text())
        data["extra_word_types_count"] = len(extra_word_types)
        data["extra_word_types_file"] = Path(args.extra_word_types).name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print(
        render_markdown(
            report,
            grid_report,
            anchored_grid_report,
            alternation_grid_report,
            context_report,
            role_tiebreak_report,
            list_tiebreak_report,
            medial_report,
        )
    )
    print(f"\nWrote {path}")
    print(f"Wall time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
