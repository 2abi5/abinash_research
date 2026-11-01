# Worked example — the citation that did not say that (Layer 3)

Layers 1 and 2 are automatable and the script runs them. Layer 3 is the one that
matters: does the source say what your sentence says it says? This example walks the
real report for `tests/fixtures/paper_mechanics.tex` against
`tests/fixtures/refs.bib` and the partial ledger `tests/fixtures/ledger_layer3.md`,
then closes each row. The bibliography entries are fixtures; two of them are
deliberately not real.

```bash
S=skills/research-pro/scripts
python3 $S/verify_citations.py tests/fixtures/refs.bib \
        --replay tests/fixtures/cite_replay.json \
        --tex tests/fixtures/paper_mechanics.tex --ledger tests/fixtures/ledger_layer3.md
```

(`--replay` serves recorded database answers so the example runs offline; drop it for
a real bibliography.)

## What the report says

```
- **RETRACTED** 1  ·  **UNVERIFIED** 2  ·  **VERIFIED** 4
## Verdict: FAIL — see findings below. Gate 2 does not pass.
```

and, further down, the part this example is about (table abridged to fit; the sentences
are the real ones):

```
Ledger `tests/fixtures/ledger_layer3.md`: 3 key(s) logged, **2 load-bearing key(s) uncovered**: `devlin2018bert`, `retracted2021example`.
Logged keys not in the .bib: `notinbib2020`.

| Section      | Keys                                 | Sentence                                                                  | Ledger   |
|---|---|---|---|
| abstract     | he2016resnet, vaswani2017attention   | Sparse expert routing cuts inference cost [vaswani2017attention], but ... | ✓        |
| Introduction | he2016resnet                         | In [he2016resnet] the authors show that residual connections ease ...     | ✓        |
| Introduction | devlin2018bert, he2016resnet, ...    | Routing has been studied widely [vaswani..., he..., devlin..., retracted...]. | **open** |
| Introduction | retracted2021example                 | Gradient echo regularisation eliminates overfitting entirely [retracted...]. | **open** |
| Introduction | devlin2018bert                       | [devlin2018bert] propose bidirectional pretraining.                       | **open** |
| Related Work | he2016resnet, vaswani2017attention   | Per-layer routing [vaswani...] and magnitude pruning [he...] share one ...  | ✓        |
```

Seven load-bearing sentences. Three are open. Each open row is a different kind of
Layer-3 failure, and each has a different honest close.

## Row 1 — the stack: "Routing has been studied widely [a, b, c, d]"

Four citations after a sentence with no content. The report also flags it under
`stack` in the mechanics section. The question "where in the source supports this
claim?" has no answer because the sentence makes no claim: "studied widely" is true
of everything that has four citations.

**Close:** delete the sentence, or make it say something and cite the one or two
papers that support that something. "Per-layer routing commits each token at the
layer where it is scored [vaswani2017attention]" is a claim with one source and one
ledger row. The stack was never a citation; it was a gesture.

## Row 2 — the retracted source: "eliminates overfitting entirely [retracted2021example]"

The script found the record and found it marked retracted. The sentence uses it as
load-bearing evidence, with an absolute ("entirely") the source would not have
supported even before the retraction.

**Close:** the claim leaves the paper. If the retraction is itself relevant (the
method was tried and withdrawn), the sentence becomes "a 2021 report of complete
overfitting elimination was later retracted [retracted2021example]", and the ledger
row records `retraction notice, cited as such`. Nothing in between is honest.

## Row 3 — the verb: "[devlin2018bert] propose bidirectional pretraining"

Two problems the script separates. The mechanical one: a parenthetical citation is
the grammatical subject (`as-subject` in the mechanics list; use `\citet`). The
Layer-3 one: the ledger has a row for this key with an **empty location**, so it
counts as uncovered. Somebody wrote the claim and meant to find the section.

**Close:** open the paper. The claim is in the abstract and §3.1. The ledger row
becomes

```
| devlin2018bert | bidirectional pretraining with a masked objective | Abstract; §3.1 |
```

and the sentence becomes `\citet{devlin2018bert} propose …`. Now check the verb
against the table in `13-citation-integrity.md`: "propose" requires that they were
first. For this paper that is defensible; for a method credited to the popular
follow-up it would not be, and the fix would be to cite the originator.

## A fourth case the fixture does not contain: claim drift

The most common Layer-3 failure in real drafts is not in this fixture because it
cannot be detected by any script. It looks like this:

> Per-layer routing degrades on rare classes~\cite{okafor2021routing}.

Open Okafor et al. The result is in §6, Table 5: a 1.9-point drop on *late-
disambiguated* classes, on ImageNet, at top-1 dispatch. Not "rare classes", not in
general, not at top-2. The sentence is a paraphrase that drifted toward what the
author needed it to say.

Three closes, in order of preference:

1. **Narrow the sentence to the source.** "Per-layer routing loses 1.9 points on
   classes disambiguated after the routing layer (ImageNet, top-1 dispatch)
   \citep{okafor2021routing}." Longer, specific, and now a reviewer who opens Table 5
   finds exactly that.
2. **Find the source that does say it.** If a paper measured rare-class degradation,
   cite that one, after opening it.
3. **`[NEEDS SOURCE]`.** Leaves a visible gap for the author instead of an invisible
   one for the reviewer.

What is not a close: softening it to "may degrade on some classes". The source still
does not say that, and the hedge tells the reviewer you knew.

## Re-run

After the three closes the ledger covers every load-bearing key, the retracted entry
and the stack are gone from the text, and the preprint has been upgraded to its
published version (the report found the DOI). The verdict line reads

```
PASS — layers 1 and 2 clear; every load-bearing citation has a ledger location (layer 3).
```

only if the two `UNVERIFIED` entries are also resolved, which in this fixture they
cannot be, because they do not exist. That is the fixture doing its job.

## Why the worklist exists

Before the worklist, Layer 3 was an instruction ("open every source") that nobody
followed under deadline. Now it is a table with a column that is either `✓` or
`open`, the gate reads the column, and the ledger is the record a co-author can audit.
The work is the same. The difference is that it gets done.
