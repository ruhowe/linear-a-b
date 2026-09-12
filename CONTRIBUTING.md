# Contributing

**This repository has one author.** What follows describes how corrections work, and it
shapes how pages are written:
each work gets its own file so that disagreement has somewhere specific to land. Treat it
as the intended structure rather than an open invitation.

Corrections are more useful here than additions. If a page misrepresents your work or
anyone else's, saying so is the most valuable thing you can do.

## Correcting or discussing a work

Every source has its own page under [docs/works/](docs/works/). Two routes.

**A pull request.** Edit the page directly. Review comments attach to the exact lines you
changed, which makes disagreement precise. This is the best route for anything
substantive.

**An email** to ru@stornaway.io naming the file, the line and what is wrong.

I read what comes in when I can, and I may not reply. I do not take part in arguments
about this material, in issues, threads or anywhere else. If something here is wrong,
assume a mistake rather than intent, say so plainly, and I will fix it. If you are the
author of a work described here and it is misrepresented, say so; one work has already
been reclassified after the paper was read instead of the press coverage, and that
correction is recorded on its page with the date rather than quietly applied.

GitHub Discussions are open for readers to talk among themselves. I will not be taking
part there, and a correction posted there may not reach me; use the two routes above.

Questions about what was done are usually best put to Claude Code with the repository
open; see [START-HERE.md](START-HERE.md).

## Adding a work

Create `docs/works/<key>.md`. The key is author plus year, lowercase, no punctuation, for
example `salgarella2020`. Copy the frontmatter shape from an existing page.

Required frontmatter: `key`, `authors`, `year`, `title`, `venue`, `scripts`, `domains`,
`verified`, `access`. Add `ref` if a DOI or stable URL exists.

Two rules about the `verified` flag, because it is the field most easily corrupted.

It records **your** diligence, not the work's quality. Mark it `Y` only if you fetched and
read the primary source yourself. If you are working from an abstract, a review or a
citation in another paper, mark it `P`. If you have only seen a search result, mark it `S`.

Never promote a flag without re-fetching. A page moving from `P` to `Y` should be a commit
that says what was read.

Then check it parses:

```bash
.venv/bin/python scripts/bib.py --stats
```

## Adding a language hypothesis

Candidate languages live in [src/hypotheses/registry.yaml](src/hypotheses/registry.yaml).
Adding one means adding a record and a lexicon loader. The test harness does not change.

A hypothesis needs an independent lexicon, meaning one assembled for some purpose other
than supporting this hypothesis. A dictionary built to fit the proposal cannot test it.
Several entries in the registry are currently marked `blocked` for exactly this reason,
with the missing resource named.

Fringe proposals are welcome in the registry. A harness that can only be pointed at claims
we already respect is rhetoric rather than an instrument.

## Assumptions

Anything a result takes as given goes in `ASSUMPTIONS.md` when it is introduced, not when
someone questions it. A new lexicon needs its representativeness and folding assumptions
entered; a new map needs its phoneme-set assumptions entered.

## Changing a protocol

In the working repository each finding's commit is tagged with its number; the published
snapshot carries the same pins through each results file's `protocol_version`, CHANGELOG
and the regression tests, so the code behind any entry can still be identified. Instrument code that produced
a finding is pinned by a regression test (for the Kober method,
`tests/test_kober_regression.py`); a change that moves those pins is a new protocol
version, needs a CHANGELOG entry, and the affected findings are rerun under it with a
dated note rather than edited. A change is merged only when it is comparable and
rollable back.


Any change that could move a result gets a new version number in the script's
`PROTOCOL_VERSION` and an entry in [CHANGELOG.md](CHANGELOG.md) in the same change:
the statistic, the null, expansion rules, sampling, lexicon set, permutation count.
Results are quoted with their version. A superseded version stays in the log with what was
wrong about it.

## Where results go

Results and verdicts go in `FINDINGS.md` only, as a dated entry naming the protocol
version. The README and the files under `docs/ai_context/` describe the project and its
instruments; they quote FINDINGS and do not assert numbers or judgements of their own. A
pull request that adds a result anywhere else will be asked to move it.

## Claims about results

Any number quoted from our own work must carry the null it was scored against. A match
rate without the rate a scrambled control achieves is not a result here, and pull requests
adding one will be asked to add the other.

Any number quoted from someone else's work must carry the differences in method alongside
it, in the same sentence rather than a footnote. See the comparison-framing section of
[the restoration write-up](docs/ai_context/linearb-restoration.md) for the worked example.

## Writing

[docs/ai_context/writing-style.md](docs/ai_context/writing-style.md) applies to prose in
this repository. The rules that matter most here: put the answer in the first sentence, use
full sentences, no em dashes, and say "I have not checked" in those words rather than
implying a confidence you do not have.

## Data

Do not commit corpus content. The Linear B database is licensed for non-commercial use
with share-alike terms, and the Linear A transcription chain has an unresolved licence.
Anything derived from either belongs in `~/.cache/linear-a-b/`, outside the repository.
Aggregate counts and metrics are fine to commit. Token lists and reconstructed text are
not. See [data/README.md](data/README.md).
