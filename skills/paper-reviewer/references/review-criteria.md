# What reviewers are actually asked

Calibrate the panel to the venue. The same manuscript draws different reviews
because the review *forms* ask different questions.

## The shared core

Almost every venue's form reduces to four questions:

1. **Are the claims supported by the evidence?**
2. **Is the contribution significant enough for this venue?**
3. **Is the work correct?**
4. **Is it clearly presented and reproducible?**

Question 1 is the one that decides papers, and the one authors most often lose on.
Weight it accordingly.

## Where venues differ

| Venue | What the form emphasises | What is *not* a criterion |
|---|---|---|
| **NeurIPS** | rigor, honest limitations, the paper checklist, reproducibility | — |
| **ICML** | claims supported by reproducible experiments or sound theory; positioning against prior work; impact statement | — |
| **ICLR** | clarity and public discussion; representation-learning relevance; author engagement in rebuttal | — |
| **CVPR** | quantitative comparison on standard benchmarks, visual quality, ablations | — |
| **ACL-family** | statistical rigor, data provenance and ethics, error analysis, required limitations | — |
| **AAAI** | formalization, algorithmic contribution, reproducibility checklist | — |
| **TMLR** | **claims versus evidence** (primary), plus "would anyone in the audience care"; clear writing | **novelty and significance are explicitly NOT criteria** |
| **TPAMI** | depth, completeness of evaluation, theoretical grounding, survey-quality related work | — |
| **Nature-family** | broad significance, accessibility to non-specialists, figure-led argument | — |

TMLR is the important special case. Reviewing a TMLR submission for novelty is
reviewing against the venue's stated policy. There, an incremental or negative
result with exactly-supported claims is an accept, and an exciting result with
overreaching claims is a revision.

## Score scales

Most ML venues use a 1–10 overall score with a separate confidence rating. The
practical reading:

```
 1-3   reject          a flaw that cannot be fixed in a revision cycle
 4-5   borderline rej.  real contribution, evidence or clarity not there yet
 6     borderline acc.  would accept if nothing better competes
 7-8   accept           solid, evidence supports the claims
 9-10  strong accept    rare; changes what people in the area do
```

Confidence matters: a 3 at confidence 5 sinks a paper, a 3 at confidence 2 is
usually discounted by the area chair. When this panel reports a finding, say how
confident it is and what would change that — an unconfident objection the author
can cheaply close is still worth reporting.

## Reviewer behaviour worth predicting

Real reviewers, reliably:

- **Read the abstract, then the figures, then the tables, then the introduction.**
  They form a prior before reading the method. A bad teaser figure costs score on a
  paper they have not read yet.
- **Check whether the strongest recent baseline is present.** In fast-moving areas
  this is the first thing a domain expert does.
- **Check whether the abstract's number appears in a table.** Mismatches are found.
- **Look for the failure case.** A paper with none is assumed to be hiding one.
- **Skim the appendix at most.** Load-bearing content there is effectively absent.
- **Read the limitations section** where the venue requires one, and read a ritual
  one ("may not generalize") as evasion.
- **Not re-run anything.** Reproducibility is judged from the paper and the artifact's
  plausibility, not from execution.
- **Remember hostile rebuttals** and discount them.

## Re-review

In re-review mode, verify against the revised text only — never against the author's
description of what they changed:

| Prior finding | Status | Evidence in the new version |
|---|---|---|
| ADE20K margin within noise | addressed | Tab.2 now 3 seeds, 85.1±0.3 vs 84.7±0.4; abstract weakened to "matches" |
| missing Liu25 baseline | partly | added to Tab.2 but not discussed in §2 |
| §3.2 unclear | not addressed | text unchanged |

"Partly" is a real category and the most common outcome. Report it as such rather
than rounding it up.
