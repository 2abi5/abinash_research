# S1 — Architecture

Two things are architected here: the **story** (what the paper argues, in what
order) and the **project** (the files, the build, the figure pipeline). Do the
story first. A tidy repository around an unclear argument is a tidy rejection.

## Part A — the story spine

### Write the spine before any prose

Six lines. If you cannot fill them, there is no paper yet and prose will not
rescue it.

```
1. TASK      We study <input> → <output>, in the setting of <scope>.
2. GAP       Prior methods <what they do>. They fail when <condition>, because
             <technical reason>.                       ← the reason is the paper
3. INSIGHT   <The one observation that makes the failure fixable.>
4. METHOD    We therefore <mechanism>, which <property that addresses the reason>.
5. EVIDENCE  On <datasets>, this <delta> versus <strongest baseline>; <ablation>
             shows the gain comes from <mechanism>, not <confound>.
6. SO WHAT   This means <what a reader now knows that they did not before>.
```

Line 2 is where papers are won and lost. "They fail when X" is a limitation;
anyone can list limitations. "They fail when X **because** Y" is a technical
challenge, and Y is what your method attacks. If you cannot name Y, you do not
yet know what your method contributes — you only know that it scores higher.

Line 6 must not restate line 5. A number is a result; the "so what" is the
transferable knowledge. If the only honest answer is "our method scores higher,"
the paper is a leaderboard entry and reviewers will say so.

### The narrative order that works

The reader must arrive at your method *already wanting it*. Build the want
first:

```
task matters  →  prior work is reasonable  →  yet it breaks here  →
because of this specific reason  →  which suggests this insight  →
which we implement as this mechanism  →  and here is the proof
```

Two failure modes, both fatal, both common:

- **Patch framing.** "A naive approach is X. We improve X by adding Y." Even when
  literally true, this reads as an increment on something obvious, and kills the
  reader's curiosity before your idea arrives. Instead: establish the challenge,
  let the reader feel that it is hard, *then* present your mechanism.
- **Mystery framing.** Withholding the mechanism behind abstract language
  ("a principled framework for adaptive representation alignment") to seem
  novel. Reviewers read this as either shallow or evasive, and they read the rest
  of the paper looking for the trick. Name the mechanism concretely and early.

### Contribution set

Two or three contributions, at most four. Each must be independently defensible
and independently ablatable. Write each as `contribution → its advantage`:

> We introduce a routing gate that selects experts from a learned sparsity
> pattern, **which cuts inference FLOPs 4× without the accuracy loss that
> magnitude pruning incurs.**

A contribution without its advantage attached is a feature list. A contribution
you cannot ablate is a claim you cannot defend at stage 9.

### Section budget

Allocate pages before writing, from the venue's limit. For an 8–9 page,
two-column ML/CV paper:

| Section | Pages | Non-negotiable content |
|---|---|---|
| Abstract | — | task, challenge, mechanism, headline result |
| 1 Introduction | 1.0–1.25 | the spine, teaser figure, contribution list |
| 2 Related work | 0.5–0.75 | 2–4 mechanism-level groupings, your distinction |
| 3 Method | 2.0–2.5 | architecture figure, per-module design/motivation/advantage |
| 4 Experiments | 2.5–3.0 | setup, main comparison, ablations, analysis |
| 5 Discussion / limitations | 0.25–0.5 | honest scope boundary |
| 6 Conclusion | 0.15 | short; no new claims |

Overruns get paid for out of Related Work and Method prose, never out of
ablations. If the budget does not close, the paper has too many contributions —
cut one rather than compressing all of them into unreadability.

### Reverse-check the spine against the evidence

Before leaving S1, walk lines 4–5 against what actually exists. Every mechanism
in line 4 needs an ablation planned in S3. Every number in line 5 needs a real
run. Mark the gaps `[NEEDS EXPERIMENT]` in the ledger now — this is the cheapest
moment in the paper's life to discover that the story requires an experiment
nobody has run.

## Part B — the project

### Scaffold

`scripts/new_paper.py --title "..." --venue <venue> --out paper/` writes this.
Do not improvise a layout; downstream scripts expect these paths.

```
paper/
├── main.tex              # document root: preamble, \input each section
├── refs.bib              # single bibliography, one entry per work, no duplicates
├── LEDGER.md             # claim/evidence ledger (see 00-operating-rules.md)
├── README.md             # how to build, who owns what, deadline
├── Makefile              # make pdf | make check | make clean
├── sections/
│   ├── 00-abstract.tex
│   ├── 01-intro.tex
│   ├── 02-related.tex
│   ├── 03-method.tex
│   ├── 04-experiments.tex
│   ├── 05-discussion.tex
│   ├── 06-conclusion.tex
│   └── 90-appendix.tex
├── figures/
│   ├── src/              # .py / .svg / .drawio — the editable source
│   └── out/              # .pdf vectors that main.tex includes
├── tables/               # generated .tex fragments, never hand-edited
├── results/              # raw run outputs (csv/json) that tables are built from
└── scripts/
    ├── make_figures.py   # results/ → figures/out/
    └── make_tables.py    # results/ → tables/
```

### Three rules that prevent the classic disasters

1. **Tables and figures are generated, never typed.** A number typed by hand
   diverges from the run that produced it, and you will not notice until a
   reviewer does. `results/*.json → scripts/make_tables.py → tables/*.tex`.
   Then a re-run updates the paper with one command.
2. **Figures are vector, from committed source.** `figures/src/x.py` produces
   `figures/out/x.pdf`. A screenshot pasted into a slide and re-exported cannot
   be regenerated when a reviewer asks for a different axis range at 11pm on
   rebuttal day.
3. **One bibliography, cleaned early.** Deduplicate on first import, not at
   submission. See `13-citation-integrity.md`.

### Build and check

```make
pdf:    ; latexmk -pdf -interaction=nonstopmode main.tex
check:  ; python3 $(S)/latex_lint.py main.tex --venue $(VENUE) \
        ; python3 $(S)/verify_citations.py refs.bib \
        ; python3 $(S)/figure_audit.py figures/out \
        ; grep -rnE '\[(NEEDS SOURCE|TBD|NEEDS EXPERIMENT|AUTHOR DECISION|VERIFY)\]' . || true
clean:  ; latexmk -C
```

Run `make check` at the end of every working session. Page-limit and
undefined-reference failures found the day before a deadline cost hours;
found weekly, they cost nothing.

### Version control hygiene

- Commit `results/` raw outputs. They are the provenance of every number.
- Never commit build artifacts (`.aux`, `.bbl`, `.pdf` of `main`).
- Tag the submitted commit: `git tag neurips-2026-submission`. When reviews
  arrive five months later you will need to know exactly what they read.
- Keep the anonymized and de-anonymized preambles in one file behind a flag, so
  camera-ready is a one-line change and not a re-audit.
