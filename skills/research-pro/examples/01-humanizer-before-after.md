# Worked example — the humanizer, with real measurements

Every number in this file is the actual output of `scripts/prose_metrics.py` on the
fixture named beside it. Nothing here is estimated. Reproduce it yourself with the
commands at the bottom.

## Stage 1 — before  (`tests/fixtures/slop.tex`)

> In recent years, there has been growing interest in leveraging deep learning for
> image classification. It is important to note that these approaches play a crucial
> role in a wide range of applications. Moreover, recent methods have utilized a
> myriad of architectures to achieve state-of-the-art performance on comprehensive
> benchmarks. Furthermore, the intricate nature of these models underscores the
> pivotal importance of efficient inference in the realm of computer vision.
>
> In this section, we describe our novel approach. Our method may potentially offer
> improvements that could possibly enhance performance in certain settings.
> Additionally, the seamless integration of our components showcases a holistic
> framework that is accurate, efficient, and scalable.

```
  [FAIL] banned phrases/words             25 hit(s) — target 0
  [FAIL] sentence-length variance         stdev 4.0 — target >= 8.0 (mean 16.4, max 24)
  [FAIL] short sentence per paragraph     66.7% of paragraphs have no sentence under 10 words — target <= 25.0%
  [FAIL] transition openers               33.3% of paragraphs open with a transition adverb — target <= 25.0%
  [FAIL] hedge stacking                   1 paragraph(s) with more than two hedges — target 0
  [FAIL] empty topic sentences            1 found — target 0
exit code 1
```

Six failures. Every sentence is 14–24 words. Two paragraphs, zero facts. Note what
did *not* fire: no em-dashes, no contrastive negation, no choppiness. This is the
smooth machine register, not the over-corrected one.

## Stage 2 — rewritten  (`tests/fixtures/clean.tex`)

> Image classifiers are deployed on devices that cannot afford their inference cost.
> A 7B vision transformer needs 4.1 GFLOPs per image; an edge accelerator budget is
> closer to 1. Existing sparsification closes part of that gap by pruning weights
> before inference, which assumes weight magnitude predicts importance — an
> assumption that fails once the discriminative signal is input-dependent.
>
> We route instead of prune. A single gate scores the whole expert bank from pooled
> sequence context, then dispatches to the top two experts. Because the gate sees the
> full sequence before committing, it can send rare inputs to specialists that
> per-layer routing must choose blind. On ImageNet this holds top-1 accuracy at four
> times fewer inference FLOPs (Table 2), and replacing the learned gate with random
> routing costs 3.1 points while matching parameter count recovers only 0.4
> (Table 4) — the gain is the routing, not the capacity.

```
  [FAIL] short sentence per paragraph     50.0% of paragraphs have no sentence under 10 words — target <= 25.0%
exit code 1
```

Five of the six blocking checks now pass (variance is 10.6, banned hits are zero, no
transition openers, no hedges, no empty topic sentence). **The rewrite still fails
one check**, and that is the useful part of this example. Paragraph 1's shortest
sentence is 12 words; the rule wants one under 10, because the short sentence is
where the argument lands. The tool is stricter than a human editor would be here,
and it is right.

`--paragraphs` shows where:

```
  #   sents  lengths                         min  hedges  opener        flags
  1   3      12,15,28                        12   0       image         N:no-short-sentence
  2   4      5,19,22,40                      5    0       we
```

Paragraph 2 has its short sentence ("We route instead of prune.", 5 words).
Paragraph 1 does not.

## Stage 3 — one sentence added  (`tests/fixtures/clean2.tex`)

Added after the pruning sentence in paragraph 1:

> Magnitude is the wrong proxy.

```
  (no FAIL lines)
  [PASS] sentence-length variance         stdev 11.1 — target >= 8.0 (mean 18.2, max 40)
  [PASS] em-dash density                  2 em-dashes, 1.37 per 100 words — above 0.5 reads as generated; ...
exit code 0
```

Five words fixed the last failure, and they also made the paragraph better: the
reader now gets the verdict on prior work in a sentence they cannot skim past.

The em-dash line is worth reading even though it passes. Two dashes in 146 words is
a high rate; the check stays quiet only because the fixture is short (it warns from
three dashes). In a full paper at this rate it would fire, and both dashes here are
replaceable: the first is an appositive (a comma works), the second introduces a
verdict (a colon, or a new sentence). Stage 3 is good prose, not finished prose.

## The proof: `--compare`

```
  metric                                    before     after     delta
  banned hits                                   25         0       -25  better
  sentence-length stdev                        4.0      11.1      +7.1  better
  paragraphs w/o short sentence %             66.7       0.0     -66.7  better
  transition openers %                        33.3       0.0     -33.3  better
  hedge-stacked paragraphs                       1         0        -1  better
  empty topic sentences                          1         0        -1  better
  em-dashes / 100 words                        0.0      1.37     +1.37  WORSE
  nominalisations / 100 words                  8.5       6.2      -2.3  better
```

One number went the wrong way, and the table says so. That is the point of running
the comparison: a rewrite that *feels* better can still have traded one tell for
another.

## What actually changed between stage 1 and stage 3

| Move | Before | After |
|---|---|---|
| Opened on the problem, not the field | "In recent years, there has been growing interest" | "deployed on devices that cannot afford their inference cost" |
| Replaced abstraction with a number | "efficient inference" | "4.1 GFLOPs per image; budget closer to 1" |
| Named the failure's **reason** | "the intricate nature of these models" | "assumes weight magnitude predicts importance; fails once the signal is input-dependent" |
| Named the mechanism concretely | "a holistic framework" | "one gate scores the bank from pooled context, dispatches to the top two" |
| Attached evidence to each claim | "may potentially offer improvements" | "four times fewer FLOPs (Table 2) … 3.1 points (Table 4)" |
| Varied the rhythm | all 14–24 words | 12, 15, 28, 5 / 5, 19, 22, 40 |
| Cut the tricolon | "accurate, efficient, and scalable" | deleted; it said nothing |
| Landed the verdict short | — | "Magnitude is the wrong proxy." |

The rewrite is **shorter in claims and longer in facts**. That is the whole trick.
It reads as human because someone with a result wrote it; the machine tells
disappeared as a side effect of saying something specific, not as the goal.

## The over-correction, for contrast  (`tests/fixtures/overcorrected.tex`)

The same argument, "humanized" by force:

> Pruning is old. Pruning is slow. Pruning is wrong here. We route instead. We gate
> once. We dispatch twice. The gain is real — and it is not about capacity, but about
> timing — which is the whole point. Why does per-layer routing fail? Because the
> signal arrives late.

```
  [FAIL] sentence-length variance         stdev 4.1 — target >= 8.0 (mean 5.9, max 18)
  [WARN] choppiness (over-correction)     mean 5.9 words, 76.2% of sentences under 7 words — ...
  [WARN] em-dash density                  6 em-dashes, 4.51 per 100 words — ...
  [WARN] contrastive negation             3 'not X, but Y' frames, 14.3 per 100 sentences — ...
  [WARN] repeated sentence openers        2 paragraph(s) with three or more consecutive sentences ...
  [WARN] rhetorical questions             2 question(s), 15.04 per 1000 words — ...
```

Zero banned words, and it fails anyway: the variance is as low as the slop's, from the
other side. Stage 3 and this fixture make the same claims. One reads like a
researcher; the other reads like a tool trying not to sound like a tool.

## Reproduce

```bash
S=skills/research-pro/scripts
python3 $S/prose_metrics.py tests/fixtures/slop.tex   --no-strict      # stage 1: 6 FAIL
python3 $S/prose_metrics.py tests/fixtures/clean.tex  --paragraphs     # stage 2: 1 FAIL, see row 1
python3 $S/prose_metrics.py tests/fixtures/clean2.tex                  # stage 3: exit 0
python3 $S/prose_metrics.py tests/fixtures/clean2.tex --compare tests/fixtures/slop.tex
python3 $S/prose_metrics.py tests/fixtures/overcorrected.tex           # the other register
```
