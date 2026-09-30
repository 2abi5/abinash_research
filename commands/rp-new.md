---
description: Start a paper — intake interview, story spine, then scaffold the project
argument-hint: "[topic or \"from codebase\"] [--venue slug]"
---
Invoke the `research-pro` skill and run stage S0 then S1.

Target: $ARGUMENTS

1. Read `references/01-intake.md` and run the intake interview. Ask the six
   questions, stop as soon as you can write the spec, and do not interrogate.
2. If the user pointed at a codebase, also read `references/22-codebase-to-paper.md`
   and run `scripts/repo_scan.py` first — then reconcile what the artifacts support
   against what the author says they found, and report every mismatch.
3. Read `references/02-architecture.md` and build the six-line story spine. Do not
   write prose until line 2 names a technical *reason*, not just a symptom.
4. Confirm the spine with the author. This is a checkpoint — do not skip it.
5. Scaffold: `python3 scripts/new_paper.py --title "..." --venue <slug> --out paper/`
6. Fill `paper/LEDGER.md` with the spine and the draft claims.

Report the spec, the spine, and the open `[AUTHOR DECISION]` items.
