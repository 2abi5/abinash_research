# ACL Rolling Review — ACL / EMNLP / NAACL / EACL 2026

> Verified 2026-09-30 against <https://aclrollingreview.org/authors>,
> <https://aclrollingreview.org/cfp>, and the Responsible NLP checklist.
> Re-verify per `VERIFY.md`.

## Hard limits

| Rule | Value | Consequence |
|---|---|---|
| Long paper | **8 pages** of content | Desk reject |
| Short paper | **4 pages** of content | Desk reject |
| **Limitations section** | **required**, after the conclusion, before references | **Desk reject** |
| Ethics statement | optional, after limitations | — |
| Excluded from limit | limitations, ethics, references, appendices — all unlimited | — |
| **Responsible NLP Research checklist** | **required** at submission | **Desk reject** |
| Anonymity | double-blind, with an anonymity period | Desk reject |

Two independent desk-reject triggers that are pure paperwork: the limitations
section and the checklist. Both cost an hour. Papers are lost to them every cycle.

## The Limitations section

Unlimited space, does not count against your 8 pages, and required. Treat it as an
asset rather than a tax:

- Be specific. "Our method may not generalize" is read as evasion.
- Name the scope boundary: languages, domains, model scales, data regimes.
- Do not relocate a missing experiment here. Reviewers notice.

See `../references/08-discussion.md`.

## Responsible NLP Research checklist

Required, and it is where the **AI-use disclosure** goes: use of AI tools for
writing or coding must be disclosed in the checklist. Also covers data
provenance and licensing, compute reporting, human annotation details, and risks.

Answer it honestly and consistently with the paper — reviewers read the checklist
against the manuscript, and an inconsistency is worse than an uncomfortable "no".

## What this venue rewards

- Careful empirical work with proper statistics — ACL-family reviewers ask about
  significance testing and seed variance more consistently than any other community.
- Honest treatment of data: provenance, licensing, annotator compensation,
  and agreement statistics.
- Multilinguality, or an explicit statement that the work is English-only.
- Error analysis. A qualitative error taxonomy carries real weight here.

## What gets rejected here

- Missing limitations section or checklist.
- English-only work presented as general, with no scope statement.
- Human evaluation with no inter-annotator agreement.
- LLM-as-judge results with no human validation.
- Undisclosed AI assistance.

## Process

ARR is a rolling review: you submit to ARR, receive reviews and a meta-review, then
*commit* the paper to a specific conference. Reviews carry forward, so a revision
that ignores prior reviewer comments is visible to the next round.
