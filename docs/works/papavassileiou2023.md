---
key: papavassileiou2023
authors: [Papavassileiou, Kosmopoulos, Owens]
year: 2023
title: A Generative Model for the Mycenaean Linear B Script
venue: ACM JOCCH
ref: 10.1145/3593431
scripts: [B]
domains: [computational]
standing: contested
verified: Y
verified_on: 2026-09-11
access: paywalled
tested_by: [linearb-restoration]
---

# Papavassileiou, Kosmopoulos, Owens (2023), *A Generative Model for the Mycenaean Linear B Script*

ACM JOCCH.

## What it claims

BiRNN infilling, KN series D. 513 real sequences augmented to 2,565 (725 augmented + 1,327 duplicates). top-1 ≈48%, top-20 ≈78–80%.

## Where to find it

- DOI [10.1145/3593431](https://doi.org/10.1145/3593431)
- Access: **paywalled**

## Our assessment

Verification **Y**. We fetched and read the primary source.

Numbers restated from the 2024 follow-up; ACM full text 403. Zenodo 7404653 releases the series D data CC BY 4.0.

Put under test here in [linearb-restoration](../ai_context/linearb-restoration.md).

Added 2026-09-11 (prior-art search): the paper's Table 2, read from the authors' own open mirror, reports their own n-gram baselines on series D. Bidirectional 3-gram reaches 44.64% top-1 against the BRNN's 48.34%. Bidirectional 2-gram reaches 31.58% top-1 and 75.24% top-20, against the BRNN's 78.17% top-20. No seen/unseen word split is reported.

## Discussion

Corrections and disagreement are welcome. Open a pull request against this file, or email ru@stornaway.io naming the file. If you are the author of this work and we have misrepresented it, say so and we will fix it.
