#!/usr/bin/env python3
"""Matplotlib style for paper figures: vector, print-legible, CVD-safe.

    import sys; sys.path.insert(0, "../skills/research-pro/templates")
    from figstyle import apply, series, save, COL, ONE_COL_IN

    apply()                                   # or apply(width_in=TWO_COL_IN)
    fig, ax = plt.subplots()
    for i, (name, xs, ys) in enumerate(runs):
        ax.plot(xs, ys, label=name, **series(i))
    ax.set_xlabel("epoch"); ax.set_ylabel("top-1 (%)")
    save(fig, "figures/out/accuracy.pdf")

Run it directly (`python3 figstyle.py`) to print the palette and the rules.

The palette is Okabe-Ito in a print-first order. That ordering was validated for
colour-vision deficiency: worst adjacent-pair separation dE 9.6 (deuteranopia),
normal-vision floor 20.0 -- both above threshold. Do not reorder it, and do not
add a seventh hue.
"""
from __future__ import annotations

# ---- palette: assign in this fixed order, never cycled -----------------------
COL = {
    "blue":       "#0072B2",   # 1
    "vermillion": "#D55E00",   # 2
    "green":      "#009E73",   # 3
    "orange":     "#E69F00",   # 4
    "purple":     "#CC79A7",   # 5
    "sky":        "#56B4E9",   # 6
    "reference":  "#000000",   # baseline / ground truth / oracle
    "grid":       "#B0B0B0",
}
PALETTE = [COL["blue"], COL["vermillion"], COL["green"],
           COL["orange"], COL["purple"], COL["sky"]]

# Secondary encodings. Colour is NEVER the only channel: papers are printed in
# grayscale, photocopied, and read by colour-blind reviewers.
LINESTYLES = ["-", "--", ":", "-.", (0, (3, 1, 1, 1)), (0, (5, 1))]
MARKERS = ["o", "s", "^", "D", "v", "P"]
HATCHES = ["", "///", "...", "\\\\\\", "xxx", "+++"]

# Sequential: one hue, light to dark. Diverging: two hues, neutral grey midpoint.
SEQUENTIAL = "cividis"          # CVD-safe and perceptually uniform
DIVERGING = "RdBu_r"            # neutral midpoint; set vcenter at the real zero

# ---- sizes: match the venue's column width, then never scale in LaTeX --------
ONE_COL_IN = 3.29     # 237pt — one column of a two-column paper
TWO_COL_IN = 6.77     # 487pt — full text width
ARTICLE_IN = 4.79     # 345pt — single-column article

BASE_PT = 8           # >= the paper's body size once placed at 100%


def rc(width_in: float = ONE_COL_IN, height_in: float | None = None,
       base_pt: int = BASE_PT) -> dict:
    """rcParams for a figure placed at `width_in` with NO further scaling."""
    return {
        "figure.figsize": (width_in, height_in if height_in else width_in * 0.72),
        "figure.dpi": 200,
        # vector out, real fonts embedded (Type 42, not Type 3 -- publishers reject Type 3)
        "savefig.format": "pdf",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.01,
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "pdf.compression": 6,
        # type sizes: at or above body text in the final PDF
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
        "mathtext.fontset": "cm",
        "font.size": base_pt,
        "axes.labelsize": base_pt,
        "axes.titlesize": base_pt,
        "xtick.labelsize": base_pt - 1,
        "ytick.labelsize": base_pt - 1,
        "legend.fontsize": base_pt - 1,
        # recessive chrome
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": COL["grid"],
        "grid.alpha": 0.30,
        "grid.linewidth": 0.4,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        # marks
        "lines.linewidth": 1.4,
        "lines.markersize": 4.0,
        "lines.markeredgewidth": 0.0,
        "errorbar.capsize": 2.0,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "legend.borderaxespad": 0.3,
        "legend.labelspacing": 0.25,
    }


def apply(width_in: float = ONE_COL_IN, height_in: float | None = None,
          base_pt: int = BASE_PT):
    """Apply the style. Returns the matplotlib.pyplot module for convenience."""
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update(rc(width_in, height_in, base_pt))
    matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(color=PALETTE)
    return plt


def series(i: int, marker: bool = True, reference: bool = False) -> dict:
    """Style kwargs for series i: colour AND linestyle AND marker.

    A seventh series does not get a new hue -- fold it into "other", facet into
    small multiples, or split the figure.
    """
    if reference:
        return {"color": COL["reference"], "linestyle": (0, (4, 2)), "linewidth": 1.0,
                "marker": "", "zorder": 1}
    if i >= len(PALETTE):
        raise ValueError(
            f"series index {i}: only {len(PALETTE)} categorical slots exist. "
            "Use small multiples or an 'other' group instead of inventing a hue.")
    kw = {"color": PALETTE[i], "linestyle": LINESTYLES[i]}
    if marker:
        kw["marker"] = MARKERS[i]
    return kw


def bar(i: int, hatch: bool = True) -> dict:
    """Bar styling: fill plus hatch, so bars survive grayscale printing."""
    if i >= len(PALETTE):
        raise ValueError(f"series index {i}: only {len(PALETTE)} categorical slots exist.")
    kw = {"color": PALETTE[i], "edgecolor": "white", "linewidth": 0.6}
    if hatch:
        kw["hatch"] = HATCHES[i]
    return kw


def label_last(ax, line, text: str, dx: float = 0.01):
    """Direct-label a series at its right end. Preferred over a legend for <= 4 series."""
    xs, ys = line.get_xdata(), line.get_ydata()
    ax.annotate(text, xy=(xs[-1], ys[-1]), xytext=(4, 0),
                textcoords="offset points", va="center",
                color=line.get_color(), fontsize=ax.xaxis.label.get_size() - 1,
                clip_on=False)


def save(fig, path: str, **kw):
    """Save as vector PDF and make the parent directory."""
    import os
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    if not path.lower().endswith((".pdf", ".eps")):
        raise ValueError(f"{path}: figures must be vector (.pdf). "
                         "Raster is only for photographs and feature maps.")
    fig.savefig(path, **kw)
    return path


RULES = """\
Rules this style cannot enforce for you
---------------------------------------
1. Re-export at the target width. Never \\includegraphics[width=0.5\\linewidth] a
   figure that is natively 20in wide -- that shrinks the fonts by the same factor.
   Check with: figure_audit.py figures/out --target-pt 237
2. No dual y-axis. Two scales invite a relationship you have not shown. Two panels.
3. No truncated y-axis on bars. The bar's length IS the encoding.
4. Legend present for >= 2 series; direct-label instead when there are <= 4.
5. Mark metric direction in the axis label: "top-1 (%) up", "FID down".
6. Show dispersion. A line without a band, or a bar without an error bar, implies a
   precision you do not have.
7. No rainbow colormaps. Sequential = one hue light to dark (cividis); diverging =
   two hues with a neutral grey midpoint at the real zero.
8. Look at the compiled PDF at 100%. No script finds colliding labels.
"""

if __name__ == "__main__":
    print(__doc__.split("\n\n")[0])
    print("\nCategorical palette (assign in this order, never cycle):")
    for i, (name, hexv) in enumerate(
            [(k, v) for k, v in COL.items() if k not in ("reference", "grid")], 1):
        print(f"  {i}. {name:11} {hexv}   linestyle={LINESTYLES[i-1]!r:18} marker={MARKERS[i-1]!r}")
    print(f"  reference/baseline: {COL['reference']}  (black, dashed, no marker)")
    print(f"\nSequential: {SEQUENTIAL}   Diverging: {DIVERGING}")
    print(f"\nWidths (inches): one column {ONE_COL_IN}, full width {TWO_COL_IN}, "
          f"article {ARTICLE_IN}")
    print(f"Base type size: {BASE_PT}pt\n")
    print(RULES)
