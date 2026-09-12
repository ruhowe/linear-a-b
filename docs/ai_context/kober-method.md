# The Kober method

Read this first if you are building, running or reading anything under `src/kober/`.
This file describes the instrument. Results live in `FINDINGS.md`; protocol versions in
`CHANGELOG.md` under "Kober method"; assumptions A-033 onward in `ASSUMPTIONS.md`. Names
follow `terminology.md`.

## What the method is

Find grammatical structure from sign patterns alone, before any sound value is assigned.
Alice Kober did this on Linear B between 1943 and 1950 with index cards. She noticed
that certain words recurred in three forms sharing the same opening signs and differing
in the last one or two: her "triplets", for example the word later read as Amnisos in
the forms a-mi-ni-so, a-mi-ni-si-jo, a-mi-ni-si-ja. Three things followed, none needing
a sound value. The language inflected by ending. The sign at the join changed with the
ending (-so against -si-), so the script was syllabic and those two signs shared a
consonant and differed in vowel. Collecting such pairs gave a grid of signs organised by
shared consonant and shared vowel. Ventris filled the grid with values in 1952. The
method is the one part of the decipherment that transfers to Linear A, because it uses
sign identity and position only.

The literature calls it internal, structural, combinatory or morphological analysis. The
computational relatives are unsupervised morphology and paradigm induction. pyaegean
already ships three exploratory tools of this kind (`aegean.analysis.morphology`,
`segmentation`, `edge`), ported from the Linear A Research Workbench. None of them has a
null model or a Linear B positive control. That is what this instrument adds.

## What Kober actually did, from her papers

Read in full 2026-09-11 (`docs/works/kober1946.md`, `kober1948.md`). Her method is seven
numbered assumptions. The ones the instrument does not encode: nouns listed together on
one tablet, each before an ideogram and a number, are in the same case (Assumption 4);
an ending recurring across one tablet's list is that case's ending (6); a variant counts
only if at least two words show it *and* the variants occur in lists homogeneous in
ending (7). Her third case rested on position on a tablet type. Her corpus was under
750 word types. Her triplets were the ethnic adjectives (-so / -si-jo / -si-ja), which
the reference list below did not cover until Kober 0.6. Of the three context encodings
tried here, word slot (0.4, F-026) hurt, entry role as a tie-break (0.5, F-029) helped
a little, and list-level homogeneity, hers, held as a corpus fact (F-030) and, as a tie-break
(0.7, F-032), changed nothing at the top. The context line is closed with three
measured encodings; every version stays as an opt-in flag with the default path pinned.

## What has already been done on Linear A by hand

The Linear A literature has structural findings that any computational run should
recover or explain why not: a prefix alternation a-/ja- on the libation-formula word
(j)a-sa-sa-ra-me (Monti 2022, Duhoux); a small set of recurring endings on the formula
words (Thomas 2020; Davis 2014); fixed word order in the formula (Davis 2013); the
transaction terms ku-ro and ki-ro in fixed slots. These are the field's own Kober-method
results. They are not used to tune anything here; they are the check that the instrument
sees what careful eyes saw.

## The instrument, version 0.1

**Unit.** Word types, not tokens. A word is a run of signs between dividers as the
edition gives it (A-002 for Linear A; DĀMOS tokenisation for Linear B). Only tokens with
`kind WORD` and `status CERTAIN`, normalised by `linearb_restore.normalise.normalise_text`
so that underdots and span brackets do not split one sign into two labels (the sizing
run below found TO and ṬỌ counted as different signs before normalisation). Words of two
signs or more.

**Stems and endings.** A stem is a word-initial sequence of at least two signs; an ending
is the remainder, of one or two signs. Every word of length n contributes candidate
splits at n−1 and n−2 (where the stem keeps at least two signs). A **paradigm** is a stem
attested with two or more distinct endings, each as a complete word type. An
**alternation** is an unordered pair of endings; its **support** is the number of stems
attested with both. A prefix channel runs the same procedure mirrored: a base is a
word-final sequence of at least two signs and a prefix is the one or two signs before
it. Version 0.1 reports the two channels separately and never merges them.

**Statistics.** Two, each with its own null.

1. *Paradigm count*: the number of stems with two or more endings, at each stem length.
2. *Alternation support*: for each alternation, the number of stems supporting it; the
   ranked list is the output Kober read by eye.

**Nulls.** The protocol 1.0 null, permuting sign identities within frequency bands, does
not apply. A consistent relabelling of signs preserves every shared prefix exactly, so
the paradigm count would be identical under the null. The nulls here destroy structure
while holding marginals fixed, in two grades.

- *N1, position-matched shuffle*: within each word-length class, the signs at each
  position are shuffled across words. Preserves the length distribution and the
  positional sign frequencies (in particular the word-final sign distribution, which is
  skewed in Linear B). Destroys shared prefixes and stem–ending pairing alike. This is
  the null for the paradigm count.
- *N2, ending shuffle*: stems are held fixed and endings are shuffled among words of the
  same length. Preserves which stems exist and how many words each stem heads, so the
  paradigm count is nearly unchanged by construction. Destroys which ending goes with
  which stem. This is the null for alternation support: it asks whether the *same pair*
  of endings recurs across many stems more often than chance pairing would produce.
  Kober's triplets are exactly this signature.

Each null is drawn 200 times; the statistic's percentile under the null is reported, and
for alternation support the null distribution of the *maximum* support is used, so the
top of the ranked list is judged against the top of a null list, not against a typical
entry.

**Positive control and criterion, Linear B.** Greek inflects by suffix, so Linear B must
show paradigms and its top alternations must be Greek grammar. The reference list of
alternations that count as grammar is fixed here, before the run, from Documents in
Mycenaean Greek (Ventris and Chadwick 1973, chapter on morphology; verification P, see
`docs/works/ventris_chadwick1973.md`):

| alternation | grammar |
|---|---|
| -o / -a on the same consonant (e.g. -to/-ta, -ro/-ra, -no/-na) | masculine and feminine of o/ā-stem nouns and adjectives |
| -jo / -ja, -i-jo / -i-ja, -si-jo / -si-ja, -wi-jo / -wi-ja | adjective and ethnic suffix, masculine and feminine |
| -o / -o-jo | nominative and genitive singular, o-stems |
| -o / -o-i, -a / -a-i | singular and dative plural |
| -a / -a-o | feminine and masculine ā-stem genitive |
| -u / -we / -wo, -e-u / -e-we / -e-wo | nominative, dative and genitive of eu-stems |
| -e / -e-i, -e / -e-o | consonant and s-stem case forms |
| -me-no / -me-na | middle participle, masculine and feminine |
| -e / -si | third person singular and plural of verbs |
| X / X-qe, X / X-de, X / X-te, X / X-pi | enclitic "and", allative, ablative and instrumental particles |

The criterion, pre-registered: **on Linear B the paradigm count at stem length two or
more exceeds the 99th percentile of N1, the maximum alternation support exceeds the 99th
percentile of N2, and at least seven of the ten best-supported ending alternations are
in the reference list.** The prefix channel on Linear B is expected to be weak, since
Greek prefixes little beyond the augment and preverbs; a strong prefix result on Linear B
would indicate the channel finds something other than grammar and would need explaining
before the prefix channel is read on Linear A.

Readings, written before the result exists, are in `CHANGELOG.md` under Kober 0.1.

**Reading rule found in the first run (F-016).** The prefix channel's base is a
word-final run of signs, so a shared base is a shared suffix, and the prefix channel's
paradigm count under N1 measures suffix sharing again. Only the prefix channel's N2
support statistic is a prefix statistic (A-047). Read prefixes by N2 support alone.

**Stage 2, the grid (pre-registered in CHANGELOG, gated open by F-016; 0.1 pooled all pairs, 0.2 anchors them to the top ten alternations, 0.3 takes the top ten alternations' own first signs directly rather than their stems' pairs, stage 1 unchanged throughout).** For a stem with endings of
different length, the first sign of each ending is a bridging pair: in X-so / X-si-jo the
pair is (so, si). Pairs supported by several stems are hypothesised to share a consonant.
On Linear B the hypothesis can be checked against the known values: the fraction of
supported bridging pairs that share a consonant under Ventris's values, against the same
fraction computed under N1. This is a value-free recovery of the Kober grid and the
strongest positive control available, because it tests the inference Ventris built on
rather than a list of endings. It runs only if stage 1 meets its criterion.

## Sizing, done read-only before the design was frozen

Counts of word types and of stems with two or more endings, unnormalised labels, no null.
Recorded so that the criterion above is read knowing what had been seen when it was set.

| corpus | word types ≥ 2 signs | stems ≥ 2 signs with ≥ 2 one-sign endings | best-supported alternation |
|---|---:|---:|---|
| Linear B | 4,263 | 516 of 2,977 | -ja / -jo, 49 stems |
| Linear A | 988 | 51 of 547 | two alternations at 2 stems, all others at 1 |

The Linear B top alternations were visible in this sizing output (-ja/-jo, -u/-we,
-ta/-to, -u/-wo, -we/-wo, -ra/-ro, -si-ja/-si-jo, -me-na/-me-no). The reference list
above was written from Mycenaean grammar, not from that output, but it was written after
the glimpse and the CHANGELOG entry says so. The criterion's null-exceedance parts and the
stage 2 grid were not glimpsed.

The Linear A row decides how item 4 of the TODO must be read: at this corpus size no
ending alternation is supported by more than two stems, so the ranked alternation list
cannot be read on Linear A at all. Only the paradigm count against N1 and the prefix
channel can be, and the pre-registration for the Linear A run has to say that before it
runs.

## Version 0.4, context-aware (pre-registered in CHANGELOG; not yet built)

Kober did not rank every alternation in the corpus; she compared forms of the same word
in the same slot on parallel tablets. 0.4 encodes the slot. Each word token gets a
context class: (support type of the document, line-initial or not, kind of the next
token on the line). A word type takes its dominant class. A stem supports an alternation
only when its two words share a class. Both nulls are stratified by (length, class) so
the context distribution is preserved under the null and cannot pass as signal. The
criterion is fixed from F-025: strict top three all on the reference list, sixteen of
twenty tablet-model subsamples at 988, with the criterion's chance rate re-measured
under the stratified null. It is calibrated on Linear B first and runs on Linear A once
only if it passes. Assumptions A-075 to A-078.

## The measured floor

`scripts/kober_floor_sweep.py` locates the corpus size at which stage 1's criterion is
met in sixteen of twenty Linear B subsamples, under two subsampling models. The tablet
model (documents removed) is the realistic one. Numbers in FINDINGS F-022; any Linear A
comparison must use the tablet-model range at the matching size, not the type model.

## The grammar-match null (TODO item 8, prerequisite 1)

Part 3 of the stage 1 criterion ("seven of the top ten on the reference list") had never
had a null of its own: `reference.is_grammar`'s rules are permissive, so a shuffled
corpus's own top-n can match some by chance. `nulls.py::grammar_matched_count(support, n)`
grades the top-n alternations by support (ties at the n-th place included, A-053, via
`paradigms.top_n_alternations_with_ties`) against `reference.is_grammar`; `run_n2`'s
`track_grammar_match` computes it, for n in (3, 5, 10), from the *same* per-draw support
mapping the N2 ending null already builds for `max_support`/`tenth_support` — no extra
draws, so every other statistic in a report is unaffected. Every report now carries this
under `ending_channel.grammar_match_null`, one `NullDistribution`-shaped block per n.
`top_n_alternations_with_ties` moved from `grid.py` to `paradigms.py` so `nulls.py` could
use it without a cycle (`grid.py` imports `nulls.py`); `grid.py` re-exports the name.

`kober_run.py --results-dir DIR` writes the results JSON under `DIR` instead of
`results/`, so a rerun for a different purpose (this null; a future recalibration) does
not overwrite the original file for the same corpus/seed/tag — the filename itself is
unchanged. `results/kober-grammar-null/` holds the full-Linear-B (seeds 0, 1) and the
forty 988-word-type-subsample (twenty type-model, twenty tablet-model, F-022's own
document counts) reruns; `scripts/kober_precision_table.py` reads them and scores
candidate precision criteria per model into `results/kober-precision-table.json`/`.md`
without choosing one (that choice is Kober 0.4's).

**The ties-included top-n inflates the null, so a strict variant sits beside it
(A-072).** At 988 word types many alternations tie at low support, so the ties-included
"top ten" (A-053) can hold dozens of alternations — the ties-included top-10 set's own
size (`ties_included_top_n_size`) has a null mean median of 349 on the type-988 model at
n=10, against a real median of 14 — and the ties-included null's matched count is
inflated by the tie set's size, not by grammar, exactly as CHANGELOG's "Null rate of the
grammar match" entry set out to measure. `nulls.py::grammar_matched_count_strict(support,
n)` grades a strict cut at exactly n (support descending, then the ending pair in sorted
lexicographic order — `paradigms.ranked_alternations`, the same ranking
`top_10_matched_to_rule` already uses) against `reference.is_grammar`, applied identically
to the real corpus and to every N2 draw's own support mapping; `run_n2` computes it from
the same per-draw support the ties-included variant already uses, so no extra draws. Every
report now also carries `ending_channel.grammar_match_null_strict` (same fields as
`grammar_match_null`, one block per n) and, inside each n's block,
`ties_included_top_n_size` (`{mean, real_value}` only, not a full percentile spread) so
the two readings of "top-n" sit side by side. The strict real value at n=10 equals
`top_10_matched_to_rule` by construction (both are the same strict cut) — confirmed on
all 42 reruns. `grammar_match_null_strict` is ending-channel only, following A-070's
scoping of the ties-included block. `scripts/kober_precision_table.py` now scores
criterion (a) under both readings and reports the median ties-included top-10 set size
(real and null mean) per model, still choosing neither.

## Version 0.5, entry-role tie-break (CHANGELOG "0.5"; stage 1 unchanged)

Motivated by F-028: on Linear B, two forms of a real paradigm share an entry role
(`scripts/kober_entry_roles.py`'s definition, now `kober.roles.word_roles`) more often
than chance, weakly, and the effect concentrates in the grammatical alternations. 0.5
changes nothing about the paradigm count, alternation support, or either null — only the
*ordering* used for the strict top-n (A-072's tie-break). An alternation's role-sharing
count is the number of its supporting stems whose two forms (the whole words, not just
the endings) share at least one role; `paradigms.ranked_alternations` takes this as an
optional key and sorts by support descending, then role-sharing count descending, then
the existing lexicographic tie-break. Default off: omitting the key reproduces the 0.3
ordering exactly, byte for byte.

Under the N2 ending null, roles stay attached to word types rather than travelling with
a shuffled ending (A-098): a draw's synthetic stem+ending recombination is looked up in
the same fixed role table the real corpus uses, so it carries roles only when that exact
sign sequence happens to be a real, role-bearing word. `nulls.run_n2`'s `word_roles`
parameter computes the role-tiebreak-ordered strict grammar-match null and the
top-three-all-matched chance rate from the *same* N2 draws already used for the
ties-included and strict (A-072) variants — no extra randomness.

Criterion, identical to 0.4's for comparability: strict top three all on the reference
list in at least sixteen of twenty tablet-model subsamples at 988 word types, chance
rate at or below one in twenty per subsample. Calibration in `results/kober-role-tiebreak/`
(full corpus seeds 0/1; twenty type-model and twenty tablet-model subsamples at 988,
same document counts as the F-022 floor sweep); `scripts/kober_tiebreak_table.py` scores
it per model into `results/kober-tiebreak-table.json`/`.md` beside the 0.3 baseline
(`results/kober-precision-table.json`) and the 0.4 result (`results/kober-context-table.json`),
choosing nothing. Numbers are FINDINGS' to state.

## Version 0.6, reference-list revision (CHANGELOG "0.6"; stage 1 and stage 2 untouched)

Rule 11, *ethnic derivation* (`reference.py::_rule11_ethnic_derivation`), covers the
pattern kober1946 built Cases I to III on and F-016's note found missing: X-so/X-si-jo,
X-so/X-si-ja, X-to/X-ti-jo, X-to/X-ti-ja. `reference.is_grammar(e1, e2, version=2)` tries
rules 1 to 10, then rule 11 last; `version=1` (the default, every existing call site)
is byte-identical to before 0.6. `nulls.grammar_matched_count`/`grammar_matched_count_strict`,
`nulls.run_n2`/`run_nulls`, `report.build_report` and `kober_run.py --reference-version
{1,2}` thread this version through to the grammar-match null alone; stage 1's paradigm
count, alternation support and each top-20 alternation's own `rule` field always use
`is_grammar`'s default (`version=1`), so a `--reference-version 2` rerun's stage 1 stays
bit-identical to the same corpus/seed/subsample's existing file (A-107).

Every existing results file is rescored, not rerun: `scripts/kober_rescore_reference.py`
adds a `reference_v2` block (each channel's top-20 alternations regraded at version 2,
and the strict top-3/5/10 matched counts under it) to every file with an `ending_channel`
under `results/` (idempotent; A-106 fixes the exact scope and the null-not-rescorable
wording). The grammar-match null itself cannot be rescored from a stored summary, so
0.6's own null is rerun once, `--reference-version 2` into `results/kober-grammar-null-v2/`,
for the full corpus (seeds 0, 1) and the forty 988-word-type subsamples
`results/kober-grammar-null/` already covers. `scripts/kober_reference_v2_table.py` scores
both, per model, into `results/kober-reference-v2-table.json`/`.md` (v1-vs-v2 strict top
three and at-least-two-of-three, v2's null-exceedance and chance rate, and the full
corpus's top fifty alternations gaining a rule under v2 — A-108 fixes what "chance rate"
means here and how the top fifty, past the stored top-20's depth, is obtained), choosing
no criterion. Numbers are FINDINGS' to state.

## Version 0.7, list-support tie-break (CHANGELOG "0.7"; stage 1 unchanged)

A fourth ordering key, after role-sharing (0.5): an alternation's *list-support* count
is the number of supporting stems whose two forms both satisfy kober1946's Assumption 7
(each form's own final sign is in the set of modal final signs of the eligible (>= 3
listed words) documents it occurs as a listed word in — `kober.lists.homogeneous_forms`,
moved from `scripts/kober_list_homogeneity.py`, A-101, A-116). `paradigms.ranked_alternations`
takes `list_support` alongside `role_sharing`: support descending, then role-sharing
descending, then list-support descending, then lexicographic. Both keys default `None`,
so 0.3 (neither) and 0.5 (role-sharing alone) reproduce byte-identically (A-118); the
key is built as a variable-length tuple rather than a fixed one with a sentinel, which
is what makes that reproduction exact by construction rather than by coincidence.

Under N2, list-support is *recomputed per draw* rather than looked up by literal word
identity the way roles are (A-098): "a draw's word gets the draw's ending; its documents
and their modal final signs are recomputed from the shuffled words." `nulls._n2_draw_and_map`
returns the draw's own `{original word: drawn word}` map alongside the usual drawn word
set (free from the same shuffle call, A-116); `kober.lists.homogeneous_forms_from_listings`
takes an optional `word_map` and substitutes every real listed word's contribution to its
document's modal-sign count with its drawn counterpart before rebuilding the per-word
mapping. The strict grammar-match null under this ordering is recomputed at n in (3, 5,
10) at *both* reference versions (1 and 2, Kober 0.6), and so is the "strict top three all
matched" chance rate, both versions — `N2Result.grammar_match_list_tiebreak_v{1,2}`,
`top_three_all_matched_chance_rate_list_tiebreak_v{1,2}`.

`kober_run.py --list-tiebreak` (implies `--role-tiebreak`, A-120) appends a `list_tiebreak`
block (`report.ListTiebreakReport`) with the real strict top ten and top three (endings,
support, role-sharing count, list-support count, `rule_v1`, `rule_v2`), the null blocks
and chance rates at both reference versions, and `positions_changed_vs_0_5` — compared
against the 0.5 (role-tiebreak-only) ordering, not the plain 0.3 ordering 0.5's own
`positions_changed_vs_0_3` uses (A-121). File-level `protocol_version` "0.7".

Criterion: identical to 0.4 and 0.5, strict top three all grammar in sixteen of twenty
tablet-model subsamples at 988, chance rate at or below one in twenty. Calibration in
`results/kober-list-tiebreak/` (full corpus seeds 0/1; twenty type-model and twenty
tablet-model subsamples at 988, same document counts and seeds as the F-022 floor sweep
and the 0.5 calibration); `scripts/kober_list_tiebreak_table.py` scores it per model,
at both reference versions, into `results/kober-list-tiebreak-table.json`/`.md` beside
the 0.3 baseline (`results/kober-precision-table.json`), the 0.5 result
(`results/kober-tiebreak-table.json`, version 1 only), and the 0.6 result
(`results/kober-reference-v2-table.json`, the plain 0.3 ordering scored at both
versions — A-122), choosing nothing. Numbers are FINDINGS' to state.

## Version 0.8, reference-list v3 (CHANGELOG "0.8"; stage 1 and stage 2 untouched)

`reference.py` gains `version=3`: rules 1 to 11 unchanged, plus eleven new rules
(12 to 22) drawn from Ventris and Chadwick 1973 chapter III §6 and
Word-formation (`docs/works/ventris_chadwick1973.md`, V) — the consonant-stem
case and suffix endings, the s-stem set, the u- and eu-stems, the -went-
adjectives, the -o/-o-te participle, the infinitive, the feminine of -eus,
the material-adjective triplet and the -a2/-ja spelling variants the v1/v2
list lacked. `version=1` and `version=2` stay byte-identical; stage 1 (paradigm
count, alternation support, each top-20 alternation's own `rule` field) always
uses `is_grammar`'s default (`version=1`), so a `--reference-version 3` rerun's
stage 1 is bit-identical to the same corpus/seed/subsample's existing file,
matching A-107's pattern.

**Rule order is fixed and produces disclosed dead code (A-124).** Four of the
eleven new rules — 16 (eu-stem plural), 17 (-went-), 18 (participle plural),
19 (infinitive) — are fully preempted by an earlier, broader rule (10
particle, 13 consonant-stem suffix, 14 s-stem) whenever they would fire, so
they never surface as the reported rule name on any input; the alternations
they were written for still match a rule under v3, just not that one. Rule 22
(spelling variant)'s "differ only as JA / A2" clause needs equal-length
endings, so it does not reach a-ke-ti-ra2 / a-ke-ti-ri-ja (A-123), one sign
against a two-sign spelling.

**The rescore, the v3 null and the table (A-037).** `scripts/kober_rescore_reference.py`
now writes both `reference_v2` and `reference_v3` blocks (idempotent, v2
untouched) to every existing results file. `nulls.py::run_n2` gained two more
statistics, computed from the same N2 draws every other grammar-match variant
already reuses (no extra randomness): `rule_firing_counts_null` (a Counter of
rule names among each draw's own strict top ten, summed over all draws — "the
rules that fire most under the null") and `top_three_all_matched_chance_rate`
(the plain-ordering companion to the role/list-tiebreak chance rates, not
tracked before 0.8 since only those two tie-break orderings tracked a per-draw
"all three matched" flag). Both are ending-channel only and graded at whatever
`reference_version` the run used (A-070's scoping). `kober_run.py --reference-version 3`
reruns the strict grammar-match null for the full corpus (seeds 0, 1) and the
forty 988 subsamples into `results/kober-grammar-null-v3/` (stage 1 verified
bit-identical to `results/kober-grammar-null/`). `scripts/kober_reference_v3_table.py`
scores v1/v2/v3 strict top-three and at-least-two-of-three per model, the v3
null's own 99th percentile and chance rate, the summed rule-firing counts, and
the full corpus's top fifty gainers (both the v2-to-v3 increment and the total
gain since v1) into `results/kober-reference-v3-table.json`/`.md`, choosing no
criterion — CHANGELOG "0.8"'s own bar (null p99 at n=10 over 3 on the full
corpus, or the 988 chance rate over one in twenty in more than two subsamples)
is quoted there, not applied here. Numbers are FINDINGS' to state.

## The floor under the current instrument (F-046)

The floor is a property of instrument and criterion, not of the method. Measured on the
tablet model with the bar of sixteen in twenty: 0.3 instrument, v1 key, three-part
criterion, 1,875 (F-022); 0.9.1 with v3 key and homophones merged, three-part criterion,
1,250; same, strict top three, 750 (F-046). At 988 the current instrument meets the full
criterion in fifteen of twenty. Quote the instrument with the number. The merge uses the
decipherment's knowledge of which signs are variants, so the merged floor describes Greek
with that help; Linear A has no equivalent list. `scripts/kober_floor_sweep.py` takes
`--merge-homophones`, `--reference-version` and `--results-dir`; its default path
reproduces the 2026-09-11 sweep. `top_10_matched_to_rule` in results files is always
graded under v1; grade at v3 from the stored top twenty, as the sweep summary does.

## Version 0.9.1, null draws reproducible across processes

Before 0.9.1 a null draw with a given seed could differ between two processes, because
`nulls.py` visited the length groups in set-iteration order (hash-seed dependent) while
consuming one random stream. Found by spike S-013; fixed by sorting the group order.
Nothing in any statistic changed; results files older than the fix carry null
percentiles that reproduce in distribution, not bit for bit. Regression pins are on
real values and are unaffected. See CHANGELOG "0.9.1" and A-057.

## Version 0.9, medial channel and homophone merge (CHANGELOG "0.9"; A-140 to A-146)

Two additive changes; stage 1 (ending and prefix channels) is untouched.

**Medial channel, `src/kober/medial.py`.** A third channel, beside ending and
prefix: for word types of three or more signs, a pair of words identical
except at one interior position (index 1 to n-2, never the first or last
sign) is a medial pair, grouped by the unordered pair of differing signs into
an alternation whose support is the number of such word pairs (A-140). This
is Packard's third alternation class, "first and third signs identical,
second differs" (his three-sign case), generalised to any interior position
on a word of any length. Found without O(n^2) comparison via a masked-bucket
grouping per length and per interior position (A-141). Two nulls: N1 (the
same full-word position shuffle stage 1's paradigm count uses) for the pair
count; N3, a new shuffle that permutes only the interior-position columns
within a length class and leaves each word's own first and last sign (the
"flanking signs") fixed, 200 draws, for the maximum support and the
consonant-sharing fraction of the top twenty pairs (a strict cut, A-143), all
from the same N3 draws. Both nulls run under their own independent stream
keys (`medial_n1`, `medial_n3`, A-142), so a `--medial` run leaves every
other block's draws bit-identical to the same seed's run without it. The
consonant-sharing answer key on Linear B is `values.consonant_of`, consulted
only after the ranking is fixed, beside its chance fraction (sum of squared
consonant proportions among the top twenty's scored signs) exactly as stage
2 reports it.

**Homophone merge, `--merge-homophones`.** A sensitivity on sign identity,
not a new statistic: `words.extract_word_types(..., merge_homophones=True)`
maps a2->A, ai2->AI, pa2->PA, pu2->PU, ra2->RA, ra3->RA, ro2->RO, ta2->TA
(Ventris and Chadwick 1973 section 13) at extraction, before the
two-or-more-sign filter; every channel, null, grid and medial statistic then
runs unchanged on whichever word set results (A-144). Default off. Recorded
at file level (`KoberReport.merge_homophones`, A-145); the resulting
(smaller-or-equal) word-type count is the "merged type count".

File-level `protocol_version` becomes "0.9" when either `--medial` or
`--merge-homophones` is used, or both (A-146). Pins:
`tests/test_kober_regression_09.py` (medial real values and merged type
counts on both corpora, against `results/kober-09/` and
`results/kober-09-merged/`); the 0.1 pins (`test_kober_regression.py`) are
untouched. Numbers are FINDINGS' to state.

## What this instrument cannot do

It cannot name a language. It cannot tell inflection from derivation, or a case ending
from a recurring second element of compound names. It finds suffixal and prefixal
structure only; infixing or vowel-change morphology is invisible to it. On Linear A it
depends on the transcription chain's sign identities (which marks are the same sign),
though not on their values (A-034). A positive result on Linear B shows it finds suffixal
grammar where suffixal grammar exists, which is all a positive control can show (A-040).

## Code layout, planned

```
src/kober/
  words.py       # word types from a corpus, normalised, CERTAIN only; counts pinned by tests;
                  # optional merge_homophones (Kober 0.9, A-144), default off
  context.py     # Kober 0.4: per-token context class, word type's dominant class, class census (A-075, A-079 to A-083)
  paradigms.py   # splits, stems, endings, prefixes; paradigm count; alternation support;
                  # context-restricted channel (build_channel_context_restricted, A-076)
  nulls.py       # N1 position-matched shuffle, N2 ending shuffle; seeded; stratified
                  # (length, class) N1/N2 for Kober 0.4 (A-084); strict-top-three chance rate;
                  # rule_firing_counts_strict, N2Result.rule_firing_counts_null and
                  # .top_three_all_matched_chance_rate (Kober 0.8, ending channel only);
                  # N3 interior-position shuffle for the medial channel (Kober 0.9, A-142)
  grid.py        # stage 2 bridging pairs; consonant check against known values (Linear B only)
  medial.py      # Kober 0.9: medial channel, word pairs identical except at one interior
                  # sign; N3 null lives in nulls.py (A-140 to A-143)
  reference.py   # the Linear B reference alternation list above, as data; is_grammar
                  # (e1, e2, version=1|2|3), rule 11 (Kober 0.6) gated behind version=2,
                  # rules 12-22 (Kober 0.8, A-123, A-124) gated behind version=3
  roles.py       # Kober 0.5: word_roles(documents), entry segmentation (moved from
                  # scripts/kober_entry_roles.py, A-092 to A-097)
  lists.py       # Kober 0.7: listed words, per-document modal final sign,
                  # homogeneous_forms(documents) (moved from
                  # scripts/kober_list_homogeneity.py, A-101 to A-104, A-116, A-117)
  report.py      # markdown and JSON, aggregate numbers only; per-block version stamps (A-090);
                  # KoberReport.reference_version (Kober 0.6, A-107), default 1;
                  # ListTiebreakReport (Kober 0.7, A-121); KoberReport.merge_homophones and
                  # build_medial_report/render_medial_markdown (Kober 0.9, A-145, A-146)
scripts/kober_run.py   # --corpus damos|lineara|sigla --stem-min 2 --perms 200 --seed 0
                        # --allow-lineara gates both lineara and sigla (A-066)
                        # --restrict-to-shared-with lineara|sigla: A-002 edition-shared-types run
                        # --results-dir DIR writes under DIR instead of results/
                        # --context: Kober 0.4, appends a context block (A-085: ending channel only)
                        # --role-tiebreak: Kober 0.5, appends a role_tiebreak block (A-098, A-099)
                        # --reference-version 1|2|3: Kober 0.6/0.8, grades the grammar-match null
                        #   only (A-107); 3 also grades rule_firing_counts_null and
                        #   top_three_all_matched_chance_rate (Kober 0.8)
                        # --list-tiebreak: Kober 0.7, appends a list_tiebreak block; implies
                        #   --role-tiebreak (A-120)
                        # --medial: Kober 0.9, appends a medial block (A-140 to A-143)
                        # --merge-homophones: Kober 0.9, sensitivity at extraction (A-144);
                        #   either flag bumps protocol_version to 0.9 (A-146)
scripts/kober_precision_table.py   # reads results/kober-grammar-null/, scores
                        # candidate precision criteria per model (TODO item 8, prereq 1/2)
scripts/kober_context_table.py     # reads results/kober-context/, scores Kober 0.4 per model
scripts/kober_tiebreak_table.py    # reads results/kober-role-tiebreak/, scores Kober 0.5 per
                        # model beside the 0.3 and 0.4 numbers
scripts/kober_rescore_reference.py # Kober 0.6/0.8: adds reference_v2 and reference_v3 blocks
                        # to every existing Kober results file under results/ (A-106), no rerun
scripts/kober_reference_v2_table.py # Kober 0.6: v1-vs-v2 per model from results/kober-grammar-null/
                        # and results/kober-grammar-null-v2/, plus the full corpus's top 50 (A-108)
scripts/kober_reference_v3_table.py # Kober 0.8: v1-vs-v2-vs-v3 per model from
                        # results/kober-grammar-null/ and results/kober-grammar-null-v3/, the v3
                        # null's own p99 and chance rate, summed rule-firing counts, and the full
                        # corpus's top 50 gainers (A-123, A-124)
scripts/kober_list_homogeneity.py  # read-only diagnostic (F-030); now a thin caller of
                        # kober.lists for listed words and modal-sign logic
scripts/kober_list_tiebreak_table.py # Kober 0.7: reads results/kober-list-tiebreak/, scores
                        # per model at both reference versions beside the 0.3, 0.5 and 0.6
                        # figures (A-122)
```

Nothing derived from the corpora is written inside the repository by the Kober line.
Word lists go to `~/.cache/linear-a-b/kober/`. The repository's one exception, the
value-transfer test's readings, is in `LICENSE.md` and does not apply here.

**SigLA (A-002, "Segmentation sensitivity on Linear A" in CHANGELOG).** `sigla` is a
second Linear A edition with its own word division (`aegean.load("sigla")`), gated by
the same `--allow-lineara` flag as `lineara`, not a separate flag (A-066). `words.py`
gates on nothing by corpus identity, so the same CERTAIN-WORD, normalised, >= 2-sign
filter that gives GORILA 988 types gives SigLA 692 (pinned by test). 577 of those are
an identical normalised sign tuple in both editions' sets (`words.py::restrict_to_shared`,
A-067); the two editions' restrictions to that shared set are the same word-type
frozenset by construction, so the design's "run stage 1 once under each edition's word
set restricted to it" is satisfied by one run (A-068).
