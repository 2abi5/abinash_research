# S6 — Citation integrity  ·  GATE 2

The hardest blocking gate in the pipeline. A fabricated or misattributed citation
is the one defect that is both trivially detectable by a reviewer and treated as a
research-integrity matter rather than a mistake.

## Why this is strict

A language model's bibliographic recall fails in a specific, dangerous way: the
title is plausible, the authors are real researchers in the right subfield, the
venue and year are consistent — and the paper does not exist. Nothing about the
output signals the failure. It cannot be caught by reading; it can only be caught
by checking against a real record.

So the rule is absolute: **every reference is verified against a bibliographic
record, or it is marked `[NEEDS SOURCE]` and the author supplies it.** There is no
third state. "Probably right" is the state that ends careers.

## Three layers — all three are required

Most tools check layer 1 and call it verified. Layer 3 is where the real damage
lives.

### Layer 1 — the record exists

Resolve each entry against at least one authority:

| Source | Endpoint | Best for |
|---|---|---|
| Crossref | `api.crossref.org/works/<doi>` | anything with a DOI; authoritative metadata |
| OpenAlex | `api.openalex.org/works/doi:<doi>` | open coverage, no key, good title search |
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/...` | CS coverage, citation counts |
| arXiv | `export.arxiv.org/api/query?id_list=<id>` | preprints |
| dblp | `dblp.org/search/publ/api?q=...&format=json` | CS venue names and versions |
| PubMed | `eutils.ncbi.nlm.nih.gov/entrez/eutils/` | biomedical |

Run it:

```bash
python3 skills/research-pro/scripts/verify_citations.py paper/refs.bib \
        --report out/citations.md --strict
```

No match from any source ⇒ `UNVERIFIED`. Treat as fabricated until the author
produces the PDF. A DOI that resolves to a *different* paper than the entry claims
is worse than no DOI, and the script flags it as `MISMATCH`.

### Layer 2 — the metadata matches

A real paper cited with wrong details is still a defect, and it propagates: other
people copy your `.bib`.

Check against the resolved record: author surnames and order, year, exact title,
venue (and whether it is the arXiv version or the published one), volume, pages,
DOI. The script reports each field-level disagreement.

The most common real-world error: **citing the arXiv preprint of a paper that was
published two years ago.** It signals that you did not read it recently and it
denies the authors their venue credit. Upgrade every preprint that has a published
version.

### Layer 3 — the source supports the claim

This is the layer that matters and the layer nobody automates well. For each
citation, ask: **does the cited work actually say what this sentence says it
says?**

Failure modes, in order of how often they appear in real drafts:

| Failure | What it looks like |
|---|---|
| **Claim drift** | The source shows an effect in one narrow setting; you cite it for the general claim |
| **Citation laundering** | You cite B, which cites A for the claim; A never made it. Check the primary source |
| **Direction error** | The source found the opposite, or found it null |
| **Attribution error** | Method credited to the wrong paper — commonly to a popular follow-up rather than the originator |
| **Support-free citation** | A general citation dropped after a specific numeric claim it does not contain |
| **Survey-as-evidence** | A survey cited for a result; surveys report, they do not establish |

Procedure, for every load-bearing citation — every citation attached to a claim
in the Abstract, Introduction, or a comparison:

1. Open the source. Not the abstract — the relevant section.
2. Find the sentence, table, or figure that supports your claim.
3. Record it in the ledger: `[12] → §4.2, Table 3` .
4. If you cannot find it, either weaken the claim to what the source supports, find
   the correct source, or mark `[NEEDS SOURCE]`.

A citation you have not opened is not a citation. It is a guess with a number.

## BibTeX hygiene

Run this early — deduplicating at submission time is how `\cite` keys break.

- **One entry per work.** Merge duplicates (the same paper imported from Google
  Scholar, from a colleague, and from a template) and fix the keys once.
- **Consistent keys**: `surnameYYYYkeyword`, e.g. `kim2024routing`.
- **Required fields**: `@inproceedings` needs author, title, booktitle, year;
  `@article` needs author, title, journal, year, volume, pages; `@misc` for a
  preprint needs `eprint`, `archivePrefix`, `primaryClass`.
- **Protect capitalization** with braces: `{BERT}`, `{ImageNet}`, `{T}ransformer`.
  Otherwise most styles lowercase them and it looks careless.
- **Prefer DOI over URL.** A URL is for something with no DOI, and then include an
  access date.
- **Consistent venue naming.** Either all abbreviated (`CVPR`) or all full
  (`Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
  Recognition`) — not a mix within one bibliography.
- **Strip the cruft** Google Scholar adds: `organization`, `publisher` on
  conference papers, stray `note` fields.

## In-text mechanics

- **Author-prominent** when the authors are the subject: `Kim et al.~\cite{kim24}
  show that…` → `\citet{kim24}`.
- **Parenthetical** when the work supports a statement: `Routing reduces FLOPs
  \citep{kim24}.` → `\citep{kim24}`.
- A citation is not a noun. Not `as shown in [12]` used as the grammatical
  subject — `\citet{kim24} shows`.
- Non-breaking space before a bracketed cite: `method~\cite{x}`.
- Citations go **before** the period.
- Multiple citations sorted and compressed: `\citep{a,b,c}` → `[1–3]`.
- Do not stack five citations after a vague claim to look thorough. Either the
  claim is specific and needs one or two, or it is too vague to need any.

## Anonymity (double-blind venues)

Citing your own prior work is allowed and expected — but in the **third person**:

- Wrong: `In our previous work~\cite{ours23}, we showed…` — de-anonymizes you.
- Right: `Prior work on sparse routing~\cite{ours23} showed…`

Also check: no acknowledgements, no funding statement, no institution in the
author block, no named internal cluster or dataset, no link to a non-anonymous
repository, and no identifying metadata in the PDF (`pdfinfo main.pdf` — LaTeX
embeds the author field if you set it). Supplementary material and figure file
paths leak identity too.

## Gate 2 — passing criteria

All of these, with no exceptions and no author override:

- [ ] Every entry in `refs.bib` resolves to a real record (Layer 1)
- [ ] Zero `MISMATCH` findings; every field-level disagreement resolved (Layer 2)
- [ ] Every load-bearing citation has a recorded location supporting its claim
      (Layer 3), logged in the ledger
- [ ] Zero `[NEEDS SOURCE]` tokens remaining
- [ ] Zero duplicate entries; every `\cite` key resolves
- [ ] No uncited entries left in the `.bib` (they are noise, and they leak what you
      read)
- [ ] Every preprint with a published version upgraded
- [ ] For double-blind: no self-citation in the first person, no identifying
      metadata

If the verifier cannot reach the network, it says so and runs structural checks
only. **Structural checks alone do not pass this gate** — report the gate as
`BLOCKED: unverified` rather than `PASS`.

## Reporting what you could not verify

When a reference genuinely cannot be resolved (a book chapter, a technical report,
a personal communication, a non-indexed workshop paper), that is fine — record how
it was verified instead: `verified against PDF held by author, 2026-09-30`. The
requirement is a verification trail, not a database hit.
