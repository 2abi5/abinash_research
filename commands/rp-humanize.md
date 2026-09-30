---
description: Edit machine-sounding prose into an authorial voice, and draft the AI disclosure
argument-hint: "[path/to/file.tex]"
---
Invoke `research-pro` and read `references/12-prose-quality.md`.

```
python3 skills/research-pro/scripts/prose_metrics.py ${ARGUMENTS:-paper/main.tex}
```

Fix what it flags, then do the part it cannot measure. Work paragraph by paragraph —
a whole-section pass smooths the text evenly, which is the defect you are removing.

For each paragraph: name its one message, put it first, make every following
sentence stand in a nameable relation to the one before, turn nominalizations back
into verbs, replace abstractions with the specific thing, vary the rhythm (land a
short sentence after a long one), and read it aloud.

Then ask of every paragraph: **what does the reader now know that they did not
before?** If the answer is "that this topic is important", delete it.

Preserve: calibrated hedges on genuinely uncertain claims, field-required formality,
and consistent technical terminology. Match the author's voice from their prior
papers where you have them.

This is prose quality, not detector evasion. Also draft the disclosure statement
from `templates/disclosure-statements.md` per the venue's policy — see
`references/18-disclosure-and-ethics.md`.
