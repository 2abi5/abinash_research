# Credits and prior art

This suite was written from scratch for this repository. No text, template, or
code was copied from the projects below. They are credited because they shaped
the design, and because anyone using this suite should know they exist and are
worth reading directly.

## 1. Research-Paper-Writing-Skills — Master-cai

<https://github.com/Master-cai/Research-Paper-Writing-Skills> (MIT)

That project packages **Prof. Peng Sida's** open study notes on writing
ML/CV/NLP papers. The craft doctrine it transmits is the strongest part of the
prior art, and this suite adopts the same underlying convictions:

- Decide the paper's story before editing sentences.
- One paragraph carries one message, stated in its first sentence.
- Lead the reader to *the technical challenge you actually solved* — never open
  with a naive baseline and then describe your patch on it.
- A method module is only explained once you have given its **design**, its
  **motivation**, and its **technical advantage**.
- Reverse-outline every section after writing it.
- Every claim in the Abstract and Introduction is checked against the evidence
  that exists, and weakened or cut when the evidence is not there.
- Figures and tables are content, not decoration.

The original notes are the primary source. Read them.

## 2. academic-research-skills — Cheng-I Wu

<https://github.com/Imbad0202/academic-research-skills> (CC-BY-NC-4.0,
DOI 10.5281/zenodo.20696614)

A far larger, multi-agent, multi-stage research system. Its **architecture**
influenced this suite: a staged pipeline, blocking integrity gates between
stages rather than advice at the end, an explicit claim/evidence carrier passed
between stages, separated reviewer roles including a devil's advocate,
treating pasted and fetched text as data rather than instructions, and
disclosure of AI assistance instead of concealment.

That project is licensed **CC-BY-NC 4.0** (non-commercial). Nothing from it is
vendored here, so this repository's MIT license applies cleanly to its own
contents. If you want that system, install it from its own repository under its
own terms.

## 3. "Academic Research Paper Writer" skill — mcpmarket.com listing

<https://mcpmarket.com/tools/skills/academic-research-paper-writer>

A compact single-file skill: clarify topic and scope, then follow a fixed
IMRaD-ish structure with numbered IEEE/ACM-style citations. Its contribution to
this design is the reminder that **the entry point must be cheap**. A
researcher who wants an abstract tightened should not have to boot a ten-stage
pipeline. Hence `SKILL.md` here is a router, and every stage is usable alone.

## 4. Venue rules

Venue profiles under `skills/research-pro/venues/` were compiled from each
venue's own author instructions and policy pages, each recorded with the date it
was checked. They are **snapshots and they go stale every cycle**. See
`skills/research-pro/venues/VERIFY.md` — the skill is required to re-read the
live call for papers before it signs off on compliance.

## 5. Writing-flow material

The reverse-outlining and transition-signposting practice in
`references/12-prose-quality.md` is standard university writing-center doctrine,
the same body of advice that reaches the Master-cai repository through a
"Does My Writing Flow?" handout. It is long-standing common practice, restated
here in our own words.
