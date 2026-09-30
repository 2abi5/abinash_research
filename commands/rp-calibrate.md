---
description: Learn a target profile from reference papers, or compare your draft to it
argument-hint: "[exemplar .tex/.txt files] | --compare"
---
Invoke `research-pro` and read `references/21-reference-paper-calibration.md`.

Input: $ARGUMENTS

**Building a profile** (1–3 accepted papers from the target venue, last two cycles,
neighbouring problem):
```
python3 skills/research-pro/scripts/exemplar_profile.py <files> --out paper/exemplar_profile.json
```
For PDFs, run `pdftotext -layout in.pdf out.txt` first and pass the .txt.

Then report the measured target: section order, page allocation per section, figure
and citation density, abstract length, register. Set the S1 section budget from
**this**, not from a generic table. Record the exemplars' identity in the ledger.

**Comparing a draft:**
```
python3 skills/research-pro/scripts/exemplar_profile.py paper/main.tex --compare paper/exemplar_profile.json
```
Report every deviation beyond ±25% and say whether it is a decision or an accident.

Copy structure, proportion, and register. **Never copy wording** — that is
plagiarism, and venues run similarity checks.
