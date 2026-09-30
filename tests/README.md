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

## Run them

```bash
bash tests/run_checks.sh
```

Expects non-zero exits from the strict runs: that is the pass condition. The script
prints each checker's verdict and a summary.
