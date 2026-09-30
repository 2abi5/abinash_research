# Overleaf integration

The normal setup: the paper lives in Overleaf because co-authors edit there, and you
want this suite's scripts and drafting to operate on the same files. Overleaf's Git
bridge makes the project a git remote, so the loop is `pull → work locally → push`.

## Prerequisites

- **Git integration is a paid Overleaf feature** (individual subscription, group
  subscription, Overleaf Commons participant, or Server Pro 4.0+). GitHub
  synchronization is likewise paid.
- **Authentication is token-only.** Password-based git authentication has been
  removed. Generate a token in Overleaf under *Account Settings → Git integration*,
  then authenticate with username `git` and the **token as the password**. One token
  works for all your projects.

## Setup, once per project

```bash
# Project ID is in the Overleaf URL: overleaf.com/project/<PROJECT_ID>
git clone https://git.overleaf.com/<PROJECT_ID> paper
cd paper
git config credential.helper store     # or use a keychain helper
# On first push/pull: username = git, password = <your Overleaf token>
```

Store the token in a credential helper or an environment variable — **never commit
it**, and never paste it into a file the skill will read into a draft. Add it to
`.git-credentials` outside the repo, or use `GIT_ASKPASS`.

If the project already exists locally and you want to attach it:

```bash
git remote add overleaf https://git.overleaf.com/<PROJECT_ID>
git fetch overleaf && git merge overleaf/master --allow-unrelated-histories
```

## The working loop

```bash
git pull                      # ALWAYS first — co-authors edit in the browser
                              # ... run the pipeline: draft, figures, checks ...
make check                    # lint, citations, figures, leftover tokens
git add -A && git commit -m "§4: 3-seed ADE80K results; tighten §3.2 motivation"
git push
```

**Pull before every session and push before ending one.** The Overleaf bridge is a
single shared branch that your co-authors are editing live in the browser. A long
local session without pulling produces conflicts in `.tex` files that someone has to
resolve by hand.

### Conflicts

- Overleaf's bridge behaves like an ordinary git remote: resolve conflicts locally,
  commit the merge, push.
- **Never force-push.** It can destroy co-authors' browser-side work that has not
  been committed to a git snapshot yet.
- If the bridge rejects a push complaining the project is out of date, pull, resolve,
  push. Do not retry with `--force`.
- Binary files (figures, PDFs) conflict badly. Keep figure *sources* in git and
  regenerate; treat `figures/out/*.pdf` as build output where your co-authors agree
  to it.

## Overleaf's constraints, and how to work with them

| Constraint | Consequence | What to do |
|---|---|---|
| Compile timeout (shorter on free plans) | Large documents or heavy TikZ fail to build in the browser | Pre-compile figures to PDF locally; `\includegraphics` instead of inline TikZ |
| Selectable TeX Live version per project | Local and Overleaf builds can differ | Set the same TeX Live version in Overleaf project settings as your local `latexmk` |
| Restricted shell-escape | Packages needing `--shell-escape` may not behave as locally | Avoid `minted` for camera-ready; use `listings`. Generate anything else externally |
| Main document must be set explicitly | Build fails or builds the wrong file | Set `main.tex` as the main document in Overleaf project settings |
| File-count and size limits | Large `results/` trees are a poor fit | Keep raw results in a separate repo or in git-lfs; commit only what tables need |
| No `results/` provenance in the browser | Co-authors cannot regenerate tables | Commit `tables/*.tex` **and** the generator, so Overleaf compiles from committed fragments |

### The tables rule, adapted for Overleaf

Locally, tables are generated from `results/`. Overleaf cannot run your Python. So:

1. Generate `tables/*.tex` and `figures/out/*.pdf` **locally**.
2. Commit the generated artifacts *and* their generators.
3. `main.tex` `\input`s the committed fragments.

Overleaf then compiles a paper whose numbers are all machine-generated, while
co-authors edit prose in the browser. This is the single most useful discipline for
a shared Overleaf project, because it removes hand-typed numbers from a workflow
where several people can edit them.

## Reference-paper upload

Reference PDFs (the exemplars from `21-reference-paper-calibration.md`) do **not**
belong in the Overleaf project — they bloat it and risk ending up in the submission
zip. Keep them in a local `refs/exemplars/` directory outside the Overleaf clone, or
in `.gitignore`.

## GitHub synchronization as an alternative

If you would rather have GitHub as the source of truth, Overleaf's GitHub sync
(also paid) links the project to a repository and you push/pull through the Overleaf
UI. This suits a workflow where CI runs `make check` on every push. The trade-off:
sync is manual in the UI rather than automatic, so the two can drift.

## Makefile targets

`new_paper.py` writes these:

```make
overleaf-pull:  ; git pull --no-rebase
overleaf-push:  ; $(MAKE) check && git add -A && git commit -m "$(M)" && git push
```

`make overleaf-push M="§4: 3-seed results"` runs the checks *before* pushing, so a
paper with a leftover `[TBD]` or an unverified citation never reaches your
co-authors.

## If you have no paid plan

The zip round-trip still works, and it is fine for a single author:

1. Overleaf → *Menu → Download → Source* (a zip of the project).
2. Unzip over your local `paper/`, commit, work.
3. Re-upload the changed files, or upload a new zip into the project.

It loses history and it is error-prone with co-authors, so prefer the Git bridge
when you can. Do not attempt to script the private Overleaf web API — it is not a
supported interface and it breaks.
