#!/usr/bin/env python3
"""S-012: is Linear A writing language at all, by the Indus-debate measures.

    .venv/bin/python spikes/S-012-is-it-language/run.py

See BRIEF.md for the question and the two readings. Per spikes/README.md rule 4,
this script imports from ``src/`` (read-only) and edits nothing there.

**Background.** Rao et al. 2009 (docs/works/rao2009.md) argued the Indus script is
language-like from block and conditional entropy on sign sequences; Sproat 2014
(docs/works/sproat2014.md) showed the test does not discriminate once matched
non-linguistic controls (heraldry, deity symbols, weather icons) are run through it,
and that Rao's own reply conceded entropy alone does not prove language. This spike
runs the same family of measures on Linear A (GORILA) with Linear B as the positive
control the Indus debate never had: a script from the same family, at the same kind
of scale, with a known answer.

**Sequences.** One sequence per document line (``Document.line_tokens``), built from
CERTAIN ``WORD`` tokens only: signs normalised via
``linearb_restore.normalise.normalise_text`` (upper-cased, underdots and span brackets
stripped -- the same normaliser ``kober.words.extract_word_types`` uses, so a damaged
sign and its plain form are one symbol, not two) and concatenated in token order, with
a boundary symbol (``#``) inserted between consecutive WORD tokens in the same line.
Logograms, numerals, separators and non-CERTAIN words are dropped; a line with no
eligible word contributes no sequence. This is the "line" variant. A second, "word
type" variant reuses ``kober.words.extract_word_types`` directly: every distinct
normalised word type (>= 2 signs, A-038's unit) once, as its own sequence, with no
boundary symbol -- a deduplicated, type-based way of forming sequences, against the
first variant's token-based, boundary-marked running text, so the two ways of
counting can be compared directly rather than assumed to agree.

**Corpora.** Linear A: ``aegean.load("lineara")`` (GORILA), the whole corpus, no
subsampling. Linear B: ``aegean.load("damos")`` full corpus once, and twenty tablet-
model subsamples (``kober.words.subsample_document_ids``, the same seeded-permutation-
prefix device ``scripts/kober_floor_sweep.py`` uses) each bisected to land within 2%
of Linear A's own total token count -- every kind of token, every reading status,
``sum(len(d.tokens) for d in corpus.documents)``, the same count CLAUDE.md's scale
constraint reports as 6,406 -- rather than Linear A's word-type or sequence count,
because "Linear A's token count" in the brief is that documented corpus-scale number.
Bisection is valid by the same non-decreasing-in-K argument A-063 records for the
floor sweep (a document subset's total token count cannot fall when a document is
added).

**Measures**, computed once per sequence set (``measures_for_sequences``): unigram
entropy; bigram conditional entropy of the next symbol given the previous one, both
plain maximum likelihood and add-half (Lidstone delta=0.5) smoothed over the full
observed alphabet x alphabet grid, reported both ways because the smoothing choice
was Sproat's main objection to Rao's numbers; block (n-gram) entropy for n=1..4,
sliding a window within each sequence (never crossing a sequence boundary); and the
ratio of conditional to unigram entropy, both smoothings. All entropies are in bits,
computed directly from each sequence set's own empirical distribution (no held-out
estimation).

**Non-linguistic references**, each built to match Linear A's own sequence count and
per-sequence length list exactly (``chop_to_lengths``, below), twenty seeds:

1. **Shuffled Linear B.** For each of the twenty Linear-B tablet-model draws (matched
   seed-for-seed), its own sequences are pooled in a seeded-shuffled order and cut
   into Linear A-shaped chunks; each chunk is then internally shuffled. Keeps Linear
   B's own unigram frequencies (a chunk's sign multiset is real Linear B material),
   destroys order both between and within chunks.
2. **Order-0 (iid) draws from Linear A's own unigram frequencies** -- a categorical
   distribution fitted to Linear A's own sequences, sampled independently symbol by
   symbol for each target length. No order at all, by construction.
3. **First-order Markov chain fitted to Linear A's own bigram counts** and sampled
   (start symbol from Linear A's own sequence-initial distribution, each next symbol
   from the fitted transition table, falling back to Linear A's own unigram
   distribution from a context with no attested outgoing transition). A
   "language-like" synthetic: built to have exactly Linear A's own first-order
   structure and nothing more, so a measure that cannot tell this apart from Linear A
   itself is not doing any work beyond first-order statistics.
4. **DNA codon sequences**, inventory of 64. A 20,000 bp fragment of the *E. coli*
   K-12 MG1655 genome (NCBI ``NC_000913.3:1-20000``, public domain), fetched once and
   cached at ``~/.cache/linear-a-b/reference/ncbi-NC_000913.3-1-20000.fasta`` (this
   repo's existing external reference-cache convention, HENGE "Repo status"; re-fetched
   live if the cache file is absent, given up as unreachable only if both fail). Read
   as a flat codon stream (non-ACGT characters dropped); each of the twenty draws
   rotates the stream to a random start offset and slices it into Linear-A-shaped
   chunks in original order -- unlike reference 1, chunks are **not** internally
   shuffled, since the point of this reference is a real biological sequence's own
   (largely near-memoryless, but not exactly zero-order) structure, not an
   artificially flattened one.
5. **Heraldic blazons**, reachable: Parker's *A Glossary of Terms used in Heraldry*
   (1894, public domain), 4,516 blazons as republished by karlwilcox.com/heraldry
   ("please feel free to download these resources and use them"; cached at
   ``~/.cache/linear-a-b/reference/parker-heraldry-corpus.csv``), Sproat's own choice
   of non-linguistic reference genre. Each blazon's ``Blazon`` field is tokenised into
   lower-cased alphabetic words with the boundary symbol inserted only where the
   source text itself has a comma or semicolon (the real editorial divider in this
   genre, playing the same role the Aegean word-divider plays for line_sequences) --
   not, as a stricter parallel would need, at the level of the heraldic sign
   inventory itself (tincture/ordinary/charge classes), which this script does not
   attempt to reconstruct; treat this reference as a lower-confidence, word-level
   stand-in, flagged as such in RESULT.md. Blazons are pooled in a seeded-shuffled
   order (by blazon, not by word) and cut into Linear-A-shaped chunks without internal
   shuffling, preserving each stretch's own local word order.

Twenty seeds (0-19) throughout, offset per source (1000s for reference 1, 2000s for
reference 2, 3000s for reference 3, 4000s for reference 4, 5000s for reference 5, and
the tablet-model subsample seed itself for Linear B) so no two draws share a stream.

**Distance.** For a fixed set of headline measures, the unit is the standard
deviation of that measure over the twenty Linear-B tablet-model draws -- Linear B's
own resampling noise floor, the quantity the brief's "more than the noise floor"
reading refers to. Every distance (Linear A to full Linear B, to each reference's
twenty-draw median) is reported in that one unit, so the reading is "how many Linear-
B-sized steps of Linear-B's own spread" rather than an arbitrary z-score against each
group's own (differently-sized) spread.

**Must not be read as.** Anything about which language, per BRIEF.md; this script
touches only aggregate sign-sequence statistics, never Linear A readings.
"""

from __future__ import annotations

import csv
import io
import json
import math
import random
import re
import statistics
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import aegean  # noqa: E402
from aegean.core.model import Document, ReadingStatus, Token, TokenKind  # noqa: E402

from kober.words import extract_word_types, subsample_document_ids  # noqa: E402
from linearb_restore.normalise import normalise_text  # noqa: E402

BOUNDARY = "#"
SEEDS = list(range(20))
TOLERANCE = 0.02  # A-063's tablet-model matching tolerance, reused here
OUT_DIR = Path(__file__).resolve().parent

REFERENCE_CACHE = Path.home() / ".cache" / "linear-a-b" / "reference"
DNA_CACHE_FILE = REFERENCE_CACHE / "ncbi-NC_000913.3-1-20000.fasta"
DNA_FETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    "?db=nuccore&id=NC_000913.3&rettype=fasta&retmode=text&seq_start=1&seq_stop=20000"
)
DNA_SOURCE_LABEL = "NCBI NC_000913.3:1-20000 (E. coli K-12 MG1655 genome fragment, public domain)"

BLAZON_CACHE_FILE = REFERENCE_CACHE / "parker-heraldry-corpus.csv"
BLAZON_FETCH_URL = "https://www.karlwilcox.com/heraldry/parker-corpus.csv"
BLAZON_SOURCE_LABEL = (
    "Parker, A Glossary of Terms used in Heraldry (1894, public domain), "
    "via karlwilcox.com/heraldry (\"please feel free to download ... and use\")"
)


# --------------------------------------------------------------------------- #
# Sequences
# --------------------------------------------------------------------------- #


def normalise_label(label: str) -> str:
    normalised, _had_underdot, _had_span = normalise_text(label)
    return normalised.upper()


def line_sequences(documents: list[Document]) -> list[tuple[str, ...]]:
    """One sequence per document line: CERTAIN WORD tokens' normalised signs,
    concatenated in order, BOUNDARY between words. Logograms, numerals,
    separators and non-CERTAIN words dropped; an empty line contributes nothing."""
    sequences: list[tuple[str, ...]] = []
    for doc in documents:
        for line in doc.line_tokens:
            signs: list[str] = []
            for tok in line:
                if tok.kind is not TokenKind.WORD or tok.status is not ReadingStatus.CERTAIN:
                    continue
                if signs:
                    signs.append(BOUNDARY)
                signs.extend(normalise_label(s) for s in tok.signs)
            if signs:
                sequences.append(tuple(signs))
    return sequences


def word_type_sequences(documents: list[Document]) -> list[tuple[str, ...]]:
    """Words-only variant: every distinct word type once (kober.words, A-038's
    >=2-sign unit), no boundary symbol. Sorted for a reproducible sequence order."""
    return sorted(extract_word_types(documents).words)


# --------------------------------------------------------------------------- #
# Entropy measures
# --------------------------------------------------------------------------- #


def _entropy(counts, total: float) -> float:
    if total <= 0:
        return float("nan")
    h = 0.0
    for c in counts.values() if hasattr(counts, "values") else counts:
        if c <= 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


def unigram_entropy(sequences: list[tuple[str, ...]]) -> tuple[float, Counter, int]:
    counts: Counter = Counter(s for seq in sequences for s in seq)
    total = sum(counts.values())
    return _entropy(counts, total), counts, total


def bigram_tables(sequences: list[tuple[str, ...]]) -> tuple[Counter, Counter]:
    pairs: Counter = Counter()
    context: Counter = Counter()
    for seq in sequences:
        for a, b in zip(seq, seq[1:]):
            pairs[(a, b)] += 1
            context[a] += 1
    return pairs, context


def conditional_entropy_mle(pairs: Counter, context: Counter) -> float:
    total = sum(pairs.values())
    if total == 0:
        return float("nan")
    return _entropy(pairs, total) - _entropy(context, total)


def conditional_entropy_smoothed(
    pairs: Counter, context: Counter, alphabet: list[str], delta: float = 0.5
) -> float:
    """Add-``delta`` (Lidstone) smoothing over the full alphabet x alphabet grid,
    Sproat's main objection to Rao's plain-MLE conditional entropy answered by
    reporting both."""
    n = len(alphabet)
    if n == 0:
        return float("nan")
    total_pairs = sum(pairs.values())
    denom = total_pairs + delta * n * n
    h = 0.0
    for a in alphabet:
        ca = context.get(a, 0)
        pa = (ca + delta * n) / denom
        if pa <= 0:
            continue
        for b in alphabet:
            cab = pairs.get((a, b), 0)
            pab = (cab + delta) / denom
            h -= pab * math.log2(pab / pa)
    return h


def block_entropy(sequences: list[tuple[str, ...]], n: int) -> float:
    counts: Counter = Counter()
    total = 0
    for seq in sequences:
        if len(seq) < n:
            continue
        for i in range(len(seq) - n + 1):
            counts[seq[i : i + n]] += 1
            total += 1
    return _entropy(counts, total)


def measures_for_sequences(sequences: list[tuple[str, ...]]) -> dict:
    alphabet = sorted({s for seq in sequences for s in seq})
    h1, _unigram_counts, n_symbols = unigram_entropy(sequences)
    pairs, context = bigram_tables(sequences)
    h_cond_mle = conditional_entropy_mle(pairs, context)
    h_cond_smoothed = conditional_entropy_smoothed(pairs, context, alphabet)
    blocks = {n: block_entropy(sequences, n) for n in (1, 2, 3, 4)}
    ratio_mle = h_cond_mle / h1 if h1 else float("nan")
    ratio_smoothed = h_cond_smoothed / h1 if h1 else float("nan")
    return {
        "n_sequences": len(sequences),
        "n_symbols": n_symbols,
        "alphabet_size": len(alphabet),
        "unigram_entropy_bits": h1,
        "conditional_entropy_bigram_mle_bits": h_cond_mle,
        "conditional_entropy_bigram_addhalf_bits": h_cond_smoothed,
        "block_entropy_bits": blocks,
        "ratio_conditional_to_unigram_mle": ratio_mle,
        "ratio_conditional_to_unigram_addhalf": ratio_smoothed,
    }


def summarize_group(dicts: list[dict]) -> dict:
    scalar_keys = [
        "n_sequences",
        "n_symbols",
        "alphabet_size",
        "unigram_entropy_bits",
        "conditional_entropy_bigram_mle_bits",
        "conditional_entropy_bigram_addhalf_bits",
        "ratio_conditional_to_unigram_mle",
        "ratio_conditional_to_unigram_addhalf",
    ]
    out: dict = {}
    for key in scalar_keys:
        vals = [d[key] for d in dicts]
        out[key] = {
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "n": len(vals),
        }
    block_out: dict = {}
    for n in (1, 2, 3, 4):
        vals = [d["block_entropy_bits"][n] for d in dicts]
        block_out[str(n)] = {
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        }
    out["block_entropy_bits"] = block_out
    return out


# --------------------------------------------------------------------------- #
# Tablet-model bisection on total token count (adapts scripts/kober_floor_sweep.py's
# bisect_k, A-063, from word-type count to total token count -- "Linear A's token
# count" per CLAUDE.md's scale constraint, not its word-type count).
# --------------------------------------------------------------------------- #


def _token_count_for_k(corpus, doc_ids_sorted: list[str], k: int, seed: int) -> int:
    chosen = subsample_document_ids(doc_ids_sorted, k, seed)
    subset = corpus.subset(chosen)
    return sum(len(d.tokens) for d in subset.documents)


def bisect_k_tokens(
    corpus, doc_ids_sorted: list[str], target: int, seed: int, tol: float = TOLERANCE
) -> tuple[int, int, float, bool]:
    """Return (k, resulting_token_count, relative_error, within_tolerance)."""
    total = len(doc_ids_sorted)
    full_count = _token_count_for_k(corpus, doc_ids_sorted, total, seed)
    if full_count < target:
        err = abs(full_count - target) / target
        return total, full_count, err, err <= tol

    lo, hi = 1, total
    while lo < hi:
        mid = (lo + hi) // 2
        c = _token_count_for_k(corpus, doc_ids_sorted, mid, seed)
        if c >= target:
            hi = mid
        else:
            lo = mid + 1
    k_hi = lo
    c_hi = _token_count_for_k(corpus, doc_ids_sorted, k_hi, seed)
    candidates = [(k_hi, c_hi)]
    if k_hi > 1:
        k_lo = k_hi - 1
        c_lo = _token_count_for_k(corpus, doc_ids_sorted, k_lo, seed)
        candidates.append((k_lo, c_lo))
    best_k, best_c = min(candidates, key=lambda kc: abs(kc[1] - target) / target)
    err = abs(best_c - target) / target
    return best_k, best_c, err, err <= tol


# --------------------------------------------------------------------------- #
# Shape-matched reference construction
# --------------------------------------------------------------------------- #


def build_pool(units: list[tuple[str, ...]], rng: random.Random) -> list[str]:
    """Flatten ``units`` (each a tuple of symbols) into one list, in a seeded-
    shuffled order of the units themselves (not of individual symbols), so local
    structure within a unit survives until ``chop_to_lengths`` decides whether to
    shuffle it away."""
    order = list(units)
    rng.shuffle(order)
    return [sym for unit in order for sym in unit]


def rotate_pool(stream: list[str], rng: random.Random) -> list[str]:
    """A seeded random rotation of one long stream (used for the DNA reference,
    which is a single real sequence rather than many independent units)."""
    if not stream:
        return []
    start = rng.randrange(len(stream))
    return stream[start:] + stream[:start]


def chop_to_lengths(
    pool: list[str], target_lengths: list[int], rng: random.Random, shuffle_within: bool
) -> list[tuple[str, ...]]:
    """``pool`` cut into consecutive chunks of ``target_lengths`` (wrapping if the
    pool is shorter than needed), each chunk internally shuffled when
    ``shuffle_within`` (reference 1's "destroys order"); left in pool order
    otherwise (references 4 and 5's "keeps whatever real local order there is")."""
    if not pool:
        return [tuple() for _ in target_lengths]
    n = len(pool)
    idx = 0
    out: list[tuple[str, ...]] = []
    for length in target_lengths:
        chunk = [pool[(idx + k) % n] for k in range(length)]
        idx = (idx + length) % n
        if shuffle_within:
            rng.shuffle(chunk)
        out.append(tuple(chunk))
    return out


def fit_unigram_dist(sequences: list[tuple[str, ...]]) -> tuple[list[str], list[float]]:
    counts: Counter = Counter(s for seq in sequences for s in seq)
    symbols = sorted(counts)
    total = sum(counts.values())
    probs = [counts[s] / total for s in symbols]
    return symbols, probs


def sample_iid(
    symbols: list[str], probs: list[float], target_lengths: list[int], rng: random.Random
) -> list[tuple[str, ...]]:
    return [tuple(rng.choices(symbols, weights=probs, k=length)) if length else tuple() for length in target_lengths]


def fit_markov1(sequences: list[tuple[str, ...]]):
    trans: dict[str, Counter] = defaultdict(Counter)
    starts: Counter = Counter()
    for seq in sequences:
        if not seq:
            continue
        starts[seq[0]] += 1
        for a, b in zip(seq, seq[1:]):
            trans[a][b] += 1
    start_symbols = sorted(starts)
    start_weights = [starts[s] for s in start_symbols]
    trans_norm: dict[str, tuple[list[str], list[int]] | None] = {}
    for a, counter in trans.items():
        keys = sorted(counter)
        trans_norm[a] = (keys, [counter[k] for k in keys])
    return start_symbols, start_weights, trans_norm


def sample_markov1(
    start_symbols: list[str],
    start_weights: list[int],
    trans_norm: dict,
    fallback_symbols: list[str],
    fallback_probs: list[float],
    target_lengths: list[int],
    rng: random.Random,
) -> list[tuple[str, ...]]:
    out: list[tuple[str, ...]] = []
    for length in target_lengths:
        if length == 0:
            out.append(tuple())
            continue
        seq = [rng.choices(start_symbols, weights=start_weights, k=1)[0]]
        for _ in range(length - 1):
            choice = trans_norm.get(seq[-1])
            if choice is None:
                nxt = rng.choices(fallback_symbols, weights=fallback_probs, k=1)[0]
            else:
                keys, weights = choice
                nxt = rng.choices(keys, weights=weights, k=1)[0]
            seq.append(nxt)
        out.append(tuple(seq))
    return out


# --------------------------------------------------------------------------- #
# External references: DNA codons, heraldic blazons
# --------------------------------------------------------------------------- #


def _read_or_fetch(cache_file: Path, url: str, timeout: int = 15) -> str | None:
    if cache_file.exists():
        return cache_file.read_text(errors="replace")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            text = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(text)
    return text


def load_codon_stream() -> list[str] | None:
    text = _read_or_fetch(DNA_CACHE_FILE, DNA_FETCH_URL)
    if not text:
        return None
    nt = "".join(line.strip() for line in text.splitlines() if not line.startswith(">"))
    nt = "".join(ch for ch in nt.upper() if ch in "ACGT")
    codons = [nt[i : i + 3] for i in range(0, len(nt) - 2, 3)]
    return codons or None


_BLAZON_TOKEN_RE = re.compile(r"[A-Za-z]+|[,;]")


def tokenize_blazon(text: str) -> tuple[str, ...]:
    out: list[str] = []
    for m in _BLAZON_TOKEN_RE.finditer(text):
        piece = m.group(0)
        if piece in ",;":
            if out and out[-1] != BOUNDARY:
                out.append(BOUNDARY)
        else:
            out.append(piece.lower())
    while out and out[-1] == BOUNDARY:
        out.pop()
    while out and out[0] == BOUNDARY:
        out.pop(0)
    return tuple(out)


def load_blazon_units() -> list[tuple[str, ...]] | None:
    text = _read_or_fetch(BLAZON_CACHE_FILE, BLAZON_FETCH_URL)
    if not text:
        return None
    reader = csv.DictReader(io.StringIO(text))
    units = [tokenize_blazon(row.get("Blazon", "")) for row in reader]
    units = [u for u in units if u]
    return units or None


# --------------------------------------------------------------------------- #
# Distance in units of Linear B's own subsample spread
# --------------------------------------------------------------------------- #

HEADLINE_MEASURES: list[tuple[str, int | None]] = [
    ("unigram_entropy_bits", None),
    ("conditional_entropy_bigram_mle_bits", None),
    ("conditional_entropy_bigram_addhalf_bits", None),
    ("ratio_conditional_to_unigram_mle", None),
    ("ratio_conditional_to_unigram_addhalf", None),
    ("block_entropy_bits", 2),
    ("block_entropy_bits", 3),
    ("block_entropy_bits", 4),
]


def _label(key: str, block_n: int | None) -> str:
    return key if block_n is None else f"{key}_n{block_n}"


def _spec_value(measures: dict, key: str, block_n: int | None) -> float:
    return measures["block_entropy_bits"][block_n] if key == "block_entropy_bits" else measures[key]


def _spec_stat(summary: dict, key: str, block_n: int | None, stat: str) -> float:
    if key == "block_entropy_bits":
        return summary["block_entropy_bits"][str(block_n)][stat]
    return summary[key][stat]


def compute_distances(
    la_measures: dict,
    lb_matched_summary: dict,
    singleton_groups: dict[str, dict],
    summary_groups: dict[str, dict | None],
) -> dict:
    out: dict = {}
    for key, block_n in HEADLINE_MEASURES:
        label = _label(key, block_n)
        la_val = _spec_value(la_measures, key, block_n)
        spread = _spec_stat(lb_matched_summary, key, block_n, "stdev")
        lb_med = _spec_stat(lb_matched_summary, key, block_n, "median")
        row = {
            "linear_a_value": la_val,
            "linear_b_matched_median": lb_med,
            "linear_b_matched_spread_stdev": spread,
            "distance_to_linear_b_matched": (la_val - lb_med) / spread if spread else None,
        }
        for name, singleton in singleton_groups.items():
            other = _spec_value(singleton, key, block_n)
            row[f"distance_to_{name}"] = (la_val - other) / spread if spread else None
        for name, summary in summary_groups.items():
            if summary is None:
                row[f"distance_to_{name}"] = None
                continue
            other = _spec_stat(summary, key, block_n, "median")
            row[f"distance_to_{name}"] = (la_val - other) / spread if spread else None
        out[label] = row
    return out


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def run_variant(
    variant: str,
    la_docs: list[Document],
    lb_full_docs: list[Document],
    lb_matched_docsets: dict[int, list[Document]],
) -> dict:
    build_seq = line_sequences if variant == "line" else word_type_sequences

    la_sequences = build_seq(la_docs)
    la_lengths = [len(s) for s in la_sequences]
    la_measures = measures_for_sequences(la_sequences)

    lb_full_sequences = build_seq(lb_full_docs)
    lb_full_measures = measures_for_sequences(lb_full_sequences)

    lb_matched_sequences = {seed: build_seq(lb_matched_docsets[seed]) for seed in SEEDS}
    lb_matched_measures = {seed: measures_for_sequences(seqs) for seed, seqs in lb_matched_sequences.items()}
    lb_matched_summary = summarize_group([lb_matched_measures[s] for s in SEEDS])

    # Reference 1: shuffled matched-size Linear B, seed-paired with the tablet draws.
    ref1_measures = {}
    for seed in SEEDS:
        rng = random.Random(1000 + seed)
        pool = build_pool(lb_matched_sequences[seed], rng)
        chunks = chop_to_lengths(pool, la_lengths, rng, shuffle_within=True)
        ref1_measures[seed] = measures_for_sequences(chunks)
    ref1_summary = summarize_group([ref1_measures[s] for s in SEEDS])

    # Reference 2: iid draws from Linear A's own unigram frequencies.
    la_symbols, la_probs = fit_unigram_dist(la_sequences)
    ref2_measures = {}
    for seed in SEEDS:
        rng = random.Random(2000 + seed)
        chunks = sample_iid(la_symbols, la_probs, la_lengths, rng)
        ref2_measures[seed] = measures_for_sequences(chunks)
    ref2_summary = summarize_group([ref2_measures[s] for s in SEEDS])

    # Reference 3: first-order Markov chain fitted to Linear A's own bigrams.
    start_symbols, start_weights, trans_norm = fit_markov1(la_sequences)
    ref3_measures = {}
    for seed in SEEDS:
        rng = random.Random(3000 + seed)
        chunks = sample_markov1(start_symbols, start_weights, trans_norm, la_symbols, la_probs, la_lengths, rng)
        ref3_measures[seed] = measures_for_sequences(chunks)
    ref3_summary = summarize_group([ref3_measures[s] for s in SEEDS])

    # Reference 4: DNA codons.
    codon_stream = load_codon_stream()
    if codon_stream:
        ref4_measures = {}
        for seed in SEEDS:
            rng = random.Random(4000 + seed)
            pool = rotate_pool(codon_stream, rng)
            chunks = chop_to_lengths(pool, la_lengths, rng, shuffle_within=False)
            ref4_measures[seed] = measures_for_sequences(chunks)
        ref4_summary = summarize_group([ref4_measures[s] for s in SEEDS])
        ref4_status = f"reached: {DNA_SOURCE_LABEL}"
    else:
        ref4_summary = None
        ref4_status = "not reachable"

    # Reference 5: heraldic blazons.
    blazon_units = load_blazon_units()
    if blazon_units:
        ref5_measures = {}
        for seed in SEEDS:
            rng = random.Random(5000 + seed)
            pool = build_pool(blazon_units, rng)
            chunks = chop_to_lengths(pool, la_lengths, rng, shuffle_within=False)
            ref5_measures[seed] = measures_for_sequences(chunks)
        ref5_summary = summarize_group([ref5_measures[s] for s in SEEDS])
        ref5_status = f"reached: {BLAZON_SOURCE_LABEL}"
    else:
        ref5_summary = None
        ref5_status = "not reachable"

    distances = compute_distances(
        la_measures,
        lb_matched_summary,
        singleton_groups={"linear_b_full": lb_full_measures},
        summary_groups={
            "reference_1_shuffled_linear_b": ref1_summary,
            "reference_2_iid_unigram": ref2_summary,
            "reference_3_markov_bigram": ref3_summary,
            "reference_4_dna_codons": ref4_summary,
            "reference_5_heraldic_blazons": ref5_summary,
        },
    )

    return {
        "linear_a_sequence_length_summary": {
            "n_sequences": len(la_lengths),
            "median": statistics.median(la_lengths) if la_lengths else None,
            "min": min(la_lengths) if la_lengths else None,
            "max": max(la_lengths) if la_lengths else None,
            "sum": sum(la_lengths),
        },
        "linear_a": la_measures,
        "linear_b_full": lb_full_measures,
        "linear_b_matched": {
            "per_seed_token_count": {
                str(seed): lb_matched_measures[seed]["n_symbols"] for seed in SEEDS
            },
            "summary": lb_matched_summary,
        },
        "reference_1_shuffled_linear_b": {"summary": ref1_summary},
        "reference_2_iid_unigram_from_linear_a": {"summary": ref2_summary},
        "reference_3_markov_bigram_from_linear_a": {"summary": ref3_summary},
        "reference_4_dna_codons": {"status": ref4_status, "summary": ref4_summary},
        "reference_5_heraldic_blazons": {"status": ref5_status, "summary": ref5_summary},
        "distances_in_linear_b_matched_spread_units": distances,
    }


def main() -> dict:
    la_corpus = aegean.load("lineara")
    la_docs = la_corpus.documents
    la_total_tokens = sum(len(d.tokens) for d in la_docs)

    damos_corpus = aegean.load("damos")
    damos_doc_ids_sorted = sorted(d.id for d in damos_corpus.documents)
    lb_full_docs = damos_corpus.documents

    lb_matched_docsets: dict[int, list[Document]] = {}
    lb_matched_bisection: dict[int, dict] = {}
    for seed in SEEDS:
        k, count, err, ok = bisect_k_tokens(damos_corpus, damos_doc_ids_sorted, la_total_tokens, seed)
        chosen = subsample_document_ids(damos_doc_ids_sorted, k, seed)
        lb_matched_docsets[seed] = damos_corpus.subset(chosen).documents
        lb_matched_bisection[seed] = {
            "documents_k": k,
            "token_count": count,
            "relative_error": err,
            "within_tolerance": ok,
        }

    payload = {
        "question": (
            "Where does Linear A fall on Rao 2009's block/conditional entropy measures, "
            "against Linear B as the positive control the Indus debate lacked and "
            "Sproat 2014's matched non-linguistic references?"
        ),
        "protocol": {
            "linear_a_corpus": "lineara (GORILA)",
            "linear_a_total_tokens": la_total_tokens,
            "linear_b_corpus": "damos",
            "linear_b_full_documents": len(lb_full_docs),
            "tablet_model_seeds": SEEDS,
            "tablet_model_tolerance": TOLERANCE,
            "tablet_model_bisection": lb_matched_bisection,
            "smoothing_delta": 0.5,
            "block_entropy_n": [1, 2, 3, 4],
        },
        "variants": {},
    }

    for variant in ("line", "word_type"):
        payload["variants"][variant] = run_variant(variant, la_docs, lb_full_docs, lb_matched_docsets)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return payload


if __name__ == "__main__":
    data = main()
    print(json.dumps(data["protocol"], indent=2, default=str))
    for variant, v in data["variants"].items():
        print(f"\n== variant: {variant}")
        print("linear_a:", {k: v["linear_a"][k] for k in ("n_sequences", "alphabet_size", "unigram_entropy_bits", "conditional_entropy_bigram_addhalf_bits")})
        print("linear_b_matched summary (unigram/cond addhalf):", {
            "unigram": v["linear_b_matched"]["summary"]["unigram_entropy_bits"],
            "cond_addhalf": v["linear_b_matched"]["summary"]["conditional_entropy_bigram_addhalf_bits"],
        })
        print("reference_4 status:", v["reference_4_dna_codons"]["status"])
        print("reference_5 status:", v["reference_5_heraldic_blazons"]["status"])
