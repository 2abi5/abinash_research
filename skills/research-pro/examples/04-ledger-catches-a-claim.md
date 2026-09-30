# Worked example — the ledger catches an unsupported claim

This is what Gate 1 is for, and it is the single most common way a good paper draws
a bad review.

## The abstract as drafted

> … On ImageNet and ADE20K our gate holds accuracy at 4× fewer inference FLOPs, and
> **remains robust under distribution shift**.

## Extracting the claims

Claims come from what the text *asserts*, not from what the authors meant.

| # | Claim | Type | Evidence | Location | Status |
|---|---|---|---|---|---|
| C1 | Holds top-1 accuracy at 4× fewer FLOPs on ImageNet | empirical | Tab.2 rows 3–5 | §5.1 | supported |
| C2 | Same on ADE20K | empirical | Tab.2 row 6 | §5.1 | **see below** |
| C3 | The gain is the routing, not added capacity | causal | Tab.4 rows 2–3 | §5.3 | supported |
| C4 | Remains robust under distribution shift | empirical | — | — | **needs-evidence** |

Two problems, of different kinds.

## C4 — a claim with no experiment

Nobody ran a shift evaluation. The sentence entered the abstract because the method
*ought* to be robust, and that is how unsupported claims get written: not
dishonestly, but aspirationally.

Gate 1 fails. Two honest closes, and the author picks:

- **Add the evidence.** ImageNet-C and ImageNet-R, versus the same baseline.
  About a day of compute, and it makes C4 a real contribution.
- **Cut the claim.** Delete the clause. The paper is not weaker for it — it is
  weaker with a claim three reviewers will notice is unsupported.

What is *not* a close: hedging it. "and may offer improved robustness in some
settings" is worse than either option. It keeps the reviewer's objection alive while
signalling that the authors knew.

## C2 — a claim at the wrong rung

The ADE20K numbers exist: 85.1 versus 84.7. But the run is single-seed, and seed
variance on that benchmark is ±0.4. So the honest rung is not "holds accuracy" —

```
5  "X causes Y"
4  "X improves Y by N% on D"       <- what the abstract implies
3  "X improves Y on D"
2  "X is associated with Y"        <- what one seed at ±0.4 supports
1  "X may help Y"
```

Three closes, in descending preference:

1. **Run three seeds.** Then report `85.1 ± 0.3 vs 84.7 ± 0.4` and say the margin is
   within variance. This is the strongest version: you have measured it and you say
   so plainly.
2. **Narrow the claim** to ImageNet, where the margin is 2.4 points and survives
   seeds. Report ADE20K as a secondary result without the headline claim.
3. **Report it as parity.** "matches on ADE20K" is a true statement and costs almost
   nothing.

## The abstract after the gate

> … On ImageNet our gate holds top-1 accuracy at 4× fewer inference FLOPs and matches
> the strongest baseline on ADE20K; an ablation shows the gain comes from routing
> rather than added capacity.

One claim removed, one downgraded, one ablation promoted into the abstract because
it is the causal claim and it is fully supported. The abstract is now **more
persuasive**, because everything in it survives checking — and the reviewer who goes
looking for overreach finds none.

## Why this is cheap now and expensive later

| When | Cost of finding C4 |
|---|---|
| Stage 4, at Gate 1 | delete a clause, or one day of compute |
| Stage 9, readiness score | a blocking gate, and you may miss the deadline |
| After submission | "the robustness claim is unsupported" from three reviewers, one cycle lost |
| After publication | a correction |

## Run it

```bash
python3 skills/research-pro/scripts/score_readiness.py \
        tests/fixtures/readiness_filled.json --venue neurips
```

That fixture carries two failed gates against a 74.6/100 score, and reports
`NOT READY (gated)` — the score does not override the gate.
