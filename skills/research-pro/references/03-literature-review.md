# S2 — Literature review methodology

Three different jobs wear this name. Do the right one.

| Job | Purpose | Output | Effort |
|---|---|---|---|
| **Scoping scan** | Is this idea already done? What are the baselines? | 15–40 papers, a one-page map | hours |
| **Related Work section** | Position *your* contribution | 2–4 groupings, 30–60 citations | days — see `04-related-work.md` |
| **Systematic review** | The review *is* the contribution | Protocol, PRISMA flow, extraction table, synthesis | weeks |

A systematic review's methods section is judged as rigorously as any
experimental methods section. If you cannot state your search string, you do not
have one.

## Never do this

Do not generate a reference list from memory. A model's recall of bibliographic
detail is unreliable in a specific and dangerous way: the titles are plausible,
the authors are real people in the right field, and the paper does not exist.
Fabricated citations survive into published literature at scale and they end
careers. Every entry gets verified against a real record — see
`13-citation-integrity.md`. Papers you have not verified are `[NEEDS SOURCE]`.

## A. Scoping scan

Fast, and enough for most method papers.

1. **Three seed papers.** The closest prior work you know, the strongest current
   baseline, and the most-cited survey in the area.
2. **Expand in both directions.** Backward: the seeds' reference lists.
   Forward: what cites the seeds (Semantic Scholar / Google Scholar "cited by").
   Forward citation chasing is what finds the paper published four months ago
   that scoops you.
3. **Stop rule.** Stop when a new paper's references contain nothing new to you.
   Usually 20–40 papers. If you are at 200, you are procrastinating.
4. **Map it**, not list it:

```markdown
| Paper | Year | Venue | Mechanism | Assumption it needs | Fails when | Baseline? |
|---|---|---|---|---|---|---|
| Kim+ | 2024 | CVPR | magnitude pruning | weights ~ importance | structured sparsity needed | yes, main table |
```

The `Fails when` column is the paper's actual product: read across it and your
gap statement writes itself. The `Baseline?` column becomes your main comparison
table, and any "no" needs a defensible reason.

### The three-question read

You cannot read 40 papers closely. Read each at the depth its role requires:

- **WHY papers** (2–5): the ones that define the problem. Read fully, including
  their limitations sections — that is where your contribution often already
  appears as an acknowledged open problem you can cite.
- **HOW papers** (5–15): direct competitors and baselines. Read method and
  experimental protocol closely. Note exact settings; protocol mismatch is the
  most common fatal flaw in a comparison table.
- **WHAT papers** (the rest): context and completeness. Abstract, figures,
  conclusion. Enough to cite accurately and not misrepresent.

Misrepresenting a paper you skimmed is worse than omitting it, and its author may
be your reviewer.

## B. Systematic review

Use when the review is the contribution, or the field demands it (clinical,
social science, software engineering). Write the protocol **before** searching,
and report deviations from it honestly.

### 1. Question

Structure it so that inclusion is decidable. In intervention fields, PICO:
Population, Intervention, Comparison, Outcome. In computing, an equivalent quad
works: Domain, Technique, Comparator, Measured outcome.

Bad: "How is deep learning used in medical imaging?" — undecidable, unbounded.
Good: "In adult chest radiograph classification (D), do transformer backbones (T)
outperform CNN backbones (C) on AUROC under identical training data (O)?"

### 2. Protocol — fix and record these before searching

- **Databases**, and why each: subject-specific (PubMed, ACM DL, IEEE Xplore,
  ACL Anthology, dblp), plus at least one broad index (Scopus, Web of Science,
  OpenAlex, Semantic Scholar). Google Scholar alone is not a protocol — it is not
  reproducible, results reorder, and coverage cannot be stated.
- **Preprints**: include or exclude, decided in advance. In fast-moving CS,
  excluding arXiv is a defensible choice only if stated; including it requires a
  note on unreviewed status.
- **Search string** per database, verbatim, with Boolean operators and
  truncation. Databases differ; record each translation.
- **Date range**, with justification (e.g. "from 2017, the year attention
  architectures entered this task").
- **Language**, and the bias that restriction introduces.
- **Inclusion / exclusion criteria**, each independently checkable.
- **Screening procedure**: how many screeners, independent or not, how conflicts
  resolve, and inter-rater agreement (Cohen's κ) if more than one.

Record the exact date each search ran. Databases change under you.

```markdown
## Search record
| DB | String | Date run | Hits |
|---|---|---|---|
| ACM DL | ("chest radiograph" OR "chest x-ray") AND (transformer OR "vision transformer") AND (classif*) | 2026-09-30 | 412 |
```

### 3. Screening and the PRISMA flow

Report counts at every stage. Reviewers check these numbers add up.

```
Identified:            n = 1,248   (ACM 412, IEEE 383, Scopus 388, arXiv 65)
Duplicates removed:    n =   287
Title/abstract screen: n =   961  →  excluded 812
Full-text screen:      n =   149  →  excluded  96  (with reasons, tabulated)
Included:              n =    53
  + snowball additions:      7
Final:                 n =    60
```

Every full-text exclusion needs a recorded reason, grouped: wrong population,
wrong outcome, no comparator, insufficient reporting, not retrievable. "Not
retrievable" counts and must be reported, not silently dropped.

### 4. Extraction

One row per study, columns fixed in the protocol. Extract into a spreadsheet,
not into prose — prose extraction guarantees inconsistency across 60 papers.

Always: citation, year, venue, peer-review status, population/dataset, n,
technique, comparator, outcome metric, effect size with dispersion, funding
source, code availability, and your risk-of-bias rating.

### 5. Quality appraisal / risk of bias

Use the instrument your field expects; do not invent one. Common: ROBINS-I and
Cochrane RoB 2 (interventions), QUADAS-2 (diagnostic accuracy), Newcastle-Ottawa
(observational), CLAIM (medical AI reporting), and in computing the
empirical-standards checklists per study type.

Rate per domain, not as one global score, and report the distribution. A review
that finds 40 of 60 studies at high risk of bias has found something — report it
as a finding, and do not pool results across it as if it were not there.

### 6. Synthesis

Choose deliberately and say which you chose:

- **Narrative synthesis** — when studies are too heterogeneous to pool. Group by
  mechanism or population, not by year. Chronological ordering conveys nothing.
- **Vote counting** — counts of positive/negative findings. Weak, and it ignores
  effect size and sample size; use only with that caveat stated.
- **Meta-analysis** — only when outcomes are commensurable. Then: effect size
  with CI per study, a pooled estimate under a random-effects model unless you
  can justify fixed-effects, heterogeneity (I², τ²), a forest plot, and a funnel
  plot or Egger test for small-study effects. Pooling incommensurable outcomes
  produces a confident number that means nothing.

State explicitly what the evidence does **not** support. A review whose every
finding is positive has a publication-bias problem it has not addressed.

### 7. Report

Follow PRISMA 2020 (reviews of interventions) or the reporting standard your
field uses, and include the item checklist. Register the protocol where the field
expects it (PROSPERO for health). Publish the search strings and extraction table
as supplementary material — a review whose search is not reproducible is an
opinion piece with a large reference list.

## Turning the review into the paper

The map from B or A feeds two different sections, and the difference matters:

- **Related Work** answers "how is my contribution different?" — organized by
  mechanism, ending in your distinction. See `04-related-work.md`.
- **Introduction paragraph 2–3** answers "why is the gap real?" — organized as a
  chain that terminates in exactly the failure your method fixes. See
  `09-abstract-title-intro.md`.

Same papers, different jobs, different orderings. Writing one and pasting it into
the other's slot is visible immediately.

## Common criticisms, and how to not earn them

| Reviewer says | Root cause | Fix |
|---|---|---|
| "Missing relevant work" | No forward citation chasing | Chase citations of your seeds; check the last two cycles of the target venue |
| "Misrepresents [X]" | Cited from the abstract | Read the method of anything you characterize |
| "Search is not reproducible" | Google Scholar only, no strings recorded | Named databases, verbatim strings, dates |
| "Cherry-picked" | No protocol, criteria written after seeing results | Write criteria first, report deviations |
| "Just a list" | Grouped by year or by author | Group by mechanism; end each group with the limitation that matters to you |
| "Conclusions exceed the evidence" | Pooled heterogeneous studies | Report heterogeneity; downgrade the claim |
