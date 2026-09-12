---
key: kober1946
authors: [Kober]
year: 1946
title: "Inflection in Linear Class B: 1. Declension"
venue: American Journal of Archaeology 50(2), 268–276
ref: 10.2307/499054
scripts: [B]
domains: [methodology, philology]
standing: accepted
verified: V
verified_on: 2026-09-11
access: paywalled (JSTOR stable 499054); read in full 2026-09-11
tested_by: [kober-method]
aliases: [Kober triplets, Kober 1946]
---

# Kober (1946), *Inflection in Linear Class B: 1. Declension*

Read in full from the JSTOR PDF. The paper is nine pages, seven numbered assumptions,
eleven figures of normalised sign groups, and a closing page on what the result would
mean for the syllabary.

## What it claims

That enough evidence exists in the published Knossos tablets to set up partial noun
paradigms. For two noun types she establishes three "cases" each, from five nouns of
Type A and three of Type B, and proposes that the two types belong to one declension.

## The method, as she states it

Seven assumptions, numbered in the paper, are the whole method.

1. The language inflected. 2. So it had paradigms. 3. Words in lists, each followed by
an ideogram and a number, are nouns, probably proper nouns. 4. **Nouns in the same list
on one inscription are all in the same case.** 5. A form in a given list is that case's
form for its declension. 6. **An ending that recurs across the words of one inscription
is the usual ending of that case for that noun type**, so other words with that ending,
elsewhere, may be in that case too. 7. A new case is demonstrated when **a reasonable
number of words have variants formed by the same rule, and the variants occur in lists
that themselves show homogeneity of ending.** Footnote 7: "reasonable number" means
"two or more. Two words out of a total of about 750 would seem to be a reasonable
number."

The procedure: start from the "Woman" tablet, where a quarter of the 43 listed words
end in one sign (B 7) and two or three in the same two signs (B 2, 7); call that Case
I. List every published word ending in B 2, 7 (eight). Look for variants: two of them
have variants replacing B 7 with B 40, and both variants occur on "saffron" tablets
where every listed word ends in B 40. Call that Case II. Look again: four words have a
variant that drops the final sign and changes B 2 to B 59, and every one of those
"appears in the same position on the same type of tablet, i.e., either as the first
word in the second register" of the sheep inventories. Call that Case III. A fourth
case is sought and not found: "no two words agree on a fourth variant."

Under Ventris's values the endings are -si-ja, -si-jo, -so (Type A) and -ti-ja, -ti-jo,
-to (Type B): the ethnic adjective and the place name it derives from.

## The grid inference

Assume a Cypriote-type syllabary, consonant plus vowel. Then B 2 and B 59 (si, so) share
a consonant and differ in vowel, as do B 36 and B 20 (ti, to); and if both types are one
declension, B 2 and B 36 share a vowel, as do B 59 and B 20. "If this interpretation is
correct, we have in our hands a means for finding out how some of the signs of the
Linear Class B script are related to one another. Several other interpretations of the
facts are, however, possible."

## What she says about scope and confidence

- "The total number of different sign groups (i.e., words of different spelling) in the
  available inscriptions is so limited (there are less than 750 in all)."
- "No results even approaching these can be demonstrated for other nouns occurring in
  the same inscriptions ... it is not encouraging."
- "There is not enough material to work with, and the relations of the signs to one
  another are unknown."
- Footnote 9: Evans (PM fig. 696) had already listed three words with the B 7 / B 40
  variation, and Sundwall (1936, figs. 3 and 15) ten such pairs and four of her five
  Type A groups: "a good deal of the evidence presented here has already been collected
  by others, although not for the same purpose, and not from the same point of view."
- Casts at the Metropolitan Museum were "far more useful than the transcriptions"; her
  own fig. 2 contains a reading error from a misleading photograph, corrected in 1948.

## What it changes for this project

1. **Her corpus was smaller than Linear A's, in word types.** Under 750 sign groups,
   against Linear A's 988 under the Kober filter. F-027's comparison "at her scale" used
   988 as a proxy for her scale; the true figure is lower, which makes the comparison
   more favourable to the instrument, not less.
2. **Her context was list-level, not word-level.** Assumptions 4, 6 and 7 use the
   tablet as a unit in which all listed nouns share a case, and Case III's evidence is
   position on a tablet type. Kober 0.4 encoded a slot each word carries (F-026); 0.5
   encodes a role within an entry (F-028). Neither encodes "co-listed words share an
   ending", which is the strongest of her three uses of context and the one she built
   Cases I and II on. Pre-registered as a read-only diagnostic (CHANGELOG, "List
   homogeneity on Linear B").
3. **Her triplets are in our output and not on our answer key.** Under Kober 0.3 on
   the full Linear B corpus the alternations -so/-si-jo, -so/-si-ja, -to/-ti-jo and
   -to/-ti-ja have support 5 to 6 and ranks 46 to 77 of 5,250, and `is_grammar` returns
   no rule for any of them, because the reference list encodes the -jo/-ja gender pair
   but not the ethnic derivation from the bare place name. F-016's nine of ten is
   unaffected, since none of the four is in the top ten, but the reference list is
   incomplete in exactly the place she started from. Pre-registered as Kober 0.6 (a
   reference-list revision, rescored on every existing file; stage 1 untouched).
4. **Her bar was two words.** "Two or more", with list homogeneity as the second
   condition. F-027 read our calibration against "a few sure paradigms"; her own number
   is written down and it is two, plus a context condition we have not yet built.
5. **The grid inference is hers, with her own caveat.** The 1948 paper repeats the
   three assumptions behind it and says "fig. 10 has no validity" until the phonetic
   relationships prove mutually confirmatory. Our stage 2 (F-017, F-018, F-021) checks
   exactly that confirmation against the known values.

## Our assessment

The method is a precise algorithm and she states it as one. Its inputs are the word
list, the tablet as a list with a shared case, and the tablet type as a position. Its
output is a handful of paradigms with a two-word bar. The instrument named after her
reproduces the first and third inputs and the bar; the second input, list homogeneity,
is the outstanding difference, and it is testable on Linear B before anything else is
built.

## Discussion

Corrections and disagreement are welcome. Open a pull request against this file, or raise
an issue linking to it.
