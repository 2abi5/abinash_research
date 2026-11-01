# abinash_research

Claude Code skills that take a research paper from an idea to a submission — with
gates that block instead of advising.

Two skills, twelve slash commands, ten deterministic checkers, and dated compliance
profiles for nine top venues. Everything is a routed reference file, so a request to
tighten one abstract does not load a ten-stage pipeline.

```
S0 Intake ........ what did you find, and why doesn't a reviewer already know it
S1 Architecture .. story spine + section budget + project scaffold
S2 Literature .... seed expansion, screening, the map, synthesis
S3 Evidence plan . one experiment per claim, decided BEFORE drafting
S4 Draft ......... section by section, paragraph by paragraph
     └─ GATE 1  every claim mapped to evidence, or cut
S5 Figures ....... teaser, architecture, analysis, results tables
S6 Citations ..... every reference resolved; load-bearing ones traced to a page
     └─ GATE 2  zero unverifiable references
S7 Prose ......... authorial voice, flow, terminology; disclosure drafted
S8 Compliance .... live venue rules: length, format, anonymity, checklists
     └─ GATE 3  zero hard-rule violations
S9 Review ........ five-seat adversarial panel → readiness score
     └─ GATE 4  readiness ≥ threshold and no failed gate
```

A gate that has not been run is not passed. No gate is waived on request.

## Install

**In a hurry? [QUICKSTART.md](QUICKSTART.md) is the copy-paste version.**

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

**Without installing** — clone it anywhere and say *"use the research-pro skill in
./abinash_research"*. Works, but the skills will not auto-trigger on their own:
Claude Code only discovers skills under `.claude/skills/`, `~/.claude/skills/`, or an
installed plugin.

Whichever route you pick, `new_paper.py` writes the correct script path into the
generated `Makefile` — relative when the skill is cloned into the project (so a
committed Makefile still works for co-authors), absolute for a global or plugin
install. Override per machine with `make check S=/path/to/scripts`.

Requirements: Python 3.9+, stdlib only. `latexmk` for building, `pdfinfo` and
`pdftotext` (poppler-utils) for PDF checks — all optional; every script degrades and
says what it could not check.

## Commands

| Command | Does |
|---|---|
| `/rp-new` | Intake interview, story spine, scaffold the project |
| `/rp-calibrate` | Learn a target profile from reference papers; compare your draft to it |
| `/rp-lit` | Seed expansion through OpenAlex, scoping scan, or full systematic review |
| `/rp-draft` | Draft or rewrite one section |
| `/rp-figures` | Design or audit figures and tables |
| `/rp-cite` | Verify every citation and work the Layer-3 list (Gate 2) |
| `/rp-humanize` | Fix machine-sounding prose; draft the AI disclosure |
| `/rp-venue` | Check against a venue's hard rules (Gate 3) |
| `/rp-review` | Five-seat adversarial review panel |
| `/rp-score` | Gated readiness score (Gate 4) |
| `/rp-rebuttal` | Response to reviewers |
| `/rp-overleaf` | Set up or run the Overleaf sync loop |

Or just describe what you want — the skills trigger on intent.

## The five things people ask for most

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

### Map the literature before you write

```bash
python3 $S/lit_scan.py --seed 10.1000/closest.2023 --seed arXiv:2401.01234 \
        --search "the mechanism, phrased as the field would" --since 2019 \
        --sentinels 10.1000/a-paper-you-know-matters.2024 --out lit/
```

Give it the two to five papers nearest your idea. It pulls what they cite and what
cites them from OpenAlex (no key needed), ranks the union by how many of your seeds
each candidate touches, and writes three things: the ranked candidate list with the
query, date and hit count recorded for the search record; a saturation table that
says how many new papers each seed added, which is the stop rule made measurable; and
a map skeleton whose `Fails when` column is what the gap paragraph gets written from.

Forward citation chasing is the step people skip and the step that finds the paper
published four months ago that scoops you. `--sentinels` is the other check: name the
papers you already know matter, and the report says whether the seeds reached them. A
search that misses what you know will miss what you do not.

It produces leads. Every candidate is still opened, read at the depth its role
requires, and verified before it becomes a citation. The worked example in
`examples/05-lit-map-to-gap.md` runs the whole chain on a recorded (fictional)
neighbourhood.

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
| `verify_citations.py` | Fabricated references (a near-miss title hit is rejected unless author or year agree), retracted papers, metadata mismatches, preprints whose published version exists, duplicates, uncited entries, citation stacks and `[12]`-as-a-noun, and the **Layer-3 worklist**: every load-bearing citation, with whether the ledger records where the source supports it |
| `prose_metrics.py` | Banned phrases with line numbers, sentence-length variance, hedge stacking, transition-opener density, empty topic sentences, em-dash density, "not X, but Y" frames, repeated openers, section-closing summaries, the over-corrected staccato register; `--paragraphs` for the rewrite loop, `--compare` for before/after deltas |
| `lit_scan.py` | Seed papers → backward references and forward citations from OpenAlex, ranked by how many seeds each candidate touches; saturation per seed (the stop rule), sentinel recall, retracted candidates, the search record, and the map skeleton |
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
  Scholar / arXiv / dblp, or marked `[NEEDS SOURCE]` for you to fill. A plausible-looking
  DOI is the single most damaging thing a writing tool can produce. A title-search hit
  is not verification either: the first author or the year has to agree, a 404 is
  treated as evidence and a timeout is not, and retracted records are flagged.
- **Never invents a result.** No numbers, no "improves by 3.2%", no significance
  claim you did not supply. Unfilled cells stay `[TBD]`.
- **Fixes prose; does not evade detectors.** `/rp-humanize` removes the machine
  register — flat rhythm, abstract nouns, stacked hedges, empty paragraphs — because
  that is what *reviewers* penalize. It also warns when a rewrite has overshot into
  the other machine register: staccato fragments, rhetorical questions, a dash in
  every sentence. It will not help conceal AI assistance a venue requires you to
  disclose, and it ships with the disclosure templates instead.
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
- **Layer 3 of citation checking is still a person reading a PDF.** The verifier now
  extracts every load-bearing citation into a worklist and checks that the ledger
  records where each source supports its claim, but whether it *does* is decided by
  opening it. The worklist makes the work visible; it does not do it.
- **The literature scanner produces leads, not a bibliography.** It sees what
  OpenAlex indexes, it needs the network, and a candidate becomes a citation only after
  it has been read and verified.
- **Venue profiles are snapshots.** Re-verify. Always.
- **An exemplar profile describes what got accepted, not a formula for acceptance.**
  Matching a NeurIPS paper's shape does not give you a NeurIPS contribution.
- **Three exemplars is a small sample.** Deviations are questions, not verdicts.

## Layout

```
skills/research-pro/         orchestrator: 23 references, 10 scripts, 9 venue profiles, 6 worked examples, templates
skills/paper-reviewer/       five-seat adversarial review panel
commands/                    twelve /rp-* slash commands
tests/                       deliberately broken fixtures + `run_checks.sh`, which every checker must still catch
```

## Worked examples

`skills/research-pro/examples/` shows the moves, not just the rules:

- **The humanizer in three measured stages** — slop → rewrite → fix, with the real
  `prose_metrics.py` output at each step, *including a stage that still fails*.
  Reproducible from the fixtures.
- **The gap paragraph** — patch framing vs limitation-without-a-reason vs challenge
  framing, analysed clause by clause. This is the paragraph papers are won on.
- **Limitations** — ritual → specific, and the line you must not cross.
- **Gate 1 catching an unsupported abstract claim** — the extraction, the two honest
  ways to close it, and why hedging is worse than either.
- **From the literature map to the gap** — a recorded scan, the reading depths, the
  filled map, and the gap paragraph and Related Work groupings read off its
  `Fails when` column.
- **The citation that did not say that** — the real Layer-3 worklist on a fixture
  with a citation stack, a retracted source and an unfinished ledger row, each closed
  honestly, plus the claim-drift case no script catches.

## Credits

Prior art that shaped this: **Master-cai/Research-Paper-Writing-Skills** (MIT),
which packages Prof. Peng Sida's writing notes — the craft doctrine here comes from
that lineage; and **Imbad0202/academic-research-skills** (CC-BY-NC-4.0), whose staged
pipeline with blocking integrity gates shaped the architecture. Nothing is vendored
from either. See [CREDITS.md](CREDITS.md).

## License

MIT — see [LICENSE](LICENSE).
