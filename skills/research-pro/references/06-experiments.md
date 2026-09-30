# S3 / Experiments — design the evidence, then write it

Two jobs in one file: **planning** the experiment set (do this before drafting)
and **writing** the section.

## Part A — the evidence plan

### Derive experiments from claims, not from availability

Take the ledger's claim list. Each claim gets an experiment whose result could
come out against you. An experiment that cannot fail is not evidence.

```markdown
| Claim | Experiment | Datasets | Baselines | Metric | Could falsify? | Status |
|---|---|---|---|---|---|---|
| C1 beats SOTA at equal FLOPs | main comparison | ImageNet, ADE20K | Kim24, Liu25, Wu25 | top-1 @ matched FLOPs | yes | done |
| C2 gain is from the gate | ablation: replace gate with random routing | ImageNet | — | top-1 delta | yes | done |
| C3 robust to shift | OOD eval | ImageNet-C/-R | Kim24 | mCE | yes | NEEDS EXPERIMENT |
```

Any claim whose row is empty is a claim that leaves the paper. This is the single
highest-leverage moment in the project: it is far cheaper to cut a sentence now
than to receive "the robustness claim is unsupported" from three reviewers.

### The three questions every reviewer asks

**1. Is it better than what exists?** — the comparison
- The strongest *published* baseline, not the convenient one. Omitting the
  current state of the art is noticed immediately.
- Identical protocol: same splits, same preprocessing, same budget, same tuning
  effort. Unequal tuning effort is the most common unfair comparison, and it is
  usually accidental.
- Report your reproduction of baseline numbers alongside their published numbers.
  A mismatch you explain is credible; one a reviewer finds is not.
- Match the cost axis. If your method uses more compute, parameters, or data,
  compare at matched cost — otherwise you have shown that more compute helps.

**2. Why is it better?** — the ablations
- One ablation per mechanism, changing exactly one thing.
- Report the delta, not just the absolute. `-2.1` is the finding.
- Prefer **replace** over **remove** where removal changes capacity: swapping the
  learned gate for random routing isolates the gate; deleting it also shrinks the
  model, confounding the result.
- Ablate interactions when modules are coupled — a 2×2 is worth the runs.
- Sweep the hyperparameter your method introduces. A method that works only at
  one value is fragile, and if you do not show the sweep, a reviewer will assume
  that is why.

**3. When does it fail?** — the boundary
- Out-of-distribution or harder setting.
- Scale in both directions: smaller and larger than your main setting.
- A named failure mode with a figure. Volunteering this *increases* trust; every
  reviewer knows there is one, and looks for the paper hiding it.

### Budget

Write the compute cost of the plan before running it. If the plan needs more than
the remaining time, cut claims now rather than discovering at the deadline that
the ablation table has holes.

## Part B — writing the section

### Structure

```latex
\section{Experiments}
\subsection{Setup}            % datasets, metrics, baselines, protocol, implementation
\subsection{Main results}     % the headline comparison
\subsection{Ablations}        % one per mechanism
\subsection{Analysis}         % why it works: the figure that shows the mechanism
\subsection{Limitations}      % or fold into Discussion
```

### Setup

Complete and boring. Per dataset: size, splits, license, preprocessing, and a
citation. Per metric: definition if not universal, and **direction** (`↑` / `↓`).
Per baseline: citation, and whether numbers are published or your reproduction.
Then the shared protocol — seeds, hardware, budget, what was tuned and where.

### Results prose

Never narrate the table. The table already contains the numbers; prose that
recites them wastes the page budget. Prose does three things a table cannot:

1. **State the finding.** `Our method improves top-1 by 2.4 points over the
   strongest baseline at matched FLOPs (Table 2).`
2. **Explain the mechanism.** `The gain concentrates on the long-tail classes
   (Fig. 4), consistent with the gate routing rare inputs to specialist experts.`
3. **Concede honestly.** `On ADE20K the margin narrows to 0.4 points, within seed
   variance; we attribute this to <reason>.`

Point 3 is not weakness. Reviewers trust a paper that reports where it is weak,
and disbelieve one that is uniformly triumphant.

### Ablation prose

Each ablation paragraph: what was changed, the delta, and the conclusion about
the mechanism. `Replacing the learned gate with random routing costs 3.1 points
(Table 4, row 2), while widening the MLP to match parameter count recovers only
0.4 — the gain comes from routing, not capacity.` That sentence is the paper's
causal claim, and it is worth more than the main results table.

### Analysis

The subsection that distinguishes a strong paper. Show *the mechanism operating*:
what the gate selects, where attention goes, how the loss landscape differs,
which examples move. One good analysis figure earns more reviewer trust than a
third dataset.

## Fatal flaws reviewers look for

| Flaw | How it is caught |
|---|---|
| Tuned on the test set | Split table has no validation set; or "best epoch" selected on test |
| Unequal tuning effort | Your method has a grid search, baselines get defaults |
| Missing current SOTA | Reviewer works in the area |
| Single seed for a sub-point margin | No dispersion reported |
| Cost mismatch presented as a win | Parameter/FLOP column missing |
| Ablation changing two things at once | Variant description mentions two changes |
| Cherry-picked qualitative figures | All examples are easy cases; no failures shown |
| Metric chosen post hoc | Metric differs from the field's standard with no justification |

## Checks

1. Does every ledger claim have an experiment row?
2. Is the strongest published baseline present and fairly tuned?
3. Is every mechanism ablated, isolating one variable?
4. Are seeds and dispersion reported where margins are small
   (`07-results-and-stats.md`)?
5. Is there at least one failure case shown?
6. Does any number in the prose disagree with the table? (Regenerate tables from
   `results/` and never hand-type.)
