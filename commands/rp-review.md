---
description: Adversarial five-seat review panel
argument-hint: "[full|quick|methodology|re-review|calibration] [venue]"
---
Invoke the `paper-reviewer` skill.

Mode: ${ARGUMENTS:-full}

Read the whole manuscript including appendix, tables, and captions. Build the claim
audit table before forming any opinion. Then run the five seats separately without
letting them converge: venue fit, methodology, domain expert, clarity/outsider,
devil's advocate.

**Read-only.** Do not edit the manuscript in this pass. Produce the report; the
author reads it; fixes are a separate pass.

Every seat produces at least two specific criticisms, each citing a location. No
praise sandwiches. Do not soften because the paper is good, and do not invent a flaw
to look rigorous.

End with the editorial synthesis: decision, blocking findings with the fix type for
each, the revision roadmap ordered by what changes the outcome, and — importantly —
**what the author should not change** under reviewer pressure.
