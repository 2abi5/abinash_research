# S5 — Figures and tables

A reviewer forms a judgment from the figures before reading a word of the method.
Figures are content, and they are graded whether or not anyone says so.

## The three figures every method paper needs

### 1. Teaser (page 1, top right)

Job: in five seconds, from figure plus caption alone, make the reader understand
the idea and want the paper.

Two forms that work:
- **The problem.** Prior method's failure case beside your result, same input. The
  most persuasive single object in a paper when the failure is visually obvious.
- **The idea.** The mechanism abstracted to its essence — three boxes, not thirty.

Never put a system diagram here. That is the architecture figure, and at this
position it reads as "we built a pipeline" rather than "we found something."

### 2. Architecture figure (§3)

Job: let a reader reimplement the dataflow, and fix the order of your method
subsections.

- Left-to-right or top-to-bottom, following the actual dataflow.
- Label every tensor with its shape. This single habit answers most
  reproducibility questions before they are asked.
- Distinguish learned components from fixed operations visually, and say how in
  the caption.
- Mark where each loss attaches.
- Annotate the *novel* part — a coloured region or a callout. Reviewers skimming
  need to find your contribution in the figure without hunting.
- Do not draw every layer. Draw the modules your Method section names, one box per
  subsection.

### 3. Analysis figure (§4)

Job: show the mechanism operating. What the gate selects, where attention lands,
which examples move, how the metric behaves across the axis you control.

This is the figure that separates a strong paper from an adequate one, and it is
the one most often missing. A reviewer who sees the mechanism working believes the
causal claim; one who sees only a results table takes it on faith.

## Design rules

### Type size is the rule people break

Figure text must be **at least as large as the paper's body text**, measured in
the final PDF, not in the plotting window. A 20% shrink in `\includegraphics`
shrinks the fonts by 20% too.

```
Body text 9–10pt  →  axis labels ≥ 8pt, tick labels ≥ 7pt, annotations ≥ 7pt
```

Check by printing the page at 100% and reading it at arm's length. If you squint,
a reviewer on a laptop at 2am will not bother.

### Vector, always

PDF or EPS from the plotting source. Never a screenshot, never a PNG of a plot,
never a figure exported from a slide deck. Rasterize only true raster content
(photographs, feature maps) and then at ≥300 dpi at final print size.

### Color: use Okabe–Ito, in this order

```
1 blue      #0072B2      4 orange     #E69F00
2 vermillion#D55E00      5 purple     #CC79A7
3 green     #009E73      6 sky        #56B4E9
   reference / baseline / ground truth: black #000000
```

This ordering was validated for colour-vision deficiency: worst adjacent-pair
separation ΔE 9.6 (deuteranopia), normal-vision floor 20.0 — both above threshold.
Assign slots **in fixed order and never cycle**. A seventh series does not get a
new hue; it becomes "other", a small multiple, or a second panel.

Three further rules that matter more in print than on screen:

- **Colour is never the only encoding.** Pair it with line style (solid, dashed,
  dotted) and marker shape (o, s, ^, D). Papers get printed in grayscale,
  photocopied, and read by colour-blind reviewers. Direct-label series where
  there are four or fewer rather than relying on a legend.
- **Sequential data: one hue, light to dark.** Never a rainbow — it invents
  boundaries the data does not have. `viridis` or `cividis` if you need a
  perceptual map; `cividis` is the CVD-safe choice.
- **Diverging data: two hues with a neutral grey midpoint**, and the midpoint at
  the meaningful zero.

### Never

- A dual y-axis chart. Two scales invite the reader to see a relationship you have
  not established. Use two panels, or index both to a common base.
- A 3D bar or pie chart.
- A truncated y-axis on a bar chart. Truncation on a line chart is acceptable when
  labelled; on bars it misrepresents magnitude, because the bar's length *is* the
  encoding.
- Chartjunk: gradients, shadows, heavy grids, boxed legends inside the data area.
- More than six series on one axis.

## Captions

Captions are read more than body text. Make them self-contained.

- **Figures: caption below.** **Tables: caption above.** This is a hard
  convention; violating it reads as inexperience.
- A figure caption states what is shown, the setting, and what to notice:
  `Figure 3: Routing entropy per layer on ImageNet. The gate concentrates on
  fewer experts in deeper layers (right), which is what reduces FLOPs.`
- A table caption states the setting, protocol, and notation — best/second-best
  marking, `↑`/`↓` direction, which numbers are reproductions, what `—` means.
- Do not argue in a caption, and do not put the finding *only* in a caption.

## Tables

Hard rules, from `booktabs`:

- `\toprule`, `\midrule`, `\bottomrule` only. No `\hline` stacks, no double rules.
- **No vertical rules.** Ever. Use column spacing to group.
- Group multi-dataset blocks with `\multicolumn` and `\cmidrule`, not with `|`.
- Metric direction in the header: `PSNR ↑`, `FID ↓`.
- Units in the header, not repeated in cells.
- Numeric columns aligned on the decimal (`siunitx`'s `S` column); text columns
  left-aligned.
- Consistent precision within a column, and no more digits than your dispersion
  justifies.
- Bold the best, underline the second-best, and say so in the caption. Colour
  sparingly — a shaded row for your method at most.
- **One table, one message.** Two unrelated result sets in one table means neither
  lands.

```latex
\begin{table}[t]
  \centering
  \caption{Top-1 accuracy at matched FLOPs. Best in \textbf{bold}, second
  \underline{underlined}. $\dagger$ = our reproduction; other baseline numbers are
  as published.}
  \label{tab:main}
  \begin{tabular}{lcc}
    \toprule
    Method & Top-1 (\%) $\uparrow$ & GFLOPs $\downarrow$ \\
    \midrule
    Kim et al.~\cite{kim24}       & 81.2\phantom{$^\dagger$} & 4.1 \\
    Liu et al.~\cite{liu25}$^\dagger$ & \underline{82.7}     & 4.0 \\
    Ours                          & \textbf{85.1}            & 4.0 \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Generate, never hand-type

`results/*.json → scripts/make_tables.py → tables/*.tex`, included by the section.
A hand-typed number silently diverges from the run that produced it, and you find
out when a reviewer recomputes it. The same holds for figures: every figure has a
committed source file in `figures/src/` that regenerates it.

Use `templates/figstyle.py` as the matplotlib style — it sets the palette above,
type sizes matched to a paper, vector output, and the no-chartjunk defaults.

## Layout

- Floats at the top of the page (`[t]`). Bottom floats break the reading flow.
- A single-column figure in a two-column paper goes in the **right** column where
  layout allows, so the reader enters the page at the top left in text.
- Reference every float in the text before it appears.
- Full-width figures use `figure*` and land at the top of a page.
- Never let a float land more than one page after its first reference.

## Audit before submission

```bash
python3 skills/research-pro/scripts/figure_audit.py paper/figures/out
```

It checks vector versus raster, embedded font sizes, raster resolution, and page
geometry. Then look at the compiled PDF at 100% — the script checks measurable
properties, not whether two labels collide.

## Checks

1. Is the teaser understandable from figure plus caption alone?
2. Is every figure vector, from committed source?
3. Is all figure text ≥ 7pt **in the final PDF**?
4. Does every series carry a non-colour encoding as well as colour?
5. Do the tables use booktabs with no vertical rules?
6. Is metric direction marked in every results header?
7. Is every number in every table generated from `results/`?
8. Table captions above, figure captions below?
