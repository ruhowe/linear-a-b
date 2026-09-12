# HENGE — AI Context Index

<!-- © Ru Howe 2026. CC BY-SA 4.0, like every document in this repository: reuse it in
any project, commercial or not, with credit, and keep adaptations under the same licence
(see LICENSE.md). -->

Compact reference files for AI tools and people working on this repo. Each file covers one domain and captures what isn't obvious from any single source file: cross-file contracts, mapping rules, invariants, and the reasons behind decisions.

## The five rules

1. One file per domain. Be efficient: split if it grows unwieldy.
2. No prose. Bullets, tables, shorthand. Every line carries signal.
3. Never restate code. Do point to it: file paths, line references, method names.
4. Capture what isn't in any single file: cross-file contracts, mapping rules, invariants, and decisions that explain why something is the way it is.
5. Update in the same change. Stale context is worse than no context.

Rule 5 reads "same change" rather than "same PR": this repo is under git but has no PR flow. See Repo status below.

## Index

| File | Load when working on... |
|---|---|
| **`../../START-HERE.md`** | Helping a visitor: the VS Code and Claude Code route, prompts to copy, and the corrections policy (pull request or email; no discussion threads) |
| **`../../REPRODUCING.md`** | Rerunning or extending any result: environment pins, the three tiers of inputs, the protocol-to-script table, what is inspect-only and why |
| [writing-style.md](writing-style.md) | Writing anything a human reads: replies, commit messages, PR descriptions, README and guide prose, work pages. Twelve rules, copied from the Stornaway HENGE where the canonical version lives |
| **`../works/*.md`** | The field catalogue, one page per source, analysis or decipherment attempt. YAML frontmatter is queryable via `scripts/bib.py`; the body carries claim, links and our assessment. Pages are the source of truth, so they can be reviewed and corrected on GitHub per-file. Replaced `bibliography.yaml` 2026-09-11 |
| **`../guides/*.md`** | Plain-English explanation for people, no linguistics assumed: the two scripts, why Linear A is hard, how we test a claim, how to read a work page. Linked from the root README |
| [terminology.md](terminology.md) | Naming the two methods before writing about either: the etymological method (sound values, then dictionary lookup) and the Kober method (structure from sign patterns, no values), their aliases in the literature, where each lives in the repo, and the fixed meanings of map, wrong real language, synthetic twin, positive control and protocol version |
| [corpus-sources.md](corpus-sources.md) | Where Linear A and Linear B data comes from, licences, DĀMOS / GORILA / SigLA via pyaegean, corpus counts, cross-script sign overlap, Unicode blocks and assigned ranges, transliteration↔glyph mapping, circularity trap in Linear A readings, image archives, NC restrictions, citation obligations |
| [state-of-the-art.md](state-of-the-art.md) | Choosing or judging a method: published results on Linear A and Linear B (computational, philological, palaeographic, imaging), decipherment-methodology lineage and analogues (Ugaritic, Iberian, Indus, Cypro-Minoan, Proto-Elamite), what the field requires of a credible claim, which pyaegean modules already implement which literature method, fringe/hype register, field-stated open problems, measured local baselines (hapax, entropy), verification status of every citation |
| [linearb-restoration.md](linearb-restoration.md) | Anything touching `src/linearb_restore/`: the DĀMOS extraction contract and its three loader traps, sequence/eligibility/masking/split protocol, frozen candidate sets, measured baseline results with CIs, the required comparison wording against the published figures, and why top-20 and single-split numbers on this corpus mislead |
| [hypothesis-harness.md](hypothesis-harness.md) | Running any test across all candidate languages at once: the registry and scenario weightings, the three generations of null and what each caught, why Greek is a contaminated control that nonetheless bounds the artifact, and the result that a known-false hypothesis outscores the one under test |
| [kober-method.md](kober-method.md) | Anything under `src/kober/`: the Kober method as an instrument, stems, endings, prefixes and paradigms defined, the two statistics and their two nulls (and why the protocol 1.0 null cannot be reused), the Linear B reference alternation list and pre-registered criterion, the stage 2 grid check, the sizing counts that show Linear A cannot support a ranked alternation list, and what the instrument cannot do |
| [value-transfer.md](value-transfer.md) | Testing A-001, the convention that Linear A signs carry Linear B values: the toponym test with values permuted at every position, its three wrong controls, what passing does and does not license, and the null that was wrong first |
| [semitic-null-test.md](semitic-null-test.md) | Testing a proposed decipherment against fictitious ones: the Hebrew root-space base rate, the Linear A sign→consonant-set map and why it is so permissive, the breadth-matched permutation null (and the false positive the naive null gives), the planted-root positive control, and what the negative result does and does not establish |
| [result-discipline.md](result-discipline.md) | Before calling any result a finding: the pre-registration, freeze, wrong-real-control, variance and same-run requirements learned from three withdrawn conclusions; the three questions to ask before reading a number; symmetry of surprise |
| **`../../spikes/`** | The experimental half: ideas tried without the standing of a finding, under the rules in `spikes/README.md` (brief first, controls travel, never edits `src/`, promotion is a rebuild). Nothing in it is quoted by claims, guides or reports |
| [claims.md](claims.md) | Saying what the project has found, in any form: the eight claims split into atoms, each tied to current FINDINGS entries, with the prior-art grade scale, the search protocol and the ledger of earlier work. Read before calling anything new, before writing a summary for a person, and before any literature search for precedent |
| [evaluation-harness.md](evaluation-harness.md) | Deciding what this repo should build or publish: why calibrated results rather than tools, the instances-before-framework sequencing rule, negative vs positive controls with sources and status, the instance registry, the Corazza and Di Mino blockers, contact-the-claimant rule, and the anti-patterns that turn this into another ignored repo |

<!-- Start flat. When the table grows past ten rows or so, group it under
     section headings so an agent can scan straight to the right group.
     Keep every entry to one line: the file name, and the trigger. -->

## Scope

Both Aegean scripts, deliberately in one repo: **Linear B** (deciphered, Mycenaean Greek) and **Linear A** (undeciphered, Minoan). They share a graphic inventory and one toolkit, and the relationship between them is the research question. See the Decisions table in [corpus-sources.md](corpus-sources.md).

## Where results live

Assumptions are registered in `ASSUMPTIONS.md` at the repo root, numbered A-nnn, the moment
they are made. A FINDINGS entry cites the assumptions it rests on. A new lexicon, map or
protocol version is not complete until its assumptions are entered.

**Results and verdicts are stated only in `FINDINGS.md` at the repo root**, as dated
entries tied to a protocol version from `CHANGELOG.md`. HENGE files describe protocols,
contracts, licences and gotchas and point to FINDINGS entries by number (F-nnn). If a
HENGE file asserts a number, it is quoting FINDINGS. Decided 2026-09-11.

Query them with `scripts/findings.py` (`--status`, `--method`, `--assumption A-nnn`,
`--cites F-nnn`, `--show F-nnn`); the index table at the top of FINDINGS.md is generated
by `--write-index` and is the one generated block in that file. `results/README.md` maps
every results file pattern to the finding it feeds. `JOURNAL.md` at the repo root is the
phase-by-phase narrative of why each stage followed the last; append an entry when a
phase closes. `docs/reports/` holds dated write-ups for specialists that quote FINDINGS
only; a report is regenerated, never edited, when the findings it quotes change (a dated
addendum is the one permitted edit). Reports: 2026-09-11 (the two methods), 2026-09-12 (a
fresh look with the primaries: assumptions, methods, what precedent hid).

## Repo status

- **Under git since 2026-09-10** (reversing the earlier same-day decision, at Ru's instruction, once real code began accumulating and an unattended build run was starting). Committing publishes nothing; the published branch is a snapshot. `.gitignore` excludes `.venv/` and every corpus-derived artifact; commit history is one commit per build step. `.backups/` is retained for the pre-git snapshot but git is the undo mechanism now.
- **pytest installed into `.venv` 2026-09-11**, outside the `pyaegean[all]` pin set, so `.venv/bin/python -m pytest tests/ -q` runs the test suite (105 tests at 2026-09-11) as the docstrings say. It is not a dependency of any source module. A rebuilt venv needs `pip install pytest` again.
- **Folder renamed 2026-09-10**: `linear-b` → `linear-a-b`, done together with the Claude Code session-history folder and the 197 `cwd` fields inside its transcript, so the session survived the move. Message content was left byte-for-byte intact, so earlier transcript text still says `linear-b` — that is the honest record, not a missed rename. The venv was relocated in place rather than rebuilt; see the Environment note in [CLAUDE.md](../../CLAUDE.md).
- `.backups/` created 2026-09-10 when `corpus-sources.md` was restructured during the state-of-the-art survey. Convention: `.backups/<date>-<file>.<why>`, a verbatim copy of the file as it was before the change. It was the only undo before git; superseded by commit history, kept for the pre-git snapshot.
- **Reference cache: `~/.cache/linear-a-b/reference/`, outside the repo and not created automatically.** Holds the third-party lexicons and the corpus derivatives that the licensing invariants keep out of git: Strong's Hebrew for `src/semitic_null/`; the ORACC, Copenhagen Ugaritic, kaikki and FrequencyWords lists for `src/hypotheses/`; per-spike caches. `scripts/fetch_reference.py` fetches the open ones and `REPRODUCING.md` lists what goes there. A clean clone has none of it and the tests need none of it. Measurements are cited from the scripts, never from anything cached.

---

## Usage and attribution

HENGE was developed by Ru Howe as a working discipline for collaborating with AI assistants on production projects for Stornaway.io. It gives you a human-readable reference and a compact, high-signal map that makes AI agents more efficient.

The HENGE files in this repository are published under CC BY-SA 4.0 (see `LICENSE.md`), which supersedes an earlier note here asking that they not be republished. If you adapt the pattern for your own workflow, keep the name, add your own branches or versions, and credit the original. If you find improvements, send them over.

Contact: ru@stornaway.io
