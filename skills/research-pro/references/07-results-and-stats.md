# Results and statistical rigor

Most rejections that cite "weak evaluation" are not about missing experiments.
They are about numbers whose reliability cannot be assessed.

## Seeds and dispersion

- **Report the number of runs.** One run is an anecdote. Three is a minimum for
  any comparison; five or more where variance is known to be high (RL, small
  datasets, fine-tuning).
- **Report dispersion, always**: mean ± standard deviation, or median with
  interquartile range for skewed outcomes. State which you used.
- **Compare like with like.** Your mean against a baseline's single published
  number is not a comparison. Either reproduce the baseline under your seed
  protocol or mark clearly which numbers are single-run published values.
- **A margin smaller than the standard deviation is not an improvement.** Saying
  so yourself costs one sentence; having a reviewer say it costs the paper.

## Significance, used properly

Significance testing is appropriate when comparing methods across a set of test
items or across runs, and it is routinely misapplied.

- Pick the test for the design: paired items → paired bootstrap or Wilcoxon
  signed-rank; independent runs → Welch's *t*-test or Mann-Whitney; several
  methods on several datasets → Friedman with a post-hoc Nemenyi, not a pile of
  pairwise *t*-tests.
- **Correct for multiple comparisons** when testing many pairs (Holm-Bonferroni,
  or Benjamini-Hochberg when controlling false discovery). Twenty uncorrected
  comparisons produce a "significant" result by construction.
- **Report effect size with the *p*-value.** A *p* of 0.03 on a 0.1-point
  difference is a statement about your sample size, not about your method.
- Prefer confidence intervals to bare *p*-values: they carry the magnitude and
  the uncertainty together.
- Never write "significant" in a paper with no test in it. Use "consistent" or
  "larger" if you did not test.

## Numbers in tables

- Consistent precision within a metric column. If seed variance is ±0.4, three
  decimal places are noise pretending to be precision.
- Never report more digits than your dispersion justifies.
- Direction in the header: `PSNR ↑`, `FID ↓`, `mCE ↓`.
- Units in the header, not in cells.
- Mark best and second-best, and say in the caption how you marked them.
- If a cell is a reproduction rather than a published number, mark it and explain
  the convention in the caption.
- Missing entries: `—` with a reason in the caption. A blank cell reads as
  something hidden.

## Aggregation honesty

- State how multi-dataset averages are computed — macro over datasets, or
  weighted by size. They differ, sometimes decisively.
- Do not average across incommensurable metrics.
- Report per-dataset results as well as the average. An average hiding one large
  regression is the thing reviewers hunt for.
- If a result is excluded, say so and why, in the paper — not in a rebuttal.

## Efficiency claims

Efficiency claims are held to a specific standard because they are so easy to
get wrong:

- Wall-clock **and** hardware, batch size, precision, implementation, and whether
  compilation or fused kernels are used.
- FLOPs or parameter counts stated with what is counted (embeddings? optimizer
  state? activation memory?).
- Compare against a baseline's optimized implementation, not its reference code.
  "We are 3× faster than the authors' unoptimized script" is not a contribution.
- Amortized versus per-sample cost, stated explicitly, including preprocessing and
  any training-time overhead your method adds.

## Human evaluation

If humans rate outputs: number of raters, recruitment and compensation, the exact
instructions given, inter-rater agreement (κ or α), and the statistical test over
ratings, not over raw means. Ethics approval where required. A human evaluation
reported without agreement statistics carries no weight.

## LLM-as-judge

If a model scores outputs: name the model and version, give the full prompt,
report position/verbosity bias controls, and validate against human judgment on
a sample. Report the agreement. An unvalidated model judge is not a measurement;
it is an opinion generated at scale.

## What never appears

- A number the author did not produce. Empty cells are `[TBD]`.
- "Significantly better" with no test.
- "Results will improve with more tuning." Either tune or do not claim.
- A metric introduced without definition because it makes the method look good.
- A comparison against a baseline you did not actually run and did not cite
  numbers for.

## Checks

1. Number of runs and dispersion reported for every headline comparison?
2. Any margin within noise described as an improvement?
3. Multiple comparisons corrected?
4. Effect sizes reported alongside significance?
5. Per-dataset numbers present, not only the average?
6. Every table cell traceable to a file in `results/`?
7. Efficiency claims fully specified as to hardware and implementation?
