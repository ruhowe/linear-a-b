---
key: papavassileiou2024
authors: [Papavassileiou, Kosmopoulos]
year: 2024
title: Restoring Mycenaean Linear B 'A&B' series tablets
venue: ML4AL@ACL
ref: 10.18653/v1/2024.ml4al-1.13
scripts: [B]
domains: [computational]
standing: contested
verified: Y
verified_on: 2026-09-10
access: open
tested_by: [linearb-restoration]
---

# Papavassileiou, Kosmopoulos (2024), *Restoring Mycenaean Linear B 'A&B' series tablets*

ML4AL@ACL.

## What it claims

BiRNN infilling KN A&B; 426 complete sequences, 75 syllables. top-1 30.3%, top-20 66.2%. D→A&B transfer no better than training from scratch.

## Where to find it

- DOI [10.18653/v1/2024.ml4al-1.13](https://doi.org/10.18653/v1/2024.ml4al-1.13)
- Access: **open**

## Our assessment

Verification **Y**. We fetched and read the primary source.

The fully-verified comparison target. Our measurement: a 15-line lexicon lookup reaches 31.5% top-1, a backoff blend 34.8%/74.9%, and a frequency floor alone gives 58.4% top-20. No code released.

Put under test here in [linearb-restoration](../ai_context/linearb-restoration.md).

## Discussion

Corrections and disagreement are welcome. Open a pull request against this file, or email ru@stornaway.io naming the file. If you are the author of this work and we have misrepresented it, say so and we will fix it.
