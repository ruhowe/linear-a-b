# What this project found, and what was known before

Plain English, for a reader with no background in the subject. Not reviewed by any
specialist. Last updated 2026-09-12, after an outside review.

This repository tests whether the statistical methods people use on Linear A and Linear B
actually work, by running them against controls. It does not decipher anything. Every
number below traces to a dated entry in [FINDINGS.md](../../FINDINGS.md), and each
section names the entries it rests on.

## Before you read this

I am not an academic. I am an old classicist with a long interest in the subject who, in
2026, is good at running Claude Code. The work here was done with Claude Code under my
direction, using HENGE, a notation, memory and context system I designed for working with
AI assistants on long projects. Why I am publishing it this way, and how I would like it
read, is in the [README](../../README.md#before-you-read-this).

Almost everything here was produced with heavy automation, including the searching and
the note-keeping, so **there is a real chance that some references or sources are wrong,
misquoted, or do not exist at all.** I have checked what I could in the time I had. It
has not been reviewed by any specialists, and I have not requested a review. I have not knowingly breached a licence or
misattributed anyone's work, and if I have, please assume a mistake rather than bad faith
and tell me: ru@stornaway.io. The full statement is in the
[README](../../README.md#before-you-read-this).

Working through the material with my guidance, I asked Claude Code to summarise what came
out of it, and the summary below is what it produced. Throughout, "I" is me: what I chose
to test, what I read, and what I accepted. "Claude Code" is the tool, and "it" refers to
it: it built the instruments, ran the counts, searched the literature and drafted the
notes and this summary. The judgements in the "What this means" sections were drafted by
Claude Code and are ones I accepted, not ones I formed independently. Where I directed a
change, the entry says so. I make no claim to expertise, and none of it is validated. I am
putting it here in case it helps someone else test, check or take the work further.

Where this builds on earlier scholarship, that work is credited by name. Where it measures
a currently active claim, the claim is described by its measurements, and any judgement
stays on the work rather than the person.

<!-- Maintenance: this is the people-facing version of docs/ai_context/claims.md. Every
section names its claim atoms in a comment; tests/test_claims.py fails if a claim in the
register is not referenced here. Update this file in the same commit as any change to
claims.md or to a FINDINGS entry a claim rests on. Writing rules: writing-style.md. -->

## The one piece of background you need

Linear A is read by giving each sign the sound that the same-looking sign has in Linear B,
which we can read because it is Greek. That is a convention, not a proven fact. If those
borrowed sounds are wrong, every translation of Linear A built on them is wrong too.

## Completely new, as far as I could find

<!-- C-4c, C-7b -->

- Checking a Linear A result in both modern editions of the texts.
- Counting how often the 2026 di Mino decipherment divides words differently from the
  standard edition.

<!-- C-4b, C-8a -->

Two more are new in how they were done, though the question itself was older: measuring
Linear A's word structure against Greek's with the same amount of text (Barber made the
comparison by eye in 1974), and putting the place-name evidence for the borrowed sounds
through a proper chance test with wrong word lists as controls (Packard ran a weaker
version in 1974).

Everything below had some earlier version. What was added here is marked in each.

## Built on earlier work

**1. Matching words to dictionaries can't pick out a language**
<!-- C-1a -->
- **Before:** Packard (1974) compared the real sounds against random ones on Linear A, and
  estimated how many matches chance alone would give. A research group in Singapore tried
  several languages and called its results inconclusive. The linguists Ringe (1992) and
  Kessler (2001) worked out how often unrelated languages match by chance (both found
  after the work here).
- **Added here:** the test on Linear B, where the answer is already known to be Greek. Finnish,
  Basque and Sumerian "matched" the Greek texts almost as well as Greek did.
- **What this means (and so what):** most attempts to decipher Linear A read its words with
  the borrowed sounds, then look for similar words in some language's dictionary. That
  method finds convincing matches for languages that are certainly wrong. **So when someone
  announces that Linear A matches Hittite, Hebrew or Basque, the matches alone prove
  nothing, and that includes the recent "AI decodes Linear A" headlines.** One limit: with
  lots of text and a different technique, computers can identify languages; a 2016 study
  got 97% right across 380 languages. Linear A has nothing like that much text.

**2. Beating random guesses is not enough**
<!-- C-1b -->
- **Before:** Packard used random sounds as his control, and trusted each kind of evidence
  only as far as it beat them. He already dismissed matches with Greek mainland words as
  "nearly worthless" for that reason.
- **Added here:** every real language beats random guesses, the wrong ones included.
- **What this means (and so what):** decipherers often defend a reading by showing it does
  better than random. **So "better than random" is not evidence a decipherment is right; a
  claim has to beat wrong real languages, and almost none has been tested that way.**

**3. Greek-looking words turn up in Linear A, but that doesn't make it Greek**
<!-- C-1c -->
- **Before:** Packard (1974) found that, read with the borrowed sounds, Linear A words match
  names from Knossos more often than any random version does, and concluded that at least
  some of the borrowed sounds are right. Reviewers at the time accepted this. Greek-looking
  words have also been picked out of Linear A by eye, in a body of work still being argued
  over. Steele and Meißner warned that borrowed sounds make such findings circular.
- **Added here:** a measurement. With the borrowed sounds, Linear A matches a Greek dictionary
  about as well as genuine Greek text does.
- **What this means (and so what):** the borrowed sounds are Greek sounds, and Minoan and
  Mycenaean Crete shared some names, so Greek-looking words appear either way. **So Greek-looking
  words in Linear A are partly an echo of how we read it and partly a sign that some of
  the borrowed sounds really are right, and they are not evidence that the Minoans spoke
  Greek.**

**4. The strongest Semitic match was produced by the method**
<!-- C-2a, C-2b -->
- **Before:** critics argued that Cyrus Gordon's 1966 Semitic reading picked matches from
  whichever Semitic language suited. Hauer and Kondrak (2016) suspected their own Hebrew
  result on the Voynich manuscript was a side-effect of their method. Kessler (2001) showed
  that the choice of word list changes results (found after the work here).
- **Added here:** Hebrew scored high from a scholarly dictionary of word roots and no better
  than unrelated languages from an everyday word list. Removing one sound-mapping rule made
  the Semitic lead disappear.
- **What this means (and so what):** the idea that the Minoans spoke a Semitic language,
  related to Hebrew and Arabic, has been argued since the 1960s. **So this particular
  evidence for it doesn't hold up. It doesn't prove the theory false; it removes one reason
  to believe it, and gives a check any future Semitic claim should pass.**

**5. Alice Kober's method works when a computer runs it**
<!-- C-3a, C-3b, C-3c, C-3d -->
- **Before:** Kober (1940s) and Ventris (1951–52) did it by hand, and it led to Linear B
  being cracked. Her 1946 paper states the method as seven numbered assumptions, from
  under 750 distinct words, with a bar of two words sharing a variant. Packard (1974)
  already set Kober's approach against the dictionary method. Computer methods for finding
  word endings (Goldsmith 2001) and for sorting letters into consonants and vowels (Kim and
  Snyder 2013) exist for other languages (found after the work here).
- **Added here:** running it on Linear B by machine, with a check against chance. Nine of the
  ten strongest patterns it found are real Greek grammar, and it recovered the sign pairs
  Kober drew by hand. Cut down to Linear A's amount of text, it does what she did: its two
  best patterns are grammar every time, all three of its top three about two times in
  three, and nine in ten once the signs the standard handbook lists as spelling variants
  are merged. Her condition that words listed together on a tablet share an ending turned out to be
  true of the corpus, nearly twice chance, but too rare to help the machine; three ways of
  giving the machine tablet context were tried and moved the result by almost nothing.
- **What this means (and so what):** Kober's method uses no sounds at all, only which signs
  repeat and where. **So there is now a tested, automatic way to study Linear A, or any
  undeciphered script, that can't be misled by wrong guesses about sounds.** One correction,
  and an example of the division of labour: the list of "what counts as Greek grammar" that
  Claude Code built, and I accepted, was missing the pattern her own triplets are made of.
  Reading her paper exposed the gap; I directed the fix, it changed the small-corpus
  numbers, and the lesson is written down.

**6. Linear A words have real stems with changing endings**
<!-- C-4a, C-4b, C-4c -->
- **Before:** Duhoux (1978), Thomas (2020) and Monti (2022) spotted prefixes and suffixes by
  eye. Packard listed word pairs with different endings, without a chance check. Kober wrote
  in 1948 that inflection of Linear B's kind "does not seem to exist" in Linear A, and
  Barber's 1974 handbook says Linear A shows almost no inflection "although a Linear B
  corpus of not much larger size gives ample evidence for suffixation", by eye. One 1999
  paper by Facchetti, "Statistical data and morphematic elements in Linear A", may have done
  part of this; I have not been able to read it yet.
- **Added here:** a check against chance (the patterns are real), a comparison with Greek at
  the same size (Linear A's pattern is weaker, at or below the bottom of Greek's range),
  and the same result in both editions of the texts. The comparison with Greek at the same
  size was stated by Barber in 1974 without a chance check. The two-edition check is new
  here. The chance test is new only if Facchetti's 1999 statistical paper, which I have not
  been able to read, did not already make it.
- **What this means (and so what):** patterns appear by accident in any large pile of
  symbols, so seeing them isn't enough. **So the grammar-like patterns scholars saw in
  Linear A are genuine, and that holds even if every borrowed sound is wrong. It is not yet
  possible to tell whether they are grammar or recurring names and set phrases, and Linear A shows less
  of them than Greek does.**

**7. Linear A's own patterns can't yet test the borrowed sounds**
<!-- C-4d -->
- **Before:** Packard (1974) ran this exact test: do the borrowed sounds make Linear A's
  changing endings line up the way real grammar does? He got 7 matches against 3.9 for
  random sounds, and called it weak.
- **Added here:** the same answer with a modern chance check (1.4 to 1, not significant), and
  the reason: there are too few changing endings in Linear A to decide. This was reached
  without having read his pages, which I only saw afterwards.
- **What this means (and so what):** the biggest open question about Linear A is whether we
  can trust the sounds we read it with. **So Linear A's internal patterns can't settle it
  either way at this size; the evidence that some borrowed sounds are right is place
  names, item 7b.**

**7b. The place names do support the borrowed sounds, for a dozen signs**
<!-- C-8a -->
- **Before:** Packard (1974) also made the argument everyone since has leaned on: Cretan
  towns named on the Greek Knossos tablets (Phaistos above all) turn up on Linear A
  tablets when you read them with the borrowed sounds. He counted 13 matches against about
  3 by chance, using nine hand-made scrambles of the sounds.
- **Added here:** the same test with a real chance check, four hundred scrambles that
  disturb every sign in every word, on both editions of the texts, and three wrong word
  lists of the same shape as controls: Knossos personal names, place names from mainland
  Pylos that a Cretan archive should not know, and the Cretan names spelled backwards.
  The place names beat chance everywhere; none of the wrong lists does.
- **What this means (and so what):** this is the first positive result on the borrowed
  sounds in the repository, and it is small: five Linear A words, three place names, a
  dozen signs, all ones specialists already counted as secure. That agreement is partly
  built in, since these same place names are among the evidence specialists have always
  cited for those signs; what the test adds is a proper chance check of that old argument.
  **So the convention has a
  tested core of about a dozen signs, and the other sixty-odd remain assumed.**

**8. There's a measurable amount of text needed, and it depends on the instrument**
<!-- C-5a, C-5b -->
- **Before:** Barber (1974) gave theoretical figures for the minimum text a decipherment
  needs (about 225 signs for a 100-sign syllabary by Shannon's formula) and said the
  practical minimum is "undetermined" and would need measuring on samples of different sizes. Both 1976 reviews of Packard said there was too little Linear A. Knight and
  Yamada (1999) and Ravi and Knight (2008) measured how accuracy grows with text for
  Japanese and for codes (Ravi and Knight found after the work here).
- **Added here:** a number for the machine version of Kober's method, found by cutting Linear
  B down to smaller sizes. To find Greek's grammar *reliably*, meaning most of its top ten
  patterns are grammar nearly every time, the first version of the instrument needed about
  1,900 different words; Linear A has 988. After I had Claude Code rebuild the "what counts
  as grammar" list from the standard handbook and merged the signs it lists as spelling variants, the same test needs
  about 1,250, and on the easier bar (the top three patterns all grammar) about 750, less
  than Linear A has. The number moved because the instrument changed; the text was the
  same throughout. The hand-built list of what counts as grammar is the biggest lever on
  these numbers, so treat them as provisional until a specialist has checked that list. With only
  Linear A's amount of text it finds a couple of sure patterns every time, which is what
  Kober herself published from fewer words than Linear A has.
- **What this means (and so what):** "there isn't enough Linear A" is usually said as a
  shrug. New inscriptions do still turn up; a Knossos ring with the longest Linear A text
  yet was published in 2025. **So Linear A isn't necessarily undecipherable forever: somewhere
  between a quarter more and double the vocabulary we have would reopen this route, which gives excavators and
  funders something concrete to aim for, though at the rate finds arrive, about 11 signs a
  year since 1985, the instrument will move the number faster than the spade will.** One
  caution: merging spelling variants uses knowledge we only have because Linear B is read,
  so the lower number describes Greek with that help. The limit is on reliability, not on
  finding anything at all: at Linear A's size the machine, like Kober, can find a few patterns it is
  sure of, and Linear A's own patterns are weaker than Greek's at that size.

**9. A published AI restoration tool may be recognising familiar text rather than recovering lost text**
<!-- C-6a, C-6b -->
- **Before:** the group that built the tool reported a simple comparison of their own on one
  set of tablets, and it came close to their tool. Restoration studies of other ancient
  texts routinely include such comparisons (Fetaya 2020, found after the work here).
- **Added here:** three things the publication does not report. A plain word-list lookup scores
  31.5% where the published tool scores 30.3%. Guessing the most common signs, which is the
  floor any method has to beat, reaches 58.4% against the published 66.2%. And that lookup's
  accuracy is almost entirely carried by words it has already seen: 82.8% on those, 3.0% on
  words it has not, with 64% of the test items being words it has not.
- **What this means (and so what):** AI tools that fill in missing parts of damaged ancient
  texts are being published and publicised. The published numbers are reproduced here by a
  much simpler method, and both sit close to the floor. Nobody has reported that last split
  for the tool itself, so this does not measure it directly. **So on this
  evidence a headline accuracy figure, quoted without a floor and without that split, may
  read as a stronger result than it is, and the open question is how much of it is
  recognition of familiar words rather than recovery of lost ones.**

**10. A 2026 Semitic decipherment uses a large share of unestablished sound values**
<!-- C-7a, C-7b -->
- **Before:** critics, online and in the press, argued that the sound values it used were
  unproven. Nobody appears to have counted them.
- **Added here:** the count. In the central inscription, a third of the sign positions use
  sounds that specialists do not list as established. On another inscription the reading
  divides seven words where the standard edition divides five, so two of its seven words
  exist only under its own way of splitting the text (new). Two things in its favour, which
  should be said: the inscription references all check out against the corpus, and nothing
  in them is invented.
- **What this means (and so what):** in 2026 a researcher, Tom Di Mino, presented a reading of Linear A as a Semitic language,
  and it got press coverage. Personally, I was quite excited about this, and admire his
  effort and use of Claude Code - I found it while planning this work in Claude Code myself.
  A substantial part of the reading rests on values and word divisions proposed by the work
  itself. That leaves it untested rather than wrong: the evidence for it has still to be
  separated from the assumptions it was built on, which is a test it could be put through.

## Sometimes I did work with Claude Code without knowing it had been done before, despite reviewing the literature first

Some of the above was reached without knowing someone had been there first. The clearest is
Packard (1974), who framed his study as Kober's method against the dictionary method, ran
the same alternation test that was run here, and got the same weak answer. I read his pages
only after the results were in, because his book is not widely available.
The full list, checked against the project's history, is in the claims register.

## Caveats to say out loud

- It has not been reviewed by any specialists, and I have not requested a review. I am not
  intending to submit it for review at the moment.
- Claude Code did the counting, the searching and the note-keeping, working within HENGE,
  so a reference may be wrong or may not exist. The judgements are checked against
  controls, not taken on trust, but the citations have not all been checked by hand.
- A few sources that could change a verdict are still unread, mostly paywalled, and the
  search for earlier work covered what is reachable online.
- This work was done in good faith. I am not looking for controversy or to mislead anyone.
