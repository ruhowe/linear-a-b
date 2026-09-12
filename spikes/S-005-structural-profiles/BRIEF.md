# S-005 · Structural profiles: Linear A against syllabically written corpora

**Question.** Kober stage 1 gives a corpus a profile without sound values: paradigm ratio
against N1, maximum alternation support against N2, ending-inventory size and entropy,
prefix-channel ratio (F-037), medial-channel ratio (F-040). Greek under Linear B spelling
is the one profile we have. What do other languages look like when written in a
CV-syllabary, and does Linear A's profile sit near any of them?

**Why a spike.** It needs syllabically respelled corpora of candidate and non-candidate
languages (Luwian in hieroglyphic Luwian's syllabary, Hittite and Akkadian in cuneiform
syllabic values with logograms dropped, Semitic and Etruscan respelled by rule as A-005
respells Greek), each cut to Linear A's size twenty times. The respelling rules are
assumptions on top of assumptions, so nothing here can be a finding; but the pattern of
where Linear A falls, if it falls anywhere at all, is the kind of thing that has never
been drawn. The inventory-dependence rule in result-discipline applies: every statistic
must be checked against the respelled corpus's signary size before it is read (F-042,
F-044).

**Method.** Reuse `scripts/kober_run.py` on private respelled corpora in the loader's
shape (never committed); twenty tablet-model or chunk subsamples at 988 word types; the
profile as a vector; distances in each reference's own subsample spread, reported per
statistic and never pooled across inventory-driven and order-driven statistics.

**Interesting.** Linear A's profile sits inside one reference's spread and outside the
others on the order-driven statistics. **Nothing.** Linear A sits outside every
reference's spread, or inside several: the profile does not discriminate at this size,
which is F-022 in another form.

**Must not be read as.** Evidence about which language Linear A writes. A profile match
is a match of spelling-plus-morphology shape, and the respelling rules are ours.
