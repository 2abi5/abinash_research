#!/usr/bin/env python3
"""Audit figure files for the defects that make reviewers squint.

Measurable properties only:
  * format -- vector (PDF/EPS) vs raster (PNG/JPG), and raster hidden inside a PDF
  * natural size from the PDF MediaBox, and the scale factor it implies at the
    target column width (a figure scaled to 40% has 40%-size fonts)
  * raster pixel dimensions and the effective DPI at that column width
  * whether a PDF embeds fonts (unembedded fonts render differently everywhere)

It cannot tell you whether two labels collide. Look at the compiled PDF too.

Stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys

VECTOR = {".pdf", ".eps", ".ps"}
RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
EDITABLE = {".svg", ".drawio", ".ai", ".key", ".pptx", ".xcf", ".psd"}

MIN_DPI = 300.0
MIN_SCALE = 0.55      # below this, body-matched fonts become illegible


def png_size(path: str) -> tuple[int, int] | None:
    try:
        with open(path, "rb") as fh:
            head = fh.read(33)
        if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
            return None
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    except Exception:
        return None


def jpeg_size(path: str) -> tuple[int, int] | None:
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        if data[:2] != b"\xff\xd8":
            return None
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + seglen
    except Exception:
        return None
    return None


def pdf_facts(path: str) -> dict:
    """MediaBox size in points, plus raster / font presence."""
    out: dict = {}
    try:
        with open(path, "rb") as fh:
            data = fh.read(4_000_000)
    except OSError:
        return out
    m = re.search(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)", data)
    if m:
        x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
        out["width_pt"], out["height_pt"] = abs(x1 - x0), abs(y1 - y0)
    out["has_raster"] = bool(re.search(rb"/Subtype\s*/Image", data))
    out["has_vector_ops"] = bool(re.search(rb"\b(re|m|c|l)\s+[\d.]", data)) or b"/Contents" in data
    out["fonts"] = sorted({n.decode("latin-1") for n in
                           re.findall(rb"/BaseFont\s*/([A-Za-z0-9+\-,_.]+)", data)})
    out["embedded_fonts"] = bool(re.search(rb"/FontFile[23]?\b", data))
    out["has_text"] = bool(out["fonts"]) or b"/Font" in data
    return out


def audit(path: str, target_pt: float) -> dict:
    ext = os.path.splitext(path)[1].lower()
    size = os.path.getsize(path)
    r: dict = {"path": path, "ext": ext, "bytes": size, "issues": [], "notes": []}

    if ext in EDITABLE:
        r["kind"] = "source"
        r["notes"].append("editable source — fine in figures/src/, must not be \\includegraphics'd")
        if ext == ".svg":
            r["issues"].append(("WARN", "SVG cannot be included by pdflatex — export to PDF"))
        return r

    if ext in RASTER:
        r["kind"] = "raster"
        dim = png_size(path) if ext == ".png" else jpeg_size(path)
        if dim:
            w, h = dim
            r["px"] = f"{w}x{h}"
            dpi = w / (target_pt / 72.0)
            r["dpi_at_target"] = round(dpi, 1)
            if dpi < MIN_DPI:
                r["issues"].append(
                    ("FAIL", f"{dpi:.0f} dpi at {target_pt:.0f}pt width — under {MIN_DPI:.0f} dpi; "
                             f"needs >= {int(MIN_DPI * target_pt / 72)}px wide"))
        else:
            r["notes"].append("could not read pixel dimensions")
        r["issues"].append(
            ("WARN", "raster figure — acceptable only for photographs or feature maps; "
                     "plots and diagrams must be vector PDF"))
        return r

    if ext in VECTOR:
        r["kind"] = "vector"
        if ext != ".pdf":
            r["notes"].append("EPS/PS works with latex+dvips, not pdflatex — prefer PDF")
            return r
        f = pdf_facts(path)
        if "width_pt" in f:
            w = f["width_pt"]
            r["natural_pt"] = f"{w:.0f}x{f['height_pt']:.0f}"
            r["natural_in"] = f"{w/72:.2f}x{f['height_pt']/72:.2f}in"
            scale = target_pt / w if w else 1.0
            r["scale_at_target"] = round(scale, 2)
            if scale < MIN_SCALE:
                r["issues"].append(
                    ("FAIL", f"natural width {w:.0f}pt ({w/72:.1f}in) must shrink to "
                             f"{scale:.0%} to fit {target_pt:.0f}pt — all text shrinks with it. "
                             f"Re-export at about {target_pt/72:.1f}in wide instead of scaling"))
            elif scale > 1.6:
                r["issues"].append(
                    ("WARN", f"natural width {w:.0f}pt is much narrower than the "
                             f"{target_pt:.0f}pt column; text will be enlarged {scale:.1f}x "
                             f"and look oversized"))
        else:
            r["notes"].append("no MediaBox found — cannot check scaling")
        if f.get("has_raster") and f.get("has_text"):
            r["issues"].append(("WARN", "PDF contains an embedded raster image — check it is a "
                                        "photograph, not a screenshotted plot"))
        elif f.get("has_raster") and not f.get("has_text"):
            r["issues"].append(("FAIL", "PDF is a wrapper around a raster image with no text — "
                                        "this is a screenshot in a PDF container"))
        if f.get("has_text") and not f.get("embedded_fonts"):
            r["issues"].append(("WARN", "fonts are referenced but not embedded — the figure will "
                                        "render differently on other machines and at the publisher"))
        if f.get("fonts"):
            r["fonts"] = ", ".join(f["fonts"][:4])
        return r

    r["kind"] = "other"
    r["notes"].append("unrecognised extension")
    return r


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="figure file or a directory of them")
    ap.add_argument("--target-pt", type=float, default=237.0,
                    help="width the figure will occupy, in points "
                         "(237 = one column of a two-column paper; 487 = full width; "
                         "345 = single-column article)")
    ap.add_argument("--strict", action="store_true", default=True)
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    targets: list[str] = []
    if os.path.isdir(args.path):
        for root, _dirs, files in os.walk(args.path):
            for fn in sorted(files):
                if os.path.splitext(fn)[1].lower() in (VECTOR | RASTER | EDITABLE):
                    targets.append(os.path.join(root, fn))
    elif os.path.isfile(args.path):
        targets = [args.path]
    else:
        print(f"error: no such path {args.path}", file=sys.stderr)
        return 2

    if not targets:
        print(f"no figure files found under {args.path}")
        return 0

    results = [audit(t, args.target_pt) for t in targets]
    n_fail = sum(1 for r in results for s, _ in r["issues"] if s == "FAIL")
    n_warn = sum(1 for r in results for s, _ in r["issues"] if s == "WARN")

    print(f"# Figure audit — {args.path}")
    print(f"\n{len(results)} file(s), assuming {args.target_pt:.0f}pt "
          f"({args.target_pt/72:.2f}in) placement width\n")

    for r in sorted(results, key=lambda x: (0 if any(s == "FAIL" for s, _ in x["issues"]) else 1,
                                            x["path"])):
        head = f"{r['path']}  [{r.get('kind','?')}, {r['bytes']/1024:.0f} KB"
        for k in ("px", "dpi_at_target", "natural_in", "scale_at_target"):
            if k in r:
                head += f", {k}={r[k]}"
        print(head + "]")
        for status, msg in r["issues"]:
            print(f"    [{status}] {msg}")
        for note in r["notes"]:
            print(f"    [INFO] {note}")
        if "fonts" in r:
            print(f"    [INFO] fonts: {r['fonts']}")

    print(f"\n{n_fail} FAIL · {n_warn} WARN")
    print("\nNot measurable here: label collisions, legend placement, colour choices,")
    print("and whether the figure communicates anything. Open the compiled PDF at 100%,")
    print("and check the palette rules in references/11-figures-tables.md.")

    if args.strict and n_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
