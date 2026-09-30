# Title, Abstract, Introduction

The first page decides most outcomes. A reviewer assigned six papers forms a
prior on yours from the title, the abstract, and the teaser figure, and then
reads the rest looking for confirmation. Write these last, revise them most.

## Title

- Name the contribution, not the topic. `Attention Is All You Need` and
  `Deep Residual Learning for Image Recognition` both state a finding.
- Twelve words or fewer. No acronym the field does not already know. No colon
  stacking two vague halves.
- A method name is worth having if it is short, pronounceable, and not already
  taken — check that it is not another paper's or product's name.
- No hype words: novel, powerful, comprehensive, revolutionary. Reviewers
  discount them.

## Abstract

150–250 words for most conferences (Nature's summary paragraph ~200; check
`venues/<venue>.md`). It is not a summary of the paper — it is the argument in
miniature, and it must stand alone.

### Structure: six sentences

```
1. TASK       What problem, one sentence, no history.
2. CHALLENGE  Why existing methods fall short — with the technical reason.
3. INSIGHT    The observation that makes it fixable.   (optional, powerful)
4. METHOD     What you built, named, concretely.
5. EVIDENCE   The headline number against the strongest baseline, on named data.
6. SO WHAT    What a reader now knows.                  (optional)
```

Three patterns, choose by contribution shape:

- **Challenge → contribution** — one mechanism, cleanest. Sentences 1,2,4,5.
- **Challenge → insight → contribution** — when the insight is the real
  contribution and the mechanism merely implements it. Sentences 1,2,3,4,5.
- **Multiple contributions** — two or three, each paired immediately with its
  advantage. Use only when they are genuinely independent.

### Rules

- **Name the mechanism.** "We propose a novel framework for adaptive
  representation learning" tells a reviewer nothing and signals evasion. "We
  route tokens through a single global gate instead of per-layer gates" tells them
  everything.
- **One number, the right one.** The headline result against the strongest
  baseline, on a dataset the reader recognizes. Not five numbers; not a percentage
  with no baseline.
- **No citations, no acronyms undefined, no forward references** ("as shown in
  §4"). It must work standing alone in a search result.
- **Every claim here goes in the ledger.** The abstract is where overreach
  concentrates, and it is the first thing reviewers check against the results.
- **Never begin with "In recent years"** or "With the rapid development of."
  These openers waste the most valuable sentence in the paper.

## Introduction

One to one-and-a-quarter pages, five paragraphs. It is the spine from
`02-architecture.md`, expanded.

### The five paragraphs

**P1 — Task and stakes.** What the problem is and why it matters, in two or three
sentences, with concrete applications rather than a gesture at importance. Two
openings work: define the task then give applications (if the task is niche), or
lead with the application (if the task is familiar). A third, stronger when you
can pull it off: open with the task *and* expose the failure immediately, so the
challenge is visible on line three.

**P2 — Prior work leads to the challenge.** Not a survey. A chain that terminates
at exactly the failure your method fixes: `Traditional methods <do X> but
<limit>. Recent methods <do Y>, which addresses that, but they <fail> because
<technical reason>.` The last clause of this paragraph is the paper's hinge — it
must name the reason, not just the symptom.

**P3 — Your method.** `We propose <name>, which <mechanism>.` Then: the insight
in one sentence, the pipeline in two or three (`Specifically, ...`), and the
advantage (`In contrast to prior methods, ours ...`). Point to the teaser figure.
Be concrete. This paragraph is where mystery framing kills papers.

**P4 — Evidence.** Two or three sentences: datasets, headline margins against the
strongest baselines, and the one ablation that establishes causality. No table
here, but real numbers.

**P5 — Contributions.** Three or four bullets, each `contribution → advantage`.
Not "we propose a method" — "we propose X, which enables Y, measured as Z."

### Do not

- Do not open with a naive baseline and describe your improvement on it. It makes
  the strongest work look incremental.
- Do not spend P1 and P2 on background before the problem appears. If the
  challenge is not visible by the end of P2, restructure.
- Do not promise what the paper does not deliver. Every promise here is a claim in
  the ledger, and the readiness gate will check it.
- Do not use the Introduction as a Related Work section. Group prior work by
  mechanism in §2; here, only the chain that leads to your gap.

## The teaser figure

The first figure, top-right of page 1. Its job: make the reader understand the
idea and want the paper, in five seconds, from the figure and caption alone.
Either the problem (a striking failure case of prior work next to your result) or
the idea (the mechanism, abstracted). Never a system diagram at this position —
that is the architecture figure and it belongs in §3. See
`11-figures-tables.md`.

## Checks

1. Does the abstract name the mechanism concretely?
2. Does the abstract's number appear in a table, matching exactly?
3. Is every abstract and introduction claim in the ledger with evidence?
4. Does P2 end with a technical *reason*, not just a symptom?
5. Can the teaser figure plus caption be understood alone?
6. Is every contribution bullet paired with an advantage?
7. Does the title state a finding rather than a topic?
