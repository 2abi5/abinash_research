---
description: Edit machine-sounding prose into an authorial voice, and draft the AI disclosure
argument-hint: "[path/to/file.tex] [--section regex]"
---
Invoke `research-pro` and read `references/12-prose-quality.md`.

```
S=skills/research-pro/scripts
python3 $S/prose_metrics.py ${ARGUMENTS:-paper/main.tex} --paragraphs
```

Measure before touching anything. Then work the flagged paragraph rows in order,
not the section at once: a whole-section pass smooths the text evenly, which is the
defect you are removing.

For each paragraph: name its one message, put it first, make every following
sentence stand in a nameable relation to the one before, turn nominalizations back
into verbs, walk each noun down the specificity ladder (field → task → dataset →
metric → number → condition), replace each em-dash with what it is doing (comma,
colon, new sentence, or nothing), vary the rhythm with one short sentence, and read
it aloud.

Then ask of every paragraph: **what does the reader now know that they did not
before?** If the answer is "that this topic is important", delete it.

Watch for over-correction: staccato fragments, rhetorical questions, folksy asides,
contractions. The `choppiness` warning fires on that register. The target is a
specific researcher stating what they measured, not "sounds human".

Preserve: calibrated hedges on genuinely uncertain claims, field-required formality,
and consistent technical terminology. If the author has prior papers, profile them
with `exemplar_profile.py` and match the sentence-length, first-person and hedging
numbers; record the targets in the ledger.

Finish with the proof:

```
python3 $S/prose_metrics.py paper/main.tex --compare <the version you started from>
```

Variance up, banned hits to zero, dashes down. If a number moved the wrong way, you
smoothed.

This is prose quality, not detector evasion. Also draft the disclosure statement
from `templates/disclosure-statements.md` per the venue's policy; see
`references/18-disclosure-and-ethics.md`.
