#!/usr/bin/env python3
"""Mechanical LaTeX defects that cost reviewer goodwill or break the build.

Checks cross-references, duplicate labels, booktabs violations, caption/label
order and placement, unreferenced floats, leftover TODOs, and -- when a build log
is present -- overfull boxes, undefined references, and the real page count.

Stdlib only. Works on source alone; pass --log for build-time findings.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import _textlib as T

FLOAT_ENVS = ("figure", "figure*", "table", "table*", "algorithm")


def floats_in(text: str) -> list[dict]:
    out = []
    for env in FLOAT_ENVS:
        pat = re.compile(rf"\\begin\{{{re.escape(env)}\}}(.*?)\\end\{{{re.escape(env)}\}}", re.S)
        for m in pat.finditer(text):
            inner = m.group(1)
            cap = inner.find("\\caption")
            lab = inner.find("\\label")
            graphic = max(inner.find("\\includegraphics"), inner.find("\\begin{tabular}"),
                          inner.find("\\input"))
            out.append({
                "env": env,
                "line": text.count("\n", 0, m.start()) + 1,
                "caption_at": cap,
                "label_at": lab,
                "graphic_at": graphic,
                "inner": inner,
                "labels": re.findall(r"\\label\s*\{([^}]*)\}", inner),
            })
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", help="main .tex file")
    ap.add_argument("--venue", help="venue slug, for the page limit")
    ap.add_argument("--log", help="latex .log file (defaults to the .tex's sibling .log)")
    ap.add_argument("--strict", action="store_true", default=True)
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    why = T.sniff_binary(args.tex)
    if why:
        print(f"error: {why}", file=sys.stderr)
        return 2
    raw = T.read_with_inputs(args.tex)
    if not raw:
        print(f"error: cannot read {args.tex}", file=sys.stderr)
        return 2
    text = T.strip_comments(raw)

    findings: list[tuple[str, str]] = []
    def fail(msg): findings.append(("FAIL", msg))
    def warn(msg): findings.append(("WARN", msg))
    def info(msg): findings.append(("INFO", msg))

    # ---- structural balance: an unbalanced brace breaks the build entirely
    depth = T.brace_balance(raw)
    if depth != 0:
        fail(f"unbalanced braces: net {depth:+d} — "
             + ("an unclosed `{` will break the build or swallow the rest of the document"
                if depth > 0 else "an extra `}` will break the build"))
    for env, net in T.env_balance(raw):
        fail(f"environment `{env}` is {'not closed' if net > 0 else 'closed too often'} "
             f"(net {net:+d} \\begin vs \\end)")

    # ---- labels and refs
    labels = re.findall(r"\\label\s*\{([^}]*)\}", text)
    refs = set()
    for m in re.finditer(r"\\(?:ref|eqref|autoref|cref|Cref|pageref|vref)\s*\{([^}]*)\}", text):
        for k in m.group(1).split(","):
            if k.strip():
                refs.add(k.strip())
    dup = sorted({l for l in labels if labels.count(l) > 1})
    for d in dup:
        fail(f"duplicate \\label{{{d}}} — cross-references will point to the wrong object")
    undefined = sorted(refs - set(labels))
    for u in undefined:
        fail(f"\\ref{{{u}}} has no matching \\label — renders as '??'")
    unused = sorted(set(labels) - refs)
    for u in unused[:12]:
        warn(f"\\label{{{u}}} is never referenced")
    if len(unused) > 12:
        info(f"...and {len(unused) - 12} more unreferenced labels")

    # ---- floats
    fl = floats_in(text)
    for f in fl:
        tag = f"{f['env']} at line {f['line']}"
        if f["caption_at"] < 0:
            fail(f"{tag}: no \\caption")
            continue
        if f["label_at"] < 0:
            fail(f"{tag}: \\caption without \\label — it cannot be referenced")
        elif f["label_at"] < f["caption_at"]:
            fail(f"{tag}: \\label appears BEFORE \\caption — \\ref will give the wrong number")
        is_table = f["env"].startswith("table")
        if f["graphic_at"] >= 0:
            if is_table and f["caption_at"] > f["graphic_at"]:
                fail(f"{tag}: table caption is below the tabular — table captions go ABOVE")
            if not is_table and f["caption_at"] < f["graphic_at"]:
                fail(f"{tag}: figure caption is above the graphic — figure captions go BELOW")
    # float referenced in text?
    for f in fl:
        for lab in f["labels"]:
            if lab not in refs:
                warn(f"{f['env']} `{lab}` (line {f['line']}) is never referenced in the text")

    # ---- tables: booktabs discipline
    for m in re.finditer(r"\\begin\{tabular\}\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", text):
        spec, line = m.group(1), text.count("\n", 0, m.start()) + 1
        if "|" in spec:
            fail(f"tabular at line {line}: vertical rules `|` in the column spec — "
                 f"never use them; group with spacing instead")
    nh = len(re.findall(r"\\hline", text))
    if nh:
        fail(f"{nh} \\hline occurrence(s) — use booktabs \\toprule/\\midrule/\\bottomrule")
    if re.search(r"\\hline\s*\\hline", text):
        fail("double \\hline — never acceptable")
    if re.search(r"\\begin\{tabular\}", text) and "booktabs" not in raw:
        warn("tabular used but booktabs is not loaded — add \\usepackage{booktabs}")

    # ---- citation/reference typography
    bad_tilde = len(re.findall(r"(?<![~\s{(\[])\s\\cite", text))
    if bad_tilde:
        warn(f"{bad_tilde} \\cite preceded by a plain space — use `word~\\cite{{..}}` "
             f"to prevent a line break before the bracket")
    if re.search(r"\\cite[a-zA-Z]*\s*\{[^}]*\}\s*\.", text) is None and re.search(
            r"\.\s*\\cite", text):
        warn("citation placed after the full stop — put it before the period")

    # ---- leftovers
    for i, line in enumerate(text.split("\n"), 1):
        if re.search(r"\\todo|\bTODO\b|\bFIXME\b|\bXXX\b|\?\?\?", line):
            fail(f"line {i}: leftover marker — {line.strip()[:90]}")
    for i, tok, snippet in T.find_gap_tokens(text):
        fail(f"line {i}: gap token {tok} — {snippet}")

    # ---- prose slips
    # Same-line repeats only, and never the CITE/REF/MATH placeholders that
    # to_prose() substitutes in -- two adjacent citations are not a doubled word.
    PLACEHOLDERS = {"cite", "ref", "math"}
    for m in re.finditer(r"\b([A-Za-z]{3,})[ \t]+\1\b", T.to_prose(T.body_only(text)), re.I):
        if m.group(1).lower() in PLACEHOLDERS:
            continue
        warn(f"doubled word: \"{m.group(0)}\"")

    # ---- build log
    log = args.log or os.path.splitext(args.tex)[0] + ".log"
    if os.path.isfile(log):
        with open(log, encoding="utf-8", errors="replace") as fh:
            lg = fh.read()
        ob = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", lg)
        big = [float(x) for x in ob if float(x) > 5]
        if big:
            fail(f"{len(big)} Overfull hbox over 5pt (worst {max(big):.1f}pt) — "
                 f"text is spilling into the margin")
        elif ob:
            info(f"{len(ob)} small overfull hbox(es), all under 5pt")
        if "LaTeX Warning: There were undefined references" in lg:
            fail("build log reports undefined references — the PDF contains '??'")
        if "LaTeX Warning: Citation" in lg:
            for m in re.finditer(r"Citation `([^']+)' on page \d+ undefined", lg):
                fail(f"undefined citation `{m.group(1)}` — key missing from the .bib")
        m = re.search(r"Output written on .*?\((\d+) pages?", lg)
        if m:
            pages = int(m.group(1))
            info(f"compiled length: {pages} pages (total, including references)")
            if args.venue:
                reg_path = T.find_registry()
                if reg_path:
                    import json
                    with open(reg_path, encoding="utf-8") as fh:
                        reg = json.load(fh)
                    V = reg["venues"].get(args.venue)
                    if V and V["length"].get("main_pages"):
                        lim = V["length"]["main_pages"]
                        if pages > lim + 3:
                            warn(f"{pages} total pages against a {lim}-page main-content limit "
                                 f"for {V['name']} — verify the main body by hand")
    else:
        info(f"no build log at {log} — compile first for overfull boxes, undefined "
             f"references, and the real page count")

    # ---- report
    print(f"# LaTeX lint — {args.tex}\n")
    if not findings:
        print("  no findings.")
    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    for status, msg in sorted(findings, key=lambda f: order.get(f[0], 9)):
        print(f"  [{status:4}] {msg}")

    fails = [f for f in findings if f[0] == "FAIL"]
    print(f"\n{len(fails)} FAIL · {sum(1 for f in findings if f[0]=='WARN')} WARN")
    if args.strict and fails:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
