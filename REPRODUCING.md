# Reproducing the results

From a clean download, the test suite and most findings run with nothing beyond the
pinned packages. The corpora fetch themselves, about 4 MB. Checked 2026-09-12 against an
empty cache: 175 tests pass, and the only thing created outside the repository was
pyaegean's own corpus cache.

If you are using Claude Code, the prompt "Set up the Python environment for this
repository following REPRODUCING.md, then run the tests" does everything in the next
section for you.

## Environment

- Python 3.14. Create the environment and install the pins:
  `python3.14 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- pyaegean is pinned at 0.59.0 because the tests pin corpus sizes to what that version
  loads. A later version may load different counts and fail those pins; that is the
  pin doing its job, not a bug in the tests.
- The first `aegean.load` fetches DĀMOS (Linear B) and SigLA (Linear A) into
  `~/.cache/pyaegean/`. GORILA (Linear A) ships inside the wheel. Network is needed once.
- Run the tests: `.venv/bin/python -m pytest tests/ -q`.

## Three tiers

**Tier A, nothing extra.** The corpora are enough.

**Tier B, one script.** `scripts/fetch_reference.py` downloads the openly licensed
lexicons the dictionary-matching line uses into `~/.cache/linear-a-b/reference/`. It
prints where each file came from, skips what is present, and says what to fetch by hand
if a URL has moved. The Perseus Greek texts arrive through pyaegean and build a ~270 MB
index on first use of the Greek lexicon.

**Tier C, inspect only.** The inputs are not redistributable and are not here. The
results files in `results/` are the record; the FINDINGS entry says what was measured.

## By protocol

Protocol names are CHANGELOG's. `scripts/findings.py --method <name>` lists every entry
under a method; `--show F-nnn` prints one.

| Protocol | Script | Findings | Extra inputs | Tier |
|---|---|---|---|---|
| Restoration 1.0, 1.1 | `src/linearb_restore/` (`report.py`), described in `docs/ai_context/linearb-restoration.md` | F-001, F-002 | none; writes its working files under `~/.cache/linear-a-b/` (override `LINEARB_RESTORE_CACHE`) | A |
| Kober 0.1 to 0.9.1 | `scripts/kober_run.py --corpus damos --perms 200 --seed 0`; `scripts/kober_floor_sweep.py`; the `scripts/kober_*_table.py` scoring scripts | F-016 to F-023, F-026, F-028 to F-034, F-037, F-040, F-046, F-049 | none | A |
| Value transfer 1.0 | `scripts/toponym_test.py` | F-041 | none | A |
| Measurements on di Mino 2026 | `scripts/audit_di_mino.py` | F-010 | none; the preprint is CC BY if you want to read it (`fetch_reference.py --only dimino`) | A |
| Underdot measurement | `scripts/lineara_underdots.py` | F-015 | none | A |
| Matching 0.1 to 1.1 (the etymological method) | `scripts/controlled_comparison.py`, `unrelated_controls.py`, `extra_lexicons.py`, `laryngeal_test.py`, `subset_decomposition.py` | F-003 to F-009, F-011 to F-014 and the rest of `--method etymological` | Strong's Hebrew, FrequencyWords, kaikki Hittite, ORACC, Copenhagen Ugaritic Corpus: all from `fetch_reference.py` | B |
| Supplement sensitivity 1.0, 1.1 | `--extra-word-types <file>` on `toponym_test.py` and `kober_run.py` | F-047, F-048 | a transcription of the 2024 GORILA supplement's *Index des signes* (Del Freo and Zurbach, Études Crétoises 21.6, in print). The JSONL shape is in `tests/test_extra_word_types.py` | C |
| Spikes S-001 to S-014 | `spikes/S-*/run.py`, each with a BRIEF and RESULT | F-038, F-039, F-042 to F-045 | each fetches its own open sources (S-005, S-010, S-012 download on first run). S-007 needs live model runs and is not deterministic | A, except S-007 |

Entries that are readings rather than runs (F-024, F-025, F-027) have nothing to rerun.
The work page cited carries the page numbers; the check is a library visit.

Each run stamps its results file with a `protocol_version`, and CHANGELOG describes
that version. A rerun that disagrees with a FINDINGS entry should first be compared on
version, seed and permutation count, all of which the entry states.

## What is not here, and why

- No corpus text. DĀMOS is CC BY-NC-SA and the Linear A transcription chain's licence is
  unresolved (`docs/ai_context/corpus-sources.md`). Only aggregate numbers are committed.
- No copies of the literature. Every work page under `docs/works/` cites by page, and
  the `access` field says whether the source is open, paywalled or in print.
- No model outputs from S-007, which contain word lists.

## Timing

The test suite is about a minute. A single Kober run at 200 permutations is minutes; the
floor sweep across sizes and seeds is the long job, hours rather than minutes. The
matching scripts at 100 permutations are minutes each. First use of the Greek lexicon
adds the one-off index build.
