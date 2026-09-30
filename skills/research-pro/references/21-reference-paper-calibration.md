# Reference-paper calibration

"Here is a paper. Make mine like this."

This is one of the most effective things you can do, because an accepted paper from
your target venue is a *measured specification* of what that venue accepts —
structure, length allocation, evidence density, figure count, register — and it is
far more reliable than anyone's memory of the guidelines.

## What to ask for

One to three exemplars. More than three and the profile averages into mush.

Ask for accepted papers **from the target venue, in the last two cycles, on a
neighbouring problem**. An exemplar from a different venue teaches the wrong page
budget; one from eight years ago teaches a structure the community has moved past.

If the author supplies their *own* prior paper, that is a style exemplar as well as a
structural one — see "voice" below.

## Extract the profile

```bash
python3 skills/research-pro/scripts/exemplar_profile.py refs/exemplars/*.tex \
        --out paper/exemplar_profile.json
# PDFs: extract text first (pdftotext -layout paper.pdf paper.txt), then pass the .txt
```

The script measures what is measurable:

| Measured | Why it matters |
|---|---|
| Section order and presence | Where Related Work sits; whether there is a separate Limitations or Analysis section |
| Words and estimated page share per section | The real budget, as opposed to the one you guessed |
| Figure and table count, and which section they land in | CVPR papers carry more figures than ICML papers; this tells you how many to plan |
| Citations per section, and total | Related-work depth expected at this venue |
| Equations per section | Whether this community expects formalism or prose |
| Sentence-length mean and standard deviation | The register to match |
| Hedge and first-person density | `we` versus passive; how much hedging is normal here |
| Claim-sentence density in the abstract | How assertive abstracts are allowed to be |

Then compare your draft against it:

```bash
python3 skills/research-pro/scripts/exemplar_profile.py paper/main.tex \
        --compare paper/exemplar_profile.json
```

The comparison output is the useful artifact: it tells you that your Method is 40%
longer than the venue's norm while your Experiments is 30% shorter — which is
exactly the imbalance that draws "insufficient evaluation" reviews.

## What to copy, and what never to copy

### Copy — structure and proportion

- Section order and naming.
- Page allocation per section. If accepted papers give Experiments 3 of 8 pages and
  you have given it 1.5, that is a finding about your paper.
- Figure and table count, and where they appear.
- Citation density.
- Whether contributions are bulleted or prose.
- How results are presented: one big table or several focused ones.
- Depth of implementation detail in the main text versus the appendix.

### Copy — register

- Sentence-length distribution.
- First person or passive.
- How citations are integrated grammatically (`\citet` narrative style versus
  parenthetical).
- Hedging level. Some communities hedge heavily; over-asserting reads as naive.
- Whether the abstract contains numbers.

### Never copy

- **Text.** Not a sentence, not a "standard" phrase from their introduction. Venues
  run similarity checks, and reusing an exemplar's prose is plagiarism whatever the
  intent. The profile is a *measurement*, not a source of wording.
- **Their claims or framing**, applied to your weaker result. If the exemplar claims
  a 10-point gain and you have 0.4, matching their assertiveness is overclaiming.
- **Their baselines**, uncritically. Their baseline set was current for their cycle;
  yours must include what has appeared since.
- **A structure that does not fit your contribution type.** A method-paper exemplar
  will mislead an analysis paper. Check `01-intake.md`'s type table first.

## Voice calibration from the author's own papers

When the exemplars are the author's own prior work, additionally match: their
characteristic sentence rhythm, their vocabulary preferences, whether they use
contractions (in most venues, no), and how they open sections.

Then apply the field's conventions over their habits where the two conflict, and say
which you overrode. A draft "improved" until it is no longer recognizably theirs is
a failure — they will spend a day undoing it, and they should.

## The workflow

```
1. Author supplies exemplars           → refs/exemplars/
2. exemplar_profile.py                 → paper/exemplar_profile.json
3. Report the target profile to the author, and confirm it
4. S1 architecture: set the section budget FROM the profile, not from a generic table
5. S4 drafting: match register and citation style
6. Before Gate 4: --compare your draft against the profile; report every deviation
   over 25% with the reason it is or is not justified
```

Record the profile's source in the ledger — which papers, which venue, which cycle.
A deviation from the profile is not automatically wrong, but it should be a decision
rather than an accident.

## Honest limits

- A profile is a description of what got accepted, not a formula that produces
  acceptance. Matching the shape of a NeurIPS paper does not give you a NeurIPS
  contribution.
- Three papers is a small sample. Treat large deviations as questions, not verdicts.
- An exemplar cannot tell you whether your evidence is sufficient. Only
  `06-experiments.md` and the review panel do that.
