---
description: Verify every citation — Gate 2
argument-hint: "[path/to/refs.bib]"
---
Invoke `research-pro` and read `references/13-citation-integrity.md`.

```
python3 skills/research-pro/scripts/verify_citations.py ${ARGUMENTS:-paper/refs.bib} \
  --tex paper/main.tex paper/sections/*.tex --ledger paper/LEDGER.md \
  --cache .cite_cache.json --report out/citations.md --strict
```

Add `--authors "Surname,Surname"` for the self-citation rate and `--mailto` for the
Crossref polite pool.

Then work the report top to bottom:

1. **`RETRACTED`** — remove, or keep only to discuss the retraction and say so in
   the text. A retracted baseline invalidates the comparison table.
2. **`UNVERIFIED`** — treated as fabricated until the author produces the PDF. The
   report shows the nearest title the databases found and why it was rejected; a
   plausible-looking DOI is the most damaging thing in a manuscript.
3. **`MISMATCH` and preprints** — resolve every field disagreement; upgrade every
   preprint whose published DOI the report found. Both block the gate.
4. **Layer 3, the worklist** — the table of load-bearing sentences (abstract,
   introduction, related work). For each row open the source, find the supporting
   sentence/table/figure, and log it in the ledger's `Citation layer-3 log`. Re-run
   with `--ledger`: uncovered keys block the gate. Check the verb too: "showed"
   after a paper that argued is a Layer-3 failure.
5. **Mechanics** (non-blocking) — citation stacks of four or more, citations after
   the period, `[12]` used as a noun, missing `~`. Fix them anyway.
6. **Profile** — recency share, self-citation rate, preprints. Read it as a reviewer.

If the network is unavailable the script reports `BLOCKED`. Report the gate as
blocked, not passed. Structural checks alone do not pass Gate 2. Never fill a
`[NEEDS SOURCE]` from memory; find the originator with `lit_scan.py` or leave the token.
