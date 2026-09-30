# abinash_research

Claude Code skills that take a research paper from an idea to a submission — with
gates that block instead of advising.

Two skills, twelve slash commands, nine deterministic checkers, and dated compliance
profiles for nine top venues. Everything is a routed reference file, so a request to
tighten one abstract does not load a ten-stage pipeline.

```
S0 Intake ........ what did you find, and why doesn't a reviewer already know it
S1 Architecture .. story spine + section budget + project scaffold
S2 Literature .... search protocol, screening, extraction, synthesis
S3 Evidence plan . one experiment per claim, decided BEFORE drafting
S4 Draft ......... section by section, paragraph by paragraph
     └─ GATE 1  every claim mapped to evidence, or cut
S5 Figures ....... teaser, architecture, analysis, results tables
S6 Citations ..... every reference resolved against a real record
     └─ GATE 2  zero unverifiable references
S7 Prose ......... authorial voice, flow, terminology; disclosure drafted
S8 Compliance .... live venue rules: length, format, anonymity, checklists
     └─ GATE 3  zero hard-rule violations
S9 Review ........ five-seat adversarial panel → readiness score
     └─ GATE 4  readiness ≥ threshold and no failed gate
```

A gate that has not been run is not passed. No gate is waived on request.

## Install

Pick one. All four give you the same skills and commands.

**As a plugin (recommended)** — in Claude Code:
```
/plugin marketplace add 2abi5/abinash_research
/plugin install abinash-research@abinash-research
```

**Project skills** — available in one repository:
```bash
git clone https://github.com/2abi5/abinash_research
mkdir -p .claude/skills .claude/commands
cp -r abinash_research/skills/*    .claude/skills/
cp -r abinash_research/commands/*  .claude/commands/
```

**Global skills** — available everywhere:
```bash
cp -r abinash_research/skills/*   ~/.claude/skills/
cp -r abinash_research/commands/* ~/.claude/commands/
```

**Without installing** — clone it and say *"use the research-pro skill in
./abinash_research"*.

Requirements: Python 3.9+, stdlib only. `latexmk` for building, `pdfinfo` and
`pdftotext` (poppler-utils) for PDF checks — all optional; every script degrades and
says what it could not check.

## Commands

| Command | Does |
|---|---|
| `/rp-new` | Intake interview, story spine, scaffold the project |
| `/rp-calibrate` | Learn a target profile from reference papers; compare your draft to it |
| `/rp-lit` | Scoping scan or full systematic review |
| `/rp-draft` | Draft or rewrite one section |
| `/rp-figures` | Design or audit figures and tables |
| `/rp-cite` | Verify every citation (Gate 2) |
| `/rp-humanize` | Fix machine-sounding prose; draft the AI disclosure |
| `/rp-venue` | Check against a venue's hard rules (Gate 3) |
| `/rp-review` | Five-seat adversarial review panel |
| `/rp-score` | Gated readiness score (Gate 4) |
| `/rp-rebuttal` | Response to reviewers |
| `/rp-overleaf` | Set up or run the Overleaf sync loop |

Or just describe what you want — the skills trigger on intent.

## The four things people ask for most

### Upload a paper, match it

An accepted paper from your target venue is a *measured specification* of what that
venue accepts. Extract it, then check your draft against it:

```bash
S=skills/research-pro/scripts
pdftotext -layout exemplar.pdf exemplar.txt            # for PDFs
python3 $S/exemplar_profile.py exemplar.txt --out paper/exemplar_profile.json
python3 $S/exemplar_profile.py paper/main.tex --compare paper/exemplar_profile.json
```

It measures section order, page allocation per section, figure/table/equation
counts, citation density, abstract length, sentence-length distribution, hedging and
first-person density — then flags every deviation beyond ±25%. That is how you find
out your Method is 40% over the venue's norm while your Experiments is 30% under,
which is exactly the imbalance that draws "insufficient evaluation".

Structure and register get copied. **Wording never does** — that is plagiarism, and
venues run similarity checks.

### Point it at a codebase

```bash
python3 $S/repo_scan.py . --out paper/provenance.json
```

Inventories configs, saved results, logged metrics, seeds, datasets, loss terms and
their weights, optimizer settings, entry points, environment pins, and git
provenance. Then it prints the eleven reconciliation questions that must be answered
before drafting — *does every number the paper will report come from a file in the
result list; does every ablation described have a config; do the hyperparameters
match the paper exactly.*

The point is the mismatches. A hyperparameter in the paper that disagrees with the
config that produced the number is the defect reviewers and reproducers find *after*
publication. This finds it before.

The scan establishes what the artifacts support. It cannot tell you what the
contribution is — that comes from you, in intake. Where the two disagree, you get
told.

### Overleaf

Your co-authors edit in the browser; you want the checks to run on the same files.

```bash
git clone https://git.overleaf.com/<PROJECT_ID> paper     # token-only auth: user "git"
cd paper && git pull                                     # always first
make check                                               # lint, cites, prose, figures, tokens
make overleaf-push M="§4: 3-seed ADE20K results"         # checks run BEFORE the push
```

Git integration is a paid Overleaf feature and password auth has been removed — use
an authentication token as the password. Overleaf cannot run your Python, so tables
and figures are generated locally and the artifacts *and* generators are both
committed. That keeps hand-typed numbers out of a project several people can edit.
`references/20-overleaf.md` covers conflicts, compile timeouts, shell-escape, and the
free-plan zip round-trip.

### Is it ready?

```bash
python3 $S/score_readiness.py paper/readiness.json --venue neurips --strict
```

Ten dimensions, weighted by what the target venue actually grades hardest, with six
hard gates that override the number. Every dimension needs an `evidence` string
naming the artifact it was scored from — **the scorer refuses to score without
one**, because a score with no artifact behind it is a guess wearing a decimal point.

## Checkers

All stdlib Python, all with `--help`, all degrade gracefully and say what they could
not check.

| Script | Finds |
|---|---|
| `verify_citations.py` | Fabricated references, metadata mismatches, duplicates, uncited entries, unupgraded preprints, unprotected capitalisation |
| `prose_metrics.py` | Banned phrases with line numbers, sentence-length variance, hedge stacking, transition-opener density, empty topic sentences, nominalisation and passive rates |
| `venue_check.py` | Page limit, required sections, anonymity leaks, named repo links, gap tokens, **prompt injection** (source and PDF text) |
| `latex_lint.py` | Undefined refs, duplicate labels, caption/label order, figure-vs-table caption placement, `\hline` and vertical rules, unreferenced floats, overfull boxes |
| `figure_audit.py` | Raster where vector belongs, raster hidden in a PDF, DPI at placement width, **natural size vs placement width** (the scaling that shrinks your fonts), unembedded fonts |
| `score_readiness.py` | The gated verdict |
| `exemplar_profile.py` | Structural profile of reference papers; deviation report for your draft |
| `repo_scan.py` | Codebase provenance and the reconciliation questions |
| `new_paper.py` | Scaffolds the project layout the rest of the pipeline expects |

## Venues

Dated profiles for **NeurIPS · ICML · ICLR · CVPR · ACL-family (ARR) · AAAI · TMLR ·
TPAMI · Nature**, each with page limits and what is excluded from them, required
sections and checklists, anonymity rules, AI-use policy, desk-reject triggers, what
the venue rewards, and what gets rejected there.

Checked 2026-09-30. **They go stale every cycle** — the skill is required to re-read
the live call for papers before Gate 3 passes, and `venues/VERIFY.md` says how. Add
your own from `venues/_template.md`.

## Where this draws its lines

- **Never fabricates a reference.** Verified against Crossref / OpenAlex / Semantic
  Scholar / arXiv, or marked `[NEEDS SOURCE]` for you to fill. A plausible-looking
  DOI is the single most damaging thing a writing tool can produce.
- **Never invents a result.** No numbers, no "improves by 3.2%", no significance
  claim you did not supply. Unfilled cells stay `[TBD]`.
- **Fixes prose; does not evade detectors.** `/rp-humanize` removes the machine
  register — flat rhythm, abstract nouns, stacked hedges, empty paragraphs — because
  that is what *reviewers* penalize. It will not help conceal AI assistance a venue
  requires you to disclose, and it ships with the disclosure templates instead.
  ICML desk-rejected 497 submissions in one cycle over LLM-policy violations; ICLR
  has desk-rejected LLM-generated papers outright. Disclosure is cheaper than the
  risk by orders of magnitude.
- **Checks for prompt injection in your own draft**, including in LaTeX comments,
  and tells you if it finds any. It is a rejection-and-report offence at several
  venues, and it can arrive via a template or a collaborator.
- **Will tell you the paper isn't ready.** If the blocking findings all need
  experiments and the deadline is in two weeks, you get told that instead of a
  polished manuscript that gets rejected.

## Limits worth knowing

- **A tool cannot supply a contribution.** These skills make a real finding legible
  and defensible, and make a thin one visibly thin. That second outcome is the useful
  one, and it arrives months earlier than a reviewer's version of it.
- **Layer 3 of citation checking is manual.** Whether a source *says what you claim
  it says* is not automatable. The scripts check existence and metadata; you open the
  PDF.
- **Venue profiles are snapshots.** Re-verify. Always.
- **An exemplar profile describes what got accepted, not a formula for acceptance.**
  Matching a NeurIPS paper's shape does not give you a NeurIPS contribution.
- **Three exemplars is a small sample.** Deviations are questions, not verdicts.

## Layout

```
skills/research-pro/         orchestrator: 23 references, 9 scripts, 9 venue profiles, templates
skills/paper-reviewer/       five-seat adversarial review panel
commands/                    twelve /rp-* slash commands
tests/                       deliberately broken fixtures + `run_checks.sh`, which every checker must still catch
```

## Credits

Prior art that shaped this: **Master-cai/Research-Paper-Writing-Skills** (MIT),
which packages Prof. Peng Sida's writing notes — the craft doctrine here comes from
that lineage; and **Imbad0202/academic-research-skills** (CC-BY-NC-4.0), whose staged
pipeline with blocking integrity gates shaped the architecture. Nothing is vendored
from either. See [CREDITS.md](CREDITS.md).

## License

MIT — see [LICENSE](LICENSE).
