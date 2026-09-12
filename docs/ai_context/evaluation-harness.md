# Evaluation Harness — calibrating claims about the Aegean scripts

Files: `src/linearb_restore/` (instance 1: `split.py`, `rankers.py`, `evaluate.py`, `report.py`), `results/`. No `src/harness/` exists, and per the sequencing rule below it should not exist yet.

See also: [state-of-the-art.md](state-of-the-art.md) for every method cited here and its verification status; [linearb-restoration.md](linearb-restoration.md) for instance 1 in full; [corpus-sources.md](corpus-sources.md) for the licence boundary that makes this shape publishable.

Derived twice independently on 2026-09-10 — once from the restoration build (session `c01d379f`), once from an assessment of what this repo could contribute (session `105fe100`) — then reconciled. Rule 4 material: the shape is in no single source file.

## The shape

- **A registry of calibration studies, not a framework.** Each entry takes one published claim, rebuilds the floor nobody built, runs it under matched controls, and reports what survives.
- The scarce commodity in this field is a **calibrated result**, not a tool. Evidence: pyaegean ships 27 analysis modules, a TUI, an MCP server, a viz layer and a React web workbench, has a Zenodo DOI and a domain — and zero citations in the peer-reviewed literature this repo surveyed. Engineering completeness is not the binding constraint.
- Everything here consumes corpus data and emits only aggregate metrics, so it never touches the NC/SA redistribution wall that blocks the field's most-wanted deliverable (Braović 2024 §9's unified dataset with candidate-language lexica).
- Precedent, and near-proof of publishability: **SIGIL** (Raghavendra 2026, arXiv:2608.02999) is this exact thing for the Indus script — 54-method registry plus a synthetic non-language generator. Nothing equivalent exists for the Aegean scripts.

## Sequencing rule — read before writing any harness code

**Instances first. The registry falls out of them. Never the reverse.**

- Two worked examples plus a registry is a paper. A framework with no results is another uncited tool — see the pyaegean evidence above.
- Instance 1 was built as a restoration study and only afterwards recognised as instance 1. That is the correct order and it should stay that way.
- Generalise a component only when a second instance needs it. `split.py`'s grouped k-fold is the first thing that will earn promotion.

## Negative controls — what must FAIL

| Control | Source | Status |
|---|---|---|
| Random reassignment of sign values within frequency bands | Packard 1974 (9 "fictitious decipherments", Ventris values as control) — Linear A specifically, then dropped by the field for 50 years | pyaegean `null_models.py` has within-word permutation + length-stratified reshuffle + `monte_carlo_p`; **the frequency-band reassignment is absent** |
| Non-linguistic control corpora | Sproat 2014 (heraldry, deity symbols, weather icons, emoticons); SIGIL synthetic generator | **Absent everywhere.** The single highest-value missing component |
| Grouped held-out split | corpus-sources.md invariant; Raghavendra 2026 measured the cost of getting it wrong: 83/88/68% in-sample → 74/61/44% grouped | **Present, instance 1 only** (`split.py`: document-grouped k-fold, `leave_one_hand_out`) |
| Frequency / prior floor | this repo | **Present, instance 1 only** (`rankers.py` prior) — and it is what made instance 1 a result |
| Size-matched random lexicon | Raghavendra 2026 protocol; needed for instance 2 | Absent |

## Positive controls — what must PASS

A harness with only negative controls is a machine that says no to everything, which is indistinguishable from broken and will be read as debunking. Every negative needs a known-good case beside it.

| Control | What it proves | Status |
|---|---|---|
| Corazza et al. 2021 fraction values | The one peer-reviewed computational Linear A result. Value-free, arithmetic-constrained. If the harness rejects this, the harness is wrong | **Blocked** — see below. No implementation exists anywhere, pyaegean included |
| Procrustes self-alignment 90.1% | Instrument works when data is adequate; the 0.000 cross-script recovery is therefore a fact about corpus size, not about the code | Measured by pyaegean 2026-07-11, **not by us** — cite, never claim |
| Instance 1 lexicon on seen word types (89.3% top-1) | Pipeline can find a real signal, so the unseen-stratum collapse to 4.3% is not a pipeline defect | Present |
| Ferrara & Salgarella 2025 logograms (*157 = "root", KA+PO = "dry stalk") | What genuine value-free progress looks like | Reference only; not operationalised |
| Davis 2026's Linear B / Cypriot control on his own syllabotactic method | The field already accepts deciphered-script controls | Reference only |

## Instance registry

| # | Claim under test | Published target | Result | State |
|---|---|---|---|---|
| 1 | Linear B restoration by BiRNN (Papavassileiou et al., JOCCH 2023; ML4AL 2024) | top-1 30.3 / top-20 66.2 (A&B, verified from PDF) | 15-line lexicon lookup 31.5, backoff 34.8; their top-20 sits ~8 pts above a 58.4% floor; unseen-type stratum collapses 82.8 → 3.0 | **Done, tested, committed.** [linearb-restoration.md](linearb-restoration.md) |
| 2 | Di Mino 2026 "Tinitic" (Minoan = Central Semitic) | 42 sign readings, 508-entry lexicon, 443 translations | — | Planned. Two blockers below |
| 0 | Distribution-only cross-script sign alignment | — | top-1 0.000, top-5 0.094 vs chance 0.068, self-alignment 90.1% | Already measured **by pyaegean's maintainer**. Usable as a registry entry with credit; not this repo's result |

## Blockers, with the fix

| Blocker | Why it bites | Fix |
|---|---|---|
| **Corazza 2021 sign-by-sign fraction table paywalled** (ScienceDirect/unifi 403; on both the Could-not-verify and INVESTIGATE lists) | Load-bearing positive control. Without it the harness has no case it is obliged to pass | Email the authors. People send PDFs |
| **Di Mino released no code or data** | His matching procedure — sibilant merger, emphatic neutralisation, which Semitic lexica, what counts as a hit — exists only as prose. It must be reconstructed before it can be null-tested, and every reconstruction choice is where a critic attacks | Write to him. CC BY 4.0, self-published, contactable, and he has more to gain from co-designing the test than from silence. A null test he helped specify is unattackable on reconstruction grounds |
| No philologist | Semitic and Mycenaean morphological judgement is not substitutable by a model | **Not needed for instance 2 as designed** — the null test measures whether *randomly reassigned values* score as well under *his own* criteria. The judgement stays his; only the comparison is ours. Do not drift into judging his roots |

## Decisions

| Decision | Date | Reason | Rejected alternative |
|---|---|---|---|
| Registry of instances, not a framework | 2026-09-10 | pyaegean is the natural experiment for "will better tools help?" and returned negative | `src/harness/` with plugins and no results |
| Every negative control ships with a positive control | 2026-09-10 | A no-only instrument is indistinguishable from broken and reads as debunking | Nulls alone |
| Borrow authority; invent no method | 2026-09-10 | Every component already survived review (Packard, Sproat, Corazza, Raghavendra). An outsider refereeing Aegean scholarship with self-invented instruments is dismissible on sight | Novel statistics of our own |
| Contact the claimant before publishing any calibration | 2026-09-10 | Instance 1 → the Patras group; instance 2 → Di Mino. Framing is calibration, not debunking, and only they can answer some questions (exact candidate set; exact matching criteria). Matters more for an outsider than for a professor | Publishing first and corresponding after |
| Report every figure against its floor and stratified seen/unseen | 2026-09-10 | Instance 1's whole finding was invisible without both | Bare aggregate accuracy |
| Publish negative and null results as the primary output | 2026-09-10 | The field is short of exactly the output career incentives suppress; no department, no grant cycle, nobody to offend | Holding results back until something positive appears |
| Frame this repo's AI use as tool-assisted (query automation, null-model construction), never as "AI found/discovered X" | 2026-09-11 | A pre-publication HN thread on the Di Mino claim (news.ycombinator.com/item?id=48600107) surfaced a lose-lose reception pattern: crediting the AI with insight reads as erasing the human contribution, while any AI involvement invites dismissal as "just regurgitating training data." This repo's own AI-assisted analysis is equally exposed to that framing | Letting Claude's role go unstated, or describing any result here as "AI discovered" |

## Anti-patterns — how this turns into another ignored repo

- Building the framework before instance 2 exists.
- A web app, a corpus browser, or a general-purpose toolkit. Query is saturated four times over (workbench, TUI, Python API, MCP server) plus SigLA, LiBER, DĀMOS and lineara.xyz.
- Anything shaped like a decipherment. GitHub holds ~15 Linear A repos, mostly 2025–26 amateur decipherments; Zenodo 9 records, 8 self-published. Their mutual incompatibility is itself the evidence against the method class.
- Claiming pyaegean's measurements (instance 0) as this repo's own.
- Letting a calibration read as a takedown. Instance 1's required wording is in [linearb-restoration.md](linearb-restoration.md) and the rule generalises: *"the published numbers are reproduced by a simpler method, and both sit close to a floor"* — never *"we beat them."*

## Honest limit

None of this deciphers Linear A, and most of it will return "not distinguishable from noise." The contribution is converting a professional intuition into a measured, citable fact, and making negative results publishable in a field where success claims are abundant and free.
