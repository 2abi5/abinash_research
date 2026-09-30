---
description: Set up or run the Overleaf sync loop
argument-hint: "[setup|pull|push] [project-id]"
---
Invoke `research-pro` and read `references/20-overleaf.md`.

Action: $ARGUMENTS

**setup** — Git integration is a paid Overleaf feature and authentication is
token-only (username `git`, the token as the password; password auth was removed).
Generate the token under Account Settings → Git integration.
```
git clone https://git.overleaf.com/<PROJECT_ID> paper
```
Never commit the token. Set the same TeX Live version locally as the Overleaf
project uses, and set `main.tex` as the project's main document.

**pull** — always before a working session; co-authors edit in the browser.

**push** — `make overleaf-push M="§4: 3-seed results"`, which runs `make check`
first, so a paper with a leftover `[TBD]` or an unverified citation never reaches
your co-authors.

Never force-push: it can destroy browser-side work that is not yet in a git
snapshot. Generate `tables/*.tex` and `figures/out/*.pdf` locally and commit the
artifacts *and* their generators — Overleaf cannot run your Python, so this is what
keeps hand-typed numbers out of a shared project.
