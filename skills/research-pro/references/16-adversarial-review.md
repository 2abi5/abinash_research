# S9 — Adversarial self-review

Run this before the readiness score. The full multi-reviewer panel lives in the
`paper-reviewer` skill; this file is the author-side pass you do first, because it
is cheaper to fix what you can find yourself.

## Stance

Read the paper as the reviewer who wants to reject it and needs a defensible
reason. That reviewer exists, is competent, has six papers to review this weekend,
and is annoyed. Find their argument before they do.

## The five dimensions, as questions

Answer each with evidence from the paper, and mark `pass` / `needs revision` /
`needs experiment`. An answer of "I think it's fine" is `needs revision`.

### Contribution
1. What does a reader know after this paper that they did not before?
2. Is the failure case we fix actually important, or is it rare and convenient?
3. Could a competent practitioner have predicted our result? If yes, where is the
   surprise?
4. Is the improvement the *point*, or is the mechanism the point? (If only the
   improvement, this is a leaderboard entry.)
5. Would we cite this paper if someone else wrote it?

### Writing
6. Could a competent graduate student reimplement the method from the text?
7. Does every module have a stated motivation tied to a named problem?
8. Is terminology identical throughout?
9. Does every section reverse-outline cleanly?
10. Is the technical challenge visible by the end of introduction paragraph 2?

### Empirical strength
11. Is the margin larger than seed variance? On *every* headline claim?
12. Is absolute performance competitive for this venue, not just relatively better?
13. Are gains consistent across datasets, or does one carry the average?
14. Do we report a failure case?

### Evaluation completeness
15. Is every mechanism ablated, isolating one variable?
16. Is the strongest published baseline present, and tuned as hard as ours?
17. Are the metrics the ones this community uses?
18. Are the datasets hard enough for the result to mean something?

### Method soundness
19. Is the experimental setting realistic, or does it assume away the hard part?
20. Does the method need per-dataset tuning to hold up?
21. Do the benefits outweigh the added complexity — and could a reviewer argue the
    net is negative?
22. What assumption, if false, breaks the whole paper? Is it stated?

## Write the reject review yourself

The highest-value fifteen minutes in a paper's life. Write the review that rejects
your paper — three specific, technically-grounded criticisms, in a reviewer's voice,
with a confidence and a score.

Then for each: fix it, or prepare the rebuttal, or accept the score you will get.
Papers are lost to criticisms the authors could have written themselves and chose
not to look for.

## The five classic rejection dimensions

Map every objection you find to one of these; it tells you what kind of fix it needs.

| Dimension | Signals | Fix type |
|---|---|---|
| **Insufficient contribution** | Target failure case is rare; the technique is well-explored; the gain is predictable | Reframe, or new analysis — not more prose |
| **Unclear writing** | Missing details; a module with no motivation; inconsistent notation | Rewrite (`12-prose-quality.md`) |
| **Weak empirical effect** | Margin within noise; absolute performance not competitive | New experiments, or a weaker claim |
| **Incomplete evaluation** | Missing ablations, baselines, or metrics; datasets too easy | New experiments |
| **Problematic method design** | Unrealistic setting; a technical flaw; fragile to hyperparameters; complexity exceeds benefit | Method change, or an honest scope limitation |

Only two of these five are fixable by writing. That is the useful thing this table
tells you: if your three self-found objections are all in rows 3–5, more editing
will not save the paper, and the honest move is to run the experiment or move the
deadline.

## Then

Hand off to the `paper-reviewer` skill for the multi-perspective panel, then to
`15-readiness-score.md`.
