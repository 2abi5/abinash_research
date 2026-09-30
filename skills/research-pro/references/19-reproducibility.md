# Reproducibility and artifacts

Reproducibility is weighed in acceptance decisions at ICML, enforced by checklist at
NeurIPS and AAAI, and asked about by every reviewer who intends to build on your
work. It is also the cheapest score in the readiness rubric to max out.

## The floor: what the paper must contain

A reviewer must be able to reimplement from the paper plus appendix, with no access
to your code.

- Every architecture dimension, layer count, and activation.
- **Every loss term and its weight.** The most common omission in ML papers.
- Optimizer, learning rate, schedule, warmup, weight decay, batch size, total steps
  or epochs.
- Initialization; the exact pretrained checkpoint by name and revision.
- Preprocessing and augmentation, in order, with parameters.
- Hardware, precision, and wall-clock, wherever cost is claimed.
- **What was tuned, on which split, over what search space.** Say "validation split,
  grid in Appendix B" — or a reviewer will assume you tuned on test.
- Number of runs and the seeds, or that seeds were unset (which is itself
  information).

## The artifact

```
repo/
├── README.md            # install, one command to reproduce Table 2, expected runtime
├── requirements.txt     # or environment.yml / pyproject.toml — pinned versions
├── configs/             # one config per reported experiment, named after the table
├── src/
├── scripts/
│   ├── reproduce_table2.sh
│   └── reproduce_fig4.sh
├── results/             # the raw outputs behind the paper's numbers
└── LICENSE
```

Rules that make the difference between an artifact people use and one they abandon:

1. **One command per reported result**, named after the table or figure it produces.
   `bash scripts/reproduce_table2.sh` is the single highest-value thing in the repo.
2. **Pin everything.** Unpinned dependencies mean the repo stops working within
   months, usually before the camera-ready.
3. **Commit the configs you actually ran**, not cleaned-up ones. A config that
   differs from what produced the number is worse than no config.
4. **Commit `results/`.** The raw outputs are the provenance of every table cell, and
   they let someone check your analysis without a GPU.
5. **State the compute cost.** "8×A100, 14 hours" tells a reader whether they can
   reproduce it at all. Report the total including failed runs where you can — it is
   honest and it is what reviewers ask about for environmental impact statements.
6. **A smoke test.** A tiny config that runs in two minutes on CPU and exercises the
   code path. Without one, nobody finds out the repo is broken until they have spent
   a day on setup.
7. **LICENSE.** Code with no licence is legally unusable, which defeats the purpose.

## Anonymized submission

Double-blind venues: submit the code itself, or an anonymized repository
(Anonymous GitHub, or a zip in supplementary). **Never a link to a named
repository** — it is an anonymity violation and it is one of the most common
avoidable desk rejections at ICML.

Check the code too: author names in file headers, institutional paths in configs,
internal cluster names in scripts, your username in a wandb URL, and identifying
data in committed logs.

## Determinism

Full bitwise determinism is often not achievable on GPU and you are not expected to
claim it. What you *are* expected to do:

- Set and report seeds.
- Report across-seed dispersion rather than implying a single number is exact.
- Note the known sources of nondeterminism (cuDNN autotuning, atomics, data loader
  ordering).
- Where a result is sensitive to seed, say so — that is a finding about your method.

## Checklists

NeurIPS, AAAI, and ARR each have one, and they are graded against the paper.

- Answer from the paper, not from intent.
- Where the honest answer is "no", answer "no" and give the reason. Area chairs
  respect this; an inconsistency between checklist and paper is what damages you.
- If answering a question reveals a gap, **fix the gap in the paper** rather than
  softening the answer. That is the checklist working as designed.

## Data

- Provenance for every dataset: source, licence, version, and how you obtained it.
- For new datasets: collection protocol, annotator instructions and compensation,
  inter-annotator agreement, known biases, intended and unintended uses. A datasheet
  is expected at several venues.
- Splits: exact, and released. "Random 80/10/10" is not reproducible without the seed.
- Where data cannot be shared, release everything else: the split indices, the
  preprocessing code, and a synthetic sample that exercises the pipeline.
