# Method

The reader must finish this section able to reimplement the work and able to say
*why each part is there*. Those are two different requirements and most drafts
satisfy only the first.

## Before writing: the module table

Do not start prose until this table is complete. It is the section's outline, and
filling it exposes modules that exist for no reason.

| Module | What it does (input → output) | Why it is needed | Why it works |
|---|---|---|---|
| Routing gate | token embeddings → expert index | per-layer routing decides before context resolves | global pooling gives the gate full context before committing |

A module whose "why it is needed" is blank is a module to cut. A module whose
"why it works" is blank is an ablation you have not run — mark it
`[NEEDS EXPERIMENT]`.

## Draw the architecture figure first

The figure fixes the section's structure: one subsection per box, in dataflow
order. Drawing it first prevents the most common structural failure — a Method
section ordered by the history of your implementation rather than by the flow of
the data. See `11-figures-tables.md`.

## Section skeleton

```latex
\section{Method}
\subsection{Overview}          % setting, notation, figure pointer, roadmap
\subsection{<Module 1>}        % motivation → design → advantage
\subsection{<Module 2>}
\subsection{Training}          % objective, losses and their weights, schedule
\subsection{Implementation details}   % or move to appendix if tight
```

### Overview

Four moves, about one paragraph:

1. Formalize the problem: given input $x \in \mathcal{X}$, produce $y$, under
   assumptions A1–A2. State assumptions here, once, plainly. Hiding an
   assumption until the experiments is how papers get rejected in rebuttal.
2. Name the core idea in one sentence, concretely.
3. Point to the architecture figure.
4. Road-map the subsections in one sentence — "§3.2 describes the gate, §3.3 the
   expert set, §3.4 the training objective."

### Each module: three parts, in this order

**Motivation (1–3 sentences).** Problem-driven. `A remaining difficulty is
<problem>. Prior approaches handle this by <approach>, which <fails how>.` The
reader must want this module before they read its mechanics.

**Design (the bulk).** Precise and ordered:

- Define structures first: representation, network shape, data structure,
  dimensions.
- Then the forward pass in strict execution order: `Given <input>, we first
  <step>, then <step>, finally <step>, producing <output>.`
- Every symbol defined at first use. Every dimension stated.
- Equations numbered only if referenced later. Every equation followed by a
  sentence of interpretation — never leave one to speak for itself.

**Advantage (1–2 sentences).** Why this design beats the obvious alternative, and
preferably in measurable terms: `Because the gate sees pooled context, it needs
one decision per sequence rather than one per layer, reducing routing overhead
from O(LN) to O(N) (Table 4).`

## Reproducibility floor

A reviewer must be able to reimplement from the paper plus appendix. Specify:

- Every architecture dimension and layer count.
- Every loss term **and its weight**. Unstated loss weights are the most common
  reproducibility gap in ML papers.
- Optimizer, learning rate, schedule, batch size, epochs or steps, warmup.
- Initialization and any pretrained checkpoint, named exactly.
- Preprocessing and augmentation, in order, with parameters.
- Hardware and precision, if runtime or memory is claimed.
- What is tuned, on what split, over what search space. "Tuned on the test set"
  is fatal; "tuned on validation, search space in App. B" is fine.

Appendix is fine for the details. Missing is not.

## Notation

- One symbol, one meaning, whole paper.
- Follow your field's conventions; do not rename $\theta$ to be distinctive.
- A notation table in the appendix once you pass roughly ten symbols.
- Do not overload subscripts to save space. `$h_{i}^{(l,t)}$` costs the reader
  more than a sentence would.

## Failure modes

| Symptom | Why it is fatal | Fix |
|---|---|---|
| Modules listed with no motivation | Reads as architecture search, not insight | Add the problem each module answers |
| Section ordered by implementation history | Reader cannot follow dataflow | Reorder to match the figure |
| Equations with no interpretation | Reader skips them; reviewer assumes you did too | One sentence of meaning after each |
| Assumptions revealed in experiments | Reviewer feels misled and re-reads hostilely | State all assumptions in §3.1 |
| Novel-sounding names on standard parts | Reads as novelty inflation | Call a residual connection a residual connection |
| "Details in the supplementary" for load-bearing content | Reviewers may not read it; page limit is not an excuse for the core | Keep the core mechanism in the main text |

## Checks

1. Could a competent graduate student implement this from the text?
2. Does every module have design, motivation, and advantage?
3. Does every claimed advantage have a planned ablation?
4. Does the prose order match the figure order?
5. Are all assumptions stated in the overview?
6. Is every symbol defined before use, and used consistently?
