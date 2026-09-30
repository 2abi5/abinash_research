# Disclosure, ethics, and authorship

## AI-use disclosure

### The position

Disclose. It is cheap, it is required at most major venues, and the alternative is a
research-integrity finding rather than a rejection. Several venues have desk-rejected
submissions over LLM-policy violations, at scale and publicly.

This suite will not help conceal AI assistance or evade detection tooling. It will
help you write well and disclose accurately — see `12-prose-quality.md` for why
those two goals point the same way.

### What each venue requires (verify live — `../venues/VERIFY.md`)

| Venue | Requirement |
|---|---|
| NeurIPS 2026 | Allowed; authors fully responsible; **methodologically significant or non-standard** LLM/agent use must be disclosed in the paper. LLMs may not be authors. Position track differs. |
| ICML 2026 | Allowed; authors fully responsible. LLMs may not be authors or be credited. **Prompt injection ⇒ rejection.** |
| ICLR 2026 | **Any significant use in ideation or writing must be disclosed.** Undisclosed use is escalated to the area chair; LLM-generated papers have been desk-rejected. |
| ACL-family (ARR) | AI tool use **for writing or coding must be disclosed in the Responsible NLP checklist.** |
| AAAI | Authors responsible; check the current policy page. |
| Nature-family | LLMs cannot be authors; use must be documented in methods or acknowledgements. |

### Where it goes

- A dedicated checklist field, where one exists (ARR; NeurIPS checklist).
- Otherwise: a short statement in the acknowledgements, or in Methods when the use
  was methodological.
- **If a model is part of your method or analysis, it belongs in Methods**, with
  model name, version, date, and prompts — that is not disclosure, it is
  reproducibility.

### Templates

Writing assistance only:

> The authors used a large language model (Claude Opus, September 2026) for language
> editing and for drafting prose from author-supplied outlines and results. All
> technical content, experimental design, analysis, and conclusions are the authors'.
> The authors reviewed and verified all text, figures, and references, and take full
> responsibility for the content.

Methodological use:

> We used <model, version, access date> as <component of the pipeline>. Prompts,
> decoding parameters, and the model version are in Appendix <X>. <N> outputs were
> manually validated by <who>, with agreement of <κ>. Model outputs were not used to
> generate any reported numerical result without the verification described in §<X>.

Code assistance:

> Portions of the implementation were written with AI coding assistance. All code was
> reviewed and tested by the authors; the experiments reported were run from the
> committed code in <repository>.

### Do not write

- A disclosure that understates what happened. If a model drafted whole sections,
  "minor language editing" is a false statement in a submitted manuscript.
- A disclosure of use that did not happen, defensively. Accuracy both ways.

## Authorship

**Authorship requires intellectual contribution plus accountability.** The usual
four conditions (ICMJE, and similar criteria elsewhere): substantial contribution to
conception or execution; drafting or critically revising; approval of the final
version; and accountability for the work.

- An LLM cannot be an author anywhere. It cannot be accountable.
- Providing funding, supplying data, or running a lab is not authorship on its own —
  it is an acknowledgement.
- Do not add an author without their knowledge and agreement, ever.
- **Ghost authorship** (omitting someone who qualifies) is as serious as gift
  authorship.
- Where a venue asks for a CRediT statement, fill it honestly per author:
  conceptualization, methodology, software, validation, formal analysis,
  investigation, data curation, writing (original draft / review & editing),
  visualization, supervision, project administration, funding acquisition.
- Settle author order before submission, in writing. It is the most common and
  most damaging dispute in research groups.

## Human subjects and sensitive data

If the work involves people or their data:

- **Ethics approval** (IRB / REC / equivalent) obtained **before** data collection,
  with the approving body and protocol number reported. Approval cannot be obtained
  retroactively, and a paper that needed it and does not have it is not publishable.
- Informed consent, and what participants were told.
- Compensation for annotators and participants — report the rate, and make it at
  least a local living wage. Reviewers at ACL-family and HCI venues check.
- De-identification, and the re-identification risk you assessed.
- Data licence and terms of use for every dataset. Scraped data used against a
  platform's terms is a real problem, not a technicality.
- Where restricted data cannot be shared, say so and say why.

## Dual submission and preprints

- Know your venue's review window and overlap threshold. CVPR: 20% overlap,
  violations reported to the other venue.
- Preprint policies differ — most ML venues allow arXiv preprints; some have
  anonymity periods during which you may not post or publicize. Check.
- Do not submit the same work to two venues simultaneously. It is detected through
  reviewer overlap more often than authors assume.

## Prompt injection

Text hidden in a manuscript intended to influence an automated reviewer (white text,
tiny fonts, figure metadata, LaTeX comments) is an explicit rejection-and-report
offence at multiple venues.

- Never add any.
- **Check for it** before submission — including in text you inherited from a
  template, a collaborator, or a previous draft. Search the extracted PDF text for
  instruction-shaped strings and compare against the visible page.
- If you find any in the author's own draft, tell them immediately and directly.

## Other integrity items

- **Plagiarism**, including self-plagiarism. Reusing your own text from a prior paper
  without attribution is a violation; venues run similarity checks.
- **Image manipulation** beyond adjustments applied uniformly and disclosed.
- **Salami slicing** — splitting one contribution across multiple papers to inflate
  a count.
- **Citation manipulation** — padding with citations to your own or a reviewer's work
  to curry favour.
- **Data availability**: state where data and code are, or why they cannot be shared.
