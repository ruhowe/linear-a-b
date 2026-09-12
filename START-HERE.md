# Start here

This repository tests whether the statistical methods people use on Linear A and Linear B
actually work, by running them against controls. It does not decipher anything. What it
found is in [docs/guides/what-we-found.md](docs/guides/what-we-found.md), in plain
English, and every number there traces to an entry in [FINDINGS.md](FINDINGS.md).

You do not need to be a programmer to use it. The easiest way in is to let Claude Code
read it for you.

The steps below are September 2026 advice. The tools move quickly, so ask whichever assistant
you use how best to work with a repository like this one with the toolkit of the day. 
What it needs to read has not changed: CLAUDE.md first, then docs/ai_context/HENGE.md.

## The easy route: Visual Studio Code with Claude Code

1. Install [Visual Studio Code](https://code.visualstudio.com/).
2. In VS Code, open the Extensions view (the four-squares icon), search for **Claude
   Code** (by Anthropic) and install it. Sign in when it asks; a Claude subscription or an
   API key works.
3. Get this repository onto your machine. On the GitHub page, **Code** then **Download
   ZIP**, unzip it, and in VS Code choose **File, Open Folder** on the unzipped folder.
   If you know git, cloning is fine too.
4. Open the Claude Code panel and type a prompt. Claude reads
   [CLAUDE.md](CLAUDE.md) on its own, so it already knows how the repository is laid
   out and what the rules are.

The first thing to ask it:

> Set up the Python environment for this repository following REPRODUCING.md, then run
> the tests and tell me what passed.

It will create the environment, install the pinned packages, fetch the corpora, run the
tests, and tell you if your machine is missing something (Python 3.14 is the one likely
gap; it will say how to get it). This takes a few minutes the first time.

## Prompts to try

Copy these in as they are, or change them.

**Finding your way around**

> Read START-HERE.md and docs/guides/what-we-found.md and tell me, in plain English, what
> this repository found and what it did not.

> Show me finding F-041, the assumptions it rests on, and the results file behind it.

> Explain the Kober method to me as if I know no linguistics, using the guides in
> docs/guides/.

> Which findings can I rerun on this machine right now, and which need downloads first?
> Use REPRODUCING.md.

**Checking the work**

> Rerun the value-transfer toponym test with the pre-registered settings and compare the
> numbers with F-041. Tell me what the null was and what the protocol version is.

> Pick one citation on docs/works/packard1974.md and tell me exactly what I would need to
> look up in the book to check it.

> Read docs/works/dimino2026.md and FINDINGS entry F-010. Is every number in the work
> page a quotation of the finding?

**Using your own material**

> I have a transliteration of a new Linear A inscription in this file. Show me how to add
> its word types with --extra-word-types and rerun the toponym test and the Kober run as
> a sensitivity, following the supplement-sensitivity protocol in CHANGELOG.md.

> Here is a new paper as a PDF. Catalogue it as a page under docs/works/ with the
> verification flag set honestly, then grade it against the claims register in
> docs/ai_context/claims.md.

> I want to test whether language X matches Linear A under the frozen protocol. What
> lexicon would I need, what does CONTRIBUTING.md say about independence, and what would
> the run look like?

**Keeping it honest**

> Before you report any number, tell me the null it was scored against and the protocol
> version it came from.

That last one is already a rule in this repository
([docs/ai_context/result-discipline.md](docs/ai_context/result-discipline.md)), and
Claude Code follows it here. Saying it out loud does no harm.

## What you can and cannot rerun

[REPRODUCING.md](REPRODUCING.md) has the full table. In short: the Kober method, the
place-name test and the Linear B restoration baselines run from a clean download once
the corpora have fetched themselves. The dictionary-matching findings need a few openly
licensed lexicons first, and `scripts/fetch_reference.py` gets them. Two findings on the
2024 GORILA supplement need a copy of that book and cannot be rerun from here; their
results files are included so the numbers can be inspected.

## Corrections, suggestions and questions

Corrections are the most useful thing you can send, and they are welcome. Two routes:

- A pull request against the page that is wrong. Every source has its own file under
  [docs/works/](docs/works/), so a disagreement has somewhere specific to land.
- An email to ru@stornaway.io saying which file, which line, and what is wrong.

I read what comes in when I can, and I may not reply. I do not take part in arguments
about this material, in issues, threads or anywhere else. If something here is wrong,
assume I made a mistake rather than that I meant it, tell me plainly, and I will fix it.
If you are the author of a work discussed here and it is misrepresented, say so; the
correction goes on the page, with the date.

GitHub Discussions are open if you want to talk about the material with other readers.
I will not be taking part, and a correction posted there may not reach me, so send
corrections by pull request or email.

Questions about what was done are usually best put to Claude Code with the repository
open. It can answer most of them from the files, faster than I can.

Please be kind. It costs nothing, and this was made to be useful to you.
