#!/usr/bin/env python3
"""Measure the structural profile of accepted papers, then compare a draft to it.

An accepted paper from your target venue is a measured specification of what that
venue accepts: section order, page allocation, figure and citation density,
register. This extracts that, and then tells you where your draft deviates.

  # build a target profile from 1-3 exemplars
  exemplar_profile.py refs/exemplars/*.tex --out paper/exemplar_profile.json

  # compare your draft against it
  exemplar_profile.py paper/main.tex --compare paper/exemplar_profile.json

PDFs: extract text first (`pdftotext -layout in.pdf out.txt`) and pass the .txt.
Text input gives section and register metrics but not LaTeX float counts.

NEVER copy an exemplar's wording. This measures shape, not prose.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys

import _textlib as T

CANON = [
    ("abstract", r"^abstract"),
    ("intro", r"^(1\.?\s*)?introduction"),
    ("related", r"^(related work|background|prior work|literature)"),
    ("method", r"^(method|methods|methodology|approach|model|our |proposed|framework|architecture)"),
    ("experiments", r"^(experiment|experiments|evaluation|experimental|results|empirical)"),
    ("analysis", r"^(analysis|ablation|discussion of results)"),
    ("discussion", r"^discussion"),
    ("limitations", r"^(limitation|limitations|threats to validity)"),
    ("ethics", r"^(ethic|ethics|broader impact|impact statement|societal)"),
    ("conclusion", r"^(conclusion|conclusions|concluding)"),
    ("acknowledgements", r"^acknowledg"),
    ("appendix", r"^(appendix|supplement)"),
]

TEXT_SECTION_RE = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?([A-Z][A-Za-z][A-Za-z \-&/]{2,45})\s*$", re.M)


def canon(title: str) -> str:
    t = title.strip().lower().lstrip("0123456789. ")
    for name, pat in CANON:
        if re.search(pat, t):
            return name
    return "other:" + t[:28]


def sections_from_tex(raw: str) -> list[tuple[str, str]]:
    out = []
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, re.S)
    if m:
        out.append(("abstract", m.group(1)))
    for lvl, title, body in T.split_sections(raw):
        if lvl in ("section", "chapter"):
            out.append((canon(title), body))
    return out


def sections_from_text(raw: str) -> list[tuple[str, str]]:
    marks = [(m.start(), m.group(1)) for m in TEXT_SECTION_RE.finditer(raw)]
    marks = [(p, t) for p, t in marks if canon(t) != "other:" + t.strip().lower()[:28]
             or len(t.split()) <= 4]
    out = []
    for i, (pos, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
        out.append((canon(title), raw[pos + len(title) : end]))
    return out


def profile(path: str) -> dict:
    is_tex = path.endswith(".tex")
    raw = T.read_with_inputs(path) if is_tex else open(
        path, encoding="utf-8", errors="replace").read()
    clean = T.strip_comments(raw) if is_tex else raw
    body = T.body_only(clean) if is_tex else clean

    secs = sections_from_tex(body) if is_tex else sections_from_text(body)
    prose_all = T.to_prose(body) if is_tex else body
    total_words = max(len(T.words(prose_all)), 1)

    sec_stats = {}
    order = []
    for name, sbody in secs:
        sprose = T.to_prose(sbody) if is_tex else sbody
        w = len(T.words(sprose))
        if name not in sec_stats:
            order.append(name)
            sec_stats[name] = {"words": 0, "figures": 0, "tables": 0,
                               "equations": 0, "citations": 0}
        s = sec_stats[name]
        s["words"] += w
        if is_tex:
            s["figures"] += T.count_env(sbody, "figure")
            s["tables"] += T.count_env(sbody, "table")
            s["equations"] += T.count_equations(sbody)
            s["citations"] += T.count_citations(sbody)
        else:
            s["citations"] += len(re.findall(r"\[\d+(?:\s*[,;–-]\s*\d+)*\]", sbody))
            s["citations"] += len(re.findall(r"\(\w+ et al\.,? \d{4}\)", sbody))
    for s in sec_stats.values():
        s["share_pct"] = round(100.0 * s["words"] / total_words, 1)

    sents = T.sentences(prose_all)
    lens = [len(T.words(s)) for s in sents]
    hedges = ["may", "might", "could", "possibly", "perhaps", "suggests", "appears",
              "seems", "likely", "potentially", "generally", "typically", "often"]

    abstract_words = sec_stats.get("abstract", {}).get("words", 0)
    return {
        "file": os.path.basename(path),
        "total_words": total_words,
        "section_order": order,
        "sections": sec_stats,
        "figures_total": sum(s["figures"] for s in sec_stats.values()),
        "tables_total": sum(s["tables"] for s in sec_stats.values()),
        "equations_total": sum(s["equations"] for s in sec_stats.values()),
        "citations_total": sum(s["citations"] for s in sec_stats.values()),
        "abstract_words": abstract_words,
        "sentence_len_mean": round(statistics.mean(lens), 1) if lens else 0,
        "sentence_len_stdev": round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
        "first_person_per_100w": round(
            100 * len(re.findall(r"\b(?:we|our|ours|us)\b", prose_all, re.I)) / total_words, 2),
        "passive_markers_per_100w": round(
            100 * len(re.findall(r"\b(?:is|are|was|were|been)\s+\w+(?:ed|en)\b",
                                 prose_all, re.I)) / total_words, 2),
        "hedges_per_100w": round(
            100 * sum(len(re.findall(rf"\b{h}\b", prose_all, re.I)) for h in hedges)
            / total_words, 2),
        "citations_per_1000w": round(1000.0 * sum(s["citations"] for s in sec_stats.values())
                                     / total_words, 1),
    }


def merge(profiles: list[dict]) -> dict:
    keys = ["total_words", "figures_total", "tables_total", "equations_total",
            "citations_total", "abstract_words", "sentence_len_mean",
            "sentence_len_stdev", "first_person_per_100w", "passive_markers_per_100w",
            "hedges_per_100w", "citations_per_1000w"]
    out = {"n_exemplars": len(profiles), "sources": [p["file"] for p in profiles]}
    for k in keys:
        vals = [p[k] for p in profiles if p.get(k) is not None]
        out[k] = round(statistics.mean(vals), 1) if vals else 0
    names = []
    for p in profiles:
        for n in p["section_order"]:
            if n not in names:
                names.append(n)
    out["section_order"] = names
    out["sections"] = {}
    for n in names:
        shares = [p["sections"][n]["share_pct"] for p in profiles if n in p["sections"]]
        figs = [p["sections"][n]["figures"] for p in profiles if n in p["sections"]]
        cits = [p["sections"][n]["citations"] for p in profiles if n in p["sections"]]
        out["sections"][n] = {
            "share_pct": round(statistics.mean(shares), 1) if shares else 0,
            "present_in": f"{len(shares)}/{len(profiles)}",
            "figures": round(statistics.mean(figs), 1) if figs else 0,
            "citations": round(statistics.mean(cits), 1) if cits else 0,
        }
    return out


def compare(draft: dict, target: dict, tol: float) -> int:
    print(f"# Draft vs exemplar profile\n")
    print(f"Draft: {draft['file']} ({draft['total_words']} words)")
    print(f"Target: {target.get('n_exemplars', '?')} exemplar(s) "
          f"{', '.join(target.get('sources', []))} "
          f"(mean {target.get('total_words', 0):.0f} words)\n")

    print("## Section allocation (% of prose words)\n")
    print(f"  {'section':18} {'draft':>7} {'target':>8} {'delta':>8}   status")
    flagged = 0
    for name in target["section_order"]:
        tgt = target["sections"][name]["share_pct"]
        got = draft["sections"].get(name, {}).get("share_pct")
        if got is None:
            present = target["sections"][name]["present_in"]
            mark = "MISSING" if not present.startswith("0") else "-"
            print(f"  {name:18} {'—':>7} {tgt:>7.1f}% {'—':>8}   {mark}"
                  f"   (in {present} exemplars)")
            if mark == "MISSING":
                flagged += 1
            continue
        delta = got - tgt
        rel = abs(delta) / tgt if tgt else 0
        status = "ok" if rel <= tol else ("THIN" if delta < 0 else "BLOATED")
        if status != "ok":
            flagged += 1
        print(f"  {name:18} {got:>6.1f}% {tgt:>7.1f}% {delta:>+7.1f}%   {status}")

    for name in draft["section_order"]:
        if name not in target["sections"]:
            print(f"  {name:18} {draft['sections'][name]['share_pct']:>6.1f}% "
                  f"{'—':>7} {'—':>8}   NOT IN EXEMPLARS")

    print("\n## Density and register\n")
    pairs = [("figures_total", "figures", 0), ("tables_total", "tables", 0),
             ("equations_total", "equations", 0), ("citations_total", "citations", 0),
             ("citations_per_1000w", "citations / 1000 words", 1),
             ("abstract_words", "abstract words", 0),
             ("sentence_len_mean", "mean sentence length", 1),
             ("sentence_len_stdev", "sentence-length stdev", 1),
             ("first_person_per_100w", "'we/our' per 100 words", 2),
             ("hedges_per_100w", "hedges per 100 words", 2)]
    for key, label, dp in pairs:
        got, tgt = draft.get(key, 0), target.get(key, 0)
        if not tgt:
            continue
        rel = abs(got - tgt) / tgt
        status = "ok" if rel <= tol else ("LOW" if got < tgt else "HIGH")
        if status != "ok":
            flagged += 1
        print(f"  {label:26} draft {got:>8.{dp}f}   target {tgt:>8.{dp}f}   {status}")

    print(f"\n{flagged} deviation(s) beyond ±{tol:.0%}.\n")
    print("A deviation is a question, not a verdict. Each one should be a decision you")
    print("made, not an accident. Copy structure and proportion — never wording.")
    return 1 if flagged else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("papers", nargs="+", help=".tex or .txt files")
    ap.add_argument("--out", help="write the merged profile here")
    ap.add_argument("--compare", help="compare the (single) input against this profile")
    ap.add_argument("--tol", type=float, default=0.25, help="deviation tolerance (default 0.25)")
    args = ap.parse_args(argv)

    profs = []
    for p in args.papers:
        if not os.path.isfile(p):
            print(f"warning: skipping missing {p}", file=sys.stderr)
            continue
        pr = profile(p)
        if pr["total_words"] < 50:
            print(f"warning: {p} has almost no prose; skipping", file=sys.stderr)
            continue
        profs.append(pr)
    if not profs:
        print("error: no readable papers", file=sys.stderr)
        return 2

    if args.compare:
        if len(profs) > 1:
            print("error: --compare takes exactly one paper", file=sys.stderr)
            return 2
        with open(args.compare, encoding="utf-8") as fh:
            target = json.load(fh)
        return compare(profs[0], target, args.tol)

    merged = merge(profs)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(merged, fh, indent=2)
        print(f"profile written to {args.out}")

    print(f"# Exemplar profile — {merged['n_exemplars']} paper(s)\n")
    print(f"  sources: {', '.join(merged['sources'])}")
    print(f"  mean length: {merged['total_words']:.0f} prose words")
    print(f"  section order: {' → '.join(merged['section_order'])}\n")
    print(f"  {'section':18} {'share':>7}  {'figs':>5} {'cites':>6}  present")
    for n in merged["section_order"]:
        s = merged["sections"][n]
        print(f"  {n:18} {s['share_pct']:>6.1f}% {s['figures']:>6.1f} "
              f"{s['citations']:>6.1f}  {s['present_in']}")
    print(f"\n  figures {merged['figures_total']:.1f} · tables {merged['tables_total']:.1f}"
          f" · equations {merged['equations_total']:.1f} · citations {merged['citations_total']:.0f}"
          f" ({merged['citations_per_1000w']:.1f}/1000w)")
    print(f"  abstract {merged['abstract_words']:.0f} words · sentences "
          f"{merged['sentence_len_mean']:.1f}±{merged['sentence_len_stdev']:.1f} words")
    print(f"  'we/our' {merged['first_person_per_100w']:.2f}/100w · hedges "
          f"{merged['hedges_per_100w']:.2f}/100w")
    print("\nUse this as the section budget in S1, and --compare your draft before Gate 4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
