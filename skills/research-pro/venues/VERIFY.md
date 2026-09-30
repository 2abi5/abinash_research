# Re-verification protocol

**Every rule in this directory is a dated snapshot. All of it goes stale.**

Page limits change. Checklists get added. Anonymity rules tighten. AI-use policies
are currently changing faster than anything else in academic publishing — several
venues revised theirs mid-cycle. A paper desk-rejected for a rule that changed is
rejected just the same.

## The rule

Before you report that a manuscript is venue-compliant — i.e. before Gate 3 passes
— re-read the live source. Not your memory, not this directory.

1. Fetch the venue's own author instructions and policy pages. The URLs are in
   `registry.json` under `urls`.
2. Compare against the profile field by field: page limit, what is excluded from
   it, required sections, required checklists, anonymity, AI policy, dual
   submission, deadlines.
3. **Where they differ, the live page wins.** Update the profile and
   `registry.json`, and bump `verified_on`.
4. Where you could not fetch (no network, page moved), say so explicitly and mark
   the compliance report `BLOCKED: unverified` with the fields you could not
   confirm. Do not report `PASS` from a snapshot.

## What to check every single time

These are the fields that move most:

- [ ] Page limit, and precisely what is excluded from it
- [ ] Required sections (limitations, impact, ethics) and whether they are desk-reject-hard
- [ ] Required checklists, and where in the PDF they go
- [ ] AI / LLM policy, and what "significant use" means this cycle
- [ ] Anonymity rules, including code and supplementary material
- [ ] Dual-submission window and overlap threshold
- [ ] The abstract deadline, where it differs from the paper deadline
- [ ] Template version (a last-cycle `.sty` can change the page count)

## Adding a venue

Copy `_template.md`, fill it from the venue's own pages, add a matching entry to
`registry.json`, and record the date. Do not fill a profile from memory — that is
the failure mode this whole directory exists to prevent.
