# S9 — Submission readiness score  ·  GATE 4

The final number, and the reason the ledger exists. A score computed from
impressions is a guess with a decimal point; this one is computed from artifacts.

## Rules

1. **Gates before score.** If Gate 1, 2, or 3 has failed, readiness is
   `NOT READY` regardless of what the dimensions sum to. A paper with a fabricated
   citation is not "87% ready."
2. **Every dimension scored from evidence**, with the artifact named. A dimension
   you cannot cite evidence for is scored from the ledger's gaps, not from optimism.
3. **Score the paper that exists.** Not the one the author intends to finish. If
   the ablation is planned but not run, experimental completeness reflects that.
4. **Report the weakest dimensions first.** The author needs the blockers, not the
   compliments.

## The ten dimensions

Each scored 0–10. Anchors at 0, 5, and 10; interpolate.

### 1. Contribution clarity and weight · default weight 12
- **0** No identifiable contribution beyond a working system.
- **5** A real contribution, but a reviewer could reasonably call it incremental; the
  "so what" is a higher number.
- **10** The paper states a finding a reviewer in the field did not know, non-obvious,
  with the reason it was not already known.

### 2. Claim–evidence integrity · default weight 16 (the heaviest)
- **0** Abstract claims with no corresponding experiments.
- **5** Main claims supported; one or two secondary claims overreach or are hedged
  into vagueness.
- **10** Every ledger claim maps to a named artifact at the rung the evidence
  supports; nothing hedged, nothing inflated.

### 3. Methodological soundness · default weight 12
- **0** A flaw that invalidates the result — test-set tuning, leakage, a broken
  protocol.
- **5** Sound, with an unstated assumption or an underspecified protocol.
- **10** All assumptions stated up front; protocol fully specified; a competent
  reader could find no hole.

### 4. Experimental completeness · default weight 12
- **0** One dataset, one weak baseline, no ablation.
- **5** Standard benchmarks and baselines present; ablations partial; single seed on
  close margins.
- **10** Strongest published baselines under a matched protocol, one ablation per
  mechanism, multiple seeds with dispersion, an out-of-distribution or scale probe,
  and a shown failure case.

### 5. Related work and positioning · default weight 8
- **0** A citation dump, or the closest competitor missing.
- **5** Organized by mechanism; the distinction from the nearest work is stated but
  not sharp.
- **10** Grouped by mechanism, closest work prominent and fairly described, and a
  distinction sentence a reviewer can check.

### 6. Writing clarity and prose quality · default weight 10
- **0** Reader cannot follow the argument; sections do not reverse-outline.
- **5** Followable; machine register, empty paragraphs, drifting terminology.
- **10** Every paragraph one message stated first; reverse-outlines cleanly; varied
  rhythm; stable terminology; no throat-clearing.

### 7. Figures and tables · default weight 8
- **0** Raster screenshots, unreadable type, `\hline`-stacked tables.
- **5** Adequate and correct; the teaser does not sell and there is no analysis figure.
- **10** Teaser lands in five seconds; architecture figure supports
  reimplementation; an analysis figure shows the mechanism; booktabs tables with
  direction marked; all vector, all generated from source.

### 8. Citation integrity · default weight 8 · **gated**
- **0** Any unverifiable reference. This forces `NOT READY`.
- **5** All references resolve and metadata is clean; layer-3 claim support spot-checked.
- **10** All three layers verified and logged, preprints upgraded, bibliography
  deduplicated, no uncited entries.

### 9. Reproducibility · default weight 8
- **0** No code, hyperparameters missing, results not traceable to runs.
- **5** Code exists; some hyperparameters implicit; numbers traceable with effort.
- **10** Code runs from a clean checkout, seeds and configs committed, every table
  cell regenerable from `results/`, environment pinned.

### 10. Venue compliance, ethics, and disclosure · default weight 6 · **gated**
- **0** Any desk-reject trigger live. Forces `NOT READY`.
- **5** Compliant on length and format; disclosure or a required statement thin.
- **10** Live-verified compliant, all required artifacts complete and consistent with
  the paper, disclosure accurate, anonymity clean in the PDF.

Weights come from `venues/registry.json` — `dimension_weights_default`, overridden
per venue by its `emphasis` list. TMLR pushes weight onto claim–evidence and
clarity; CVPR onto figures and experiments; AAAI and NeurIPS onto reproducibility.

## Hard gates

Any one of these forces `NOT READY` at any score:

| Gate | Condition |
|---|---|
| G-CITE | Any reference unverifiable, or any `MISMATCH` unresolved |
| G-CLAIM | Any abstract or introduction claim with no supporting evidence |
| G-VENUE | Any live desk-reject trigger: page limit, missing required section or checklist, anonymity leak, template violation |
| G-ETHICS | Required ethics/IRB approval absent where human subjects or restricted data are involved |
| G-INTEGRITY | Fabricated result, undisclosed AI use where policy requires disclosure, prompt injection present, or undeclared dual submission |
| G-TOKEN | Any `[NEEDS SOURCE]`, `[TBD]`, `[NEEDS EXPERIMENT]`, or `[VERIFY]` token left in the manuscript |

Gates are **not** author-overridable. The author may of course submit anyway — it is
their paper — but the report says `NOT READY` and names why, and that judgment stays
in the ledger.

## Bands

| Score | Band | Meaning |
|---|---|---|
| 90–100 | **Submit** | Nothing blocking. Remaining items are polish. |
| 80–89 | **Submit after the listed fixes** | Fixable in days. Competitive. |
| 70–79 | **Borderline** | Would likely draw a major-revision or weak-reject. Fix the two lowest dimensions first. |
| 55–69 | **Not ready** | Structural work needed: a missing experiment, unsupported claims, or a rewrite. |
| < 55 | **Not ready** | The paper needs a different plan, not another editing pass. |
| any | **NOT READY (gated)** | A hard gate failed. Score is reported but not the verdict. |

## Running it

```bash
python3 skills/research-pro/scripts/score_readiness.py paper/readiness.json \
        --venue neurips --strict
```

Fill `paper/readiness.json` from `templates/readiness.json`: a score, the evidence
you scored it from, and the gate states. The script applies venue weights, enforces
the gates, and emits the report. It refuses to score a dimension whose `evidence`
field is empty — which is the point.

## Report format

```markdown
# Readiness — <paper> → NeurIPS 2026 · 2026-09-30

## Verdict: NOT READY (gated)
Score 81/100 (band: submit after fixes) — but G-CITE failed.

## Blocking
1. **G-CITE** — 3 of 61 references unresolved: `zhang2024`, `patel2023`, `oss2025`.
   → Supply PDFs or remove. `out/citations.md` has the detail.
2. **G-TOKEN** — `[TBD]` at sections/04-experiments.tex:112 (Table 3, ADE20K column).

## Weakest dimensions
| Dim | Score | Weighted loss | Fix |
|---|---|---|---|
| Experimental completeness | 5/10 | -6.0 | Single seed on a 0.4-point margin (Tab.2). Run 3 seeds. |
| Figures | 6/10 | -3.2 | No analysis figure. Plot routing entropy per layer. |

## Strongest
Claim–evidence 9/10 · Methodological soundness 9/10

## If you submit as-is
Predicted reviewer objections, in the order they will arrive:
1. "The ADE20K margin is within noise." — true as written.
2. "Where does the gain come from?" — Tab.4 answers it; surface it in the abstract.
```

Predicting the reviewer objections is the most useful part of the report. Write
them in the reviewer's voice, and be specific enough that the author can pre-empt
each one.
