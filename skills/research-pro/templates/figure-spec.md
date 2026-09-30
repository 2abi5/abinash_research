# Figure spec — Figure <n>: <short name>

Fill this before drawing. A figure without a stated job becomes decoration.

- **Job (one sentence):** what the reader should understand from this alone.
- **Role:** teaser · architecture · results · analysis · qualitative · failure case
- **Placement:** §<n>, column width / full width · target width <237 / 487>pt
- **Understandable from figure + caption alone?** yes / no (for a teaser it must be yes)

## Content
- **What is shown:**
- **What the reader should notice first:**
- **Data source:** `results/<file>` (never hand-entered)
- **Source file:** `figures/src/<name>.py` → `figures/out/<name>.pdf`

## Encoding
| Channel | Used for |
|---|---|
| position | |
| colour (Okabe-Ito slot) | |
| line style | |
| marker shape | |
| panel / facet | |

- Colour is **not** the only encoding for any series: yes / no
- Series count ≤ 6: yes / no  (if no → small multiples or an "other" group)
- Dispersion shown (band / error bars): yes / no
- Metric direction in the axis label (`↑` / `↓`): yes / no

## Caption draft
> Figure <n>: <what is shown>, <setting/protocol>. <What to notice.>

## Checks
- [ ] vector PDF, re-exported at target width (not `\includegraphics`-scaled)
- [ ] all text ≥ 7pt in the final PDF (`figure_audit.py`)
- [ ] no dual y-axis, no truncated bar axis, no rainbow colormap
- [ ] referenced in the text before it appears
- [ ] legible in grayscale
