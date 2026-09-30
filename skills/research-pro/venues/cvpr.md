# CVPR 2026

> Verified 2026-09-30 against <https://cvpr.thecvf.com/Conferences/2026/AuthorGuidelines>
> and the Call for Papers. Re-verify per `VERIFY.md`.

## Hard limits

| Rule | Value | Consequence |
|---|---|---|
| Main text | **8 pages** including figures and tables | **Rejected without review** |
| Excluded from limit | references only | — |
| Template | official CVPR style, from the author kit | **Rejected without review** |
| Anonymity | double-blind | **Rejected without review** |

Three independent ways to lose the paper before anyone reads it. Check all three
with `scripts/latex_lint.py --venue cvpr` and then check the compiled PDF by eye.

## Dual submission

Strict and actively enforced:

- No publication substantially similar in content — defined as **20% or more
  overlap** — may be under review anywhere else during the review period.
- Review period for this cycle: **2025-11-13 to 2026-02-20**.
- Violation means rejection **and a report to the other venue.**

If you have a related workshop paper or a journal submission in flight, compute the
overlap honestly before submitting. This is the rule authors most often break by
accident, and the consequence reaches beyond CVPR.

## What this venue rewards

- **Visual quality.** CVPR reviewers look at figures first and form a judgment
  before reading. A clean teaser, a legible architecture figure, and qualitative
  comparisons that show your method winning are worth real score.
- Strong quantitative comparison against the current state of the art on the
  standard benchmarks, with the same protocol.
- Ablations that isolate each contribution.
- Qualitative results including failure cases.

## What gets rejected here

- Any of the three desk-reject triggers above.
- Missing a baseline from the last two CVPR/ICCV/ECCV cycles. Reviewers know the
  field and notice immediately.
- Marginal gains within noise on saturated benchmarks, with no analysis.
- Cherry-picked qualitative figures, which reviewers detect by asking for more.
- Bad figures. This venue punishes them harder than any other.

## Notes

- The author kit at <https://github.com/cvpr-org/author-kit> is the authority on
  formatting; use the current cycle's version, since page counts shift with
  `.sty` revisions.
- CVPR's LLM policy has moved between cycles — re-verify it rather than assuming
  it matches NeurIPS or ICML.
