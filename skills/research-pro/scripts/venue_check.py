#!/usr/bin/env python3
"""Check a manuscript against a target venue's hard rules (Gate 3).

Reads venues/registry.json, checks length, required sections, required artifacts,
anonymity, gap tokens, and prompt injection. Mechanical checks only -- every
finding here is something that causes a desk rejection without a reviewer's
judgment entering into it.

IMPORTANT: a PASS here is provisional. Venue rules change every cycle. Gate 3 does
not pass until the live call for papers has been re-read (venues/VERIFY.md).

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import _textlib as T

NAMED_REPO = re.compile(r"(?:github\.com|gitlab\.com|bitbucket\.org|huggingface\.co)/"
                        r"(?!anonymous|anon)([A-Za-z0-9_.\-]+)", re.I)
ANON_OK = re.compile(r"anonymous\.4open\.science|anonymous\.github|/anonymous", re.I)
INJECTION = re.compile(
    r"(ignore (?:all )?(?:previous|prior|above) instructions"
    r"|disregard (?:the )?(?:above|previous)"
    r"|you are (?:a|an) (?:helpful )?(?:AI|assistant|language model)"
    r"|as an AI language model"
    r"|give (?:this|the) paper a (?:high|positive|strong)"
    r"|recommend acceptance"
    r"|accept this paper"
    r"|do not mention (?:this|these) instruction"
    r"|system prompt"
    r"|LLM reviewers?[:,]? )", re.I)
FIRST_PERSON_SELFCITE = re.compile(
    r"\b(?:our|my)\s+(?:previous|prior|earlier|own)\s+(?:work|paper|method|study|approach)\b"
    r"|\bin\s+our\s+(?:previous|prior|earlier)\s+", re.I)
ACK_SECTION = re.compile(r"\\(?:section|subsection)\*?\s*\{\s*Acknowledg", re.I)


def load_venue(slug: str, registry_path: str | None) -> tuple[dict, dict]:
    path = registry_path or T.find_registry()
    if not path:
        raise SystemExit("error: cannot locate venues/registry.json (pass --registry)")
    with open(path, encoding="utf-8") as fh:
        reg = json.load(fh)
    if slug not in reg["venues"]:
        raise SystemExit(f"error: unknown venue '{slug}'. known: {', '.join(sorted(reg['venues']))}")
    return reg, reg["venues"][slug]


def estimate_pages(prose_words: int, family: str) -> float:
    """Rough page estimate when no compiled PDF is available."""
    per_page = 750 if "ml" in family or "cv" in family or "nlp" in family or "ai" in family else 600
    return round(prose_words / per_page, 1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--venue", required=True, help="venue slug, e.g. neurips")
    ap.add_argument("--paper", required=True, help="main .tex file")
    ap.add_argument("--pdf", help="compiled PDF, for a real page count and text scan")
    ap.add_argument("--registry", help="path to venues/registry.json")
    ap.add_argument("--list", action="store_true", help="list known venue slugs and exit")
    ap.add_argument("--strict", action="store_true", default=True)
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    if args.list:
        path = args.registry or T.find_registry()
        with open(path, encoding="utf-8") as fh:
            reg = json.load(fh)
        for k, v in sorted(reg["venues"].items()):
            print(f"{k:12} {v['name']} ({v['cycle']})")
        return 0

    reg, V = load_venue(args.venue, args.registry)
    why = T.sniff_binary(args.paper)
    if why:
        print(f"error: {why}", file=sys.stderr)
        return 2
    raw = T.read_with_inputs(args.paper)
    if not raw:
        print(f"error: cannot read {args.paper}", file=sys.stderr)
        return 2
    clean = T.strip_comments(raw)
    body = T.body_only(clean)
    prose = T.to_prose(body)
    words = len(T.words(prose))

    findings: list[tuple[str, str, str]] = []      # (status, rule, detail)

    def add(ok, rule, detail, warn=False):
        findings.append(("PASS" if ok else ("WARN" if warn else "FAIL"), rule, detail))

    # ---- length
    limit = V["length"].get("main_pages")
    pdf_pages = T.pdf_page_count(args.pdf) if args.pdf else None
    if limit is None:
        add(True, "page limit", f"{V['name']} has no page limit; length must still be justified")
    elif pdf_pages is not None:
        excl = ", ".join(V["length"].get("excluded_from_limit", [])) or "nothing"
        add(pdf_pages <= limit + 2, "page count (PDF)",
            f"PDF has {pdf_pages} pages; limit is {limit} for main content "
            f"(excluded: {excl}). Count the main body by hand — this is the total.",
            warn=True)
    else:
        est = estimate_pages(words, V.get("family", ""))
        add(est <= limit, "page count (estimated)",
            f"~{est} pages from {words} prose words; limit {limit}. "
            f"ESTIMATE ONLY — compile and pass --pdf for the real count.", warn=True)

    # ---- required sections
    for sec in V.get("required_sections", []):
        name = sec["name"]
        present = re.search(rf"\\(?:section|subsection|paragraph)\*?\s*\{{\s*{re.escape(name.split()[0])}",
                            clean, re.I) is not None
        hard = sec.get("enforcement") == "hard"
        detail = f"{name} — {sec.get('placement', '')}".strip(" —")
        if not present and sec.get("enforcement") == "optional":
            findings.append(("WARN", f"optional section: {name}", "not present (optional here)"))
        else:
            add(present, f"required section: {name}",
                detail + ("  ⇒ DESK REJECT if missing" if hard else ""))

    # ---- required artifacts (cannot be verified from the .tex alone)
    for art in V.get("required_artifacts", []):
        findings.append(("MANUAL", f"required artifact: {art['name']}",
                         f"{art.get('placement','')} — confirm it is present and complete"
                         + ("  ⇒ DESK REJECT if missing" if art.get("enforcement") == "hard" else "")))

    # ---- anonymity
    if "double-blind" in str(V.get("anonymity", "")).lower():
        ack = ACK_SECTION.search(clean)
        add(not ack, "anonymity: no acknowledgements",
            "acknowledgements section present — remove for review" if ack else "none found")
        sc = FIRST_PERSON_SELFCITE.findall(clean)
        add(not sc, "anonymity: third-person self-citation",
            f"{len(sc)} first-person self-reference(s) e.g. \"{sc[0] if sc else ''}\" — "
            "rewrite as 'Prior work [n] showed'" if sc else "clean")
        repos = [m.group(0) for m in NAMED_REPO.finditer(clean) if not ANON_OK.search(m.group(0))]
        add(not repos, "anonymity: no named repository",
            f"named repo link(s): {', '.join(sorted(set(repos))[:3])}" if repos else "none found")
        if args.pdf:
            ptxt = T.pdf_text(args.pdf)
            if ptxt:
                findings.append(("MANUAL", "anonymity: PDF metadata",
                                 "run `pdfinfo main.pdf` and confirm Author/Title carry no identity"))
        thanks = re.search(r"\\thanks\s*\{", clean)
        add(not thanks, "anonymity: no \\thanks",
            "\\thanks present (usually funding/affiliation)" if thanks else "none")

    # ---- gap tokens
    gaps = T.find_gap_tokens(clean)
    add(not gaps, "no gap tokens",
        f"{len(gaps)} left: " + "; ".join(f"line {l} {t}" for l, t, _ in gaps[:4]) if gaps else "clean")

    # ---- prompt injection
    # Scan the RAW source, comments included: a LaTeX comment is a classic hiding
    # place, and it travels with the source even though it does not render.
    inj = [(i, ln.strip()[:100]) for i, ln in enumerate(raw.split("\n"), 1) if INJECTION.search(ln)]
    add(not inj, "no prompt injection",
        f"SUSPECTED INJECTION at line {inj[0][0]}: \"{inj[0][1]}\" — "
        f"{len(inj)} site(s). This is a rejection-and-report offence at multiple "
        "venues. Check LaTeX comments, white/tiny text, and figure metadata."
        if inj else "clean (source, comments included)")
    if args.pdf:
        ptxt = T.pdf_text(args.pdf)
        if ptxt and INJECTION.search(ptxt):
            findings.append(("FAIL", "no prompt injection (PDF text)",
                             "injection-shaped text found in the extracted PDF text — "
                             "check for hidden/white/tiny text"))

    # ---- policy reminders that need a human
    ai = V.get("ai_policy", {})
    if ai.get("disclosure"):
        findings.append(("MANUAL", "AI-use disclosure", ai["disclosure"]))
    if V.get("dual_submission"):
        ds = V["dual_submission"]
        findings.append(("MANUAL", "dual submission",
                         f"no >{ds.get('overlap_threshold_percent','?')}% overlapping work under "
                         f"review during {ds.get('review_period','the review period')} — "
                         f"{ds.get('consequence','')}"))
    if V.get("submission_process", {}).get("two_stage"):
        findings.append(("MANUAL", "two-stage submission", V["submission_process"]["note"]))

    # ---- report
    print(f"# Venue compliance — {V['name']} {V['cycle']}")
    print(f"\nPaper: `{args.paper}`   Registry verified: {reg['verified_on']}\n")
    order = {"FAIL": 0, "WARN": 1, "MANUAL": 2, "PASS": 3}
    for status, rule, detail in sorted(findings, key=lambda f: order.get(f[0], 9)):
        print(f"  [{status:6}] {rule:38} {detail}")

    if V.get("desk_reject_triggers"):
        print("\n## Desk-reject triggers at this venue\n")
        for t in V["desk_reject_triggers"]:
            print(f"  - {t}")

    print("\n## Re-verification required\n")
    for k, u in V.get("urls", {}).items():
        print(f"  {k}: {u}")
    print("\n  Gate 3 does NOT pass on this snapshot alone. Re-read the live pages above,")
    print(f"  compare field by field, and update the registry (currently {reg['verified_on']}).")

    fails = [f for f in findings if f[0] == "FAIL"]
    if args.strict and fails:
        print(f"\nFAIL — {len(fails)} hard-rule violation(s).")
        return 1
    print("\nNo hard-rule violation detected by measurement (provisional — see above).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
