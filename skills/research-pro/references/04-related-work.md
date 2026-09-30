# Related Work

Purpose: make your novelty **verifiable**. A reviewer reads this section asking
one question — "has this been done?" — and your job is to answer it in technical
terms they can check, not to demonstrate that you have read widely.

## Placement

- **After the Introduction (§2)** when the reader needs the landscape before your
  method makes sense.
- **After the Method (late §)** when your idea is easier to grasp first, and the
  comparison is sharper once the reader knows your mechanism. This also protects
  the first two pages for your own story. Increasingly common at ML venues.
- Never both, and never a third place.

## Structure

Two to four groupings, each named for a **mechanism or assumption**, never for a
period or a research group. Inside each grouping:

```
1. Scope sentence     — what this line of work does, mechanistically.
2. Representatives    — two or three, compressed, with citations.
3. The shared limit   — the assumption they all need, and when it breaks.
4. Your distinction   — one sentence, in technical terms.
```

Sentence skeletons:

- `A first line of work <does X> by <mechanism> [refs]. These methods assume
  <assumption>, which holds for <cases> but breaks when <condition>.`
- `Closest to ours is <method> [ref], which also <shared property>. It differs in
  that it <their mechanism>, so <consequence>; we instead <our mechanism>, which
  <property that matters>.`
- `<Technique> has been applied to <adjacent problem> [refs]. We adopt <the
  component we reuse> but <what we change and why the naive transfer fails>.`

## The distinction sentence

This is the load-bearing sentence of the section, and the one reviewers quote
back at you. It must be checkable.

- **Bad:** "Unlike prior work, our method is more general and efficient."
  Marketing. Unfalsifiable. Reads as if you have not read prior work carefully.
- **Good:** "Prior routing methods select experts per layer, which forces a
  routing decision before the token's context is resolved; we defer selection to
  a single global gate, so the decision sees the full context at the cost of one
  extra forward pass."

The good version tells a reviewer exactly what to check, and concedes a cost.
Naming your own cost is what makes the rest credible.

## Handling the closest competitor

Never bury or soften it. Reviewers know the field; if the nearest work appears
late, in a subordinate clause, minimized, that reads as intellectual dishonesty
and it is the single fastest way to earn a hostile review.

Give it its own paragraph or a clearly signposted passage. State what it does
well. Then state the specific technical difference and — if you can — show the
comparison in your main results table. A strong paper beats its closest
competitor in public.

If a concurrent preprint overlaps heavily: cite it, note concurrency and the
dates, and state what is independently yours. Silence will be noticed.

## "First to" claims

One counterexample destroys the claim and damages every other claim in the
paper. Prefer a bounded formulation:

- Instead of `the first method to X` → `to our knowledge, the first method to X
  under <specific setting>`
- Or drop it. The contribution stands on its mechanism and its evidence; priority
  claims add risk and almost no value.

## Do and do not

| Do | Do not |
|---|---|
| Compare mechanisms, assumptions, failure modes | List titles and years |
| Cite the strongest and most recent competitors | Omit the ones you lose to |
| End each grouping with the limitation your work addresses | End with "however, these methods are limited" and no reason |
| Keep it tight — 0.5 to 0.75 page in an 8-page paper | Pad to signal diligence |
| Match every baseline in your results table to a paragraph here | Cite a method as related, then never compare against it |

## Checks before moving on

1. Is every baseline in the results table discussed here, and vice versa?
2. Would each cited author agree with your one-line characterization of their
   work? If you are unsure, you read the abstract, not the method.
3. Is the closest work prominent and fairly described?
4. Does every grouping end in a limitation that connects to your contribution?
5. Is there a citation dump — three or more references in one bracket with no
   individual discussion? Either discuss them or move them to the Introduction.
