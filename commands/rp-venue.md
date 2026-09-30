---
description: Check the manuscript against a venue's hard rules — Gate 3
argument-hint: "[venue slug] [--pdf paper/main.pdf]"
---
Invoke `research-pro` and read `references/14-venue-compliance.md` plus
`venues/<slug>.md`.

Venue: $ARGUMENTS

```
python3 skills/research-pro/scripts/venue_check.py --venue <slug> --paper paper/main.tex --pdf paper/main.pdf --strict
python3 skills/research-pro/scripts/latex_lint.py paper/main.tex --venue <slug>
```

**Then re-verify against the live call for papers.** This is mandatory, not
optional: venue rules change every cycle and AI-use policies are currently moving
mid-cycle. The URLs are in the venue profile. A `PASS` from the snapshot alone is
not a Gate 3 pass — see `venues/VERIFY.md`.

Report every rule as pass/fail with the value found against the value required.
Then inspect the compiled PDF for the things that exist only there: the real page
count after float placement, embedded author metadata (`pdfinfo`), and figure
legibility.

`python3 skills/research-pro/scripts/venue_check.py --list` shows the known venues.
