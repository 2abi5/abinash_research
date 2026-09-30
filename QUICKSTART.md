# Quickstart

From zero to a drafted section. Copy-paste, in order.

## 1. Install (once per machine)

```bash
git clone https://github.com/2abi5/abinash_research ~/abinash_research
mkdir -p ~/.claude/skills ~/.claude/commands
cp -r ~/abinash_research/skills/*   ~/.claude/skills/
cp -r ~/abinash_research/commands/* ~/.claude/commands/
```

That's it. Every project on this machine now has it — you never repeat this.

> Prefer the plugin? `/plugin marketplace add 2abi5/abinash_research` then
> `/plugin install abinash-research@abinash-research`. Same result, updates with
> `/plugin update`. Don't do both.

## 2. Start a new Claude Code session

Skills load at session start, so an already-open session won't see them.

```bash
cd ~/my-research-project
claude
```

## 3. Check it loaded

Type a forward slash and look for the `rp-` commands:

```
/rp-
```

You should see `rp-new`, `rp-draft`, `rp-cite`, `rp-humanize`, `rp-score` and the
rest. If not, see Troubleshooting below.

## 4. Start the paper

```
/rp-new
```

It will ask you roughly six things. The two that matter:

- **What did you find?** One sentence. No methods, no motivation.
- **What do you already have?** Which datasets, which baselines, how many seeds,
  where the numbers live, whether the code runs.

Then it builds a six-line story spine, shows it to you, and waits. **Read the
spine.** If line 2 doesn't name a *reason* prior work fails — not just that it
fails — push back before drafting. That line is the paper.

Say yes and it scaffolds:

```
paper/
├── main.tex            LEDGER.md        <- your claims and their evidence
├── sections/           VENUE.md         <- your venue's hard rules
├── figures/ tables/ results/            Makefile
```

## 5. Draft

```
/rp-draft method
/rp-draft experiments
/rp-draft intro
/rp-draft abstract
```

Draft the abstract and intro **last** — they make promises the rest of the paper
has to keep.

Or skip the slash commands and just talk: *"draft §4.2 from results/imagenet/*.json"*,
*"tighten the second paragraph of the intro"*, *"this related work section is a
citation dump, fix it"*.

Each pass returns LaTeX ready to paste, plus the gaps it could not fill:
`[TBD]` (a number you must supply), `[NEEDS SOURCE]` (a citation to verify),
`[NEEDS EXPERIMENT]` (a claim with no experiment), `[AUTHOR DECISION]` (yours).

**Those gaps are the product, not a failure.** Each one is something a reviewer
would have found.

## 6. Check, every session

```bash
cd paper && make check
```

Runs the LaTeX lint, citation verification, prose metrics, figure audit, venue
compliance, and a leftover-token grep. Takes seconds. Run it weekly and it costs
nothing; run it the night before a deadline and it costs hours.

## 7. Before you submit

```
/rp-cite          # verify every reference (Gate 2)
/rp-humanize      # kill the machine register, draft the AI disclosure
/rp-venue neurips # hard rules, re-verified against the live CFP (Gate 3)
/rp-review        # five-seat adversarial panel — the review you'd rather get now
/rp-score neurips # the gated verdict (Gate 4)
```

`/rp-score` tells you `SUBMIT`, `BORDERLINE`, or `NOT READY` — and if a gate
failed, `NOT READY` regardless of the number. It also predicts the reviewer
objections in the reviewer's voice, in the order they will arrive.

---

## Other entry points

You don't have to start at step 4.

| You have | Do this |
|---|---|
| A codebase, no paper | `/rp-new from codebase` — scans configs and `results/`, so Method and Implementation come from what you actually ran |
| A paper you want to match | `/rp-calibrate exemplar.txt` — measures its section budget and register, drafts to match. PDFs: `pdftotext -layout in.pdf out.txt` first |
| A half-written draft | Point at the `.tex`: *"rewrite §3 using the research-pro skill"* |
| Reviewer comments | `/rp-rebuttal` and paste them |
| An Overleaf project | `/rp-overleaf setup` |
| No topic yet | `/rp-lit "your area"` — scoping scan first |

## Overleaf

```bash
git clone https://git.overleaf.com/<PROJECT_ID> paper   # user: git, password: your token
cd paper
git pull                                   # ALWAYS first — co-authors edit in the browser
make check
make overleaf-push M="§4: 3-seed results"  # checks run BEFORE the push
```

Git integration is a paid Overleaf feature and auth is token-only (Account Settings
→ Git integration). Never force-push.

## Troubleshooting

**`/rp-` commands don't appear**
- Start a *new* session — skills and commands load at startup.
- `ls ~/.claude/commands/ | head` should list `rp-new.md` and friends.
- `ls ~/.claude/skills/` should show `research-pro` and `paper-reviewer`.

**It didn't trigger when I just described what I wanted**
- Name it: *"use the research-pro skill to draft the method section"*.

**`make check` says a script isn't found**
- Point it at your install: `make check S=~/.claude/skills/research-pro/scripts`

**Citation verification says BLOCKED**
- No network. It needs `api.crossref.org`, `api.openalex.org`,
  `api.semanticscholar.org`, `export.arxiv.org`. Structural checks alone do **not**
  pass Gate 2 — that's deliberate.

**"Unknown venue"**
- `python3 ~/.claude/skills/research-pro/scripts/venue_check.py --list`
- Add your own from `skills/research-pro/venues/_template.md`.

**A venue rule looks out of date**
- It probably is. Profiles are dated snapshots; the skill is required to re-read the
  live CFP before Gate 3. Fix the profile and bump `verified_on` in
  `venues/registry.json`.

## Two things it will not do

- **Invent a number.** Empty cells come back `[TBD]`.
- **Invent a citation.** Unverified references come back `[NEEDS SOURCE]`.

Bring your results. It writes the paper around them.
