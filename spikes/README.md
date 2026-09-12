# spikes/

The experimental half of the repository. The rest of the repo answers "what can be shown
on this corpus with controls the field agrees on". This folder asks "what else could be
tried", without the standing that the main line gives a result and without the fear of
looking like a crank. Same rigour, different status. Like spikes in a product repo: fast,
scoped, disposable, and never shipped as a feature without being rebuilt properly.

## Rules

1. **Nothing here is a finding.** A spike's outcome is written in its own folder and, if
   worth recording, in FINDINGS.md as **exploratory** (as F-033 is). No claim in
   `docs/ai_context/claims.md`, no sentence in a guide or report, ever rests on a spike.
2. **Every spike starts with a brief**, written before any code: the question, why it
   sits outside the main line, what would count as interesting and what as nothing, and
   what the result must not be read as. The brief is the pre-registration. It is short.
3. **The controls travel.** Where Linear B can serve as the answer key it is used; where
   a null can be run it is run. A spike may skip a control the main line requires, but
   the brief says which and why.
4. **Spikes build on the main line, never edit it.** They import from `src/`; they do not
   change it. A spike that needs a change to the instrument proposes a pre-registered
   version in CHANGELOG instead.
5. **Promotion is a rebuild.** A spike that looks like it should be a finding is redone
   under the main-line discipline (pre-registration, frozen protocol, wrong controls,
   two samples) as a new protocol version. The spike stays here as the record of where
   the idea came from.
6. **Results files stay aggregate**, as everywhere: no corpus text, no word lists, no
   Linear A readings in the repo. The one repository-wide exception is what a
   value-transfer test stores so it can be checked: the published place-name readings and
   the Linear A words that matched them (S-003, S-003b and the main-line toponym test);
   [LICENSE.md](../LICENSE.md) lists it.
7. **Version and commit** like everything else. Each spike has a number, S-nnn, and a
   dated status line in `INDEX.md`.

## Layout

```
spikes/
  README.md          this file
  INDEX.md           one line per spike: id, title, status, date
  S-001-<slug>/
    BRIEF.md         the question and the readings, written first
    run.py           or notebooks; imports from src/, edits nothing there
    RESULT.md        what happened, numbers only, and the reading against the brief
```

Status values: **proposed**, **running**, **done: nothing**, **done: interesting**,
**promoted (protocol x.y)**, **abandoned (reason)**.
