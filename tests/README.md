# Fixtures

Deliberately broken inputs, one per checker. Every defect here is one the
corresponding script must catch; if a change makes a script quieter on these, the
change is a regression.

| Fixture | Planted defects |
|---|---|
| `refs.bib` | missing required fields, unprotected capitalisation (`BERT`, `ImageNet`, `CNN`), arXiv preprint with no published version, duplicate entry (same DOI *and* title), Google Scholar `organization` cruft, a non-existent paper with a plausible DOI, an entry never cited |
| `paper.tex` | cites a key absent from the `.bib` |
| `slop.tex` | 25 banned phrases/words, uniform sentence length, stacked hedges, empty topic sentence, transition-adverb paragraph opener, tricolon |
| `bad_paper.tex` | missing required Limitations section, acknowledgements left in, first-person self-citation, named GitHub link, `\thanks`, two gap tokens, prompt injection in a LaTeX comment |
| `latex_sins.tex` | duplicate label, undefined `\ref`, figure caption above the graphic, table caption below the tabular, `\caption` with no `\label`, vertical rules, four `\hline` including a double, unreferenced floats, doubled word, `TODO` |
| `exemplar1.tex` | *not* broken — a well-formed short paper used as a calibration exemplar |
| `figs/` | oversized PDF needing 16% downscaling, PDF that is a raster wrapper, 122-dpi PNG, SVG, unembedded font, one correctly sized figure |
| `repo/` | a small research repo: config, two seed results, loss weights, logged metrics |
| `readiness_filled.json` | two failing gates against a 74.6/100 score — checks that gates override the number |
| `clean.tex` | the rewritten prose from `examples/01` — passes 5 of 6 checks; the remaining FAIL is deliberate |
| `clean2.tex` | same plus one five-word sentence — must pass everything (exit 0) |
| `unbalanced.tex` | an unclosed `{`, which breaks the LaTeX build outright |
| `corrupt.pdf` | random bytes named `.pdf` — must be rejected, not measured |
| `notjson.json` | malformed scorecard — must produce a clean exit 2, never a traceback |

## Run them

```bash
bash tests/run_checks.sh
```

Expects non-zero exits from the strict runs: that is the pass condition. The script
prints each checker's verdict and a summary. 20 assertions, covering three groups:

1. **Fixtures with planted defects** — the checker must find them (exit 1).
2. **Clean inputs** — the checker must pass (exit 0).
3. **Hostile inputs** — a PDF passed as `.tex`, malformed JSON, a missing file,
   random bytes named `.pdf`. Each must produce a clean exit 2 with an explanation,
   **never a Python traceback**. A traceback in the script that issues the final
   readiness verdict is a defect in its own right.
