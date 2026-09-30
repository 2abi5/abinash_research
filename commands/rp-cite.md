---
description: Verify every citation — Gate 2
argument-hint: "[path/to/refs.bib]"
---
Invoke `research-pro` and read `references/13-citation-integrity.md`.

```
python3 skills/research-pro/scripts/verify_citations.py ${ARGUMENTS:-paper/refs.bib} \
  --tex paper/main.tex paper/sections/*.tex --report out/citations.md --strict
```

Then work all three layers:

1. **Exists** — anything `UNVERIFIED` is treated as fabricated until the author
   produces the PDF. A plausible-looking DOI is the most damaging thing in a
   manuscript.
2. **Metadata matches** — resolve every `MISMATCH`. Upgrade preprints that have a
   published version.
3. **Supports the claim** — this one is manual and it is where the real damage
   lives. For every citation attached to an abstract, introduction, or comparison
   claim: open the source, find the supporting sentence/table/figure, log it in the
   ledger. A citation you have not opened is not a citation.

If the network is unavailable the script reports `BLOCKED`. Report the gate as
blocked, not passed. Structural checks alone do not pass Gate 2.
