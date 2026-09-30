# Codebase to paper

"Open the repo, write the paper." The right version of this is not generating prose
about code — it is **grounding the paper in artifacts that exist**, so every number,
hyperparameter, and method claim traces to a file and a commit.

Done properly, this is the highest-leverage entry point in the suite, because it
removes the two things that sink papers written from memory: hyperparameters that
disagree with what was run, and claims about experiments nobody actually ran.

## Scan first

```bash
python3 skills/research-pro/scripts/repo_scan.py . --out paper/provenance.json
```

It inventories:

| Found | Feeds |
|---|---|
| Config files (`configs/`, `*.yaml`, `*.json`, argparse defaults) | Method §, implementation details, reproducibility checklist |
| Result files (`results/`, `*.csv`, `*.json`, tensorboard/wandb logs) | Every table cell, with provenance |
| Metric names logged in code | The metrics you can honestly report |
| Seeds set in code or configs | The seed/dispersion story |
| Dataset loaders and paths | Datasets §, licensing questions |
| Baseline implementations or references | The comparison table, and what is missing |
| Model definitions, layer/dim counts | Architecture figure and Method § |
| Loss terms and their weights | Method § — the most commonly omitted detail |
| `requirements.txt` / lockfiles | Environment reporting |
| Git log dates and tags | Timeline, and which commit produced which result |
| README / notes | The author's own account of what the code does |

## Then reconcile — this is the part that matters

The scan produces claims-in-waiting. Check each against the paper's intended story
and report every mismatch **to the author**, before drafting:

| Mismatch | Why it is dangerous |
|---|---|
| A hyperparameter in the paper differs from the config that produced the result | The number in the table is not reproducible from the stated setup. Reviewers who try will find out |
| A metric reported in the paper is not computed anywhere in the code | The number came from somewhere else, or from a different version. Find out which |
| A baseline in the comparison table has no implementation and no cited published number | Either cite the published number explicitly or run it |
| An ablation described in the paper has no config | It was not run. Mark `[NEEDS EXPERIMENT]` |
| `results/` has runs the paper does not report | Ask why. If they are worse, selective reporting is a serious problem; if they are irrelevant, fine |
| The dataset loader applies preprocessing the paper does not mention | Undisclosed preprocessing is a protocol difference, and it invalidates comparisons |
| Seeds are unset in the code but the paper reports variance | The variance came from something else |

**Never paper over a mismatch.** Report it plainly. This is the single most valuable
thing this stage does: it catches, before submission, the discrepancies that reviewers
and reproducers catch afterwards.

## What the code can and cannot tell you

**Can:** what was implemented, what was configured, what was run, what was measured,
in what order, and when.

**Cannot:** why it matters, what the contribution is, whether the comparison is fair,
or whether the result is interesting. Those come from the author, through
`01-intake.md`. A paper written from the code alone documents an implementation; it
does not make an argument, and reviewers reject implementations.

So the order is: **intake first, scan second.** The author says what they found; the
scan establishes what the artifacts support. Where the two disagree, that is the
conversation to have.

## Drafting from provenance

Once reconciled:

- **Method §** — architecture from the model definition, losses and weights from the
  loss module, training from the config. Every number in implementation details cites
  a config path in the ledger.
- **Experiments setup** — datasets from the loaders, splits from the split logic,
  metrics from the metric code, protocol from the run scripts.
- **Tables** — generated from `results/` by `make_tables.py`. Never hand-typed. This
  is where the provenance chain pays off: a re-run updates the paper.
- **Reproducibility statement / checklist** — answerable directly and honestly from
  the scan, which is why this stage makes checklist sections cheap.
- **Ablation table** — one row per config in `configs/ablations/`. Configs with no
  corresponding row are unreported results; rows with no config are unrun
  experiments. Both need explaining.

## Provenance in the ledger

Every table cell should be traceable in three hops:

```
Table 2, row "Ours", col "top-1"
  → results/imagenet/ours_seed{0,1,2}.json
  → configs/imagenet/ours.yaml
  → commit a3f9c21
```

Record this mapping. When a reviewer asks "what settings produced Table 2?", the
answer is one lookup instead of an afternoon of archaeology. When a number changes
because you re-ran something, you know every place in the paper that must change.

## Honest boundaries

- Code that exists is not a result. A script that *can* run the ablation is not the
  ablation; only an entry in `results/` is.
- Do not infer a result's value from a config's defaults.
- Do not describe code paths the experiments did not exercise as part of the method.
  Dead options in a config file are not contributions.
- If the repository is a research sandbox with no configs and no saved results —
  which is common and not a criticism — say so, and the first deliverable is not a
  draft. It is a reproduction script that regenerates the paper's numbers. Without
  it, every number in the paper is unverifiable, including to the author.
