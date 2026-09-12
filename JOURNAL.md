# Journal

A dated narrative of the investigation: what each phase did, what it found, and why the
next phase followed from it. It is the reading order for someone who wants to understand
how the project got where it is, rather than what it currently claims. Results are quoted
from FINDINGS entries (F-nnn); protocol details live in CHANGELOG; assumptions in
ASSUMPTIONS (A-nnn). One entry per phase, appended as phases close. Kept concise on
purpose: this is the map, the other files are the territory. Written by Claude Code at
the close of each phase; "Ru" is the author directing the work.

---

## 2026-09-10 · Phase 1 · Survey and choice of first problem

Read the field. Wrote `docs/ai_context/state-of-the-art.md`: what has been tried on
Linear A and Linear B, what the field requires of a credible claim, what pyaegean
already implements. Two facts decided everything after: the corpora are tiny (54,476
and 6,406 tokens), and Linear A transcriptions use Linear B sound values by convention,
so any phonetic argument about Linear A is circular unless controlled. Decision: start
with a value-free problem where a published benchmark exists, Linear B text
restoration, to learn the data and its traps before touching Linear A.

## 2026-09-10 · Phase 2 · Linear B restoration baseline (F-001, F-002)

Rebuilt the published restoration benchmark from DĀMOS. Found three loader traps
(underdots do not affect reading status; one-sign words misclassified; restored text
lives inside "unclear" tokens). Result: a lookup of training word types matches the
published neural network, the published top-20 metric sits near a frequency floor, and
accuracy collapses from about 90% on word types seen in training to under 10% on
unseen ones. Lesson carried forward: an aggregate number on this corpus is a
memorisation measurement unless it is split by seen and unseen, and every headline needs
its floor beside it.

## 2026-09-10 · Phase 3 · First null test of a Linear A claim (F-003, F-004)

Turned to the 2026 Di Mino "Linear A is Semitic" preprint, read in full rather than
from press summaries. Built the obvious test: match Linear A words to Hebrew roots,
compare with scrambled sign values. It gave a false positive (p = 0.016) because the
real map reaches more candidate roots than the scrambled ones. Fixed by matching
candidate breadth: p = 0.15. A planted-root positive control passed too easily. Lesson:
the first null anyone builds is wrong, and a positive control must be as hard as the
real case.

## 2026-09-11 · Phase 4 · Greek as the known-false control, and the method that "could not work" (F-005 to F-007)

Ran Greek on Linear A, where it is not the language: it scored higher than Semitic,
because the transcription values are Greek. Ran the method on Linear B, where Greek is
the answer: it failed, and Claude Code wrote that consonant matching cannot work on Linear B. Ru
asked whether the known spelling rules could be compensated for. They could. Encoding
Mycenaean spelling and weighting by dictionary frequency made Greek detectable on Linear
B. F-006 withdrawn. Lesson: "cannot work" was an artefact of not encoding what we
already knew, and the user's question was the right one.

## 2026-09-11 · Phase 5 · Frozen protocol and the harness (F-008)

Froze the instrument as protocol 1.0 before running Linear A once. Built the hypothesis
harness so every test runs against every candidate language with scenario weights.
Added wrong real languages (Finnish, Turkish, Basque, Hungarian) as controls. They beat
the synthetic controls on Linear B at the level Greek did. Verdict: the method detects
that a dictionary is a real language, not which one. Also this day, at Ru's request:
the repo restructured into per-work catalogue pages and guides, a versioned CHANGELOG,
a dated FINDINGS file as the only place results are stated, and the writing-style rules.

## 2026-09-11 · Phase 6 · The Semitic pattern taken apart (F-009 to F-012)

Ugaritic and Hebrew came top on Linear A and bottom on Linear B. Four pre-registered
tests: a second word sample (the ordering held, magnitudes moved by up to 1.3), a
Modern Hebrew frequency list (same language, scored with the unrelated pack), laryngeals
removed from the map (Ugaritic's lead halved), Arabic (fell as predicted). Three
samples under both protocols: Ugaritic's lead over Basque about one standard error.
Verdict: dictionary shape, the laryngeal channel and sampling variance, not a language
signal. ASSUMPTIONS.md created at Ru's request, A-001 onward, three already falsified.

## 2026-09-11 · Phase 7 · More languages, and the positive control's margin measured (F-013)

Hittite via Wiktionary (67 headwords: uninformative, not negative) and Sumerian as a
typology-matched wrong answer. Sumerian and Finnish fit Mycenaean Greek text at +2.3
under the Greek map against Greek's +2.8 to +3.2. The positive control's lead over a
wrong real language is about one sample standard error. F-008 downgraded. Rule added:
every "detects" claim quotes the best wrong real language beside it.

## 2026-09-11 · Phase 8 · A confound found in our own sensitivity (F-014, F-015)

Ru asked for a TODO list with a model per item and "go ahead" as the resume word. Item
1, corpus hygiene: no underdots in Linear A (F-015); the 25-secure-sign restriction
appeared to make Greek's signal vanish. It did not. The null's frequency bands are
computed from the sample, so restricting the pool changed the null. Under one fixed
null, every lexicon's per-word gap is larger on the secure signs. First verdict
withdrawn, A-042 falsified, discipline rule added. Lesson: two seeds on a pool smaller
than the sample are one sample.

## 2026-09-11 · Phase 9 · Naming the methods, and the Kober design

Ru asked whether there was a better way than dictionary matching, and what to call each.
Fixed the names in `terminology.md`: the etymological method and the Kober method.
Designed the Kober method as an instrument before writing code: stems, endings,
paradigms, two statistics with two nulls (the protocol 1.0 null cannot be reused since
relabelling preserves shared prefixes), a reference list of Mycenaean endings as the
answer key consulted after the ranking, and a three-part criterion. Disclosed that a
read-only sizing count had shown the Linear B top alternations before the list was
written. Ru approved the design.

## 2026-09-11 · Phase 10 · The Kober method works on Linear B (F-016 to F-018, F-021)

Kober 0.1 met all three parts: 932 paradigms against a null ceiling of 634; nine of the
top ten alternations are Mycenaean grammar; Kober's triplets fell out at the top. The
prefix channel's paradigm count turned out to measure suffixes (A-047). Stage 2, the
grid: pooling every pair gave a real but weak consonant signal and no grid (F-017);
anchoring by stem made it worse (F-018); taking one pair per strong alternation, which
is what Kober did by hand, recovered four of seven same-consonant pairs against a null
of one in ten (F-021). Ru asked that refinements be versioned as one line: 0.1, 0.2,
0.3, stage 1 unchanged throughout.

## 2026-09-11 · Phase 11 · Linear A, its floor, and a correction (F-019, F-020, F-022)

Pre-registered the Linear A reading, then ran a size-matched Linear B control first,
then Linear A. Linear A's paradigm count is above its null; nothing else is readable.
The head-to-head (F-020): the etymological method is a false-positive instrument, the
Kober method a floor-limited one. Then the floor sweep: the method becomes readable on
Greek at about 1,875 word types when a corpus is shrunk by tablets, 2,750 when shrunk by
random words. Adding the tablet-model row at Linear A's size corrected my own sentence:
Linear A's structure is at or below the low end of Greek's at matched size, not "about
as strong". Both earlier entries carry the dated correction.

## 2026-09-11 · Phase 12 · Edition sensitivity and the second session (F-023, F-024)

The one untested assumption under the Linear A statement was the word dividers. SigLA's
edition gives the same statement (F-023). Meanwhile a second session began cataloguing
prior art for every claim, writing `claims.md` and F-024. Reviewed it: append-only,
consistent, one grading disputed here (Packard's 2:1 is agreement in direction with a
weaker instrument, not contradiction). Added a findings query tool, a generated index,
a results map, a claims-consistency check, and a written division of which session owns
which files. Backed the repository up as a dated bundle.

## 2026-09-11 · Phase 13 · Towards a context-aware Kober instrument (item 8, in progress)

The other session proposed closing the gap between our 1,875-type floor and Kober's
roughly 200 tablets by using tablet context and asking for fewer, surer findings.
Accepted, with two prerequisites in front: measure the null rate of the "grammar match"
part of the criterion, which had never had a null and whose rules are permissive; and
re-score the existing small-corpus runs under precision criteria so the context version
has a bar to beat. Both pre-registered and run.

## 2026-09-11 · Phase 14 · The grammar match gets its null; two floors (F-025)

The first pass used a top ten that included ties, which at Linear A's size becomes a
set of hundreds and made both real and null counts meaningless; a strict top ten fixed
it. Result: on the full corpus the real nine matches stand against a chance ceiling of
two or three. At 988 word types the real top ten beats chance in 17 to 19 of 20
subsamples, so the "seven of ten" bar in the original criterion was stricter than chance
required, and F-022's floors are floors of a *mostly* grammatical list, with a second,
null-referenced floor at or below 988 now beside them. But the list is unreliable item by
item at that size: all top three right in only five or six of twenty. That number is the
target frozen for Kober 0.4, the context-aware version, designed and pre-registered in
the same phase: tablet context as a slot class, support counted only between words that
share a slot, nulls stratified by slot so context cannot pass as signal. Before 0.4
touched the shared code, Ru asked that earlier findings stay reproducible and rollable
back: every finding's commit now carries an F-nnn tag, a regression test pins the stage 1
values to the committed results files, results files will stamp the version of every
block, and 0.4 is opt-in so the old paths are unchanged.

## 2026-09-11 · Phase 15 · Slot context fails, and the reason is measured (F-026)

Kober 0.4 gave every word a slot (document type, line-initial, what follows it) and
counted a stem as inflecting only when its two forms shared one. Calibrated on Linear B
at Linear A's size, it did worse than the version without context: two of twenty
against a bar of sixteen and a baseline of six. A read-only diagnostic on the full
corpus explained it: the two forms of a real Linear B paradigm share a slot about one
time in five and show no consistent slot pair either, so the feature carries almost no
information about which words are forms of one another, and a filter on it can only
remove evidence. The natural follow-up on slot pairs was ruled out by the same numbers
before being built. What Kober used was more likely the alignment of entries across
parallel tablets, which is a different representation and a new instrument, left as an
open design question. Linear A was not run, as the pre-registration required.

## 2026-09-11 · Phase 16 · Did we replicate Kober? Yes, in kind; the gap was between bars (F-027)

Ru asked whether Kober's success had actually been replicated. Re-reading the F-025
table under the pre-registered candidate criterion closest to what she published, a
few sure paradigms rather than a mostly grammatical top ten, the answer is yes: at her
corpus size on Greek text the instrument's two best alternations are grammar in every
tablet-model subsample and its top three stand above chance in sixteen of twenty. The
gap that motivated 0.4 was between her bar and ours. Linear A remains below that scale
in signal, not in word types: its best alternations sit at the null. Two of her short
pieces (1944, 1945) were then read in full: the 200-inscription
corpus is her own figure, and the one contextual inference she shows is a word placed as
a list total, entry-in-list structure rather than a word-level slot, which is consistent
with why 0.4 failed. The 1946 triplets paper and the 1948 method paper are still unread
(verification P); reading them comes before any further redesign.

## 2026-09-11 · Phase 17 · Entry role, measured before the papers arrive (F-028)

Ru asked whether to wait for Kober's 1946 paper before testing entry alignment. No: Linear
B's answer to "do forms of one word share a role across tablets" does not depend on
whether she used it. Pre-registered and run as a read-only diagnostic. Forms of one word
share an entry role six times more often than chance, and the grammatical alternations
carry it, but only one pair in eleven shares a role at all. So a filter on roles would
lose nine tenths of the evidence, as the slot filter did; a tie-break by role-sharing,
acting exactly where Linear A's ranking is decided among tied supports, is the one design
left. Pre-registered as Kober 0.5 with the same bar as 0.4 so the two are comparable.

## 2026-09-11 · Phase 18 · Kober's own papers, read (kober1946, kober1948)

The 1946 and 1948 papers were read in full. Three things changed. Her corpus was under
750 word types, fewer than Linear A's 988, so the F-027 comparison was conservative. Her
method is a stated algorithm whose strongest context condition is list-level: words
listed together on one tablet share a case, and a variant counts only if its list is
homogeneous in ending. Neither the slot version (0.4) nor the entry-role version (0.5)
encodes that, so it is pre-registered as a read-only diagnostic before anything is
built. And her actual triplets, the ethnic adjectives -so/-si-jo and -to/-ti-jo, are in
our Linear B output at ranks 46 to 77 but score no rule, because the answer key lacks
that derivation; the revision is versioned as Kober 0.6 and rescored on every existing
file rather than rerun. Her 1948 verdict that Linear A shows less inflection than B, and
of a different type, is what F-019 and F-022 measured.

## 2026-09-11 · Phase 19 · The role tie-break, calibrated (F-029)

Kober 0.5 orders tied alternations by how many of their stems share an entry role, and
changes nothing else. On Linear B at Linear A's size it lifted "top three all grammar"
from six subsamples in twenty to nine, with a chance rate of zero, against a bar of
sixteen. Improves, below the bar, Linear A not run, as pre-registered. Three encodings
of tablet context have now been tried; the one Kober herself stated, that words listed
together share an ending, is the one still being measured.

## 2026-09-11 · Phase 20 · Her list condition, measured (F-030)

Words listed together on a Linear B tablet share their final sign nearly twice as often
as chance: Kober's Assumption 4 is a fact of the corpus. But the condition she used to
admit a variant admits one stem pair in eighteen and admits grammar and non-grammar at
the same rate. Real and unselective. It is pre-registered as a fourth ordering key, 0.7,
with the expectation written that it will not reach the bar, so the context line closes
on a measurement. Ru's question about what the primary papers had that the literature
review lacked produced three rules for the discipline page: read the primary before
building, check the answer key against the canonical example, and register a method's
stated assumptions as atoms on day one.

## 2026-09-11 · Phase 21 · The answer key corrected from her paper (F-031)

One rule added to the reference list, the ethnic derivation her triplets are made of,
and every earlier run rescored rather than rerun. On the full corpus nothing in the top
ten changes and her triplets finally score at ranks 46 and 50. At Linear A's size the
tablet-model baseline for "top three all grammar" moves from six to eleven, and with the
role tie-break from nine to twelve, against a bar of sixteen. Five subsamples in twenty
had been lost to an answer key that could not read the example every summary quotes.
Her seven assumptions are now rows in the register, marked encoded, not encoded, or
tested. 0.7, the list tie-break, runs against the corrected baseline.

## 2026-09-11 · Phase 22 · The context line closes (F-032)

Kober 0.7 added her list condition as the last ordering key and reproduced 0.5's counts
exactly: nine and twelve of twenty against a bar of sixteen, chance rate zero. Three
encodings of tablet context have now been measured on Linear B at Linear A's size. The
answer-key correction moved the count by five; the three encodings together by one. What
remains between twelve and sixteen is the corpus, not the context. No version from 0.4
to 0.7 touched Linear A, because none earned it. The Kober line on Linear A stands where
F-027 and F-022 left it, and is closed on this corpus unless more Linear A is published.

## 2026-09-11 · Phase 23 · Written up

A single report for a specialist reader, `docs/reports/2026-09-11-two-methods.md`, built
from the journal and F-020's table, every number quoted from a finding, the three rules
first. The repository at this point: F-001 to F-032, A-001 to A-122, three protocol
lines versioned and pinned, twenty-three journal phases, a fresh backup bundle. The
etymological method is closed as a false-positive instrument on this corpus; the Kober
line is closed on Linear A at one edition-independent sentence, with its floor measured
and three context encodings tried. Open: the prior-art grading of the two new atoms, and
more Linear A.

## 2026-09-11 · Phase 24 · An exploratory run on Linear A, to see the failure mode (F-033)

Ru asked what would happen if the context version ran on Linear A anyway. Pre-registered
as exploratory with rule names withheld, it ran in a second. The keys reordered the whole
top ten, the opposite of my expectation, and for a clear reason: Linear A has 207
alternations tied at support one and two at support two, so there is no ranking to
refine, only a pool to select from, and a quarter of the pool shares a role by chance.
The top three it printed would look like a result on a page. That is exactly what the
gate prevents, now shown rather than argued.

## 2026-09-11 · Phase 25 · Prior art closed out, single session

The prior-art session was closed and its item taken over here. Packard 1974 read from the
cached primary: 7 of 34 hand-collected pairs against 3.9, read by him as largely
fortuitous, same direction as ours and no contradiction. Barber 1974 unreachable online;
one atom stays open for a library copy. The two atoms from the Kober papers were searched
and graded: her list condition as a statistic is a precursor of hers and nobody's since;
the answer-key gap is a correction to us, and the search found that DĀMOS already carries
the morphological annotation the list should have been derived from, which pyaegean does
not fetch. The claims register, the plain-English guide and the ledger now match F-001 to
F-033, with awareness read from git rather than memory, which corrected two rows.

## 2026-09-12 · Phase 26 · The primaries arrive

Packard 1974 in full, Facchetti's 1999 companion paper, and Barber 1974 were read.
Packard's Tables 13 and 14, unreadable in the archive.org text, are now read: the
"2:1" that circulated was his weakest class, and his real evidence for the borrowed values
was the Knossos toponyms, not internal alternations. His one-in-twelve chance model is
our F-017 chance fraction; his 1974 sentence that ignoring vowels yields hundreds of
matches for wrong values is our F-006 and F-012. Facchetti's a-/ja- pair is the one our
instrument put at the top of Linear A's prefix list at chance level. Barber is being read.
The README gained a scope statement: a targeted catalogue of 79 works, not a
comprehensive one, and what it does and does not cover.

## 2026-09-12 · Phase 27 · Barber 1974, read

Three hundred pages read and every number checked against the
page. She gives theoretical thresholds and says the practical minimum is undetermined
and needs measuring on samples of different sizes; the floor sweep is that measurement.
She proposes no null for Kober's method. And on p. 212 she states, from internal
analysis, that Linear A shows almost no inflection while a Linear B corpus of similar size
shows ample suffixation: the comparison F-022 measured, said in prose fifty years earlier.
One of the three atoms the register had marked "not found" is regraded to "stated". The
prior-art line is closed; two leads remain for a library.

## 2026-09-12 · Phase 28 · The answer key's source arrives

*Documents in Mycenaean Greek* was read. The morphology chapter, read against the
reference list, shows the list was three revisions short: consonant-stem cases, the
s-stem set, u-stems, the eu-stem plural, the -went- adjectives, the participle plural,
the infinitive, the feminine of -eus, the material adjectives and the spelling variants
were all absent. Rebuilt as reference list v3, pre-registered as Kober 0.8 with the rule
table in the CHANGELOG and a permissiveness check written first: the broader the list,
the more a shuffled corpus's own top ten will match, so the null is rerun and a v3 that
lets chance through is reported as unusable rather than adopted. The spelling rules
checked the etymological expansion: the coda rule matches; initial s- before a consonant
was never expanded. Their Linear A pages state the value-transfer caution in the
repository's own words.

## 2026-09-12 · Phase 29 · What the checks found (F-035)

No line fragments in the word types; a corpus that stops in 1985, missing the 2024
supplement and the longest Linear A text; SigLA's lines are not lines; and a third of the
alternation material Packard collected by hand in 1974 does not exist under today's
edition, three of his sign values among the casualties. The medial class he counted is
confirmed as invisible to the stem-and-ending model, 28 pairs of 29. Kober 0.9 is
pre-registered to add a medial channel and a homophone-merge sensitivity, with readings
written first.

## 2026-09-12 · Phase 30 · The answer key from the book, and the register refreshed (F-034)

Reference list v3, derived from the morphology chapter, passed the permissiveness check
written before it ran: a shuffled corpus's top ten still matches only three rules at the
99th percentile, and chance never reaches the top-three bar. On Linear B at Linear A's
size it moved "top three all grammar" to thirteen of twenty without context and fourteen
with; the bar is sixteen. The key, not the instrument, had been most of the shortfall.
The register was then refreshed against the primaries: eight rows amended with the
sources that state what we measured, and a new section H for eight assumptions
inherited from precedent without a recorded decision, two of which are Kober 0.9's
changes.

## 2026-09-12 · Phase 31 · The first spike results, and one caught null

Overnight the spikes started landing. S-003, Packard's toponym argument under a modern
null, came back "nothing", and on reading the numbers the null was wrong: it took label
identity between the scripts as fixed, and label identity is the value transfer under
test, so the null was handed most of the real count. Withdrawn, recorded in its own
result file, and rerun as S-003b with values rotated at every position, Packard's own
construction with two hundred draws. The discipline page gains the rule: a null varies
the thing under test and nothing else. The Anetaki ring's sign-by-sign edition turns out
to be forthcoming and the 2024 supplement is print only, so "more Linear A" is one book
purchase away and otherwise not available.

## 2026-09-12 · Phase 32 · The first positive result on the sound values (F-036 to F-038)

Three spikes landed. The etymological method's floor lies above the whole of Linear B:
at no size does dictionary matching separate Greek from Finnish and Sumerian by two
units (F-036). The prefix channel is the ending channel mirrored, exactly, so Linear A's
null prefix result is a corpus fact (F-037). And Packard's toponym argument, rerun with
values rotated at every position and two hundred draws, holds on both editions while a
same-size personal-name lexicon does not: Linear A words match Knossos place names
beyond chance (F-038). That is the first positive result in the repository on the
assumption every phonetic test rests on, and it is narrow, a handful of signs in a
handful of place names. It is the first spike to meet the promotion rule; Value
transfer 1.0 is pre-registered with a third wrong control the spike lacked, Pylos place
names, and is running.

## 2026-09-12 · Phase 33 · Kober 0.9: the medial channel, and the merge that closes the argument (F-040)

Packard's medial class got its channel. On the full Linear B corpus it sees variation
beyond chance, but the differing signs share a consonant only at the null's edge, and at
Linear A's size the channel sees nothing even on Greek; Linear A's own medial pairs are
at chance. The homophone merge, folding the spelling variants Ventris and Chadwick list
into their base signs, did something no context encoding did: it carried Greek at Linear
A's size past the sixteen-of-twenty bar, to eighteen. The Linear A run under that
instrument, made as part of the version, changed nothing: 101 paradigms, maximum support
two, both where they were. With the answer key from the book and the variants merged,
nothing is left in the instrument to account for the difference between the two
corpora. The closing sentence of the context line stands in its strongest form.

## 2026-09-12 · Phase 34 · The sound values get their first passed test, and Linear A passes the Indus test (F-041, F-042)

The toponym spike was rebuilt as Value transfer 1.0 with everything pre-registered: a
cited place-name list, two more wrong controls, both editions, both bandings, two seeds,
four hundred draws. It passed in every cell. Packard's argument of 1974, that Cretan
place names known from the Knossos tablets recur on Linear A tablets under the borrowed
values, now has the null it never had, and three wrong lexicons that never clear it.
The register's first assumption, that Linear A signs carry Linear B values, is amended:
tested positive for thirteen sign labels, all in the demonstrably shared set, and a
stated limit for the rest. Alongside it, the spike asking whether Linear A writes
language at all by the Indus-debate measures came back "nothing", with something worth
keeping: on the measures that survive the alphabet-size objection Linear A sits with
Greek at the same size, and the pair of numbers that would have read it as
non-linguistic is driven by its larger signary. Sproat's reversal, reproduced from a
real control.

## 2026-09-12 · Phase 35 · Two more spikes come back empty, one of them carrying a bug (F-043, Kober 0.9.1)

Reading direction and word division were the two remaining "what did we miss"
questions with a cheap test. Reversing any support type's words changes nothing on
either corpus, and the prefix-ending mirror holds on Linear A as it did on Linear B.
Barber's boundary test, the one she designed in 1974 and nobody ran on Linear A, puts
Linear A at the bottom of Greek's own range at the same size: no sign that the dividers
under-divide, and no power to say they are right. The reading-direction spike also
found that the null draws were not reproducible across processes, because the length
groups were visited in set order. Fixed as Kober 0.9.1 with nothing redefined; the old
results reproduce in distribution, which is what they were ever read as.

## 2026-09-12 · Phase 36 · The Egyptian question (F-044)

Ru's two "crazy" questions got their spike. Is Linear A one sign per word? No: words
average two to three signs against exactly one for the Chinese calibration case, and
the signary grows far too slowly. Is it Egyptian-like? The spike's pooled distance said
Egyptian was nearest on both editions, and the decomposition says why: six of the ten
statistics track signary size, Linear A's signary is larger than Linear B's at the same
size, and on the three statistics that measure order Linear A is no nearer Egyptian than
Ugaritic, Linear B or Sumerian. The same lesson as the Indus measures a few hours
earlier, from the other direction. Any future statistic on Linear A's sign sequences
has to be checked for inventory dependence before it is read.

## 2026-09-12 · Phase 37 · The edition concordance (F-045)

The two editions of Linear A were known to disagree on most documents (F-023). The
concordance says where: mostly in how the two loader chains tag words against
logograms, and, among the sign readings, in the same sign wearing two names. The text
itself differs in about eighty documents. Two gotchas for corpus-sources: the label
aliases, and ten tablets sited at two different places by the two chains. This matters
for the supplement work in the morning: its sign numbers have to be reconciled with
the loader's labels before a single word type is compared, or the join undercounts.

## 2026-09-12 · Phase 38 · Kober's third assumption stays untested (S-008)

Are listed words nouns? On Linear B the cheap proxy sees only that listed words recur
more and are less often one-offs, which is a fact about lists, not about parts of
speech; the ending-diversity signature does not separate, and the rule-based proxy for
"not a noun" never fired. Her Assumption 3 needs a part-of-speech key, which means the
DĀMOS annotation, still parked. Recorded on A-111 and nowhere else.

## 2026-09-12 · Phase 39 · The floor moves with the instrument (F-046)

Ru's observation that discovery adds about eleven signs a year made the question
sharp: if the floor cannot be met by finds, can it be met by the instrument? The sweep
under the current instrument, run in minutes where the first took hours, says partly.
On the sweep's own criterion the floor is 1,250 word types, down from 1,875, and at
Linear A's size Greek passes fifteen of twenty, one short of the bar; on the strict
top-three bar the floor is 750, below Linear A's size. Nothing new was read; the answer
key and the merge did it. The claim about "twice as much text" is rewritten to name the
instrument, and the guide with it. The caution that travels: the merge is knowledge the
decipherment gave us, and Linear A has no such list.

## 2026-09-12 · Phase 40 · The supplement, transcribed and joined, corrects the corpus story (F-035 correction)

The sign index of the 2024 supplement was transcribed as 619 rows and 24
complete word types. Joined to the loaded corpus by identifier, the surprise was the
other way round: most of it was already there. The chain we load carries Younger's
readings of the post-1985 finds, so the "1985 corpus" written into F-035 on Friday
afternoon was wrong, and is withdrawn. What the supplement adds to this repository is
a few dozen documents and four word types, two of them sharing a stem with a known
word. Ru's arithmetic about the rate of discovery is unchanged; what changed is that
the repository already had most of what was discovered.

## 2026-09-12 · Phase 41 · The supplement, measured against the corpus (F-047)

The rest of the book was read in the morning: preface, introduction, the four
concordances, the doubtful list, and every inscription page. The tablets turned out to
be printed as glyph copies with French apparatus, not Latin values, so the index
remains the text and the entry pages are the context. The Concordance générale, joined
to the loader, gave the number that ends the question: 89 of the supplement's 107
documents are already in the loaded chain, 18 are not, and those 18 carry four complete
word types. A sensitivity is pre-registered to put the four through the toponym test
and the paradigm count with the expectation, written first, that nothing moves.

## 2026-09-12 · Phase 42 · The supplement closed (F-048)

The first sensitivity appended the four complete word types from the eighteen absent
documents and found every one already attested elsewhere in GORILA. The second
appended the four types the loader lacks and found them to be word divisions: two
Petras documents where the supplement writes two words and the loader one. Neither run
moved a toponym count, a matched pair, a paradigm count or a maximum support. The
supplement item that opened on Friday evening as "more Linear A" closes on Saturday
noon as a complete local transcription of 107 documents, a corrected account of what the
loaded chain already holds, and two divider variants. The Anetaki ring is the one
addition still outside the corpus.

## 2026-09-12 · Phase 43 · The afternoon's loose ends

Four things were left after the supplement, and each closed in its own way. The DĀMOS
morphological annotation, the one remaining lever inside the instrument, is unexported
and unfinished; only a request to its curator could get it, and that is Ru's decision.
The Anetaki ring's article names signs but prints no text; its edition is forthcoming.
The prior-art search for the toponym claim found nobody has run it with a null and a
wrong lexicon; Packard stays the precursor. And the instrument's Linear A list, read
beside the field's proposals, agrees with them in one place, the a-/ja- prefix, at the
noise floor. A brief for a specialist reader is written. What the repository can do on
its own is, for now, done; what it needs next is a reader and a new kind of text.

## 2026-09-12 · Phase 44 · The last two spikes (F-049, S-007)

The "go ahead" list ended with the two spikes that cost the most. Structural profiles
against five respelled languages came back with Linear A nearest respelled Greek and
real Linear B, and the reason is genre: those two are running text and the rest are
dictionaries, which have no endings to vary. What survives is that Linear A's word list
behaves like text of an inflecting language and not like a lemma list, on both
editions, which is F-019 said another way. The model-as-Kober spike showed a frontier
model finds the same stems with the labels hidden, so it analyses rather than
remembers, and that a reader's paradigm, one stem with several endings, is exactly what
no null can tell from chance; it produced ten on a shuffled list as readily as on the
real one. Both are "nothing" by their briefs, and both are worth having asked. The
list is empty; what is left needs Ru, a reader, or a new kind of text.

