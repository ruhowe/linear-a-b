---
key: barber1974
authors: [Barber]
year: 1974
title: "Archaeological Decipherment: A Handbook"
venue: Princeton University Press
ref: ISBN 978-0-691-03544-4
scripts: [A, B, other]
domains: [methodology, computational]
standing: accepted
verified: V
verified_on: 2026-09-12
access: in print only; read in full 2026-09-12
tested_by: [kober-method, hypothesis-harness]
aliases: [Barber, Archaeological Decipherment]
---

# Barber (1974), *Archaeological Decipherment: A Handbook*

Princeton University Press, 1974. Read in full, with every
number below checked against the page. Fifteen chapters: historical and theoretical
perspectives, then methodology (scripts, data design, "toys", boundaries, alternation and
cooccurrence, indexes, the strategy of making decisions, comparative evidence, wider
contexts, future research), a glossary and an index.

## What it says that bears on this project

**How much text is needed (pp. 4–5, 17–19, 40, 55–56, 202–207, 237–238).** No single
threshold; several figures for several sub-problems, and a repeated statement that the
practical minimum is unknown. "One estimate is that five to seven hundred words of text
are needed to make it worth touching a completely new system. Another places a threshold
at forty to sixty letters of alphabetic text, that is, about double the number of distinct
signs in the script, to begin to get a useful frequency chart" (p. 40). Shannon's unicity:
about 30 letters for a simple substitution of English; "a syllabic script with 100
sign-types, treated as a simple substitution cipher, would have a unicity distance of
about 225 signs", with the caveat that treating an ancient script as a substitution
cipher "is questionable at best" (p. 204). The Phaistos Disk's 241 tokens are "barely
equal to its theoretical unicity, and thus far below its practical one" (p. 205).
Householder's empirical version: coherent sense breaks down "within a few hundred words"
(p. 206). "Unicity may be the absolute theoretical minimum, but the practical minimum is
much higher, and higher by an as yet undetermined amount" (p. 238, note). On Linear A:
"a mere hundred and fifty short texts form the core of what is known" (p. 4); "structural
regularities cannot be expected to show up in a small corpus of this sort" (p. 17).

**Linear A's inflection, compared with Linear B at matched size (pp. 212–214).** "A good
case for this exercise is Linear A, which shows no systematic and almost no suspectable
inflection, although a Linear B corpus of not much larger size gives ample evidence for
suffixation." She notes records are shorter on average in Linear A, concludes "from
surface evidence alone" that Linear A "appears to represent an analytic language", and
adds, on the Semitic candidates, that they "are also heavily prefixing, a feature which
has not been internally demonstrated for Linear A" (p. 213, note 2).

**Kober's method (ch. X, pp. 145–170).** Paradigms and alternations described as the
core internal method, Ventris's grid and Kober's paradigms "first cousins" (p. 41);
Kober's 1946 argument that list-texts of word, ideogram and number must contain nouns is
quoted with approval (pp. 165–166). No chance baseline, null or significance test is
proposed for the alternation method itself; the safeguard offered is "complexity, as
insurance against randomness".

**Statistical tests she does give.** In ch. IX (boundaries), digram frequency against
the joint probability of the two signs, with a significance criterion of "a factor of six
or more", calibrated on her own Linear B comparison corpus. In ch. XII, a formal
decision-theoretic framing (Bayes, minimax, Neyman–Pearson) applied to those boundary
tests with a reported false-alarm rate of about .05 (p. 187). In ch. V, a random corpus
"of the same length, with the same number of signs" as a non-linguistic "toy" for
comparison (p. 78), citing Packard's 1967 dissertation for fictitious decipherments.

**On transferring values by shape (p. 98).** "One wonders why scholars tried for so long
to wrestle sense out of Cypriot values for Linear B signs of similar shape: less than ten
percent turned out to be the same in both form and value ... One wonders even more, in
the face of the Cypriot–Linear B fiasco, why so many scholars are now trying the very
same approach to Linear A, using Linear B values for Linear A signs of similar shape after
no more than a cursory inspection of function."

**On vocabulary matching (p. 209).** "Vocabulary, as historical linguists are well aware,
is a very risky indication of genetic relation, especially in a small sample and even
more in a sample of unknown contents."

**Not in the book.** No test of a decipherment against a deliberately wrong language; no
number for a syllabary beyond the unicity estimate above; no measured floor from
subsampling a deciphered corpus.

## What it verifies for this project

- **C-5a.** She gives numbers, all theoretical or rules of thumb, and says the practical
  minimum is undetermined. The measured floor (F-022) is the "statistical analysis of
  different-sized language samples" she asks for on p. 237, done for one method on one
  deciphered corpus. Grade: Shown elsewhere for the bound; the measurement is ours.
- **C-4a, C-4b.** Her pp. 212–214 state, in 1974 and from internal analysis without a
  null, what F-019 and F-022 measure: Linear A shows less inflection than a Linear B
  corpus of comparable size. C-4b, previously "Not found", is therefore **Stated** by
  Barber; ours supplies the null, the size-matched subsamples and the second edition.
- **A-001 and the circularity trap.** Her p. 98 is the warning in `corpus-sources.md`,
  stated in 1974 with the Cypriot precedent as the argument.
- **C-3d.** She proposes no null for Kober's method; her ch. IX digram test is a null for
  boundaries, not for paradigms.

## Our assessment

The methodological handbook the field had in 1974 and the clearest statement of what a
statistical decipherment programme should look like. Its two gaps are the ones this
project's instruments fill: a null for the alternation method, and a measured rather than
theoretical text floor. Its two warnings, on value transfer by shape and on vocabulary
matching, are the project's two negative results, stated fifty years earlier.

## Discussion

Corrections and disagreement are welcome. Open a pull request against this file, or raise an
issue linking to it. If you are the author of this work and we have misrepresented it, say so
and we will fix it.
