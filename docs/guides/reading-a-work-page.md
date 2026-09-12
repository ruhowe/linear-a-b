# Reading a work page

Every source we have looked at has a page in [docs/works/](../works/). This explains what
the fields mean, so you can tell at a glance how much weight a page carries.

## The shape of a page

Each page opens with machine-readable frontmatter, then four sections: what the work
claims, where to find it, our assessment, and an invitation to disagree.

The separation matters. "What it claims" is the author's position stated as fairly as we
can manage. "Our assessment" is ours, and includes how thoroughly we checked.

## Verification flags

This is the most important field and it describes **our** diligence, not the work's
quality. A careful peer-reviewed paper we only saw an abstract of gets a P.

| Flag | Meaning |
|---|---|
| **V** | We read the primary source in full |
| **Y** | We fetched and read the primary source, at least the passages the page relies on |
| **P** | We have only seen it restated in a review, an index record or a later paper |
| **S** | We have only seen a search-result snippet |
| **N** | Not checked |

On 2026-09-13, after a pass that re-checked every P and S page, 21 of 80 pages are P or S;
the README's scope section carries the current count, checked by a test. Anything below Y should be
re-verified before it appears in something published. To list them:

```bash
.venv/bin/python scripts/bib.py --verified P
```

## Standing

Where the work sits in the field, as best we can judge.

| Value | Meaning |
|---|---|
| `accepted` | Mainstream, cited approvingly |
| `contested` | Taken seriously, not settled |
| `untested` | A specific claim nobody has checked, including us until recently |
| `fringe` | Outside the field's engagement, with reasons given on the page |
| `superseded` | Overtaken or no longer available |

`fringe` is a judgement and the page says why. We have moved a work out of it once
already, after reading the paper rather than the press coverage about it, and that
correction is recorded on the page.

## Access

Whether you can read it. `open`, `paywalled`, `blocked` for hosts that refused us,
`print-only`, `offline` for things that have disappeared from the web. The last category
is not rare and is part of why this catalogue exists.

## Scripts and domains

Tags, and a work can carry several. A study covering both Linear A and Linear B is filed
once with both tags rather than duplicated or arbitrarily assigned.

Domains are `computational`, `philology`, `palaeography`, `imaging`, `edition`,
`methodology`, `survey`, `decipherment-claim` and `resource`.

## Tested by

If we have put a work under test, this links to the write-up. Seven pages currently carry
it. A claim being catalogued is not the same as a claim being checked, and this field
keeps the difference visible.

## Querying

```bash
.venv/bin/python scripts/bib.py --stats
.venv/bin/python scripts/bib.py --script A --standing contested
.venv/bin/python scripts/bib.py --grep entropy --full
```

Filters combine. The tool reads the frontmatter from the pages themselves, so editing a
page updates the catalogue with no separate step.
