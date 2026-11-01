# Fixtures

Deliberately broken inputs, one per checker, plus recorded database answers so the
network-dependent checkers can be tested without a network. Every defect here is one
the corresponding script must catch; if a change makes a script quieter on these, the
change is a regression.

| Fixture | Planted defects |
|---|---|
| `refs.bib` | missing required fields, unprotected capitalisation (`BERT`, `ImageNet`, `CNN`), arXiv preprint whose published version exists, duplicate entry (same DOI *and* title), Google Scholar `organization` cruft, a non-existent paper with a plausible DOI, an entry never cited, a **retracted** paper (fictional) |
| `cite_replay.json` | recorded Crossref / OpenAlex / Semantic Scholar / arXiv answers for the entries above, in each API's real shape: a near-miss title for the fabricated DOI (must be rejected), `is_retracted: true` for the retracted one, the published DOI for the preprint. `--replay` serves these and never touches the network |
| `paper.tex` | cites a key absent from the `.bib` |
| `paper_mechanics.tex` | abstract/intro/related/method with a four-citation stack, a citation after the period, `\cite` as a noun and as a grammatical subject, breakable spaces before `\cite`, a retracted source used as evidence, and a Method-section citation that must *not* appear in the default layer-3 worklist |
| `ledger_layer3.md` | a `Citation layer-3 log` covering two keys, one key with an empty location, and one key not in the `.bib` |
| `refs_clean.bib`, `paper_clean.tex`, `ledger_clean.md` | *not* broken: two entries that resolve under replay, both cited, both logged. The verifier must exit 0 here, which proves the PASS path and not only the FAIL paths |
| `slop.tex` | 25 banned phrases/words, uniform sentence length, stacked hedges, empty topic sentence, transition-adverb paragraph opener, tricolon |
| `clean.tex` | the rewritten prose from `examples/01`; passes 5 of 6 blocking checks; the remaining FAIL is deliberate |
| `clean2.tex` | same plus one five-word sentence; must pass everything (exit 0) |
| `overcorrected.tex` | the *other* machine register: staccato fragments, six em-dashes, three "not X, but Y" frames, repeated sentence openers, rhetorical questions, a section-closing summary. Zero banned words; must still FAIL on variance and draw every advisory WARN |
| `lit_replay.json` | recorded OpenAlex answers for a two-seed scan: seed lookups, batched reference fetches, forward-citation pages, a keyword search. Every paper in it is fictional (`10.1000/…` DOIs, invented counts), one is marked retracted |
| `lit_scan_dump.json` | the `scan.json` the scanner writes from that replay; `--from-json` must re-rank it offline |
| `bad_paper.tex` | missing required Limitations section, acknowledgements left in, first-person self-citation, named GitHub link, `\thanks`, two gap tokens, prompt injection in a LaTeX comment |
| `latex_sins.tex` | duplicate label, undefined `\ref`, figure caption above the graphic, table caption below the tabular, `\caption` with no `\label`, vertical rules, four `\hline` including a double, unreferenced floats, doubled word, `TODO` |
| `exemplar1.tex` | *not* broken: a well-formed short paper used as a calibration exemplar |
| `figs/` | oversized PDF needing 16% downscaling, PDF that is a raster wrapper, 122-dpi PNG, SVG, unembedded font, one correctly sized figure |
| `repo/` | a small research repo: config, two seed results, loss weights, logged metrics |
| `readiness_filled.json` | two failing gates against a 74.6/100 score; checks that gates override the number |
| `unbalanced.tex` | an unclosed `{`, which breaks the LaTeX build outright |
| `corrupt.pdf` | random bytes named `.pdf`; must be rejected, not measured |
| `notjson.json` | malformed JSON; every script that reads JSON must exit 2 cleanly on it, never traceback |

## Run them

```bash
bash tests/run_checks.sh
```

Expects non-zero exits from the strict runs: that is the pass condition. The script
prints each assertion's verdict and a summary. Two kinds of assertion:

- **exit code**: the checker must fail on a broken fixture (1), pass on a clean one
  (0), or refuse a hostile input cleanly (2).
- **output contains**: the report must *say* the specific thing (`RETRACTED`,
  `2 load-bearing key(s) uncovered`, `[WARN] choppiness`). An exit code alone does
  not prove a finding was made for the right reason.

Groups:

1. **Fixtures with planted defects**: the checker must find them.
2. **Clean inputs**: the checker must pass.
3. **Replay runs**: the citation verifier and the literature scanner against recorded
   API answers, so the resolution logic (near-miss rejection, retraction, preprint
   upgrade, layer-3 coverage, seed ranking, saturation, sentinel recall) is tested
   deterministically and offline. A live run is not asserted, because CI may have no
   network; `--replay` and `--cache` share a format, so a real run's cache can become
   a fixture.
4. **Hostile inputs**: a PDF passed as `.tex`, malformed JSON, a missing file, random
   bytes named `.pdf`. Each must produce a clean exit 2 with an explanation, **never a
   Python traceback**. A traceback in the script that issues the final readiness
   verdict is a defect in its own right.
5. **Scaffold round-trip**: the generated project lints, and its Makefile points at
   the real scripts directory.

## Recording a new replay fixture

Run the script against the real APIs once with `--cache fixture.json -v`; the cache
file is a replay file. Trim it to the URLs the test needs. For a fabricated entry,
simply leave its URLs out: an absent URL replays as a clean 404.
