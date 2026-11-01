# S6 — Citation integrity  ·  GATE 2

The hardest blocking gate in the pipeline. A fabricated or misattributed citation
is the one defect that is both trivially detectable by a reviewer and treated as a
research-integrity matter rather than a mistake.

## Why this is strict

A language model's bibliographic recall fails in a specific, dangerous way: the
title is plausible, the authors are real researchers in the right subfield, the
venue and year are consistent, and the paper does not exist. Nothing about the
output signals the failure. It cannot be caught by reading; it can only be caught
by checking against a real record.

So the rule is absolute: **every reference is verified against a bibliographic
record, or it is marked `[NEEDS SOURCE]` and the author supplies it.** There is no
third state. "Probably right" is the state that ends careers.

## Three layers. All three are required

Most tools check layer 1 and call it verified. Layer 3 is where the real damage
lives, and this suite makes it a worklist instead of a wish.

```bash
python3 skills/research-pro/scripts/verify_citations.py paper/refs.bib \
        --tex paper/main.tex paper/sections/*.tex \
        --ledger paper/LEDGER.md \
        --authors "Panta,Kim" \
        --cache .cite_cache.json --mailto you@university.edu \
        --report out/citations.md --strict
```

| Status | Means | Gate |
|---|---|---|
| `VERIFIED` | A real record, metadata agrees | passes |
| `MISMATCH` | A real record, but title, first author or year disagree | blocks |
| `UNVERIFIED` | Reachable databases returned no match | blocks: treat as fabricated |
| `RETRACTED` | The record is marked retracted | blocks: see below |
| `OFFLINE` | No database could be reached | blocks: `BLOCKED`, never `PASS` |

Two distinctions the script draws that most do not. A **404 is evidence** and a
timeout is not: a fabricated DOI gets a clean "no such record" from Crossref and is
reported `UNVERIFIED`, while a proxy failure is reported `OFFLINE`. And a **title
search is not verification**: a search for any plausible title returns something.
A hit is accepted only when the title is close *and* the first author or the year
agrees; otherwise the nearest title is reported as rejected, so you can see what the
database thought you meant.

### Layer 1 — the record exists

| Source | What it is best for |
|---|---|
| Crossref | anything with a DOI; authoritative publisher metadata |
| OpenAlex | open coverage, no key, retraction flag from Retraction Watch, good title search |
| Semantic Scholar | CS coverage, arXiv to published-version mapping |
| arXiv | preprints, by identifier |
| dblp | CS venue names and versions; catches "which year was this NeurIPS paper" |
| PubMed | biomedical; use the PubMed connector where available |

No match from any source means `UNVERIFIED`. Treat it as fabricated until the author
produces the PDF. A DOI that resolves to a *different* paper than the entry claims
is worse than no DOI and comes back `MISMATCH`.

### Layer 2 — the metadata matches

A real paper cited with wrong details is still a defect, and it propagates: other
people copy your `.bib`. The script compares author surnames, year and title against
the resolved record and reports each disagreement.

The most common real-world error is **citing the arXiv preprint of a paper that was
published two years ago.** It signals that you did not read it recently and it denies
the authors their venue credit. The script finds the published DOI through Crossref,
OpenAlex or Semantic Scholar and the gate blocks until the entry is upgraded.

Cite the version you read. If the published version changed a number you quote, the
preprint is the wrong source and so is your sentence.

### Layer 3 — the source supports the claim

This is the layer that matters and the layer nobody automates well. For each
citation, ask: **does the cited work actually say what this sentence says it says?**

Failure modes, in order of how often they appear in real drafts:

| Failure | What it looks like |
|---|---|
| **Claim drift** | The source shows an effect in one narrow setting; you cite it for the general claim |
| **Citation laundering** | You cite B, which cites A for the claim; A never made it. Check the primary source |
| **Direction error** | The source found the opposite, or found it null |
| **Attribution error** | A method credited to the popular follow-up rather than the originator |
| **Support-free citation** | A general citation dropped after a specific numeric claim it does not contain |
| **Survey-as-evidence** | A survey cited for a result; surveys report, they do not establish |
| **Stale citation** | A 2019 "state of the art" cited as current in 2026 |

**The worklist.** With `--tex`, the script extracts every sentence in the abstract,
introduction and related work that carries a citation, de-duplicated, one row per
sentence, and prints it as a table. Those are the load-bearing citations: the ones a
reviewer checks first. Work the table:

1. Open the source. Not the abstract: the section, table or figure.
2. Find the sentence, table or figure that supports *your* sentence.
3. Record it in the ledger's `Citation layer-3 log`:
   `| kim2024routing | per-layer routing commits before context resolves | §3.1, Fig. 2 |`
4. If you cannot find it: weaken the claim to what the source supports, find the
   right source, or mark `[NEEDS SOURCE]`.

With `--ledger`, the script reads that table back and reports every load-bearing key
without a location. **Uncovered keys block the gate.** Pass `--all-sections` for a
camera-ready pass over the whole paper.

A citation you have not opened is not a citation. It is a guess with a number.

### What the verb commits you to

The verb between a claim and its citation is a claim about the source. Choose it
from what the source did, not from what sounds strong:

| You write | The source must contain |
|---|---|
| `X showed / demonstrated that` | a controlled result establishing it |
| `X measured / reported` | the number, in a table or figure you can cite by location |
| `X found` | an empirical finding, in their setting (say the setting) |
| `X proposed / introduced` | the method, and they were first; check the originator |
| `X argued / hypothesised` | an argument, not evidence; do not later treat it as evidence |
| `X observed` | a qualitative or incidental finding, not the paper's main result |
| `X reviewed / surveyed` | a survey; it points to evidence and is not itself evidence |
| `see X` | background a reader may want; never a load-bearing claim |

"Showed" after a paper that argued is a Layer-3 failure even though the paper exists.

### Finding a source for an orphan claim

A sentence that needs a citation and has none is `[NEEDS SOURCE]`, not an invitation
to recall one. To fill it:

1. **Name the claim precisely.** "Per-layer routing degrades on rare classes" is
   searchable; "routing has limitations" is not.
2. **Look for the originator**, not the most-cited restatement. Forward-chase from
   the oldest paper you know to find who said it first (`lit_scan.py`).
3. **Prefer a measurement to an assertion.** A table beats a sentence in a related
   work section beats a survey.
4. **If only a secondary source is obtainable**, cite it as such: `(A, as cited in
   B)` or `B, citing A`, and say in the ledger that the primary was not seen.
5. **If nothing supports it**, the claim leaves the paper or moves to Discussion
   as a stated hypothesis. Hedging it in place is the worst option.

## Retractions and corrections

The script flags `RETRACTED` from Retraction Watch data via OpenAlex, and flags a
DOI that is itself a retraction notice. A retracted paper may be cited only to
discuss the retraction, and the text must say it is retracted. A paper with a
published correction is cited together with the correction when the corrected
content is what you rely on. Check the strongest recent baseline especially: a
retracted baseline in your comparison table invalidates the comparison.

## What to cite, and how

| Thing | Cite |
|---|---|
| A dataset | the dataset paper **and** the version or split you used; the URL alone is not a citation |
| Software and models | the paper if one exists, plus the release: `CITATION.cff` or a Zenodo DOI, with version and access date |
| A pretrained checkpoint | the model's report or card, with the exact identifier you loaded |
| A metric or protocol | its originating paper, not the toolkit that implements it |
| A web page, blog, documentation | `@misc` with `url` and `urldate`; acceptable for facts about artifacts, never for scientific results |
| A thesis or technical report | `@phdthesis` / `@techreport` with the institution; verified against the holding repository |
| A talk or personal communication | in the text with permission, not in the bibliography |
| An LLM used in writing | in the disclosure statement, not in the references (`18-disclosure-and-ethics.md`) |

Wikipedia, lecture slides and preprint-aggregator summaries are not sources for
scientific claims. Find what they cite.

## The shape of the reference list

The report ends with a profile. Read it as a reviewer would:

- **Recency.** The share of references from the last three years. Low in a
  fast-moving area means the last two cycles of the target venue were not searched.
- **Self-citation rate** (`--authors`). Above about 20% reads as padding or as an
  attempt to lift one's own metrics. Keep the self-citations the argument needs.
- **Originators vs. restatements.** The method should be credited to the paper that
  introduced it, with the popular follow-up cited for what *it* added.
- **Breadth.** Twelve citations from one group is a signal; so is zero citations to
  the group whose method you beat.

## BibTeX hygiene

Run this early. Deduplicating at submission time is how `\cite` keys break.

- **One entry per work.** Merge duplicates (the same paper imported from Google
  Scholar, from a colleague, and from a template) and fix the keys once. The script
  reports pairs with the reason they matched.
- **Consistent keys**: `surnameYYYYkeyword`, e.g. `kim2024routing`.
- **Required fields**: `@inproceedings` needs author, title, booktitle, year;
  `@article` needs author, title, journal, year, volume, pages; `@misc` for a
  preprint needs `eprint`, `archivePrefix`, `primaryClass`.
- **Protect capitalization** with braces: `{BERT}`, `{ImageNet}`, `{T}ransformer`.
  Otherwise most styles lowercase them and it looks careless.
- **Prefer DOI over URL.** A URL is for something with no DOI, and then include
  `urldate`.
- **Consistent venue naming.** Either all abbreviated (`CVPR`) or all full
  (`Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
  Recognition`), never a mix within one bibliography.
- **Strip the cruft** Google Scholar adds: `organization`, `publisher` on
  conference papers, stray `note` fields.
- **No uncited entries.** They are noise, and they leak what you read.

## In-text mechanics

The script reports these from the `.tex` as non-blocking findings with file and
line. Fix them anyway; reviewers read them as carelessness.

- **Author-prominent** when the authors are the subject: `\citet{kim24} show
  that…`. **Parenthetical** when the work supports a statement: `Routing reduces
  FLOPs~\citep{kim24}.`
- A citation is not a noun. Not `as shown in [12]`, not `[12] proposes`. Name the
  authors or use `\citet`.
- Non-breaking space before a bracketed cite: `method~\cite{x}`.
- Citations go **before** the period.
- Multiple citations sorted and compressed: `\citep{a,b,c}` renders as `[1–3]`.
- Do not stack four or more citations after a vague claim to look thorough. Either
  the claim is specific and needs one or two, or it is too vague to need any. Each
  stacked citation is also a Layer-3 row you now owe.

## Anonymity (double-blind venues)

Citing your own prior work is allowed and expected, in the **third person**:

- Wrong: `In our previous work~\cite{ours23}, we showed…` de-anonymizes you.
- Right: `Prior work on sparse routing~\cite{ours23} showed…`

Also check: no acknowledgements, no funding statement, no institution in the author
block, no named internal cluster or dataset, no link to a non-anonymous repository,
and no identifying metadata in the PDF (`pdfinfo main.pdf`; LaTeX embeds the author
field if you set it). Supplementary material and figure file paths leak identity too.
`venue_check.py` tests for the first-person self-citation pattern.

## Gate 2 — passing criteria

All of these, with no exceptions and no author override:

- [ ] Every entry in `refs.bib` resolves to a real record (Layer 1)
- [ ] Zero `MISMATCH`; every field-level disagreement resolved (Layer 2)
- [ ] Zero `RETRACTED` entries, unless cited to discuss the retraction and labelled so
- [ ] Every preprint with a published version upgraded
- [ ] Every load-bearing citation has a recorded location in the ledger's layer-3 log,
      and `--ledger` reports zero uncovered keys (Layer 3)
- [ ] Zero `[NEEDS SOURCE]` tokens remaining
- [ ] Zero duplicate entries; every `\cite` key resolves; no uncited entries
- [ ] For double-blind: no self-citation in the first person, no identifying metadata

If the verifier cannot reach the network, it says so and runs structural checks
only. **Structural checks alone do not pass this gate.** Report `BLOCKED:
unverified`, never `PASS`. Cache the responses (`--cache`) so the weekly `make check`
does not depend on the network being up at the moment you run it.

## Reporting what you could not verify

When a reference genuinely cannot be resolved by any index (a book chapter, a
technical report, a non-indexed workshop paper), record how it was verified instead:
`verified against PDF held by author, 2026-09-30`, in the ledger next to the key.
The requirement is a verification trail, not a database hit.
