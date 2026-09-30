#!/usr/bin/env python3
"""Verify every BibTeX entry against real bibliographic records.

Three layers (see references/13-citation-integrity.md):
  L1  the record exists        -- resolved against Crossref / OpenAlex / arXiv / S2
  L2  the metadata matches     -- title, first author, year, venue
  L3  the source supports the claim  -- NOT automatable; reported as a manual TODO

Statuses: VERIFIED | MISMATCH | UNVERIFIED | OFFLINE
Exit code is non-zero under --strict unless every entry is VERIFIED.

Stdlib only. Network is optional; without it the script runs structural checks
and reports OFFLINE, which does NOT pass Gate 2.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import _textlib

UA = "research-pro-citation-verifier/1.0 (academic reference checking)"
TIMEOUT = 20

REQUIRED_FIELDS = {
    "article": ["author", "title", "journal", "year"],
    "inproceedings": ["author", "title", "booktitle", "year"],
    "incollection": ["author", "title", "booktitle", "year"],
    "book": ["author", "title", "publisher", "year"],
    "inbook": ["author", "title", "publisher", "year"],
    "phdthesis": ["author", "title", "school", "year"],
    "mastersthesis": ["author", "title", "school", "year"],
    "techreport": ["author", "title", "institution", "year"],
    "misc": ["author", "title", "year"],
    "unpublished": ["author", "title", "note"],
}

# Words that are commonly lowercased by BibTeX styles unless brace-protected.
NEEDS_BRACES = re.compile(
    r"\b(BERT|GPT|LSTM|CNN|RNN|GAN|VAE|NeRF|ImageNet|CIFAR|COCO|MNIST|SQuAD|GLUE|"
    r"ReLU|Adam|SGD|CUDA|GPU|TPU|API|NLP|LLM|SOTA|IoU|mAP|PSNR|SSIM|FID|BLEU|ROUGE|"
    r"English|German|Chinese|French|Japanese|Bayesian|Gaussian|Markov|Fourier|"
    r"Transformer|Python|PyTorch|TensorFlow)\b"
)

DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+$")
ARXIV_RE = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$|^([a-z-]+(\.[A-Z]{2})?/\d{7})(v\d+)?$")


# ---------------------------------------------------------------- bibtex parsing
def strip_braces(value: str) -> str:
    v = value.strip()
    while len(v) >= 2 and ((v[0] == "{" and v[-1] == "}") or (v[0] == '"' and v[-1] == '"')):
        v = v[1:-1].strip()
    return v


def parse_bibtex(text: str) -> list[dict]:
    """Minimal BibTeX parser: balanced braces, quoted values, @string ignored."""
    entries = []
    i = 0
    n = len(text)
    while i < n:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*[{(]", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        body_start = at + m.end()
        if etype in ("string", "comment", "preamble"):
            i = body_start
            continue
        # find matching close brace
        depth = 1
        j = body_start
        while j < n and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[body_start : j - 1]
        line_no = text.count("\n", 0, at) + 1

        key, _, rest = body.partition(",")
        fields = {}
        buf, depth, in_quote = "", 0, False
        parts = []
        for ch in rest:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == '"' and depth == 0:
                in_quote = not in_quote
            if ch == "," and depth == 0 and not in_quote:
                parts.append(buf)
                buf = ""
            else:
                buf += ch
        parts.append(buf)
        for part in parts:
            if "=" not in part:
                continue
            k, _, v = part.partition("=")
            k = k.strip().lower()
            if k:
                fields[k] = strip_braces(v)
        entries.append(
            {"type": etype, "key": key.strip(), "fields": fields, "line": line_no}
        )
        i = j
    return entries


# ---------------------------------------------------------------- normalisation
def norm_title(s: str) -> str:
    s = re.sub(r"\{|\}|\\[a-zA-Z]+", "", s or "")
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return " ".join(s.split())


def title_ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


def first_surname(author_field: str) -> str:
    if not author_field:
        return ""
    first = re.split(r"\s+and\s+", author_field)[0].strip()
    first = re.sub(r"\{|\}|\\[a-zA-Z]+", "", first)
    if "," in first:
        return first.split(",")[0].strip().lower()
    parts = first.split()
    return parts[-1].lower() if parts else ""


def clean_doi(raw: str) -> str:
    d = (raw or "").strip()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d, flags=re.I)
    d = re.sub(r"^doi:\s*", "", d, flags=re.I)
    return d.rstrip(".")


# ---------------------------------------------------------------- http
class Net:
    def __init__(self, enabled: bool, mailto: str = ""):
        self.enabled = enabled
        self.mailto = mailto
        self.failures = 0
        self.blocked = False

    def get(self, url: str) -> dict | str | None:
        if not self.enabled or self.blocked:
            return None
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read().decode("utf-8", "replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        except Exception:
            self.failures += 1
            if self.failures >= 4:
                self.blocked = True  # network is unavailable; stop hammering it
            return None
        finally:
            time.sleep(0.12)  # be polite to public APIs


# ---------------------------------------------------------------- resolvers
def from_crossref(net: Net, doi: str) -> dict | None:
    suffix = f"?mailto={urllib.parse.quote(net.mailto)}" if net.mailto else ""
    d = net.get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}{suffix}")
    if not isinstance(d, dict) or "message" not in d:
        return None
    m = d["message"]
    authors = m.get("author") or []
    date = m.get("issued", {}).get("date-parts") or [[None]]
    return {
        "source": "crossref",
        "title": (m.get("title") or [""])[0],
        "first_surname": (authors[0].get("family", "") if authors else "").lower(),
        "year": str(date[0][0]) if date and date[0] and date[0][0] else "",
        "venue": (m.get("container-title") or [""])[0],
        "doi": m.get("DOI", ""),
        "type": m.get("type", ""),
    }


def from_openalex(net: Net, doi: str = "", title: str = "") -> dict | None:
    if doi:
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    elif title:
        q = urllib.parse.quote(norm_title(title)[:250])
        url = f"https://api.openalex.org/works?filter=title.search:{q}&per-page=3"
    else:
        return None
    d = net.get(url)
    if not isinstance(d, dict):
        return None
    work = d
    if "results" in d:
        if not d["results"]:
            return None
        work = d["results"][0]
    auths = work.get("authorships") or []
    surname = ""
    if auths:
        nm = (auths[0].get("author") or {}).get("display_name", "")
        surname = nm.split()[-1].lower() if nm else ""
    loc = (work.get("primary_location") or {}).get("source") or {}
    return {
        "source": "openalex",
        "title": work.get("title") or work.get("display_name") or "",
        "first_surname": surname,
        "year": str(work.get("publication_year") or ""),
        "venue": loc.get("display_name", "") or "",
        "doi": clean_doi(work.get("doi") or ""),
        "type": work.get("type", ""),
    }


def from_s2(net: Net, doi: str = "", title: str = "") -> dict | None:
    fields = "title,year,authors,venue,externalIds"
    if doi:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields={fields}"
    elif title:
        q = urllib.parse.quote(title[:250])
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=3&fields={fields}"
    else:
        return None
    d = net.get(url)
    if not isinstance(d, dict):
        return None
    paper = d
    if "data" in d:
        if not d["data"]:
            return None
        paper = d["data"][0]
    auths = paper.get("authors") or []
    surname = ""
    if auths and auths[0].get("name"):
        surname = auths[0]["name"].split()[-1].lower()
    return {
        "source": "semanticscholar",
        "title": paper.get("title") or "",
        "first_surname": surname,
        "year": str(paper.get("year") or ""),
        "venue": paper.get("venue") or "",
        "doi": clean_doi((paper.get("externalIds") or {}).get("DOI") or ""),
        "type": "",
    }


def from_arxiv(net: Net, arxiv_id: str) -> dict | None:
    raw = net.get(f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}")
    if not isinstance(raw, str) or "<entry>" not in raw:
        return None
    def tag(t):
        m = re.search(rf"<{t}>(.*?)</{t}>", raw, re.S)
        return " ".join(m.group(1).split()) if m else ""
    names = re.findall(r"<name>(.*?)</name>", raw, re.S)
    surname = names[0].split()[-1].lower() if names else ""
    published = tag("published")
    doi_m = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", raw, re.S)
    return {
        "source": "arxiv",
        "title": tag("title"),
        "first_surname": surname,
        "year": published[:4] if published else "",
        "venue": "arXiv",
        "doi": clean_doi(doi_m.group(1)) if doi_m else "",
        "type": "preprint",
        "published_doi": clean_doi(doi_m.group(1)) if doi_m else "",
    }


# ---------------------------------------------------------------- checks
def structural(entry: dict) -> list[str]:
    issues = []
    f, et = entry["fields"], entry["type"]
    for req in REQUIRED_FIELDS.get(et, ["author", "title", "year"]):
        if not f.get(req):
            issues.append(f"missing required field `{req}` for @{et}")
    if et == "article" and not f.get("pages"):
        issues.append("journal article without `pages`")
    if et == "article" and not f.get("volume"):
        issues.append("journal article without `volume`")
    title = f.get("title", "")
    for word in set(NEEDS_BRACES.findall(title)):
        if "{" + word + "}" not in title and "{" + word not in title:
            issues.append(f"capitalisation of `{word}` in title is not brace-protected")
    doi = f.get("doi", "")
    if doi and not DOI_RE.match(clean_doi(doi)):
        issues.append(f"malformed DOI `{doi}`")
    if f.get("url") and doi:
        issues.append("both `url` and `doi` present; prefer DOI alone")
    if not entry["key"] or not re.match(r"^[A-Za-z][A-Za-z0-9_:.\-]*$", entry["key"]):
        issues.append(f"suspicious cite key `{entry['key']}`")
    venue = (f.get("booktitle") or f.get("journal") or "")
    if "arXiv" in venue and et != "misc":
        issues.append("arXiv given as the venue: check for a published version")
    if f.get("eprint") and not f.get("archiveprefix"):
        issues.append("`eprint` present without `archivePrefix`")
    for junk in ("organization", "publisher"):
        if et == "inproceedings" and f.get(junk):
            issues.append(f"`{junk}` on @inproceedings is usually Google Scholar cruft")
    return issues


def resolve(net: Net, entry: dict) -> tuple[str, dict | None, list[str]]:
    """Return (status, record, mismatches)."""
    f = entry["fields"]
    doi = clean_doi(f.get("doi", ""))
    arxiv_id = (f.get("eprint") or "").strip()
    title = f.get("title", "")
    failures_before = net.failures

    rec = None
    if doi:
        rec = from_crossref(net, doi) or from_openalex(net, doi=doi) or from_s2(net, doi=doi)
    if rec is None and arxiv_id and ARXIV_RE.match(arxiv_id):
        rec = from_arxiv(net, arxiv_id)
    if rec is None and title:
        rec = from_openalex(net, title=title) or from_s2(net, title=title)

    if rec is None:
        # A lookup that errored out is NOT evidence of a fabricated reference.
        # Only a clean "no match" from a reachable database counts as UNVERIFIED.
        if not net.enabled or net.blocked or net.failures > failures_before:
            return "OFFLINE", None, []
        return "UNVERIFIED", None, []

    mism = []
    r = title_ratio(title, rec["title"])
    if r < 0.60:
        mism.append(
            f"title mismatch (similarity {r:.2f}) — record says: \"{rec['title'][:110]}\""
        )
    elif r < 0.90:
        mism.append(f"title differs slightly (similarity {r:.2f}) — check wording")
    ours = first_surname(f.get("author", ""))
    if ours and rec["first_surname"] and ours != rec["first_surname"]:
        mism.append(f"first author `{ours}` vs record `{rec['first_surname']}`")
    ry, oy = rec.get("year", ""), (f.get("year") or "").strip()
    if ry and oy and ry != oy:
        mism.append(f"year {oy} vs record {ry}")
    if rec.get("published_doi") and rec["source"] == "arxiv":
        mism.append(
            f"a published version exists (DOI {rec['published_doi']}) — cite that, not the preprint"
        )
    status = "MISMATCH" if any(
        m.startswith(("title mismatch", "first author", "year")) for m in mism
    ) else "VERIFIED"
    return status, rec, mism


def find_duplicates(entries: list[dict]) -> list[tuple[str, str, str]]:
    """One row per duplicated pair, with every reason it matched."""
    pairs: dict[tuple[str, str], list[str]] = {}
    seen_doi: dict[str, str] = {}
    seen_title: dict[str, str] = {}
    for e in entries:
        doi = clean_doi(e["fields"].get("doi", ""))
        if doi:
            if doi in seen_doi:
                pairs.setdefault((e["key"], seen_doi[doi]), []).append(f"same DOI {doi}")
            else:
                seen_doi[doi] = e["key"]
        nt = norm_title(e["fields"].get("title", ""))
        if len(nt) > 25:
            if nt in seen_title:
                pairs.setdefault((e["key"], seen_title[nt]), []).append("identical title")
            else:
                seen_title[nt] = e["key"]
    return [(a, b, "; ".join(why)) for (a, b), why in pairs.items()]


def cited_keys(paths: list[str]) -> set[str]:
    keys: set[str] = set()
    pat = re.compile(r"\\(?:[a-zA-Z]*cite[a-zA-Z]*)\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")
    for p in paths:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
        except OSError:
            continue
        for m in pat.finditer(txt):
            for k in m.group(1).split(","):
                if k.strip():
                    keys.add(k.strip())
    return keys


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib", help="path to refs.bib")
    ap.add_argument("--report", help="write a markdown report here")
    ap.add_argument("--offline", action="store_true", help="skip all network lookups")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="non-zero exit unless every entry is VERIFIED (default)")
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    ap.add_argument("--mailto", default=os.environ.get("CROSSREF_MAILTO", ""),
                    help="contact email for the Crossref polite pool")
    ap.add_argument("--tex", nargs="*", default=[],
                    help="tex files, to find uncited entries and unresolved keys")
    args = ap.parse_args(argv)

    why = _textlib.sniff_binary(args.bib)
    if why:
        print(f"error: {why}", file=sys.stderr)
        return 2
    try:
        with open(args.bib, encoding="utf-8", errors="replace") as fh:
            entries = parse_bibtex(fh.read())
    except OSError as exc:
        print(f"error: cannot read {args.bib}: {exc}", file=sys.stderr)
        return 2

    if not entries:
        print(f"error: no BibTeX entries found in {args.bib}", file=sys.stderr)
        return 2

    net = Net(enabled=not args.offline, mailto=args.mailto)
    results = []
    for e in entries:
        struct = structural(e)
        status, rec, mism = resolve(net, e)
        results.append({"entry": e, "status": status, "record": rec,
                        "mismatches": mism, "structural": struct})

    dups = find_duplicates(entries)
    keys = {e["key"] for e in entries}
    cited = cited_keys(args.tex) if args.tex else set()
    uncited = sorted(keys - cited) if cited else []
    unresolved = sorted(cited - keys) if cited else []

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    offline = net.blocked or args.offline
    gate_ok = (
        counts.get("VERIFIED", 0) == len(results)
        and not dups
        and not unresolved
        and not any(r["structural"] for r in results)
    )
    if offline:
        verdict = "BLOCKED: network unavailable — structural checks only. Gate 2 CANNOT pass."
    elif gate_ok:
        verdict = "PASS — layers 1 and 2 clear. Layer 3 (claim support) is still manual."
    else:
        verdict = "FAIL — see findings below. Gate 2 does not pass."

    lines = [
        "# Citation integrity report",
        "",
        f"- Source: `{args.bib}`  ·  {len(entries)} entries",
        f"- Network: {'DISABLED' if args.offline else ('UNAVAILABLE' if net.blocked else 'available')}",
        "- " + "  ·  ".join(f"**{k}** {v}" for k, v in sorted(counts.items())),
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    problems = [r for r in results if r["status"] != "VERIFIED" or r["mismatches"] or r["structural"]]
    if problems:
        lines += ["## Findings", ""]
        order = {"UNVERIFIED": 0, "MISMATCH": 1, "OFFLINE": 2, "VERIFIED": 3}
        for r in sorted(problems, key=lambda x: order.get(x["status"], 9)):
            e = r["entry"]
            lines.append(f"### `{e['key']}` — {r['status']}  (line {e['line']})")
            t = e["fields"].get("title", "(no title)")
            lines.append(f"*{t[:140]}*")
            if r["status"] == "UNVERIFIED":
                lines.append("- **No matching record in any database. Treat as fabricated "
                             "until the author supplies the PDF.**")
            if r["status"] == "OFFLINE":
                lines.append("- Not checked against a database (no network).")
            for m in r["mismatches"]:
                lines.append(f"- metadata: {m}")
            for s in r["structural"]:
                lines.append(f"- structure: {s}")
            if r["record"]:
                lines.append(f"- matched via {r['record']['source']}"
                             + (f", DOI `{r['record']['doi']}`" if r["record"]["doi"] else ""))
            lines.append("")

    if dups:
        lines += ["## Duplicates", ""]
        lines += [f"- `{a}` duplicates `{b}` ({why})" for a, b, why in dups] + [""]
    if unresolved:
        lines += ["## Cited but missing from the .bib", ""]
        lines += [f"- `{k}`" for k in unresolved] + [""]
    if uncited:
        lines += ["## In the .bib but never cited", "",
                  "Remove these: they are noise, and they leak what you read.", ""]
        lines += [f"- `{k}`" for k in uncited] + [""]

    lines += [
        "## Layer 3 — claim support (manual, and required)",
        "",
        "Layers 1 and 2 cannot tell you whether a source says what you claim it says.",
        "For every citation attached to a claim in the Abstract, Introduction, or a",
        "comparison: open the source, find the supporting sentence/table/figure, and",
        "record it in the ledger as `[key] -> section, table`. A citation you have not",
        "opened is not a citation.",
        "",
    ]

    report = "\n".join(lines)
    if args.report:
        os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"report written to {args.report}")
    print(report if not args.report else f"\nVerdict: {verdict}")

    if args.strict and (offline or not gate_ok):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
