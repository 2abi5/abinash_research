# Worked example — Limitations

Required at ACL-family venues (desk reject without one). High return everywhere else.

## Before — ritual (reads as evasion)

> Our method may not generalize to all settings and datasets. Future work could
> explore additional domains. There are also some limitations related to
> computational cost that could be addressed in future work.

Three sentences, zero information. A reviewer reads this as "we did not think about
it", and then goes looking for the limitation you are hiding — which is worse than
anything you could have written.

## After — specific

> Our results are subject to three limitations. First, the expert bank is fixed at
> training time: adding an expert requires retraining the gate, which we have not
> evaluated, so the method does not suit settings where the label space grows after
> deployment. Second, the gate pools the full sequence before dispatch, which makes
> it unsuitable for streaming inference where the sequence is not yet complete; for
> that regime per-layer routing remains the right choice. Third, the 4× FLOP
> reduction is measured on an A100 with fused kernels at batch size 64; at batch size
> 1 the gate's overhead is no longer amortised and the reduction falls to 1.8×
> (Appendix C), which matters for single-request serving.

## What makes the difference

| Property | Why it matters |
|---|---|
| Each limitation names a **condition** | "when the label space grows", "batch size 1" — checkable |
| Each names a **consequence for whom** | "single-request serving", "streaming inference" |
| Two name **what to use instead** | this is generous and it signals command of the area |
| One reports a **number against yourself** | "falls to 1.8×" — an author who volunteers this is believed elsewhere |
| None is a missing experiment in disguise | a limitations section is a scope statement, not a confession |

## The line you must not cross

Do **not** relocate a required experiment here:

> ~~A limitation is that we did not compare against the current state of the art.~~

That is not a limitation. That is the reason the paper gets rejected, moved to page 8.
Run the comparison.

## Checklist

- [ ] Every item names a condition, not a mood
- [ ] Every item names who is affected
- [ ] At least one reports a number that is unflattering
- [ ] Nothing here is a missing experiment
- [ ] Nothing here contradicts a claim in the abstract
