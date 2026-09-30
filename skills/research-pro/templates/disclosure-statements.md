# AI-use disclosure — pick one and make it accurate

Verify the venue's current requirement first: `../venues/<venue>.md` and
`../references/18-disclosure-and-ethics.md`. Accuracy runs both ways — do not
understate what happened, and do not disclose use that did not happen.

## A. Writing and language assistance only

> The authors used a large language model (<model, version, month year>) for
> language editing and for drafting prose from author-supplied outlines and results.
> All technical content, experimental design, analysis, and conclusions are the
> authors'. The authors reviewed and verified all text, figures, and references, and
> take full responsibility for the content.

## B. Methodological use — belongs in Methods, not acknowledgements

> We used <model, version, access date> as <the component it served as>. Prompts,
> decoding parameters, and the model version are given in Appendix <X>. <N> outputs
> were manually validated by <who>, with <κ / agreement>. Model outputs were not
> used to produce any reported numerical result without the verification described
> in §<X>.

## C. Code assistance

> Portions of the implementation were written with AI coding assistance. All code was
> reviewed and tested by the authors; the reported experiments were run from the
> committed code at <repository / commit>.

## D. Literature search assistance

> AI tools were used to help identify candidate related work. Every cited reference
> was retrieved and read by the authors, and its bibliographic record verified
> against <Crossref / OpenAlex / the publisher>.

## E. No AI use

> The authors did not use generative AI tools in the preparation of this manuscript.

## Where it goes
- A checklist field where one exists (ARR's Responsible NLP checklist; the NeurIPS
  checklist).
- Otherwise the acknowledgements — or **Methods**, whenever the use was
  methodological, because then it is reproducibility rather than disclosure.
