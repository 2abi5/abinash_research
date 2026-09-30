#!/usr/bin/env python3
"""Compute the gated submission-readiness score (Gate 4).

Reads a filled scorecard (JSON or YAML), applies the target venue's dimension
weights from venues/registry.json, enforces the hard gates, and prints the report.

Design rules, from references/15-readiness-score.md:
  * Gates outrank the score. Any failed gate => NOT READY, whatever the total.
  * A dimension with an empty `evidence` field is REFUSED, not assumed fine.
  * Venue `emphasis` reweights the dimensions toward what that venue actually
    grades hardest.

Stdlib only (YAML input needs PyYAML; JSON always works).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import NoReturn

import _textlib as T

DIMENSIONS = [
    ("contribution", "Contribution clarity and weight"),
    ("claim_evidence", "Claim-evidence integrity"),
    ("methodological_soundness", "Methodological soundness"),
    ("experimental_completeness", "Experimental completeness"),
    ("related_work", "Related work and positioning"),
    ("writing_clarity", "Writing clarity and prose quality"),
    ("figures_tables", "Figures and tables"),
    ("citation_integrity", "Citation integrity"),
    ("reproducibility", "Reproducibility"),
    ("venue_compliance", "Venue compliance, ethics, disclosure"),
]

GATES = {
    "G-CITE": "Every reference verified; no unresolved MISMATCH",
    "G-CLAIM": "Every abstract/introduction claim has supporting evidence",
    "G-VENUE": "No live desk-reject trigger (length, required sections, anonymity, template)",
    "G-ETHICS": "Ethics/IRB approval in place where human subjects or restricted data apply",
    "G-INTEGRITY": "No fabricated result, no undisclosed AI use, no prompt injection, no undeclared dual submission",
    "G-TOKEN": "No [NEEDS SOURCE] / [TBD] / [NEEDS EXPERIMENT] / [VERIFY] tokens remain",
}

BANDS = [(90, "SUBMIT", "Nothing blocking. Remaining items are polish."),
         (80, "SUBMIT AFTER FIXES", "Fixable in days. Competitive."),
         (70, "BORDERLINE", "Likely major revision or weak reject. Fix the two lowest dimensions."),
         (55, "NOT READY", "Structural work needed: a missing experiment, unsupported claims, or a rewrite."),
         (0, "NOT READY", "The paper needs a different plan, not another editing pass.")]

EMPHASIS_BOOST = 1.5      # emphasised dimensions get 1.5x their default weight


def _die(msg: str) -> "NoReturn":
    """Usage error: stderr plus exit 2, matching the other scripts here."""
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def load_card(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        _die(f"error: cannot read scorecard {path}: {exc}\n"
             f"  create one with: score_readiness.py --template --venue <slug>")
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            _die("error: YAML scorecard needs PyYAML; use JSON instead")
        try:
            card = yaml.safe_load(text)
        except Exception as exc:
            _die(f"error: {path} is not valid YAML: {exc}")
    else:
        try:
            card = json.loads(text)
        except json.JSONDecodeError as exc:
            _die(f"error: {path} is not valid JSON: {exc}")
    if not isinstance(card, dict):
        _die(f"error: {path} must contain an object, got {type(card).__name__}")
    return card


def weights_for(reg: dict, venue: str | None) -> dict[str, float]:
    base = dict(reg["dimension_weights_default"])
    if venue and venue in reg["venues"]:
        for dim in reg["venues"][venue].get("emphasis", []):
            if dim in base:
                base[dim] *= EMPHASIS_BOOST
    total = sum(base.values())
    return {k: 100.0 * v / total for k, v in base.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scorecard", nargs="?", help="filled scorecard (.json or .yaml)")
    ap.add_argument("--venue", help="venue slug, for weighting")
    ap.add_argument("--registry", help="path to venues/registry.json")
    ap.add_argument("--template", action="store_true", help="print a blank scorecard and exit")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="refuse to score dimensions with no evidence (default)")
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    if args.template:
        blank = {
            "paper": "<short name>",
            "venue": args.venue or "<venue slug>",
            "date": _dt.date.today().isoformat(),
            "gates": {g: {"status": "not_run", "note": ""} for g in GATES},
            "dimensions": {k: {"score": None, "evidence": "", "fix": ""} for k, _ in DIMENSIONS},
        }
        print(json.dumps(blank, indent=2))
        return 0

    if not args.scorecard:
        ap.error("scorecard is required (or pass --template)")

    reg_path = args.registry or T.find_registry()
    if not reg_path:
        print("error: cannot locate venues/registry.json", file=sys.stderr)
        return 2
    with open(reg_path, encoding="utf-8") as fh:
        reg = json.load(fh)

    card = load_card(args.scorecard)
    venue = args.venue or card.get("venue")
    if venue and venue not in reg["venues"]:
        print(f"warning: unknown venue '{venue}'; using default weights", file=sys.stderr)
        venue = None
    W = weights_for(reg, venue)

    dims = card.get("dimensions", {})
    rows, refused, missing, malformed = [], [], [], []
    for key, label in DIMENSIONS:
        d = dims.get(key) or {}
        score, evid = d.get("score"), (d.get("evidence") or "").strip()
        if score is None:
            missing.append(key)
            continue
        if args.strict and not evid:
            refused.append(key)
            continue
        try:
            score = max(0.0, min(10.0, float(score)))
        except (TypeError, ValueError):
            malformed.append((key, score))
            continue
        w = W[key]
        rows.append({"key": key, "label": label, "score": score, "weight": w,
                     "earned": score / 10.0 * w, "lost": (10.0 - score) / 10.0 * w,
                     "evidence": evid, "fix": (d.get("fix") or "").strip()})

    if malformed:
        print("MALFORMED SCORES — these are not numbers:\n")
        for k, v in malformed:
            print(f"  - {k}: {v!r}")
        print("\nScores are 0-10. Anchors are in references/15-readiness-score.md.")
        return 2
    if refused:
        print("REFUSED TO SCORE — these dimensions have a score but no `evidence`:\n")
        for k in refused:
            print(f"  - {k}")
        print("\nA score without cited evidence is a guess with a decimal point.")
        print("Fill the `evidence` field (the table, figure, section, or report it came from),")
        print("or drop the score. Re-run with --no-strict only if you accept a guess.")
        return 2
    if missing:
        print(f"note: {len(missing)} dimension(s) unscored and excluded from the total: "
              f"{', '.join(missing)}", file=sys.stderr)

    scored_weight = sum(r["weight"] for r in rows)
    total = round(sum(r["earned"] for r in rows) * (100.0 / scored_weight), 1) if scored_weight else 0.0

    gates = card.get("gates", {})
    failed = [g for g in GATES if str((gates.get(g) or {}).get("status", "not_run")).lower()
              in ("fail", "failed", "false")]
    notrun = [g for g in GATES if str((gates.get(g) or {}).get("status", "not_run")).lower()
              in ("not_run", "notrun", "", "none", "null")]

    band, band_note = "NOT READY", ""
    for cut, name, note in BANDS:
        if total >= cut:
            band, band_note = name, note
            break

    gated = bool(failed) or bool(notrun)
    verdict = "NOT READY (gated)" if gated else band

    vname = reg["venues"][venue]["name"] + " " + str(reg["venues"][venue]["cycle"]) if venue else "no venue set"
    print(f"# Readiness — {card.get('paper','<paper>')} → {vname} · {card.get('date','')}\n")
    print(f"## Verdict: {verdict}")
    print(f"Score {total}/100 (band: {band} — {band_note})")
    if gated:
        print("A hard gate has failed or has not been run. The score is reported, "
              "but it is not the verdict.")
    print()

    print("## Gates\n")
    for g, desc in GATES.items():
        st = str((gates.get(g) or {}).get("status", "not_run")).lower()
        mark = {"pass": "PASS", "true": "PASS", "ok": "PASS",
                "fail": "FAIL", "failed": "FAIL", "false": "FAIL",
                "n/a": "N/A", "na": "N/A", "not_applicable": "N/A"}.get(st, "NOT RUN")
        note = (gates.get(g) or {}).get("note", "")
        print(f"  [{mark:7}] {g:12} {desc}")
        if note and mark != "PASS":
            print(f"              -> {note}")
    print()

    if rows:
        rows_sorted = sorted(rows, key=lambda r: -r["lost"])
        print("## Dimensions (weakest first)\n")
        print(f"  {'dimension':36} {'score':>6} {'weight':>7} {'lost':>7}")
        for r in rows_sorted:
            print(f"  {r['label'][:36]:36} {r['score']:>5.1f}  {r['weight']:>6.1f}  {r['lost']:>6.1f}")
        print("\n## Where the points went\n")
        for r in rows_sorted:
            if r["lost"] < 0.5:
                continue
            print(f"  - **{r['label']}** {r['score']}/10 (-{r['lost']:.1f})")
            print(f"      evidence: {r['evidence'][:160]}")
            if r["fix"]:
                print(f"      fix:      {r['fix'][:160]}")

    if venue:
        em = reg["venues"][venue].get("emphasis", [])
        if em:
            print(f"\n## Weighting\n\n  {vname} emphasises: {', '.join(em)}")
            print(f"  Those dimensions carry {EMPHASIS_BOOST}x their default weight here.")

    print("\n## Before you submit\n")
    if failed:
        print("  Blocking gates: " + ", ".join(failed))
    if notrun:
        print("  Gates not yet run: " + ", ".join(notrun)
              + "\n  A gate that has not been run is not passed.")
    if not gated and total >= 90:
        print("  Nothing blocking. Do a final read-aloud pass and submit.")
    elif not gated:
        print("  Fix the dimensions listed above, starting from the top.")

    if args.strict and gated:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
