# linear-a-b

Statistical review of how the Aegean Bronze Age scripts are read, and of the claims made
about them. **Linear B** was deciphered in 1952 as an early form of Greek. **Linear A**
has resisted a century of attempts.

This project does not try to decipher Linear A. It checks whether the methods people use
on these scripts work, by running them against controls the field agrees are necessary
but which have not always been applied at scale. What it found is in
[docs/guides/what-we-found.md](docs/guides/what-we-found.md), in plain English, and
every number there traces to an entry in [FINDINGS.md](FINDINGS.md). The automation that Claude Code and
HENGE make possible allows large-scale verification of claims against established
controls. A mix of Claude models did the work, with Fable, the newest at the time of
writing, on the most demanding analysis. Fable is what made me think the work could reach
a quality worth sharing.

No background in linguistics is assumed anywhere in this repository. New here?
[START-HERE.md](START-HERE.md) is the plain-English way in. [REPRODUCING.md](REPRODUCING.md)
says what a clean download can rerun.

## Using this repository with Claude Code

The easiest way to use this repository is to open it in Visual Studio Code with the
Claude Code extension and ask: what was found, what a finding rests on, how to rerun a
test, how to add your own material. [START-HERE.md](START-HERE.md) walks through the
setup and gives prompts to copy. Claude reads [CLAUDE.md](CLAUDE.md) and the HENGE files
under [docs/ai_context/](docs/ai_context/) on its own, which is what makes the
repository navigable without knowing the code.

This is September 2026 advice. The tools move quickly: the extension, the models and
the way an assistant reads a repository will all have changed by the time you read
this. If it is later than that, ask whichever assistant you use how best to work with a
repository like this one using the toolkit of the day. What it needs to read is the
same: CLAUDE.md first, then docs/ai_context/HENGE.md.

## Before you read this

I am not an academic. I am an old classicist with a long interest in the subject who, in
2026, is good at running Claude Code. The work here was done with Claude Code under my
direction, using HENGE, a notation, memory and context system I designed for working with
AI assistants on long projects. I am publishing it because it might save someone else
time.

Throughout, "I" is me: what I chose to test, what I read, and what I accepted. "Claude
Code" is the tool, and "it" refers to it: it built the instruments, ran the counts,
searched the literature and drafted the notes and the summaries. The judgements in the
findings and guides were drafted by Claude Code and are ones I accepted, not ones I formed
independently. Where I directed a change, the entry says so.

I run a business full time. I am not intending to submit this anywhere, present it, or take
part in arguments that tend to form around this kind of thing. Corrections I am glad to
have. Bad faith assumptions and insults I am not interested in. I have seen others who have
tried to contribute to the field using AI insulted as cranks and dismissed. That kind of 
behaviour has a chilling effect on innovation and contribution and I'm not interested, 
so I'm staying away from engaging in a formal submission process. If you find this
repository via search, please read it with that context in mind and be kind.

Almost everything here was produced with heavy automation: the counting, the searching,
the note-keeping and much of the drafting. **There is a real chance that some references
or sources are wrong, misquoted, or do not exist at all.** I have checked what I could in
the time I had, and the verification flag on each page in [docs/works/](docs/works/) says
what was checked and how. It has not been reviewed by any specialists, and I have not
requested a review. Read it on that basis.

I have not knowingly included anything that breaches a licence or a copyright, and I have
not knowingly misattributed anyone's work. No corpus data is redistributed here, only
aggregate numbers. If you find something wrong on either count, please assume I made a
mistake rather than that I acted in bad faith, and tell me so I can fix it:
ru@stornaway.io.

On naming. Where this work builds on earlier scholarship, that scholarship is credited by
name, because that is what credit is for. Where it measures a currently active claim, the
claim is described by its measurements, and any judgement stays on the work rather than
the person. Every source is in [docs/works/](docs/works/).

## Where things are stated

This file describes the project. It states no results.

| Document | Holds |
|---|---|
| [FINDINGS.md](FINDINGS.md) | Every result and verdict, as dated entries tied to a protocol version. Superseded entries are kept and marked. The only place a number or a judgement is asserted. |
| [CHANGELOG.md](CHANGELOG.md) | Every version of every test protocol: what changed, why, and what was wrong with the version it replaced. |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Every assumption a result rests on, numbered, with where it enters, what it would change if wrong, and whether it has been tested. |
| [JOURNAL.md](JOURNAL.md) | The investigation as a dated narrative, one entry per phase: what was done, what it found, and why the next phase followed. The reading order for how the project got here. |
| [docs/ai_context/](docs/ai_context/) | Protocols, data contracts, licences and gotchas, written tersely for AI agents. Describes instruments; points to FINDINGS for what they produced. |
| [docs/works/](docs/works/) | One page per published source, analysis or decipherment attempt, with a verification flag and an assessment. |
| [docs/guides/](docs/guides/) | Plain-English explanations of the material. |
| [docs/reports/](docs/reports/) | Dated write-ups for a specialist reader, quoting FINDINGS only. The first, 2026-09-11, covers both methods and the three rules; the second, 2026-09-12, re-reads the assumptions and methods against the primary sources and lists what was missed by following precedent. |

## Why I thought this was worth doing

Both corpora are tiny. Linear B is about 54,000 words across 5,932 documents. Linear A is
about 6,400 words, roughly a long magazine article, spread over 1,534 broken tablets and
stone vessels that mostly list sheep and offerings. Corpus size is the fact that decides
what is possible here.

Three lines of work exist. One rebuilds a published Linear B text-restoration
benchmark from the source database and reports it against the floors and splits the
publication did not. The other tests whether the etymological method, matching Linear A
words to a candidate language's dictionary, which is the method behind most proposed
decipherments, can tell languages apart at all. The third, the Kober method, looks for
grammatical structure in sign patterns before any sound value is assigned, with Linear B
as the positive control and a measured corpus-size floor. A fourth, value transfer,
tests the convention that Linear A signs carry Linear B sound values, through place
names under a permutation null. The names are fixed in
[docs/ai_context/terminology.md](docs/ai_context/terminology.md). What each found is in
[FINDINGS.md](FINDINGS.md).

## Scope and coverage

This is not a comprehensive catalogue of Aegean-script scholarship, and it does not claim
to be. It is a targeted one. The catalogue holds the works that bear on the two methods
tested here, the published decipherment claims those methods can be pointed at, the
computational literature on both scripts, and the editions and data sources everything
rests on. At 2026-09-12: 79 works, of which 48 are verified from a primary text, 21 are
recorded from a reliable pointer but unread, and 10 rest on a search snippet; 41 concern
Linear A, 26 Linear B, the rest analogues from other scripts and from computational
linguistics. The verification flag on every page says which.

What it covers in depth: the etymological method from 1974 to 2026; Alice Kober's method
from her own papers to its computational relatives; Linear B restoration and its
baselines; the corpus editions and their transcription chains. 

What it covers thinly or not at all: Linear A palaeography and archaeology, Cretan
Hieroglyphic and Cypro-Minoan except as analogues, and the philological literature on
Linear A morphology beyond the works the claims register needed. A comprehensive
bibliography of Linear A research would run to several hundred items; Younger's online
bibliography and Davis 2026 are the seeds if that is ever built, and it is listed as a
parked item.

## Why both scripts share one repository

Linear B is the control. That is the whole reason the two scripts are kept together rather
than in separate projects.

Any test aimed at Linear A has the same problem: there is no answer key, so a result that
looks impressive cannot be checked. Linear B fixes that. It is the same family of script,
carrying the same kind of palace accounting, and it was deciphered in 1952, so the answer
is known. A test can be run there first.

The rule that follows is simple. If a method cannot detect that Linear B is Greek, it has
no business being pointed at Linear A. A test that finds structure everywhere, including
in a corpus where we know what the structure is, has told us nothing.

The relationship between the two scripts is also the open research question in its own
right, since Linear B was adapted from Linear A and they share many signs. Splitting them
would put the interesting part across a boundary. But the practical reason is the control.

## Guides

Start here if you are new to the material.

| Guide | What it covers |
|---|---|
| [The two scripts](docs/guides/the-two-scripts.md) | What Linear A and Linear B are, who wrote them and what the tablets say |
| [Why Linear A is hard](docs/guides/why-linear-a-is-hard.md) | The circularity trap, the corpus size problem, and why confident readings keep appearing |
| [How a claim is tested here](docs/guides/how-we-test-a-claim.md) | Null models, controls and what a result has to beat, in plain English |
| [Reading a work page](docs/guides/reading-a-work-page.md) | How the catalogue is structured and what the verification flags mean |
| [What this project found](docs/guides/what-we-found.md) | The results so far, what was known before each, and why each matters, in plain English |

## The catalogue

Every source, analysis and decipherment attempt looked at has its own page under
[docs/works/](docs/works/), with links to the original material and an assessment of it.
Each page can be commented on, corrected by pull request, or linked from an issue.

```bash
.venv/bin/python scripts/findings.py --status current     # what stands
.venv/bin/python scripts/findings.py --assumption A-001   # what rests on an assumption
.venv/bin/python scripts/bib.py --stats
.venv/bin/python scripts/bib.py --script A --domain computational
.venv/bin/python scripts/bib.py --verified P          # what still needs checking
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to correct a page or add one.

## Layout

| Path | Contents |
|---|---|
| `START-HERE.md` | How to use the repository, with Claude Code or without, and how to send corrections |
| `REPRODUCING.md` | What a clean download can rerun, by protocol, and what each needs |
| `requirements.txt` | The pinned packages every finding was produced with |
| `FINDINGS.md` | Results and verdicts, dated and versioned |
| `CHANGELOG.md` | Protocol versions |
| `ASSUMPTIONS.md` | The assumptions register |
| `TODO.md` | The ordered work list, with the model each item runs on |
| `JOURNAL.md` | Phase-by-phase narrative of the investigation |
| `docs/works/` | One page per source, analysis or decipherment attempt |
| `docs/guides/` | Plain-English explanations |
| `docs/reports/` | Dated specialist write-ups |
| `spikes/` | Experiments outside the main line, under their own rules; never the basis of a claim |
| `docs/ai_context/` | Protocols and contracts, written for AI agents |
| `src/linearb_restore/` | Linear B text restoration and its baselines |
| `src/semitic_null/` | Etymological method, first instrument (protocol versions 0.1 to 0.2) |
| `src/hypotheses/` | Etymological method: candidate languages as data; lexicon loaders; phonology maps |
| `scripts/` | The frozen protocols, the findings query tool and the catalogue query tool |
| `results/` | Aggregate numbers only, each stamped with its protocol version |
| `tests/` | Checks pinning the pipeline to published corpus sizes |

Nothing derived from the corpora is stored here. The source databases are licensed for
non-commercial use, so anything built from them lives outside the repository in
`~/.cache/linear-a-b/`. See [data/README.md](data/README.md).

## Licence and attribution

Code is MIT; everything else, findings, documents, the HENGE files and the results, is
CC BY-SA 4.0: reuse it anywhere with credit and keep adaptations under the same terms. The split by
path, and the citations for DĀMOS, GORILA and SigLA, are in [LICENSE.md](LICENSE.md).
The corpora themselves are not included.

## Status

Public repository, one author, not peer reviewed, not submitted anywhere. No
correspondence has been sent to any researcher whose work is discussed, and none is
planned for now. Corrections: a pull request, or ru@stornaway.io. The published branch is
a snapshot of the working repository; protocol versions are pinned in CHANGELOG.md and
in every results file.

## Credits

Linear B corpus: DĀMOS (Aurora 2015), CC BY-NC-SA 4.0. Linear A: GORILA (Godart and
Olivier 1976 to 1985) through the pyaegean transcription chain, with SigLA (Salgarella and
Castellan) for palaeography. Greek: Perseus canonical texts and LSJ, CC BY-SA. Hebrew:
Strong's (1894), public domain. Unrelated-language word lists: FrequencyWords
(OpenSubtitles-derived). Ugaritic: Copenhagen Ugaritic Corpus, CC BY-NC. Akkadian: ORACC,
CC BY-SA 3.0. Toolkit: pyaegean by Ryan Pavlicek, Apache-2.0.
