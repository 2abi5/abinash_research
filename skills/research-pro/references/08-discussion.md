# Discussion and Limitations

The most skipped section and the most diagnostic one. Reviewers read it to find
out whether the authors understand their own result. A paper with no Discussion,
or one that only restates the results, reads as work that was measured but not
thought about.

## What a Discussion is for

Results say *what happened*. Discussion says *what it means*, and it is the only
place where you are licensed to reason beyond the measurements — as long as you
mark where the measurement stops and the reasoning begins.

Four moves, in this order:

**1. Interpretation.** Why did it come out this way? Give the mechanism, and tie
it to evidence. `The gain concentrates on rare classes (Fig. 4), consistent with
the gate assigning them to specialist experts; this also explains why the margin
narrows on ADE20K, where the class distribution is flatter.` That sentence does
real work: it explains a strength and a weakness with one mechanism.

**2. Relation to prior findings.** Does your result agree with the literature? If
it contradicts a published finding, say so directly and propose why — a
difference in protocol, scale, or data. Do not quietly disagree with a
well-known result; a reviewer who knows that result will assume you did not.

**3. Implications.** What can someone now do, or stop doing? Be concrete.
`Methods relying on per-layer routing can adopt a global gate without
architectural change` is an implication. `This opens exciting new directions` is
filler.

**4. Limitations and scope.** See below.

## Limitations

Several venues now **require** a limitations section and desk-reject papers
without one (all ACL-family venues, via ARR). Even where optional, it is one of
the highest-return paragraphs in the paper.

### Distinguish two kinds

- **Scope boundaries** — the setting your evidence covers. "Evaluated on English
  only." "Assumes calibrated camera intrinsics." "Tested to 7B parameters."
  These are honest and expected; state them plainly.
- **Technical defects** — something works worse than the alternative, or the
  method needs per-dataset tuning to hold up. These need care: state them, and
  state the conditions under which the method is still the right choice.

### How to write one that helps you

- **Specific, not ritual.** "Our method may not generalize to all settings" is
  worthless and reviewers read it as evasion. "Our method assumes the expert set
  is fixed at training time; adding experts requires retraining the gate, which
  we have not evaluated" is a real limitation, and it forecloses a reviewer's
  criticism by owning it first.
- **One sentence of consequence each.** What breaks, for whom.
- **Do not volunteer fatal flaws you have not actually got.** A limitations
  section is not a confession; it is a scope statement. If the limitation is
  "we did not compare against the state of the art," that is not a limitation,
  it is a missing experiment. Run it.
- **Do not bury a required experiment here.** Reviewers notice when a limitation
  is actually the paper's central gap relocated to page 8.
- **Mark the ones you plan to fix** and the ones that are intrinsic. That
  distinction is what "future work" should be made of.

### Template

```
Our results are subject to three limitations. First, <scope boundary>, so
<consequence for whom>. Second, <assumption>, which fails when <condition>; in
that regime <what to use instead>. Third, <cost or tradeoff>, which we measure at
<number> — acceptable for <use case> but not for <use case>.
```

## Negative and null results

If part of the work did not pan out, report it. A well-characterized negative
result — "attention sparsification did not help here, and here is why" — is often
the most-cited part of a paper, and hiding it makes the rest look selective.

## Threats to validity

In empirical software engineering, HCI, and social-science venues this is a named
subsection and is graded. Cover four:

- **Internal** — could something other than your manipulation explain the result?
- **External** — to what populations, datasets, or scales does it generalize?
- **Construct** — does your metric measure what you say it measures?
- **Conclusion** — is the statistical inference sound?

In ML venues the same content usually lives in Limitations. The categories are
still the right checklist.

## Future work

Two or three sentences, each a concrete next step someone could start on Monday.
Not a wish list. And never use it to imply that a missing experiment is optional:
"we leave a comparison to the state of the art to future work" invites rejection.

## Broader impact

ICML requires an impact statement; NeurIPS handles this through its checklist;
ACL-family venues have an optional ethics section. Write it as real analysis, not
boilerplate: who could be harmed, by what mechanism, what mitigations exist, and
which risks you are not able to mitigate. Generic paragraphs about "responsible
use of AI" are recognizable and count against the paper. See
`18-disclosure-and-ethics.md`.

## Checks

1. Does the Discussion say anything the Results section did not?
2. Is every interpretation tied to a specific figure, table, or section?
3. Is any reasoning beyond the evidence marked as such (`we hypothesize`,
   `this suggests`) rather than stated as established?
4. Are limitations specific enough to be checkable?
5. Is anything in Limitations actually a missing experiment?
6. Does any contradiction with the published literature go unaddressed?
7. Is the required limitations / impact section present for the target venue?
