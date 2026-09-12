# S-006 result · Read the Linear A list anyway

Run: `.venv/bin/python spikes/S-006-read-the-list/run.py` (2026-09-12). Source file:
`results/kober-09/kober-lineara-seed0.json` (Kober 0.9, unmerged, `lineara`, seed 0,
stem_min 2 — the file F-040 reports). The script recomputes the full ranked alternation
list from the same corpus and settings by importing `kober.words`/`kober.paradigms`
(never editing `src/`); its own top twenty reproduces the stored file exactly (checked
at run time, printed as the first block of output). Field citations are in
`field-proposals.json`, sign labels only — this file carries no Linear A word.

Sources actually read this session, with what they yielded: Facchetti 1999b
(pp. 121–136, read in full); Thomas 2020 (full text); Duhoux 1978, Monti 2022, Davis 2013/2014 as already catalogued in `docs/works/`
(verification S or P — search-snippet or restated-elsewhere only, not re-verified here);
Schoep 2002 (not catalogued anywhere in the repo; `claims.md` lists it only as a lead on
Hagia Triada toponyms, not morphology); Younger's suffix list (could not be retrieved —
see below).

## Table 1 · ending-channel top twenty

| rank | pair | support | N2 percentile | field proposal |
|---:|---|---:|---|---|
| 1 | KU / MA | 2 | 91.0 (of the *maximum*, this pair) | — |
| 2 | RA / RA-ME | 2 | 91.0 (of the *maximum*, this pair) | — |
| 3 | \*118 / JA-KA | 1 | n/a | — |
| 4 | \*118 / KI-RA | 1 | n/a | — |
| 5 | \*118-KA / NI | 1 | n/a | — |
| 6 | \*21F-RI / RA | 1 | n/a | — |
| 7 | \*21F-RI / RO | 1 | n/a | — |
| 8 | \*301 / MA-TA | 1 | n/a | — |
| 9 | \*301 / MI-NE | 1 | n/a | — |
| 10 | \*321 / TU-KU | 1 | n/a | — |
| 11 | \*329 / NE-TE | 1 | n/a | — |
| 12 | \*350 / DE | 1 | n/a | — |
| 13 | \*350 / NA | 1 | n/a | — |
| 14 | \*350 / NA-JE | 1 | n/a | — |
| 15 | \*350 / NA-TE | 1 | n/a | — |
| 16 | \*350 / RE | 1 | n/a | — |
| 17 | \*802-ME / RA | 1 | n/a | — |
| 18 | \*802-ME / RA-ME | 1 | n/a | — |
| 19 | A / DA | 1 | n/a | — |
| 20 | A / KA | 1 | n/a | — |

"N2 percentile" is the file's own `n2_alternation_support.max_support` block, which
grades only the single highest-support value (91.0th percentile, against F-033/F-040's
"maximum support 2 against a 99th percentile of 3"); no per-pair percentile exists for
the eighteen pairs at support 1, so those rows read "n/a" rather than a number, and
"n/a" is not "at the null" — it is "the file cannot say."

Zero of the twenty carries a field proposal. Two signs worth flagging without reading
them as matches: `*301` (rank 8–9) is exactly the sign Thomas 2020 identifies as the
libation formula's verbal root (`i-*301-`), and `*350`/`DE`/`NA` echo signs Thomas lists
among the root's own affixes — but here they occur as a word-*final* ending on an
unrelated stem, never in the root's actual word-medial position, so this is the same
sign playing an unrelated structural role, not corroboration of anything Thomas argued.

## Table 2 · prefix-channel top twenty

| rank | pair | support | N2 percentile | field proposal |
|---:|---|---:|---|---|
| 1 | A / JA | 3 | 99.5 (of the *maximum*, this pair) | **facchetti1999b**, p.132 n.73 — the ja-/a- alternation on (j)a-sa-sa-ra-me, "attested in a securely connected context"; **monti2022** — reads a-/ja- as an article-like prefix on the same word |
| 2 | A / DA | 2 | n/a | — |
| 3 | A / SI | 2 | n/a | — |
| 4 | A-SA / JA-SA | 2 | n/a | **facchetti1999b**, p.132 n.73 — the same (j)a-sa-sa-ra-me word pair, read one sign further in (the two-sign prefix split of the same pair of word types) |
| 5 | KU / SA | 2 | n/a | — |
| 6 | \*118 / A-KU | 1 | n/a | — |
| 7 | \*118 / NE | 1 | n/a | — |
| 8 | \*164 / DA | 1 | n/a | — |
| 9 | \*21F / QE | 1 | n/a | — |
| 10 | \*28B-NU / WA-TU | 1 | n/a | — |
| 11 | \*304+PA / KA | 1 | n/a | — |
| 12 | \*306 / RI | 1 | n/a | — |
| 13 | \*309 / \*309B | 1 | n/a | — |
| 14 | \*324 / ZU | 1 | n/a | — |
| 15 | \*333 / JA | 1 | n/a | — |
| 16 | \*415-VS / QE | 1 | n/a | — |
| 17 | \*47 / DA | 1 | n/a | — |
| 18 | \*47-NU / KI-KI | 1 | n/a | — |
| 19 | A / A-DU | 1 | n/a | — |
| 20 | A / A-RU | 1 | n/a | — |

Rank 1 (support 3, 99.5th percentile of its own null — the highest percentile anywhere
in either channel, though still short of the pre-registered 99th-percentile bar by
construction of a two-sided read) is the field's single most-cited Linear A
morphological alternation. Rank 4 is very likely the *same* pair of word types read at
the other split point stage 1 always tries (`kober-method.md`: "every word of length n
contributes candidate splits at n−1 and n−2"): for a-sa-sa-ra-me / ja-sa-sa-ra-me, the
n−1 split gives prefix A/JA over base SA-SA-RA-ME, and the n−2 split gives prefix
A-SA/JA-SA over base SA-RA-ME. This is an inference from public knowledge of the word
pair (already stated in `facchetti1999b.md` and cited by F-019), not a corpus lookup: it
is offered as "very likely," not certain, since support 3 and 2 could each partly come
from other stems. Neither the `A/DA` (rank 2), `A/SI` (rank 3) nor `KU/SA` (rank 5)
pairs match anything in the four sources read.

## Table 3 · field's best-known proposals, in or out of the top twenty

| proposal | source | pair | in top twenty? | where it ranks |
|---|---|---|---|---|
| a-/ja- prefix (1-sign split) | facchetti1999b, monti2022 | A/JA (prefix) | **yes, rank 1** | support 3, of 143 prefix alternations |
| a-/ja- prefix (2-sign split) | facchetti1999b | A-SA/JA-SA (prefix) | **yes, rank 4** | support 2, of 143 |
| -ja/-e suffix | facchetti1999b, §3.2.1 | JA/E (ending) | no | rank 54 of 209, support 1 — tied with 205 other pairs at the floor |
| -si/-ti suffix | facchetti1999b, §3.2.1 | SI/TI (ending) | no | rank 195 of 209, support 1 |
| -te/-ti suffix ("from/of") | thomas2020, p.5 | TE/TI (ending) | no | rank 203 of 209, support 1 |
| -wa-/-u- suffix | thomas2020, p.4 n.5 | WA/U (ending) | no | **not attested anywhere**, support 0 |
| general prefixing/suffixing | duhoux1978 | (no specific pair; S-verified snippet only) | n/a | not checked |
| Hagia Triada toponyms | schoep2002 | (not catalogued; not a morphology claim) | n/a | not checked |
| VSO word order; vowel frequencies | davis2013, davis2014 | (no specific ending/prefix pair) | n/a | not checked |
| suffix list | younger_texts | (site decommissioned; no mirror found) | n/a | **could not be retrieved this session** |

Reading each row against the corpus, not just against rank:

- **-ja/-e is attested but at the floor.** The pair the field reads on
  `a-ta-i-*301-wa-ja` / `a-ta-i-*301-wa-e` is a real, if single-instance, same-stem
  alternation somewhere in the 988 word types — support 1, indistinguishable from the
  207-of-209 pairs the corpus produces by chance pairing at this size (F-033's "pool of
  207").
- **-si/-ti and -te/-ti are also attested, equally uninformative.** Both sit deep in the
  same support-1 pool; their numeric rank (195, 203) is an artefact of the lexicographic
  tie-break among equals, not a distance from the top.
- **-wa-/-u- is not attested as a same-stem pair at all.** Thomas's own illustrating
  example, qe-ra2-u / qa-ra2-wa, differs at *both* ends (qe-/qa- and -u/-wa
  simultaneously), so it would not satisfy the instrument's single-position-difference
  definition even in principle; the phenomenon is cited as occurring "elsewhere" in the
  corpus, but no stem anywhere in the 988 word types supports a clean WA/U ending
  alternation.
- **Duhoux, Schoep and Davis give nothing to search for** at the level this instrument
  reads (specific sign-label pairs): Duhoux's claim is general and unread beyond a
  snippet, Schoep's known subject is toponymy rather than morphology, and Davis's two
  catalogued claims are syntactic (word order) and phonological (vowel counts), not
  affixal.
- **Younger's suffix list is a genuine gap, not a zero.** `younger_texts.md` already
  records the host as decommissioned in 2024; the live `lineara.xyz` mirror (checked by
  WebFetch this session) is Robert Hogan's Linear A Explorer, a browsing tool with no
  morphology or suffix page, and `web.archive.org` is unreachable from this environment.
  This row is honestly "not checked," not "checked and absent."

## Reading against the brief's criterion

Pre-registered bar: **interesting** if more than half of the top ten are proposals the
field has already made by eye; **nothing** if fewer than half, or if the field's
proposals sit below the top twenty (a result worth its own line either way).

- Ending channel, top ten: **0 of 10** match anything in the five named sources.
- Prefix channel, top ten: **2 of 10** match — both readings of the single a-/ja- pair
  on (j)a-sa-sa-ra-me, at the instrument's two split depths.
- Combined (twenty pairs considered, ten per channel): 2 of 20, well under half.

By the letter of the pre-registered bar this is **done: nothing**. The one line worth
keeping past that verdict: the single highest-supported, highest-percentile prefix
alternation the instrument found on the whole Linear A corpus is the same pair the field
has been citing since at least Facchetti 1999 as its most secure piece of Linear A
morphology. F-019 and `facchetti1999b.md` already say this in words; this spike is the
first place it is checked against the machine's own top of the list, twice over
(support 3 and support 4-ranked support 2), rather than asserted. Support 3 against a
null still centred near 2 (F-033/F-040) means the machine and the eye are looking at the
same three-or-so recurrences in a 988-word-type corpus, not that either has found
grammar — exactly the brief's own caution ("supports at the null are at the null
whoever else has noticed the pair").

**Must not be read as**, restated: none of this is evidence for any proposal. The
percentile columns say how far above chance the corpus supports each pair; not proposed
alternation exceeds its channel's null, on the instrument's own numbers (F-019, F-033,
F-040).
