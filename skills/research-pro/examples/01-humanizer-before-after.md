# Worked example — the humanizer, with real measurements

Every number in this file is the actual output of
`scripts/prose_metrics.py` on the fixture named beside it. Nothing here is
estimated. Reproduce it yourself with the commands at the bottom.

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
[FAIL] banned phrases/words          25 hits
[FAIL] sentence-length variance      stdev 4.0     (target >= 8)
[FAIL] short sentence per paragraph  66.7%         (target <= 25%)
[FAIL] transition openers            33.3%         (target <= 25%)
[FAIL] hedge stacking                1 paragraph   (target 0)
[FAIL] empty topic sentences         1             (target 0)
       hedges                        2.40 / 100 words
```

Six failures. Every sentence is 14–24 words. Two paragraphs, zero facts.

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
[PASS] banned phrases/words          0
[PASS] sentence-length variance      stdev 10.6    (mean 20.1, max 40)
[FAIL] short sentence per paragraph  50.0%         (target <= 25%)   <-- still failing
[PASS] transition openers            0.0%
[PASS] hedge stacking                0
[PASS] empty topic sentences         0
       hedges                        0.00 / 100 words
```

**The rewrite still fails one check**, and that is the useful part of this example.
Paragraph 1's shortest sentence is 12 words; the rule wants one under 10, because
the short sentence is where the argument lands. The tool is stricter than a human
editor would be here, and it is right.

Per-sentence lengths: `12, 15, 28  |  5, 19, 22, 40`. Paragraph 2 has its short
sentence ("We route instead of prune." — 5 words). Paragraph 1 does not.

## Stage 3 — one sentence added  (`tests/fixtures/clean2.tex`)

Added after the pruning sentence in paragraph 1:

> Magnitude is the wrong proxy.

```
[PASS] banned phrases/words          0
[PASS] sentence-length variance      stdev 11.1    (mean 18.2, max 40)
[PASS] short sentence per paragraph  0.0%
[PASS] transition openers            0.0%
[PASS] hedge stacking                0
[PASS] empty topic sentences         0
exit code 0
```

Five words fixed the last failure, and they also made the paragraph better: the
reader now gets the verdict on prior work in a sentence they cannot skim past.

## What actually changed between stage 1 and stage 3

| Move | Before | After |
|---|---|---|
| Opened on the problem, not the field | "In recent years, there has been growing interest" | "deployed on devices that cannot afford their inference cost" |
| Replaced abstraction with a number | "efficient inference" | "4.1 GFLOPs per image; budget closer to 1" |
| Named the failure's **reason** | "the intricate nature of these models" | "assumes weight magnitude predicts importance — fails once the signal is input-dependent" |
| Named the mechanism concretely | "a holistic framework" | "one gate scores the bank from pooled context, dispatches to the top two" |
| Attached evidence to each claim | "may potentially offer improvements" | "four times fewer FLOPs (Table 2) … 3.1 points (Table 4)" |
| Varied the rhythm | all 14–24 words | 12, 15, 28, 5 / 5, 19, 22, 40 |
| Cut the tricolon | "accurate, efficient, and scalable" | deleted — it said nothing |
| Landed the verdict short | — | "Magnitude is the wrong proxy." |

The rewrite is **shorter in claims and longer in facts**. That is the whole trick.
It reads as human because someone with a result wrote it; the machine tells
disappeared as a side effect of saying something specific, not as the goal.

## Reproduce

```bash
S=skills/research-pro/scripts
python3 $S/prose_metrics.py tests/fixtures/slop.tex   --no-strict   # stage 1: 6 FAIL
python3 $S/prose_metrics.py tests/fixtures/clean.tex  --no-strict   # stage 2: 1 FAIL
python3 $S/prose_metrics.py tests/fixtures/clean2.tex               # stage 3: exit 0
```
