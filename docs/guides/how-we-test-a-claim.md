# How a claim is tested here

Every result here is reported against what nonsense would score on the same test. That
single rule is most of the method.

## The problem it solves

Suppose someone proposes that Linear A records Language X, and shows you fifty Linear A
words that match real words in X. Impressive or not?

You cannot tell, because you have not been told how many matches you would get from a
reading that is definitely wrong. If a scrambled reading also produces fifty matches, the
fifty tell you nothing about X.

This failure happens in practice. When we ran it, a genuinely random reading of Linear A
matched Hebrew roots for about seventy percent of words.

## The null model

A null model is a deliberately wrong version of the thing being tested, scored identically.

For a proposed decipherment the natural null is to keep everything except the part under
test. Take the proposed sign values, shuffle which sign gets which value, and rerun the
whole matching procedure. Word lengths, sign frequencies and repeated signs all stay
exactly as they were. Only the assignment changes, and the assignment is the claim.

Do that a thousand times and you get a distribution of scores that wrong readings achieve.
If the real reading sits inside that distribution, it has not demonstrated anything. If it
sits far outside, it has.

David Packard did precisely this for Linear A in 1974, calling the shuffled versions
"fictitious decipherments". The idea is fifty years old, and the field dropped it.

## The positive control

A test that only ever says no is indistinguishable from a broken test.

So alongside the null we run a case where we know the answer should be yes. For the
Semitic test we took real Hebrew words, re-encoded them in the Linear A writing system,
and ran the identical procedure. The real assignment recovered them completely, far
outside its null.

That result is what licenses the negative one. Without it, "Linear A does not look Semitic"
could just mean our code does not work.

## The trap we nearly fell into

The obvious way to run this test gives the wrong answer, and it is worth understanding why
because anyone repeating the work will meet it.

Our first null shuffled sign values freely. The real reading beat it, apparently
significantly. The effect was an artefact. Some sign values are more permissive than
others, standing for several possible sounds rather than one. A free shuffle changes how
many candidate words the corpus can reach in total, and reaching more candidates means
more matches regardless of whether the reading is correct.

Once we held that fixed, shuffling only which sound goes with which sign and never how
many options a sign has, the effect disappeared.

The lesson generalises. A null has to hold constant everything except the claim, and
working out what "everything except" means is where the thinking is.

## Testing every hypothesis at once

Testing a single proposal in isolation still answers the wrong question. Knowing that
Semitic scores slightly above its null does not tell you whether Anatolian, Etruscan or
Greek would score higher on the same data.

So candidate languages are stored as data in `src/hypotheses/`, each with its lexicon and
the sound mappings it implies, and a test runs across all of them at once. Each is scored
against its own null, because lexicons differ in size and permissiveness, and comparing
raw match rates between them would measure dictionary size rather than fit.

This is fairer as well as more informative. Running one person's proposal through a test
built for it invites the charge of a vendetta. Running every proposal, including the
mainstream position and a deliberately false control, is a survey.

## Weighting and scenarios

People disagree about which hypotheses deserve to be taken seriously, and that disagreement
is honest. Rather than pick one set of prior beliefs and hide it, `src/hypotheses/scenarios.yaml`
holds several named ones, including a weighting maximally favourable to the proposal under
test.

A finding that survives its own proponent's priors is much harder to argue with than one
that only holds under priors the proponent rejects.

## What this can and cannot do

It can show that a particular kind of evidence carries no weight. It can, in principle,
show the opposite, and a claim that cleared these bars would be a genuine finding that
nobody has yet produced.

It cannot tell you whether a piece of grammatical analysis is any good. Whether a proposed
verb form is plausible in a given language needs a specialist in that language. This
measures the size of the haystack, not the quality of the needle.
