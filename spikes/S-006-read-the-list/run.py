#!/usr/bin/env python3
"""S-006 · Read the Linear A list anyway.

Loads the top twenty ending-channel and prefix-channel alternations from
``results/kober-09/kober-lineara-seed0.json`` (Kober 0.9, unmerged, seed 0 --
the same file F-040 reports), plus the file's own N2 null statistics for the
maximum support in each channel. Beside each top-twenty pair, records whether
it appears in ``field-proposals.json``, the hand-maintained catalogue of
by-eye alternations the field has proposed (Duhoux, Facchetti 1999b, Thomas
2020, Monti 2022; Schoep 2002, Davis 2013/2014 and Younger's suffix list
checked and found to carry no specific checkable pair -- see that file's
citations for what was and was not read this session).

Also recomputes the *full* ranked alternation list for each channel, by
importing ``kober.words``/``kober.paradigms`` on the same corpus, stem_min
and merge_homophones setting the results file used (never editing ``src/``,
per spikes/README.md rule 4) -- the results file itself only stores the top
twenty, so a field proposal that misses the top twenty is searched for in
this recomputed list instead. Prints the recomputation's own top twenty
first, as a check that it reproduces the stored file exactly.

Spike S-006 (spikes/S-006-read-the-list/BRIEF.md). Aggregate only: sign
labels, supports, counts and citations, never Linear A words. Imports from
src/kober and pyaegean; writes nothing under results/ or src/.

    .venv/bin/python spikes/S-006-read-the-list/run.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402

from kober.paradigms import ending_channel, prefix_channel, ranked_alternations  # noqa: E402
from kober.words import extract_word_types  # noqa: E402

RESULTS_FILE = ROOT / "results" / "kober-09" / "kober-lineara-seed0.json"
PROPOSALS_FILE = Path(__file__).resolve().parent / "field-proposals.json"


def label_pair(entry: dict) -> frozenset[str]:
    return frozenset((entry["e1_label"], entry["e2_label"]))


def full_ranked_index(channel_result) -> dict[frozenset[str], tuple[int, int]]:
    """label-pair -> (1-based rank in the recomputed full list, support)."""
    ranked = ranked_alternations(channel_result.alternation_support, None)
    index: dict[frozenset[str], tuple[int, int]] = {}
    for i, ((e1, e2), support) in enumerate(ranked, start=1):
        index[frozenset(("-".join(e1), "-".join(e2)))] = (i, support)
    return index


def build_full_lists():
    """Recompute both channels' full alternation lists on the same corpus,
    stem_min and merge_homophones setting as the stored results file, so a
    field proposal outside the top twenty can still be located. Imports
    only; never writes under src/ or results/ (spikes/README.md rule 4)."""
    stored = json.loads(RESULTS_FILE.read_text())
    assert stored["corpus"] == "lineara"
    assert stored["merge_homophones"] is False
    stem_min = stored["stem_min"]

    corpus = aegean.load("lineara")
    word_types = extract_word_types(corpus.documents, merge_homophones=False)
    ending = ending_channel(word_types.words, stem_min=stem_min)
    prefix = prefix_channel(word_types.words, stem_min=stem_min)
    return stored, ending, prefix


def check_reproduction(stored: dict, ending, prefix) -> list[str]:
    """Sanity check: the recomputed top twenty must equal the stored file's,
    entry for entry. Returns a list of mismatch descriptions (empty if the
    reproduction is exact)."""
    problems = []
    for name, channel_result, stored_key in (
        ("ending", ending, "ending_channel"),
        ("prefix", prefix, "prefix_channel"),
    ):
        stored_top20 = stored[stored_key]["top_20_alternations"]
        recomputed = ranked_alternations(channel_result.alternation_support, 20)
        if len(stored_top20) != len(recomputed):
            problems.append(f"{name}: length mismatch")
            continue
        for i, (entry, ((e1, e2), support)) in enumerate(zip(stored_top20, recomputed)):
            recomputed_pair = frozenset(("-".join(e1), "-".join(e2)))
            stored_pair = label_pair(entry)
            if recomputed_pair != stored_pair or support != entry["support"]:
                problems.append(
                    f"{name} rank {i + 1}: stored {sorted(stored_pair)}={entry['support']} "
                    f"vs recomputed {sorted(recomputed_pair)}={support}"
                )
    return problems


def max_support_percentile(stored: dict, channel_key: str) -> dict:
    return stored[channel_key]["n2_alternation_support"]["max_support"]


def render_top20_table(channel_name: str, stored: dict, channel_key: str, proposals: list[dict]) -> str:
    entries = stored[channel_key]["top_20_alternations"]
    max_stat = max_support_percentile(stored, channel_key)
    real_max = max_stat["real_value"]
    max_pctile = max_stat["real_percentile"]

    by_pair: dict[frozenset[str], list[dict]] = {}
    for p in proposals:
        if p.get("channel") == channel_name and p.get("pair"):
            by_pair.setdefault(frozenset(p["pair"]), []).append(p)

    lines = [
        f"| rank | pair | support | N2 percentile | field proposal |",
        f"|---:|---|---:|---|---|",
    ]
    for i, entry in enumerate(entries, start=1):
        pair = label_pair(entry)
        support = entry["support"]
        pctile = f"{max_pctile:.1f} (of the *maximum*, this pair)" if support == real_max else "n/a (file carries the max only)"
        hits = by_pair.get(pair, [])
        if hits:
            field = "; ".join(f"**{h['source']}** — {h['paraphrase']}" for h in hits)
        else:
            field = "—"
        lines.append(f"| {i} | {entry['e1_label']} / {entry['e2_label']} | {support} | {pctile} | {field} |")
    return "\n".join(lines)


def render_missing_table(stored: dict, ending_full, prefix_full, proposals: list[dict]) -> str:
    lines = [
        "| proposal | source | pair | in top twenty? | where it ranks |",
        "|---|---|---|---|---|",
    ]
    channel_top20 = {
        "ending": {label_pair(e) for e in stored["ending_channel"]["top_20_alternations"]},
        "prefix": {label_pair(e) for e in stored["prefix_channel"]["top_20_alternations"]},
    }
    channel_full = {"ending": ending_full, "prefix": prefix_full}
    for p in proposals:
        channel = p.get("channel")
        pair = p.get("pair")
        source = p["source"]
        if pair is None:
            lines.append(
                f"| {p['id']} | {source} | (none) | n/a | not checked — {p['paraphrase']} |"
            )
            continue
        pair_set = frozenset(pair)
        in_top20 = pair_set in channel_top20[channel]
        full_index = channel_full[channel]
        if pair_set in full_index:
            rank, support = full_index[pair_set]
            where = f"rank {rank} of {len(full_index)}, support {support}"
        else:
            where = "not attested as a same-stem alternation anywhere in the corpus (support 0)"
        lines.append(
            f"| {p['id']} | {source} | {pair[0]}/{pair[1]} ({channel}) | {'yes' if in_top20 else 'no'} | {where} |"
        )
    return "\n".join(lines)


def main() -> None:
    stored, ending, prefix = build_full_lists()

    problems = check_reproduction(stored, ending, prefix)
    print("=== Reproduction check ===")
    if problems:
        for p in problems:
            print("MISMATCH:", p)
    else:
        print("Recomputed top twenty (both channels) matches "
              f"{RESULTS_FILE.relative_to(ROOT)} exactly.")
    print()

    proposals = json.loads(PROPOSALS_FILE.read_text())["proposals"]

    ending_full = full_ranked_index(ending)
    prefix_full = full_ranked_index(prefix)

    print("=== Table 1: ending-channel top twenty ===")
    print(render_top20_table("ending", stored, "ending_channel", proposals))
    print()

    print("=== Table 2: prefix-channel top twenty ===")
    print(render_top20_table("prefix", stored, "prefix_channel", proposals))
    print()

    print("=== Table 3: field proposals, in or out of the top twenty ===")
    print(render_missing_table(stored, ending_full, prefix_full, proposals))
    print()

    print(f"Ending channel: {len(ending.alternation_support)} alternations total, "
          f"paradigm_count_total {ending.paradigm_count_total}.")
    print(f"Prefix channel: {len(prefix.alternation_support)} alternations total, "
          f"paradigm_count_total {prefix.paradigm_count_total}.")


if __name__ == "__main__":
    main()
