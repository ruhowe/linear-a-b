---
key: fetaya2020
authors: [Fetaya, Lifshitz, Aaron, Gordin]
year: 2020
title: Restoration of fragmentary Babylonian texts using recurrent neural networks
venue: "PNAS 117(37):22743–22751"
ref: 10.1073/pnas.2003794117
scripts: [other]
domains: [computational]
standing: accepted
verified: Y
verified_on: 2026-09-13
access: open
tested_by: []
---

# Fetaya, Lifshitz, Aaron, Gordin (2020), *Restoration of fragmentary Babylonian texts using recurrent neural networks*

PNAS 117(37):22743-22751.

## What it claims

RNN restoration of Akkadian, compared against a simple 2-gram baseline.

## Where to find it

- DOI [10.1073/pnas.2003794117](https://doi.org/10.1073/pnas.2003794117)
- Access: **open**

## Our assessment

Verification **Y**. We fetched and read the primary source.

Reporting a non-neural baseline is standard in ancient-text restoration outside the Aegean.

Graded in the prior-art ledger of [claims.md](../ai_context/claims.md).

Checked 2026-09-13: read the full text at PubMed Central
(https://pmc.ncbi.nlm.nih.gov/articles/PMC7502733/), PMC7502733, open access. Title,
authors, journal, volume, issue and pages all confirmed against Crossref and the article
itself. The claim that the RNN restoration is compared against a simple 2-gram baseline is
confirmed: the paper reports LSTM test perplexity of 5.05 against 11.60 for the 2-gram
baseline, and 85.4% versus 74.8% top-1 token completion accuracy, stating "the RNN greatly
outperforms the n-gram baseline." Nothing on the page needed correction.

## Discussion

Corrections and disagreement are welcome. Open a pull request against this file, or raise an
issue linking to it. If you are the author of this work and we have misrepresented it, say so
and we will fix it.
