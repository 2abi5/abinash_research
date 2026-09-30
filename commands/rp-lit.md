---
description: Literature review — scoping scan or full systematic review
argument-hint: "[topic] [--systematic]"
---
Invoke `research-pro` and read `references/03-literature-review.md`.

Topic: $ARGUMENTS

Pick the right job and say which you are doing: scoping scan (hours, 20–40 papers),
Related Work section, or systematic review (weeks, the review *is* the contribution).

For a scoping scan: three seeds, expand backward through references and **forward
through citations** (this is what finds the paper that scooped you), stop when a new
paper's references hold nothing new. Produce the map table with a `Fails when` column
and a `Baseline?` column.

For a systematic review: write the protocol **before** searching — databases and
why, verbatim search strings per database with the date each ran, date range,
inclusion/exclusion criteria, screening procedure. Then PRISMA counts, extraction
table, risk-of-bias per domain, and a synthesis method you name.

**Never generate a reference list from memory.** Every paper you name is either
verified against a real record or marked `[NEEDS SOURCE]`. Then run
`scripts/verify_citations.py`.
