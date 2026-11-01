# S2 — Literature review methodology

Three different jobs wear this name. Do the right one.

| Job | Purpose | Output | Effort |
|---|---|---|---|
| **Scoping scan** | Is this idea already done? What are the baselines? | 15–40 papers, a one-page map | hours |
| **Related Work section** | Position *your* contribution | 2–4 groupings, 30–60 citations | days; see `04-related-work.md` |
| **Systematic review** | The review *is* the contribution | Protocol, PRISMA flow, extraction table, synthesis | weeks |

A systematic review's methods section is judged as rigorously as any experimental
methods section. If you cannot state your search string, you do not have one.

Templates for every artifact below are in `templates/lit-review.md`.

## Never do this

Do not generate a reference list from memory. A model's recall of bibliographic
detail is unreliable in a specific and dangerous way: the titles are plausible, the
authors are real people in the right field, and the paper does not exist. Fabricated
citations survive into published literature at scale and they end careers. Every
entry gets verified against a real record; see `13-citation-integrity.md`. Papers
you have not verified are `[NEEDS SOURCE]`.

The scanner below produces *leads*. A lead becomes a citation only after you have
opened it, read it at the depth its role requires, and `verify_citations.py` has
resolved it.

## A. Scoping scan

Fast, and enough for most method papers.

### 1. Seeds

Two to five papers. Choose them by role, not by fame:

- the **closest prior work** (what a reviewer will say you are a variant of),
- the **strongest current baseline** (what your main table must beat),
- the **most-cited survey** in the area (its reference list is a free backward pass),
- optionally the **paper that would scoop you**: search for it by the mechanism you
  are about to propose, phrased three ways. If it exists, better to know now.

### 2. Expand in both directions

```bash
python3 skills/research-pro/scripts/lit_scan.py \
    --seed 10.1000/closest.2023 --seed arXiv:2401.01234 --seed W2000000001 \
    --search "global gating pooled context mixture of experts" --since 2019 \
    --sentinels 10.1000/known-relevant.2024 \
    --mailto you@university.edu --out lit/
```

Backward: everything the seeds cite (the field they stand on). Forward: everything
that cites the seeds (what came after). **Forward citation chasing is what finds the
paper published four months ago that scoops you.** Google Scholar's "cited by" does
this by hand; OpenAlex does it in one call and records the query, the date and the
hit count for the search record.

Read `lit/candidates.md` in this order:

1. **Links ≥ 2** first. A paper connected to several of your seeds is in your
   neighbourhood whatever its citation count. Relation `both` (cites a seed and is
   cited by one) is the strongest signal.
2. **The retraction flag.** A `⚠ RETRACTED` candidate is a trap, especially if it is
   someone's baseline.
3. **High `cited by`, one link**: probably a foundation paper to cite in the
   introduction, not a competitor.
4. **Recent, few citations, one link**: probably concurrent work. Read the abstract
   now; decide later.

### 3. Stop rule, measured

The table `Saturation` reports how many *new* candidates each seed added. Stop adding
seeds when a new seed adds nothing you had not seen. Typical scans converge at 20–40
papers worth reading. If you are at 200, you are procrastinating; if the last seed
still added forty, the seeds are from different fields and you have two scans.

`Sentinel recall` answers the other question: did the scan reach the papers you
already know matter? Give `--sentinels` two or three known-relevant DOIs. A sentinel
the seeds do not reach means the seeds sit in the wrong neighbourhood, and a search
that misses what you already know will miss what you do not.

### 4. The three-question read

You cannot read 40 papers closely. Read each at the depth its role requires, and
write a reading note (template in `templates/lit-review.md`) for everything you will
characterise in the paper:

- **WHY papers** (2–5): the ones that define the problem. Read fully, including the
  limitations sections; that is where your contribution often already appears as an
  acknowledged open problem you can cite.
- **HOW papers** (5–15): direct competitors and baselines. Read method and
  experimental protocol closely. Note exact settings; protocol mismatch is the most
  common fatal flaw in a comparison table.
- **WHAT papers** (the rest): context and completeness. Abstract, figures,
  conclusion. Enough to cite accurately and not misrepresent.

Misrepresenting a paper you skimmed is worse than omitting it, and its author may be
your reviewer. The reading note is what lets you write "Kim et al. assume weight
magnitude predicts importance (§3.1)" with a location you can defend, and it is the
row you will later copy into the ledger's layer-3 log.

### 5. Map it, not list it

The scanner writes `lit/map.md` with the top candidates pre-filled and the columns
that matter empty. Fill them from the reading notes:

```markdown
| Paper | Year | Venue | Depth | Mechanism | Assumption it needs | Fails when | Baseline? | Verified (key) |
|---|---|---|---|---|---|---|---|---|
| Kim+ | 2024 | CVPR | HOW | magnitude pruning | weights ~ importance | signal is input-dependent | yes, main table | kim2024pruning |
```

The `Fails when` column is the map's actual product: read down it and the gap
statement writes itself (`examples/05-lit-map-to-gap.md` shows the move). The
`Baseline?` column becomes your main comparison table, and any "no" needs a
defensible reason written in the cell. `Verified (key)` stays `[NEEDS SOURCE]` until
`verify_citations.py` has resolved the entry.

Snowball additions found by hand go in the same table with `hand` in the Depth column
so the search record stays honest about what the protocol found and what you did.

## B. Search strings

Needed for a systematic review; useful for the `--search` arm of a scoping scan.
Build them, do not improvise them.

1. **Concept blocks.** Decompose the question into two to four concepts (for a
   computing question: domain, technique, comparator, outcome). One block per
   concept.
2. **Synonyms inside a block**, joined by OR: harvest them from the seeds' titles,
   abstracts and keyword fields, and from the thesaurus the database offers (MeSH,
   ACM CCS, IEEE thesaurus). Include spelling variants and the field's older name.
3. **Truncation and phrases.** `classif*` for classify/classification/classifier;
   quotes for multi-word terms. Each database has its own wildcard rules; record the
   translation.
4. **Blocks joined by AND.** Rarely more than three ANDs; a fourth usually encodes
   an inclusion criterion that belongs in screening, not in the search.
5. **Field tags** where the database supports them (title/abstract/keywords), so a
   stray word in a reference list does not produce a hit.
6. **Test for recall** against the sentinel papers: a string that does not retrieve
   the five papers you already know are relevant is a wrong string, whatever its hit
   count. Then test for precision on the first fifty hits; below one relevant in ten,
   tighten a block.
7. **Record verbatim**, per database, with the date and the hit count. Databases
   change under you.

```markdown
| DB | String | Date run | Hits |
|---|---|---|---|
| ACM DL | ("chest radiograph" OR "chest x-ray") AND (transformer OR "vision transformer") AND (classif*) | 2026-09-30 | 412 |
```

Google Scholar alone is not a protocol: it is not reproducible, results reorder, and
coverage cannot be stated. Use it as a snowball tool and record it as one.

## C. Systematic review

Use when the review is the contribution, or the field demands it (clinical, social
science, software engineering). Write the protocol **before** searching, and report
deviations from it honestly.

### 1. Question

Structure it so that inclusion is decidable. In intervention fields, PICO:
Population, Intervention, Comparison, Outcome. In computing, an equivalent quad
works: Domain, Technique, Comparator, Measured outcome.

Bad: "How is deep learning used in medical imaging?" Undecidable, unbounded.
Good: "In adult chest radiograph classification (D), do transformer backbones (T)
outperform CNN backbones (C) on AUROC under identical training data (O)?"

### 2. Protocol: fix and record these before searching

- **Databases**, and why each: subject-specific (PubMed, ACM DL, IEEE Xplore, ACL
  Anthology, dblp), plus at least one broad index (Scopus, Web of Science, OpenAlex,
  Semantic Scholar).
- **Preprints and grey literature**: include or exclude, decided in advance. In
  fast-moving CS, excluding arXiv is a defensible choice only if stated; including it
  requires a note on unreviewed status and a plan for the version that later gets
  published.
- **Search strings** per database, verbatim (section B).
- **Date range**, with justification ("from 2017, the year attention architectures
  entered this task").
- **Language**, and the bias that restriction introduces.
- **Inclusion / exclusion criteria**, each independently checkable by a second
  person.
- **Screening procedure**: how many screeners, independent or not, how conflicts
  resolve, and inter-rater agreement (Cohen's κ) if more than one. Pilot the criteria
  on twenty records first and revise them before the real screen.
- **Extraction form**, piloted on five included papers before the rest; the columns
  you did not think of appear in the pilot.
- **Sentinels**: the known-relevant papers the search must retrieve.

Register the protocol where the field expects it (PROSPERO for health; OSF
elsewhere). Record the exact date each search ran.

### 3. Screening and the PRISMA flow

Report counts at every stage. Reviewers check that these numbers add up.

```
Identified:            n = 1,248   (ACM 412, IEEE 383, Scopus 388, arXiv 65)
Duplicates removed:    n =   287
Title/abstract screen: n =   961  →  excluded 812
Full-text screen:      n =   149  →  excluded  96  (with reasons, tabulated)
Included:              n =    53
  + snowball additions:      7
Final:                 n =    60
```

Every full-text exclusion needs a recorded reason, grouped: wrong population, wrong
outcome, no comparator, insufficient reporting, not retrievable. "Not retrievable"
counts and must be reported, not silently dropped. Keep the screening log (template)
as supplementary material.

### 4. Extraction

One row per study, columns fixed in the protocol. Extract into a spreadsheet, not
into prose; prose extraction guarantees inconsistency across sixty papers.

Always: citation key (verified), year, venue, peer-review status, population or
dataset, n, technique, comparator, outcome metric, effect size with dispersion,
funding source, code availability, and your risk-of-bias rating per domain.

### 5. Quality appraisal / risk of bias

Use the instrument your field expects; do not invent one. Common: ROBINS-I and
Cochrane RoB 2 (interventions), QUADAS-2 (diagnostic accuracy), Newcastle-Ottawa
(observational), CLAIM (medical AI reporting), and in computing the
empirical-standards checklists per study type.

Rate per domain, not as one global score, and report the distribution. A review that
finds 40 of 60 studies at high risk of bias has found something: report it as a
finding, and do not pool results across it as if it were not there.

### 6. Synthesis

Choose deliberately and say which you chose:

- **Narrative synthesis** when studies are too heterogeneous to pool. Group by
  mechanism or population, not by year. Chronological ordering conveys nothing.
- **Vote counting**: counts of positive and negative findings. Weak, and it ignores
  effect size and sample size; use only with that caveat stated.
- **Meta-analysis** only when outcomes are commensurable. Then: effect size with CI
  per study, a pooled estimate under a random-effects model unless you can justify
  fixed effects, heterogeneity (I², τ²), a forest plot, and a funnel plot or Egger
  test for small-study effects. Pooling incommensurable outcomes produces a confident
  number that means nothing.

**The synthesis matrix** (template) is how narrative synthesis stays a synthesis
instead of an annotated bibliography. Rows are the included papers; columns are the
themes or mechanisms; cells hold what that paper contributes to that theme, with a
location. A synthesis paragraph is then written down a column, not across a row:

```
1. The claim the column supports, in one sentence.
2. The evidence: at least two studies, with their settings and numbers.
3. The disagreement, if any, and what plausibly explains it (population, protocol, scale).
4. What the column does not show. State it.
```

A paragraph that walks through papers one at a time ("Kim et al. did X. Liu et al.
did Y.") is a list wearing prose. Write down the column.

State explicitly what the evidence does **not** support. A review whose every finding
is positive has a publication-bias problem it has not addressed.

### 7. Report

Follow PRISMA 2020 (reviews of interventions) or the reporting standard your field
uses, and include the item checklist. Publish the search strings, the screening log
and the extraction table as supplementary material. A review whose search is not
reproducible is an opinion piece with a large reference list.

### 8. Keeping it alive

A review goes stale at the rate of its field. Before submission, and at each revision,
re-run the search record from the last run date with the same strings, screen the
delta with the same criteria, and report the update date. The scanner's saturation
table on a fresh run tells you how much moved.

## Turning the review into the paper

The map from A or C feeds two different sections, and the difference matters:

- **Related Work** answers "how is my contribution different?", organized by
  mechanism, ending in your distinction. See `04-related-work.md`.
- **Introduction paragraphs 2–3** answer "why is the gap real?", organized as a
  chain that terminates in exactly the failure your method fixes. See
  `09-abstract-title-intro.md` and `examples/05-lit-map-to-gap.md`.

Same papers, different jobs, different orderings. Writing one and pasting it into
the other's slot is visible immediately.

Every sentence that characterises a paper must trace to a reading note, and every
load-bearing one to a row in the ledger's layer-3 log. That is what Gate 2 checks.

## Common criticisms, and how to not earn them

| Reviewer says | Root cause | Fix |
|---|---|---|
| "Missing relevant work" | No forward citation chasing | `lit_scan.py` forward arm; check the last two cycles of the target venue |
| "Misrepresents [X]" | Cited from the abstract | Reading note with a location for anything you characterise |
| "Search is not reproducible" | Google Scholar only, no strings recorded | Named databases, verbatim strings, dates, hit counts |
| "Cherry-picked" | Criteria written after seeing results | Write criteria first, pilot them, report deviations |
| "Just a list" | Grouped by year or by author | Group by mechanism; write down the synthesis-matrix column |
| "Conclusions exceed the evidence" | Pooled heterogeneous studies | Report heterogeneity; downgrade the claim |
| "Cites retracted work" | No retraction check | `verify_citations.py` flags it; the scanner marks it in the candidate list |
| "No recent work" | Scan stopped at the survey | Forward-chase the newest seed; read the profile's recency share |
| "A survey cited as evidence" | Convenience | Cite what the survey cites |
