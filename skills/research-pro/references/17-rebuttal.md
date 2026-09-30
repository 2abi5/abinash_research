# Rebuttal and response to reviewers

Rebuttals change outcomes more often than authors expect, and they are usually
written badly — defensively, at the last minute, and over the word limit.

## Read the reviews twice

First pass: read all of them, then stop. Do not draft anything. The first reaction
to a hostile review is always wrong.

Second pass, a day later: extract every point into a table, whatever tone it came
in.

```markdown
| # | R | Point | Type | Our response | Action | Where |
|---|---|---|---|---|---|---|
| 1 | R2 | "ADE20K margin within noise" | valid | agree | run 3 seeds, revise claim | Tab.2, §5.1 |
| 2 | R2 | "missing comparison to Liu25" | valid | agree | add row | Tab.2 |
| 3 | R3 | "method is just pruning" | misunderstanding | disagree, clarify | rewrite §3.2 opening | §3.2 |
| 4 | R1 | "should evaluate on video" | out of scope | partially agree | state as limitation | §6 |
```

Four types, four different responses:

- **Valid** — concede immediately and clearly. Say what you changed. Conceding a
  real point buys credibility for the ones you contest.
- **Misunderstanding** — your writing's fault, even when the reviewer misread.
  Clarify, and say where the text now makes it unmissable. Never "the reviewer
  appears to have misunderstood"; write "we did not state this clearly — §3.2 now
  says…".
- **Out of scope** — acknowledge the value, explain the boundary, and add it as a
  limitation or future work. Do not promise experiments you will not run.
- **Wrong** — push back, once, with evidence. Cite the section, table, or a new
  result. One clear paragraph, no indignation.

## Structure

Respect the word or page limit exactly — over-limit rebuttals get truncated, and
the truncated part is the end, where your best argument usually sits.

```markdown
We thank the reviewers. We have added [the two or three concrete new things:
"3-seed results for ADE20K (Tab. 2)", "a comparison to Liu et al. (Tab. 2, row 4)"]
and clarified [the main misunderstanding].

**R2.1 — ADE20K margin within seed variance.** Agreed. We reran with 3 seeds:
85.1 ± 0.3 versus 84.7 ± 0.4. The margin is within variance, and we have weakened
the claim in the abstract from "outperforms" to "matches" on this dataset. The
ImageNet result (2.4 points, 3 seeds) is unaffected.

**R2.2 — Missing comparison to Liu et al. (2025).** Added as row 4 of Table 2: 82.7
top-1 at 4.0 GFLOPs, against our 85.1 at 4.0.

**R3.1 — "The method is equivalent to magnitude pruning."** We should have made the
distinction explicit. Magnitude pruning removes weights by static magnitude; our
gate selects experts per input at inference, so capacity is retained and allocated
conditionally. Table 4 row 2 makes this measurable: static pruning at matched FLOPs
costs 3.1 points. §3.2 now opens with this contrast.
```

## Rules

- **Lead with what you added.** Reviewers and area chairs read the first three lines
  and skim the rest. New results go there.
- **Number responses to match the reviews** (`R2.1`) so an area chair can follow.
- **Concede first, contest second.** A rebuttal that concedes nothing is read as
  not having engaged, whatever its content.
- **Every claim of a change names where it is.** "We have clarified this" without a
  section number is not verifiable and will not be believed.
- **No new claims that the new results do not support.** Rebuttal-phase overclaiming
  is caught immediately, and it is fatal because it is deliberate.
- **Answer every reviewer**, including the positive one. Silence toward a supportive
  reviewer loses their advocacy in the discussion.
- **Never attack a reviewer's competence**, even when the review is bad. Area chairs
  discount hostile rebuttals and remember them.
- Where a venue allows a revised PDF, mark changes (a colour, or a change log).

## What actually moves a score

In descending order of effect:

1. A **new experiment** that answers the objection. Even a small one. Nothing else
   comes close.
2. Conceding a real flaw and **weakening the claim** to match. Reviewers raise scores
   for this because it demonstrates you can be trusted.
3. A crisp clarification of a misunderstanding **plus** the text change that
   prevents it.
4. Pointing out that the requested result is already in the paper — politely, with
   the reference. (And then asking yourself why the reviewer missed it, because that
   is a writing defect.)

What moves nothing: restating the paper, appealing to effort, listing the venue's
acceptance rate, or arguing that the reviewer is not an expert.

## Journal major revision

A different document: a point-by-point response, often many pages, with no word
limit, plus a revised manuscript with changes marked. Same discipline, more depth.
Answer literally every numbered point, including the ones you refuse, and provide a
change log mapping each point to each edit. Unanswered points are the most common
reason a second round is required.

## Re-submission after rejection

- Read the old reviews before writing anything. The new reviewers may be the same
  people, and at ARR the prior reviews carry forward explicitly.
- Fix what was valid. Resubmitting unchanged with a different framing is noticed.
- Where you disagreed and did not change, pre-empt it in the paper itself so the
  next reviewer does not have to raise it.
