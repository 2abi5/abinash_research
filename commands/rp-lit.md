---
description: Literature review — scoping scan, search strings, or full systematic review
argument-hint: "[topic or seed DOIs] [--systematic]"
---
Invoke `research-pro` and read `references/03-literature-review.md`.

Topic: $ARGUMENTS

Pick the right job and say which you are doing: scoping scan (hours, 20–40 papers),
Related Work section (`references/04-related-work.md`), or systematic review (weeks,
the review *is* the contribution).

**Scoping scan.** Ask for two to five seeds by role (closest prior work, strongest
baseline, the survey), then expand them:

```
python3 skills/research-pro/scripts/lit_scan.py --seed <doi|arXiv:id|W-id> [--seed ...] \
    [--search "mechanism phrased as the field would"] [--since YYYY] \
    [--sentinels <doi,doi>] --out lit/
```

Read `lit/candidates.md`: links ≥ 2 first, then the retraction flags, then recent
one-link papers as possible concurrent work. Report the saturation table (stop when a
new seed adds nothing) and sentinel recall (a known paper the seeds do not reach means
wrong seeds). Assign each paper a depth (WHY / HOW / WHAT), write reading notes for
the WHY and HOW papers, and fill `lit/map.md`: the `Fails when` column is what the gap
statement is written from, `Baseline?` is the main table.

If OpenAlex is unreachable the scanner reports `BLOCKED`. Do the expansion by hand
(reference lists backward, "cited by" forward) and record each query, date and hit
count anyway.

**Systematic review.** Write the protocol **before** searching: question in
PICO/DTCO form, databases and why, search strings built from concept blocks and
tested for recall on sentinel papers, verbatim per database with the date each ran,
date range, inclusion/exclusion criteria piloted on twenty records, screening
procedure with κ, extraction form piloted on five papers. Then PRISMA counts, the
screening log, risk of bias per domain, a named synthesis method, and the synthesis
matrix written down its columns. Templates: `templates/lit-review.md`.

**Never generate a reference list from memory.** Every paper you name is either
verified against a real record or marked `[NEEDS SOURCE]`. Every candidate is a
lead until it has been opened. Finish by running `scripts/verify_citations.py` on
whatever reached the `.bib`.
