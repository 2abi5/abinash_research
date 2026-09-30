#!/usr/bin/env python3
"""Scaffold a paper project: the layout the rest of the pipeline expects.

Writes main.tex, per-section files, a ledger, a Makefile with the check targets,
a readiness scorecard stub, figure/table generators, and a README -- pre-filled
with the target venue's hard rules from venues/registry.json.

  new_paper.py --title "Sparse Expert Routing" --venue neurips --out paper/

Stdlib only. Refuses to overwrite unless --force.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

import _textlib as T

SECTIONS = [
    ("00-abstract", "Abstract", "% 150-250 words. Task / challenge+reason / mechanism /\n"
     "% headline number / so-what. See references/09-abstract-title-intro.md.\n"
     "% Every claim here goes in LEDGER.md.\n"),
    ("01-intro", "Introduction", "% P1 task and stakes\n% P2 prior work -> the challenge, ending in the technical REASON\n"
     "% P3 our method, concretely, + teaser figure pointer\n% P4 evidence\n% P5 contributions, each paired with its advantage\n"),
    ("02-related", "Related Work", "% 2-4 groupings BY MECHANISM. Each ends in the limitation that matters to us,\n"
     "% then one checkable distinction sentence. Not a citation list.\n"),
    ("03-method", "Method", "% 3.1 Overview: formalism, assumptions A1-A2, figure pointer, roadmap\n"
     "% then one subsection per module: motivation -> design -> advantage\n"),
    ("04-experiments", "Experiments", "% 4.1 Setup  4.2 Main results  4.3 Ablations  4.4 Analysis\n"
     "% Tables are \\input from tables/, generated from results/. Never hand-typed.\n"),
    ("05-discussion", "Discussion", "% interpretation -> relation to prior findings -> implications -> limitations\n"),
    ("06-conclusion", "Conclusion", "% 5-8 sentences. No new claims. No new citations.\n"),
    ("90-appendix", "Appendix", "% implementation details, proofs, extra ablations, notation table\n"),
]


def venue_block(V: dict | None, slug: str | None) -> str:
    if not V:
        return "No venue set. Set one before drafting: it decides length, structure,\nanonymity, and required sections.\n"
    L = V["length"]
    out = [f"Target: {V['name']} {V['cycle']}  (slug: {slug})", ""]
    if L.get("main_pages"):
        out.append(f"- Main content limit: {L['main_pages']} pages "
                   f"({L.get('enforcement','?')} — {L.get('consequence','see CFP')})")
        if L.get("excluded_from_limit"):
            out.append(f"- Excluded from the limit: {', '.join(L['excluded_from_limit'])}")
    else:
        out.append("- No page limit (length must still be justified)")
    out.append(f"- Anonymity: {V.get('anonymity','?')}")
    for s in V.get("required_sections", []):
        hard = " [DESK REJECT IF MISSING]" if s.get("enforcement") == "hard" else ""
        out.append(f"- REQUIRED section: {s['name']} — {s.get('placement','')}{hard}")
    for a in V.get("required_artifacts", []):
        hard = " [DESK REJECT IF MISSING]" if a.get("enforcement") == "hard" else ""
        out.append(f"- REQUIRED artifact: {a['name']} — {a.get('placement','')}{hard}")
    ai = V.get("ai_policy", {})
    if ai.get("disclosure"):
        out.append(f"- AI disclosure: {ai['disclosure']}")
    if V.get("dual_submission"):
        ds = V["dual_submission"]
        out.append(f"- Dual submission: no >{ds.get('overlap_threshold_percent')}% overlap under "
                   f"review during {ds.get('review_period')}")
    if V.get("submission_process", {}).get("two_stage"):
        out.append(f"- {V['submission_process']['note']}")
    out += ["", "Re-verify all of the above against the live call for papers before Gate 3:"]
    for k, u in V.get("urls", {}).items():
        out.append(f"  {k}: {u}")
    return "\n".join(out) + "\n"


def write(path: str, content: str, force: bool) -> bool:
    if os.path.exists(path) and not force:
        print(f"  skip (exists): {path}")
        return False
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  wrote: {path}")
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", required=True)
    ap.add_argument("--venue", help="venue slug from venues/registry.json")
    ap.add_argument("--out", default="paper", help="output directory (default: paper/)")
    ap.add_argument("--deadline", default="", help="YYYY-MM-DD")
    ap.add_argument("--registry")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args(argv)

    V, reg = None, {}
    reg_path = args.registry or T.find_registry()
    if reg_path:
        with open(reg_path, encoding="utf-8") as fh:
            reg = json.load(fh)
        if args.venue:
            V = reg["venues"].get(args.venue)
            if V is None:
                print(f"error: unknown venue '{args.venue}'. known: "
                      f"{', '.join(sorted(reg['venues']))}", file=sys.stderr)
                return 2

    out = args.out.rstrip("/")
    today = _dt.date.today().isoformat()
    short = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:40]
    print(f"scaffolding {out}/ for \"{args.title}\"" + (f" → {V['name']}" if V else ""))

    for d in ("sections", "figures/src", "figures/out", "tables", "results", "scripts"):
        os.makedirs(os.path.join(out, d), exist_ok=True)

    inputs = "\n".join(f"\\input{{sections/{n}}}" for n, _, _ in SECTIONS if n != "00-abstract")
    write(os.path.join(out, "main.tex"), f"""% {args.title}
% Scaffolded {today} by research-pro. Replace the documentclass with the venue template.
\\documentclass[10pt,twocolumn]{{article}}

% ---- venue template goes here (neurips_2026.sty / cvpr.sty / acl.sty / icml2026.sty)
\\usepackage{{booktabs}}      % ALWAYS. No \\hline, no vertical rules.
\\usepackage{{graphicx}}
\\usepackage{{amsmath,amssymb}}
\\usepackage{{siunitx}}       % decimal-aligned numeric columns
\\usepackage[capitalize]{{cleveref}}

% ---- anonymity switch: flip ONE line for camera-ready
\\newif\\ifanon \\anontrue     % \\anonfalse for camera-ready
\\ifanon
  \\title{{{args.title}}}
  \\author{{Anonymous Author(s)}}
\\else
  \\title{{{args.title}}}
  \\author{{Author Name\\\\ Institution}}
\\fi

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
\\input{{sections/00-abstract}}
\\end{{abstract}}

{inputs}

\\bibliographystyle{{plain}}
\\bibliography{{refs}}

\\end{{document}}
""", args.force)

    for name, heading, hint in SECTIONS:
        if name == "00-abstract":
            body = hint + "\n[TBD]\n"
        elif name == "90-appendix":
            body = f"\\appendix\n\\section{{{heading}}}\n{hint}\n"
        else:
            body = f"\\section{{{heading}}}\n\\label{{sec:{name.split('-',1)[1]}}}\n{hint}\n"
        write(os.path.join(out, "sections", f"{name}.tex"), body, args.force)

    write(os.path.join(out, "refs.bib"),
          "% One entry per work. Deduplicate on import, not at submission.\n"
          "% Brace-protect capitals: {BERT}, {ImageNet}.\n"
          "% Prefer DOI over URL. Upgrade preprints to their published version.\n"
          "% Verify every entry: verify_citations.py refs.bib --strict\n", args.force)

    write(os.path.join(out, "LEDGER.md"), f"""# Ledger — {short}

venue: {args.venue or '[AUTHOR DECISION]'} | deadline: {args.deadline or '[TBD]'} | stage: S1 | updated: {today}

## Story spine
1. TASK      —
2. GAP       — prior methods ... fail when ... **because** ...
3. INSIGHT   —
4. METHOD    —
5. EVIDENCE  —
6. SO WHAT   —

## Contribution claims
| # | Claim (one sentence, falsifiable) | Type | Evidence | Location | Status |
|---|---|---|---|---|---|
| C1 | | empirical | — | — | needs-evidence |

Types: empirical · causal · theoretical · comparative · generality · efficiency
Status: supported · needs-evidence · unsupported

## Evidence plan
| Claim | Experiment | Datasets | Baselines | Metric | Could falsify? | Status |
|---|---|---|---|---|---|---|
| C1 | | | | | yes | NEEDS EXPERIMENT |

## Provenance
| Table/Figure | results/ file | config | commit |
|---|---|---|---|

## Gates
| Gate | Stage | Status | Blocking issues |
|---|---|---|---|
| G1 claim/evidence | S4 | not run | |
| G2 citations | S6 | not run | |
| G3 venue compliance | S8 | not run | |
| G4 readiness | S9 | not run | |

## Open items
- [ ] fill the story spine before drafting any prose
- [ ] confirm the target venue and re-verify its live rules
""", args.force)

    write(os.path.join(out, "VENUE.md"), f"# Venue rules\n\n{venue_block(V, args.venue)}\n"
          f"Snapshot date: {reg.get('verified_on','unknown')}. "
          f"These go stale every cycle.\n", args.force)

    # Point the Makefile at wherever THIS script actually lives, so `make check`
    # works whether the skill was installed globally (~/.claude/skills/), as a
    # plugin, or cloned into the project. Prefer a relative path when the scripts
    # sit near the paper (keeps a committed Makefile portable for co-authors);
    # fall back to absolute when they are somewhere else entirely.
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    rel = os.path.relpath(scripts_dir, os.path.abspath(out))
    # One ".." means the scripts are a near neighbour of the paper (cloned into the
    # project) -- keep it relative so a committed Makefile still works for a
    # co-author who clones elsewhere. Anything deeper is a different tree
    # (a global or plugin install), where only an absolute path is stable.
    S = rel if rel.count("..") <= 1 else scripts_dir
    write(os.path.join(out, "Makefile"), f"""# {args.title}
# S is this machine's path to the research-pro scripts. Override per machine with
#   make check S=/your/path/to/skills/research-pro/scripts
S      ?= {S}
VENUE  ?= {args.venue or 'neurips'}
MAIN   ?= main
TARGET_PT ?= 237     # one column of a two-column paper

.PHONY: pdf check cites prose figs lint venue score tokens tables clean overleaf-pull overleaf-push

pdf:
\tlatexmk -pdf -interaction=nonstopmode $(MAIN).tex

tables:
\tpython3 scripts/make_tables.py && python3 scripts/make_figures.py

check: lint cites prose figs venue tokens
\t@echo "--- all checks run ---"

lint:
\tpython3 $(S)/latex_lint.py $(MAIN).tex --venue $(VENUE) --no-strict

cites:
\tpython3 $(S)/verify_citations.py refs.bib --tex $(MAIN).tex sections/*.tex \\
\t  --report out/citations.md --no-strict

prose:
\tpython3 $(S)/prose_metrics.py $(MAIN).tex --no-strict

figs:
\tpython3 $(S)/figure_audit.py figures/out --target-pt $(TARGET_PT) --no-strict

venue:
\tpython3 $(S)/venue_check.py --venue $(VENUE) --paper $(MAIN).tex --no-strict

score:
\tpython3 $(S)/score_readiness.py readiness.json --venue $(VENUE)

tokens:
\t@grep -rnE '\\[(NEEDS SOURCE|TBD|NEEDS EXPERIMENT|AUTHOR DECISION|VERIFY)\\]' \\
\t  sections/ *.tex 2>/dev/null || echo "no gap tokens"

overleaf-pull:
\tgit pull --no-rebase

overleaf-push:
\t$(MAKE) check && git add -A && git commit -m "$(M)" && git push

clean:
\tlatexmk -C
""", args.force)

    write(os.path.join(out, "scripts", "make_tables.py"), '''#!/usr/bin/env python3
"""results/*.json -> tables/*.tex.  Never hand-type a number into the paper."""
import glob, json, os

os.makedirs("tables", exist_ok=True)
rows = []
for p in sorted(glob.glob("results/*.json")):
    with open(p) as fh:
        rows.append((os.path.basename(p)[:-5], json.load(fh)))

if not rows:
    raise SystemExit("no results/*.json yet — run an experiment first")

metrics = [k for k in rows[0][1] if isinstance(rows[0][1][k], (int, float))]
with open("tables/main.tex", "w") as fh:
    fh.write("% GENERATED by scripts/make_tables.py — do not edit\\n")
    fh.write("\\\\begin{tabular}{l" + "c" * len(metrics) + "}\\n\\\\toprule\\n")
    fh.write("Run & " + " & ".join(m.replace("_", " ") for m in metrics) + " \\\\\\\\\\n\\\\midrule\\n")
    for name, d in rows:
        fh.write(name.replace("_", " ") + " & "
                 + " & ".join(f"{d.get(m, float('nan')):.2f}" for m in metrics)
                 + " \\\\\\\\\\n")
    fh.write("\\\\bottomrule\\n\\\\end{tabular}\\n")
print("wrote tables/main.tex")
''', args.force)

    write(os.path.join(out, "scripts", "make_figures.py"), '''#!/usr/bin/env python3
"""figures/src/*.py -> figures/out/*.pdf.  Vector only, fonts matched to the paper.

Palette: Okabe-Ito, validated colour-vision-deficiency safe in this order.
Always pair colour with line style AND marker shape — papers get printed in
grayscale and read by colour-blind reviewers.
"""
import glob, os, runpy, sys

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7", "#56B4E9"]
REFERENCE = "#000000"     # baseline / ground truth
LINESTYLES = ["-", "--", ":", "-."]
MARKERS = ["o", "s", "^", "D", "v", "P"]

RC = {                       # apply with matplotlib.rcParams.update(RC)
    "figure.figsize": (3.3, 2.4),      # one column; re-export, never \\includegraphics-scale
    "savefig.format": "pdf", "savefig.bbox": "tight", "savefig.pad_inches": 0.01,
    "pdf.fonttype": 42, "ps.fonttype": 42,     # embed real fonts, not Type 3
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.4,
    "lines.linewidth": 1.4, "lines.markersize": 4,
    "legend.frameon": False, "figure.dpi": 200,
}

if __name__ == "__main__":
    os.makedirs("figures/out", exist_ok=True)
    srcs = sorted(glob.glob("figures/src/*.py"))
    if not srcs:
        print("no figures/src/*.py yet. Import PALETTE/RC from this module in each one.")
        sys.exit(0)
    for s in srcs:
        print(f"running {s}")
        runpy.run_path(s, run_name="__main__")
''', args.force)

    write(os.path.join(out, "readiness.json"), json.dumps({
        "paper": short, "venue": args.venue or "", "date": today,
        "gates": {g: {"status": "not_run", "note": ""} for g in
                  ("G-CITE", "G-CLAIM", "G-VENUE", "G-ETHICS", "G-INTEGRITY", "G-TOKEN")},
        "dimensions": {k: {"score": None, "evidence": "", "fix": ""} for k in
                       ("contribution", "claim_evidence", "methodological_soundness",
                        "experimental_completeness", "related_work", "writing_clarity",
                        "figures_tables", "citation_integrity", "reproducibility",
                        "venue_compliance")},
    }, indent=2) + "\n", args.force)

    write(os.path.join(out, ".gitignore"),
          "*.aux\n*.bbl\n*.blg\n*.log\n*.out\n*.fls\n*.fdb_latexmk\n*.synctex.gz\n"
          "main.pdf\nout/\n__pycache__/\nrefs/exemplars/\n", args.force)

    write(os.path.join(out, "README.md"), f"""# {args.title}

Scaffolded {today}. Deadline: {args.deadline or '[TBD]'}.

## Order of work

1. `LEDGER.md` — fill the story spine. Six lines. Do this before any prose.
2. `VENUE.md` — confirm the venue and re-verify its live rules.
3. Evidence plan in `LEDGER.md` — one experiment per claim, decided before drafting.
4. Draft `sections/` — one paragraph at a time; reverse-outline each section after.
5. `make tables` — every number generated from `results/`, never typed.
6. `make check` — run at the end of EVERY session, not the day before the deadline.
7. `make score` — the gated readiness verdict.

## Rules this layout enforces

- Numbers live in `results/`, become `tables/*.tex` via `scripts/make_tables.py`,
  and are `\\input` by the sections. A hand-typed number is a number that will
  disagree with its run.
- Figures come from committed sources in `figures/src/` and land in `figures/out/`
  as vector PDFs, re-exported at the target width rather than scaled down.
- Anonymity is one `\\anontrue`/`\\anonfalse` line in `main.tex`.
- Nothing ships with `[TBD]`, `[NEEDS SOURCE]`, `[NEEDS EXPERIMENT]`,
  `[AUTHOR DECISION]`, or `[VERIFY]` in it. `make tokens` checks.

## Venue

{venue_block(V, args.venue)}
""", args.force)

    print(f"\ndone. next:\n  1. fill the story spine in {out}/LEDGER.md\n"
          f"  2. drop the venue template .sty next to main.tex and update \\documentclass\n"
          f"  3. cd {out} && make check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
