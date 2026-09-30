---
description: Design or audit figures and tables
argument-hint: "[teaser|architecture|analysis|tables|audit]"
---
Invoke `research-pro` and read `references/11-figures-tables.md`.

Task: $ARGUMENTS

For design: fill `templates/figure-spec.md` before drawing. Name the figure's job in
one sentence. Use `templates/figstyle.py` — Okabe-Ito in the validated order, with
line style and marker shape alongside colour so the figure survives grayscale and
colour-blind readers.

For tables: booktabs only, no vertical rules, metric direction in the header,
consistent precision, generated from `results/` by `scripts/make_tables.py` and
never hand-typed.

For audit:
```
python3 skills/research-pro/scripts/figure_audit.py paper/figures/out --target-pt 237
```
It measures format, natural size versus placement width (the scaling that shrinks
your fonts), raster DPI, and font embedding. Then open the compiled PDF at 100% —
no script finds colliding labels.
