# Value transfer — testing the convention that Linear A signs carry Linear B values

Read this before touching `scripts/toponym_test.py` or citing A-001 as tested. This file
describes the instrument; results are in FINDINGS (F-041, current, which supersedes
the spike's F-038); the protocol is CHANGELOG, "Value transfer (A-001)".

## The question and why it has a mechanism

Every phonetic reading of Linear A uses Linear B sound values by convention (A-001). The
field's positive evidence for that convention is not internal alternation (weak in
Packard's hands and ours, F-019) but place names: Cretan towns named on Knossos tablets
recur, under the transferred values, on Linear A tablets, Phaistos above all. Place
names persist across a change of language; that is the one lexicon with a mechanism.
Packard 1974 tested it (Table 14: 13 matches against 3 by chance) with nine hand-built
random decipherments. Spike S-003b redid it with 200 draws and both editions.

## The instrument

- **Assignment.** A map from each Linear A sign label to a Linear B label. Real: identity
  (the convention). Null: labels permuted within frequency bands at every position of
  every word (Packard's construction), groups of ten and four bands, seeded.
- **Match.** Packard's "3=": first two assigned labels equal the toponym's, third shares a
  consonant (`values.consonant_of`). "4=": four equal, or three equal plus a shared
  consonant. Literal identity: stricter than Packard's hand-admitted parallels (A-135).
- **Lexicons.** Knossos toponyms (32, verified in DĀMOS, cited per entry; A-133). Wrong
  controls, same script and size: Knossos personal names; Pylos toponyms, mainland places
  a Cretan archive should not name (A-134); the Knossos toponyms reversed.
- **Corpora.** GORILA and SigLA, word types of three or more certain signs.
- **Criterion (1.0).** Toponyms above the null's 99th percentile in the 3= class on both
  editions, both bandings, both seeds; every wrong control below it everywhere.

## What passing does and does not mean

The 1.0 run passed (F-041): the criterion was met in every cell, and three cautions
travel with the result, quoted there: five Linear A words and three long-read place
names carry it; the Pylos control is high without clearing; the SigLA 4= count is one.

Passing supports the transferred values for the signs that occur in the matched place
names, and nothing beyond them: a handful of signs, all long read in both scripts. It
does not bear on the other seventy-odd signs, on the language, or on any word that is
not a place name. A-001 has moved from "stated limit" to "tested positive for the signs
in the matched toponyms", with the sign list attached; every one of those signs is in
Meißner and Steele's demonstrably shared set, so the convention's secure core is
confirmed and its assumed remainder is untouched.

## The null that was wrong first

S-003 fixed label identity at the first two positions and let only the third vary;
since identity is the transfer under test, the null was handed most of the real count
and the result read "nothing". The rule that came out of it is in result-discipline: a
null varies the thing under test and nothing else.
