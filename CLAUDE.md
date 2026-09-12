# linear-a-b

Research repo: machine reading, analysis and decipherment work on the Aegean scripts — **Linear B** (deciphered, Mycenaean Greek) and **Linear A** (undeciphered, Minoan) — aimed at contributing to academic understanding of both.

Both scripts live here deliberately. They share a graphic inventory, one toolkit and one data model, and the relationship between them is the research question rather than a side note.

## HENGE knowledge folder

**Always start here.** Before exploring code, opening references, or answering a scoping
question, read `docs/ai_context/HENGE.md` and load any relevant file from its index. The
HENGE files capture cross-file contracts and decisions that aren't visible in any single
source file. Skipping them leads to confidently wrong answers about what already exists.

Re-read the relevant HENGE file at the point you start each task, not once per session.
Your own earlier summary of a file is not the file.

When a change alters behaviour documented in a HENGE file, update that file in the same
change. If you find yourself working out the same thing twice in one session, propose a
new HENGE file before the session ends.

## Visitors

If the person you are working with did not write this repository, they are a visitor:
possibly a specialist in the scripts, possibly not technical at all. Start from
`START-HERE.md` and `REPRODUCING.md`. Orient before running anything: what the project
found is in `docs/guides/what-we-found.md`, what each number rests on is in `FINDINGS.md`
(`scripts/findings.py --show F-nnn`). Set the environment up for them rather than
describing it: `requirements.txt`, then `scripts/fetch_reference.py` if they need the
etymological line. Before reporting any number, follow `docs/ai_context/result-discipline.md`:
name the null and the protocol version. When they want to add their own material, the
supplement-sensitivity protocol in CHANGELOG is the template. When they find an error or
disagree, route it as `START-HERE.md` says: a pull request against the page, or an email.
The author does not take part in discussion threads and may not reply; do not promise
otherwise.

## Repo status

This repo is **under git since 2026-09-10**. Committing publishes nothing; the published
branch is a snapshot. Commit per logical step; `.gitignore` already excludes `.venv/` and every
corpus-derived artifact, and it must stay that way (see the licensing invariants below).
Rule 5 still reads "update in the same change", meaning the same commit, since there is
no PR flow.

## Standing constraints

The corpus data is licensed, not open. Before writing anything that copies, commits or
publishes corpus content, read the Invariants section of
[docs/ai_context/corpus-sources.md](docs/ai_context/corpus-sources.md).

- DĀMOS (Linear B) is CC BY-NC-SA 4.0 — NonCommercial, ShareAlike, attribution required.
- Never commit fetched corpus data into this repo. pyaegean fetches it to `~/.cache/pyaegean/` deliberately.
- LiBER images are personal/non-profit use only under Greek heritage law.
- **Linear A transliterations are Linear B sound values applied by convention.** Treating
  them as evidence about the Minoan language is circular, and is the most common reason
  Linear A work gets dismissed.

## Scale constraint

Linear B is 54,476 tokens. Linear A is 6,406. These are the entire corpora. Method
selection should start from this fact, not arrive at it.

## Environment

- `.venv/` — Python 3.14.7, pyaegean 0.59.0 and pytest, pinned in `requirements.txt`
  (`.venv/bin/pip install -r requirements.txt`). `REPRODUCING.md` says what a clean clone
  can run; `scripts/fetch_reference.py` fetches the open lexicons the etymological line needs.
- `aegean.load("damos")` → Linear B, 5,932 docs. `aegean.load("lineara")` → Linear A (GORILA), 1,721 docs. `aegean.load("sigla")` → Linear A (SigLA), 802 docs.
- `.venv` hardcodes the absolute project path in 34 text files (`pyvenv.cfg` plus 33 `bin/`
  shims) and in ~10,000 `.pyc` caches. If the repo folder moves, rewriting the path in
  those 34 is sufficient — the `.pyc` paths only surface in tracebacks, and `bin/python`
  is a symlink to Homebrew, outside the repo. Prefer this to a rebuild: reinstalling from
  `pyaegean[all]` would re-resolve all 87 pinned versions.
