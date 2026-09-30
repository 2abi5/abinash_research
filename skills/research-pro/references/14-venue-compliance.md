# S8 — Venue compliance  ·  GATE 3

Desk rejection is the cheapest way to lose a good paper and the easiest to prevent.
Every trigger in this file is mechanical: a page count, a missing section, a name in
a PDF field. None of them require judgment, and all of them end the submission
before a reviewer reads a word.

## Procedure

1. **Read the profile.** `venues/<venue>.md` and the venue's entry in
   `venues/registry.json`.
2. **Re-verify it live.** Mandatory. `venues/VERIFY.md` says how. A snapshot is
   never sufficient for a `PASS` — venue rules move every cycle, and AI-use policies
   are currently moving mid-cycle.
3. **Run the checks.**
   ```bash
   python3 skills/research-pro/scripts/venue_check.py --venue <v> --paper paper/main.tex --strict
   python3 skills/research-pro/scripts/latex_lint.py  --venue <v> paper/main.tex
   ```
4. **Inspect the compiled PDF.** Some things only exist in the PDF: real page
   count after float placement, embedded author metadata, figure legibility.
5. **Report.** Every item pass/fail with the value found and the value required.

## The universal checklist

Run this for every venue, whatever the profile says.

### Length
- [ ] Page count of the main body, **measured in the compiled PDF**, within the limit
- [ ] You know exactly what is excluded — references, appendix, checklist,
      limitations, impact statement all differ by venue
- [ ] No content smuggled into the excluded region. Reviewers report it and it reads
      as bad faith
- [ ] Margins, font size, and line spacing unmodified. Shrinking `\baselineskip` or
      `\textfloatsep` to fit is detected by the template check at several venues
- [ ] The **current cycle's** template `.sty`, not last year's

### Anonymity (double-blind venues)
- [ ] No author names or affiliations in the PDF body
- [ ] No acknowledgements, no funding statement
- [ ] Self-citations in the third person (`Prior work [12] showed`, never `our
      previous work [12]`)
- [ ] No link to a named repository, homepage, or non-anonymous artifact
- [ ] `pdfinfo main.pdf` shows no author, no institution, no identifying title
- [ ] No identifying paths inside figure files, no institutional dataset names, no
      internal cluster names
- [ ] Supplementary material anonymized too — it is the usual leak

### Required sections and artifacts
- [ ] Every required section present, correctly placed
      (limitations · impact statement · ethics · data and code availability)
- [ ] Every required checklist present, in the right position in the PDF, complete
- [ ] Checklist answers consistent with the paper. Area chairs read them against each
      other, and an inconsistency is worse than an uncomfortable honest answer

### Bibliography and references
- [ ] Citation style matches the template
- [ ] All `\cite` keys resolve; no `?` in the compiled PDF
- [ ] References complete and verified (Gate 2)

### AI-use policy
- [ ] Current cycle's policy read — not last cycle's, not another venue's
- [ ] Disclosure statement written where required
      (`18-disclosure-and-ethics.md`)
- [ ] No prompt injection anywhere in the manuscript, including white text, figure
      metadata, and LaTeX comments. This is an explicit rejection-and-report offence
      at multiple venues. If you find any, tell the author immediately — including
      the possibility that it arrived via a template or a collaborator

### Submission mechanics
- [ ] Abstract deadline, where separate from the paper deadline (AAAI: about a week
      earlier — the most-missed deadline in the field)
- [ ] Per-author submission caps
- [ ] Dual submission: nothing substantially overlapping under review elsewhere
      during the venue's review window. CVPR sets the threshold at 20% overlap and
      reports violations to the other venue
- [ ] Subject area and keywords selected
- [ ] Conflicts of interest declared accurately
- [ ] Supplementary material in the accepted format and under the size limit
- [ ] Compiles from a clean checkout with the venue's TeX distribution

## Gate 3 — passing criteria

- [ ] Live re-verification done, with the date recorded in the ledger
- [ ] Zero hard-rule violations
- [ ] Every required section and artifact present
- [ ] Anonymity clean, checked in the PDF and not only in the source
- [ ] Disclosure present per policy
- [ ] Deadlines and caps confirmed

A single hard-rule violation fails the gate. There is no partial credit here,
because the venue does not give any.

## Choosing between venues

When the author has not decided, present the trade-off rather than picking:

| Consider | Favours |
|---|---|
| Work is complete but incremental, claims modest | TMLR — no novelty requirement, claims-versus-evidence bar |
| Strong benchmark result, good figures | CVPR / ICCV / ECCV |
| Learning insight or new representation | ICLR / NeurIPS |
| Algorithmic or non-learning AI contribution | AAAI / IJCAI |
| Careful empirical NLP with error analysis | ACL-family via ARR |
| Depth, many experiments, no page pressure | TPAMI or another journal |
| Result that changes a broad audience's beliefs | Nature-family, expecting editorial triage |
| Negative or replication result | TMLR, or a dedicated workshop |
| Deadline is in two weeks and experiments are missing | the next cycle |

Say the last one out loud when it is true.
