---
description: Gated submission-readiness score — Gate 4
argument-hint: "[venue slug]"
---
Invoke `research-pro` and read `references/15-readiness-score.md`.

Venue: $ARGUMENTS

Fill `paper/readiness.json` (template: `templates/readiness.json`) from real
artifacts — each dimension needs an `evidence` string naming the table, figure,
section, or report it was scored from. The scorer refuses to score a dimension with
an empty evidence field, and that refusal is the point.

```
python3 skills/research-pro/scripts/score_readiness.py paper/readiness.json --venue <slug> --strict
```

Rules: gates outrank the score — any failed or unrun gate means `NOT READY`
whatever the total. Score the paper that exists, not the one the author intends to
finish. Report the weakest dimensions first.

Then write the most useful part of the report: **the reviewer objections you predict,
in the reviewer's voice, in the order they will arrive**, each specific enough that
the author can pre-empt it.
