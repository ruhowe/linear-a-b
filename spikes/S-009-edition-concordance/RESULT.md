# S-009 result: the concordance, and where the two editions actually disagree

Ran 2026-09-12. Code: `run.py`. Raw numbers: `results.json` (aggregate only, per
`spikes/README.md` rule 6: per-document rows carry ids, site, support, token counts
and disagreement kind, never a reading; the sign-label table carries labels and
counts, never words).

**Alignment reused, not invented.** Normalising both editions' document ids by
stripping whitespace and upper-casing (`corpus-sources.md` Gotchas) gives 697 aligned
documents, exactly the count that entry records. The same comparison also reproduces
F-023's "96 agree word for word" exactly, and its "508 differ" as a total, even though
the three-way split below (43 / 44 / 421) differs from F-023's own uncommitted
breakdown (13 / 137 / 365): F-023's script no longer exists to compare against, and
this one classifies from the flat sign stream across a whole document rather than
word by word, which draws the divider/reading boundary differently. Both totals
agreeing is the evidence that the alignment itself, not just its headline count,
matches.

## Headline numbers

604 of 697 aligned documents have a word token in at least one edition (93 have none
in either and are excluded from every rate below). Of those 604: 96 identical, 508
differ, split as:

| kind | count | share of 604 |
|---|---:|---:|
| identical | 96 | 15.9% |
| divider placement only | 43 | 7.1% |
| sign readings differ | 44 | 7.3% |
| line coverage differs | 421 | 69.7% |

## The line-coverage bucket is mostly a tagging boundary, not missing text

GORILA and SigLA do not always agree on which class a commodity sign belongs to: on
the same tablet, GORILA reads `TE` as a LOGOGRAM and SigLA reads it as a WORD. Folding
LOGOGRAM tokens into the comparison stream for every document classified as
`line_coverage_differs` under WORD tokens alone reclassifies 339 of 421 (80.5%): 200
become identical or divider-only, 139 become ordinary sign-reading disagreements, and
only 82 remain a genuine coverage gap once logograms are counted. Four in five of the
apparent "different line coverage" documents are the WORD/LOGOGRAM line drawn in a
different place, not a word one edition has and the other lacks. Any statistic run on
GORILA and SigLA WORD tokens separately is sensitive to this boundary before it is
sensitive to anything about the language.

## Disagreement is not diffuse across the sign inventory

44 documents disagree in sign readings alone; across them 51 distinct sign labels
appear on one side or the other of a substitution, 135 occurrences in total. Six
labels account for 53% of those occurrences, and asterisk-numbered (unidentified)
signs account for 44%:

| label | occurrences |
|---|---:|
| *56 | 14 |
| PA₃ | 13 |
| ZU | 12 |
| *79 | 12 |
| *21F | 10 |
| QI | 10 |

Reading differences concentrate on signs neither edition can name and on a handful of
named signs, not evenly across the ~340-label inventory.

## Disagreement rises with document length

| length band (max words, either edition) | n with text | disagreement rate |
|---|---:|---:|
| 1-2 | 390 | 78.0% |
| 3-5 | 117 | 94.0% |
| 6-10 | 75 | 96.0% |
| 11-20 | 22 | 100% |

Mechanical (a longer document gives more positions at which the editions can differ),
and worth stating anyway: any comparison restricted to longer Linear A documents is
running on the sub-population where edition disagreement is close to universal.

## By site and support

Disagreement rate is high everywhere with text (60% to 100% across sites with 10 or
more aligned documents; full table in `results.json`), so site alone does not sort
documents into agreeing and disagreeing groups the way the sign-label table does.
Two site/support figures are notable on their own terms, not as disagreement-rate
outliers:

- **Arkhalkhori / Arkhanes.** GORILA's ten `ARKH1a`–`ARKH7` documents are sited at
  Arkhalkhori; SigLA's ten `ARKH 1a`–`ARKH 7` (identical numbering, identical support,
  "Tablet") are sited at Arkhanes — two distinct real findspots, not a spelling
  variant. The other 21 of 31 site-metadata mismatches are spelling only (`Malia` /
  `Mallia`, 18; three single typos). This one is a genuine attribution conflict
  between the two editions' metadata and is reported as a fact, not adjudicated, per
  the brief.
- **Support-type granularity differs by convention.** 72 of 98 support mismatches are
  SigLA calling a document "Tablet" where GORILA gives a finer class (`Stone vessel`
  43, `Lames` 18, `3-sided bar` 5, `4-sided bar` 4, `Label` 2); the rest are vessel
  subtypes (`Pithos`, `Sherd`, `Lamp`) under GORILA's single `Clay vessel`. Any
  support-type analysis that mixes editions is comparing two different granularities,
  not two readings of the same classification.

## Documents in one edition only

GORILA holds 1,024 documents SigLA does not catalogue at all: 783 at Haghia Triada
(76%) and 747 tagged `Nodule` (73%) — GORILA's Haghia Triada nodule collection is far
larger than what SigLA has entered. SigLA holds 105 documents absent from GORILA's id
space: 45 at Haghia Triada, and by support mostly `Roundel` (41) and `Tablet` (29).
Full breakdown in `results.json`.

## Reading against the brief

**Interesting**, on the brief's own terms. Disagreement does not spread evenly across
sites, supports or the sign inventory: it concentrates in one structural boundary (the
WORD/LOGOGRAM line, 80% of the largest disagreement bucket), in a small set of sign
labels dominated by unidentified signs, and in one specific site-metadata conflict
worth checking by hand (Arkhalkhori/Arkhanes). None of this says which edition is
right anywhere, per the brief's own limit: it says where a structural test's edition
sensitivity lives, which is what the brief asked the concordance to show.

## What this tells the supplement work

The 2024 GORILA supplement (Del Freo & Zurbach, *Supplément 1*, Études Crétoises
21.6, print-only, 107 documents, finds 1985-2023; see `docs/works/gorila.md`) has no
site or support breakdown anywhere in this repo — it is not digitised, and F-035
already records that none of its texts have surfaced in SigLA, Younger's site or any
preprint. So this cannot say which sites the supplement adds documents at; that would
need the print volume itself. What it can say: if the supplement's finds skew toward
Haghia Triada, as most Linear A material historically does, they arrive at the site
already carrying most of GORILA's SigLA-uncatalogued documents (783 of 1,024) and most
of the WORD/LOGOGRAM tagging sensitivity measured above, since that sensitivity is a
property of how each loader chain tags commodity signs, not of any one site. The
concrete recommendation is procedural: when the supplement enters the `lineara` chain,
rerun this script before rerunning any Kober or toponym statistic on the enlarged
corpus, rather than assuming the new documents behave like the old ones.
