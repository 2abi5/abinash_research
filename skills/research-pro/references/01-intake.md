# S0 — Intake

Fifteen minutes here saves a rewrite. The purpose is not to collect metadata; it
is to find out whether there is a paper, and if so, which paper.

## Ask these, in this order

Stop as soon as you have enough to write the spec. Do not interrogate.

**1. What did you find?** One sentence, no methods, no motivation. If the author
cannot produce it, that is the finding of the intake — the paper has no thesis
yet, and S1 is about building one, not about outlining sections.

**2. Why would a reviewer in your area not already know that?** This separates a
contribution from a competent engineering exercise. Push here. "Nobody has tried
it" is not an answer; "it was believed not to work because X, and X turns out to
be an artifact of Y" is.

**3. What do you already have?** Be concrete and get a list:
- Results: which datasets, which baselines, how many seeds, where the numbers live
- Code: runnable? by whom? on what?
- Figures: none, sketches, or final
- Prior text: notes, a draft, a rejected submission plus its reviews
- Data: yours, public, licensed, restricted, human-subjects

**4. Which venue and which deadline?** Both. "A good journal" is not a target.
The venue sets page budget, structure, anonymity, checklists, and what counts as
enough evidence. If undecided, offer two candidates with the trade-off named and
let them choose — this is `[AUTHOR DECISION]`.

**5. What is the weakest part?** Authors almost always know. Their answer tells
you where stage 9 will fail, months early.

**6. Who are the three reviewers?** Not names — the three research lines whose
authors will be asked to referee this. Their papers are the baselines you cannot
omit and the related work you cannot misrepresent.

## Ask only if relevant

- Human subjects / IRB status, if the work involves people or their data.
- Funding and conflicts, for the statements the venue will require.
- Author list and contribution split, if a CRediT statement is needed.
- Prior submission history — a resubmission is a different job (see
  `17-rebuttal.md`); reviewers may be the same people.
- Dual submission exposure: anything substantially overlapping under review
  elsewhere. Several venues treat ~20% overlap as a violation and will report it.

## Write the spec

Emit this, get it confirmed, then proceed to S1. It seeds the ledger.

```markdown
# Paper spec — <short name>
- **Finding (one sentence):** …
- **Why non-obvious:** …
- **Contribution type:** new task / new method / new module / new analysis /
  new dataset / negative or replication result / theory
- **Target venue:** <venue-year>  (page budget: N, anonymity: yes/no,
  required checklists: …)
- **Deadline:** YYYY-MM-DD  (working back: freeze results by …, draft by …,
  figures by …, internal review by …)
- **Claims (draft C1..Cn):** …
- **Evidence in hand:** …
- **Evidence missing:** …
- **Three reviewer lines:** …
- **Known weakest point:** …
- **Open author decisions:** …
```

## Read the paper type off the answers

The contribution type dictates structure, and structure dictates everything
downstream. Do not default to IMRaD for a method paper or to a method skeleton
for an analysis paper.

| Type | Load-bearing section | Where reviewers attack |
|---|---|---|
| New method | Method + ablations | "Why does it work?" and "is the baseline fair?" |
| New task / benchmark | Task definition + dataset construction + baselines | "Why does this task matter?" and "is the data sound?" |
| Empirical analysis | Experimental design | "Is the conclusion an artifact of your setup?" |
| Theory | Assumptions + proof | "Do the assumptions hold where it matters?" |
| Replication / negative | Protocol fidelity | "Did you implement the original faithfully?" |
| Position | Argument structure | "Is this argued or asserted?" |
| Survey / systematic review | Search and inclusion protocol | "Is the coverage complete and unbiased?" |

Then go to `02-architecture.md`.

## Honest intake outcomes

Say these plainly when true. Saying them now is a kindness; saying them at stage
9 is a waste of the author's months.

- *There is no contribution yet, there is a working system.* The paper needs an
  analysis that turns the system into a finding.
- *The contribution exists but the evidence does not.* Name the experiments
  needed before drafting starts; drafting first wastes the writing.
- *This is a workshop paper, not a main-conference paper.* Scope that reviewers
  would call incremental at NeurIPS can be a strong workshop contribution.
- *The deadline is not reachable.* If the missing experiments take six weeks and
  the deadline is in two, say so and name the next cycle.
