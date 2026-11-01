#!/usr/bin/env python3
"""Verify every BibTeX entry against real bibliographic records.

Three layers (see references/13-citation-integrity.md):
  L1  the record exists        -- resolved against Crossref / OpenAlex / arXiv / S2 / dblp
  L2  the metadata matches     -- title, first author, year; preprint vs published
  L3  the source supports the claim  -- NOT automatable. With --tex this script
      extracts the load-bearing citations (abstract, introduction, related work)
      into a worklist; with --ledger it checks which of them have a recorded
      supporting location, and the uncovered ones block the gate.

Statuses: VERIFIED | MISMATCH | UNVERIFIED | RETRACTED | OFFLINE
Exit code is non-zero under --strict unless every entry is VERIFIED, every
preprint with a published version is upgraded, and (with --ledger) every
load-bearing citation is covered.

Network failures and "no such record" are different things. An HTTP 404 from a
reachable database is evidence that the record does not exist; a timeout is not.
Only the second kind counts toward declaring the network unavailable.

Stdlib only. Without network the script runs structural checks and reports
OFFLINE, which does NOT pass Gate 2. --replay FILE serves recorded responses
instead of the network (same format as --cache), for tests and offline re-runs.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import os
import re
import sys

import _textlib as T
from _netlib import Net, load_replay
from _netlib import q as _q
from _netlib import qp as _qp

UA = "research-pro-citation-verifier/1.1 (academic reference checking)"
ARXIV_DOI_PREFIX = "10.48550/"

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

# Sections whose citations are load-bearing by default (Layer 3 worklist).
LOAD_BEARING_SECTIONS = re.compile(
    r"abstract|introduction|related|background|prior work|literature|motivation|positioning", re.I)

CITE_MACRO = re.compile(r"\\(?:[a-zA-Z]*cite[a-zA-Z]*)\*?\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")


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


def surnames(author_field: str) -> list[str]:
    out = []
    for a in re.split(r"\s+and\s+", author_field or ""):
        a = re.sub(r"\{|\}|\\[a-zA-Z]+", "", a).strip()
        if not a:
            continue
        if "," in a:
            out.append(a.split(",")[0].strip().lower())
        else:
            parts = a.split()
            out.append(parts[-1].lower() if parts else "")
    return [s for s in out if s]


def first_surname(author_field: str) -> str:
    s = surnames(author_field)
    return s[0] if s else ""


def clean_doi(raw: str) -> str:
    d = (raw or "").strip()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d, flags=re.I)
    d = re.sub(r"^doi:\s*", "", d, flags=re.I)
    return d.rstrip(".")


def is_preprint_entry(entry: dict) -> bool:
    f = entry["fields"]
    venue = (f.get("booktitle") or f.get("journal") or f.get("howpublished") or "")
    doi = clean_doi(f.get("doi", ""))
    return bool(f.get("eprint")) or "arxiv" in venue.lower() or doi.startswith(ARXIV_DOI_PREFIX)


def entry_year(entry: dict) -> int | None:
    m = re.search(r"\d{4}", entry["fields"].get("year", "") or "")
    return int(m.group(0)) if m else None


# ---------------------------------------------------------------- resolvers
def _oa_record(work: dict) -> dict:
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
        "retracted": work.get("is_retracted"),
    }


def _s2_record(paper: dict) -> dict:
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
        "retracted": None,
    }


def _dblp_record(hit: dict) -> dict:
    info = hit.get("info") or {}
    authors = (info.get("authors") or {}).get("author") or []
    if isinstance(authors, dict):
        authors = [authors]
    surname = ""
    if authors:
        nm = authors[0].get("text", "") if isinstance(authors[0], dict) else str(authors[0])
        nm = re.sub(r"\s+\d{4}$", "", nm)  # dblp disambiguation suffixes
        surname = nm.split()[-1].lower() if nm else ""
    return {
        "source": "dblp",
        "title": (info.get("title") or "").rstrip(". "),
        "first_surname": surname,
        "year": str(info.get("year") or ""),
        "venue": info.get("venue") or "",
        "doi": clean_doi(info.get("doi") or ""),
        "type": info.get("type", ""),
        "retracted": None,
    }


def from_crossref(net: Net, doi: str) -> dict | None:
    suffix = f"?mailto={_q(net.mailto)}" if net.mailto else ""
    d = net.get(f"https://api.crossref.org/works/{_qp(doi)}{suffix}")
    if not isinstance(d, dict) or "message" not in d:
        return None
    m = d["message"]
    authors = m.get("author") or []
    date = m.get("issued", {}).get("date-parts") or [[None]]
    notice_types = {u.get("type", "").lower() for u in (m.get("update-to") or [])}
    relation_keys = {k.lower() for k in (m.get("relation") or {})}
    return {
        "source": "crossref",
        "title": (m.get("title") or [""])[0],
        "first_surname": (authors[0].get("family", "") if authors else "").lower(),
        "year": str(date[0][0]) if date and date[0] and date[0][0] else "",
        "venue": (m.get("container-title") or [""])[0],
        "doi": m.get("DOI", ""),
        "type": m.get("type", ""),
        "retracted": True if any("retract" in k for k in relation_keys) else None,
        "is_notice": bool(notice_types & {"retraction", "withdrawal", "removal"}),
    }


def openalex_by_doi(net: Net, doi: str) -> dict | None:
    d = net.get(f"https://api.openalex.org/works/doi:{_qp(doi)}")
    return _oa_record(d) if isinstance(d, dict) and ("id" in d or "title" in d) else None


def openalex_search(net: Net, title: str) -> list[dict]:
    q = _q(norm_title(title)[:250])
    d = net.get(f"https://api.openalex.org/works?filter=title.search:{q}&per-page=5")
    if not isinstance(d, dict):
        return []
    return [_oa_record(w) for w in (d.get("results") or [])]


def s2_by_id(net: Net, ident: str) -> dict | None:
    fields = "title,year,authors,venue,externalIds"
    d = net.get(f"https://api.semanticscholar.org/graph/v1/paper/{_qp(ident)}?fields={fields}")
    return _s2_record(d) if isinstance(d, dict) and "title" in d else None


def s2_search(net: Net, title: str) -> list[dict]:
    fields = "title,year,authors,venue,externalIds"
    q = _q(title[:250])
    d = net.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=5&fields={fields}")
    if not isinstance(d, dict):
        return []
    return [_s2_record(p) for p in (d.get("data") or [])]


def dblp_search(net: Net, title: str) -> list[dict]:
    q = _q(norm_title(title)[:200])
    d = net.get(f"https://dblp.org/search/publ/api?q={q}&format=json&h=5")
    if not isinstance(d, dict):
        return []
    hits = (((d.get("result") or {}).get("hits") or {}).get("hit")) or []
    return [_dblp_record(h) for h in hits]


def from_arxiv(net: Net, arxiv_id: str) -> dict | None:
    raw = net.get(f"https://export.arxiv.org/api/query?id_list={_qp(arxiv_id)}")
    if not isinstance(raw, str) or "<entry>" not in raw:
        return None

    def tag(t):
        m = re.search(rf"<{t}>(.*?)</{t}>", raw, re.S)
        return " ".join(m.group(1).split()) if m else ""

    names = re.findall(r"<name>(.*?)</name>", raw, re.S)
    surname = names[0].split()[-1].lower() if names else ""
    published = tag("published")
    doi_m = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", raw, re.S)
    pub_doi = clean_doi(doi_m.group(1)) if doi_m else ""
    return {
        "source": "arxiv",
        "title": tag("title"),
        "first_surname": surname,
        "year": published[:4] if published else "",
        "venue": "arXiv",
        "doi": pub_doi,
        "type": "preprint",
        "retracted": None,
        "published_doi": pub_doi,
    }


def pick_candidate(entry: dict, candidates: list[dict]) -> tuple[dict | None, dict | None]:
    """Choose the search hit that is actually this entry.

    A title search returns *something* for almost any string. Accepting the first
    hit is how a fabricated reference gets stamped VERIFIED. A hit is accepted
    only when the title is close AND the first author or the year agrees (a
    near-exact title alone is also enough). Returns (accepted, nearest_rejected).
    """
    f = entry["fields"]
    title = f.get("title", "")
    ours = first_surname(f.get("author", ""))
    oy = entry_year(entry)
    nearest, nearest_r = None, -1.0
    for c in candidates:
        if not c.get("title"):
            continue
        r = title_ratio(title, c["title"])
        if r > nearest_r:
            nearest, nearest_r = c, r
        if r < 0.60:
            continue
        surname_ok = bool(ours and c.get("first_surname") and ours == c["first_surname"])
        cy = re.search(r"\d{4}", c.get("year") or "")
        year_ok = bool(oy and cy and abs(int(cy.group(0)) - oy) <= 1)
        if r >= 0.95 or surname_ok or year_ok:
            return c, None
    return None, nearest


def published_version_of_preprint(net: Net, entry: dict, rec: dict) -> str:
    """Return a non-arXiv DOI when the cited preprint has a published version."""
    if rec.get("published_doi"):
        return rec["published_doi"]
    rd = rec.get("doi") or ""
    if rd and not rd.startswith(ARXIV_DOI_PREFIX):
        return rd
    arxiv_id = (entry["fields"].get("eprint") or "").strip()
    if arxiv_id and ARXIV_RE.match(arxiv_id):
        s2 = s2_by_id(net, f"arXiv:{re.sub(r'v\d+$', '', arxiv_id)}")
        if s2 and s2.get("doi") and not s2["doi"].startswith(ARXIV_DOI_PREFIX):
            return s2["doi"]
    return ""


# ---------------------------------------------------------------- checks
def structural(entry: dict, this_year: int) -> list[str]:
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
    if f.get("url") and not doi and not f.get("urldate") and not f.get("note"):
        issues.append("`url` without an access date (`urldate`)")
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
    y = entry_year(entry)
    if y is not None and (y < 1800 or y > this_year + 1):
        issues.append(f"implausible year `{y}`")
    return issues


def resolve(net: Net, entry: dict, check_retraction: bool) -> tuple[str, dict | None, list[str], dict]:
    """Return (status, record, notes, flags). flags: {"upgrade": doi, "nearest": title}."""
    f = entry["fields"]
    doi = clean_doi(f.get("doi", ""))
    arxiv_id = (f.get("eprint") or "").strip()
    title = f.get("title", "")
    failures_before = net.failures
    flags: dict = {}

    rec = None
    if doi:
        rec = from_crossref(net, doi) or openalex_by_doi(net, doi) or s2_by_id(net, f"DOI:{doi}")
    if rec is None and arxiv_id and ARXIV_RE.match(arxiv_id):
        rec = from_arxiv(net, arxiv_id)
    if rec is None and title:
        nearest = None
        for search in (openalex_search, s2_search, dblp_search):
            cands = search(net, title)
            rec, near = pick_candidate(entry, cands)
            if rec is not None:
                break
            if near is not None and nearest is None:
                nearest = near
        if rec is None and nearest is not None:
            flags["nearest"] = nearest.get("title", "")

    if rec is None:
        # A lookup that errored out is NOT evidence of a fabricated reference.
        # Only a clean "no match" from reachable databases counts as UNVERIFIED.
        if not net.enabled or net.blocked or net.failures > failures_before:
            return "OFFLINE", None, [], flags
        return "UNVERIFIED", None, [], flags

    notes = []
    r = title_ratio(title, rec["title"])
    if r < 0.60:
        notes.append(f"title mismatch (similarity {r:.2f}) — record says: \"{rec['title'][:110]}\"")
    elif r < 0.90:
        notes.append(f"title differs slightly (similarity {r:.2f}) — record says: \"{rec['title'][:110]}\"")
    ours = first_surname(f.get("author", ""))
    if ours and rec["first_surname"] and ours != rec["first_surname"]:
        notes.append(f"first author `{ours}` vs record `{rec['first_surname']}`")
    ry, oy = rec.get("year", ""), (f.get("year") or "").strip()
    if ry and oy and ry != oy:
        notes.append(f"year {oy} vs record {ry}")

    if is_preprint_entry(entry):
        pub = published_version_of_preprint(net, entry, rec)
        if pub:
            flags["upgrade"] = pub
            notes.append(f"a published version exists (DOI {pub}) — cite that, not the preprint")

    retracted = rec.get("retracted")
    if check_retraction and retracted is None and (rec.get("doi") or doi):
        oa = openalex_by_doi(net, rec.get("doi") or doi)
        if oa is not None:
            retracted = oa.get("retracted")
    if rec.get("is_notice"):
        notes.append("this DOI is a retraction/withdrawal notice, not the paper")
        retracted = True
    if retracted:
        notes.append("RETRACTED — the record is marked retracted (Retraction Watch via OpenAlex). "
                     "Cite only to discuss the retraction, and say so in the text.")
        return "RETRACTED", rec, notes, flags

    status = "MISMATCH" if any(
        n.startswith(("title mismatch", "first author", "year")) for n in notes
    ) else "VERIFIED"
    return status, rec, notes, flags


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


def expand_inputs(paths: list[str]) -> list[str]:
    """The given files plus whatever they \\input or \\include, each once, in order."""
    out: list[str] = []
    seen: set[str] = set()

    def visit(p: str, depth: int) -> None:
        ap = os.path.abspath(p)
        if ap in seen or depth > 4 or not os.path.isfile(ap):
            return
        seen.add(ap)
        out.append(p)
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                txt = T.strip_comments(fh.read())
        except OSError:
            return
        base = os.path.dirname(ap)
        for m in re.finditer(r"\\(?:input|include)\s*\{([^}]*)\}", txt):
            target = m.group(1).strip()
            for cand in (target, target + ".tex"):
                full = os.path.join(base, cand)
                if os.path.isfile(full):
                    visit(full, depth + 1)
                    break

    for p in paths:
        visit(p, 0)
    return out


def read_tex(paths: list[str]) -> list[tuple[str, str]]:
    out = []
    for p in expand_inputs(paths):
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                out.append((p, fh.read()))
        except OSError:
            continue
    return out


def cited_keys(docs: list[tuple[str, str]]) -> set[str]:
    keys: set[str] = set()
    for _p, txt in docs:
        for m in CITE_MACRO.finditer(T.strip_comments(txt)):
            for k in m.group(1).split(","):
                if k.strip() and k.strip() != "*":
                    keys.add(k.strip())
    return keys


# ---------------------------------------------------------------- in-text mechanics
# Non-blocking: these are style defects a copy-editor would mark, not integrity
# failures. They are reported because reviewers read them as carelessness.
_OPT = r"\*?\s*(?:\[[^\]]*\])*\s*\{"
MECHANICS = [
    ("after-period",
     re.compile(r"(?<!\bal)(?<!e\.g)(?<!i\.e)(?<!\bcf)(?<!\bvs)[.!?][\"')]*\s*~?\\cite(?:p)?" + _OPT),
     "citation placed after the sentence's period — move it before the period"),
    ("as-noun",
     re.compile(r"\b(?:in|by|of|from|following|unlike|than|to|with|as in)\s+~?\\cite(?:p)?" + _OPT, re.I),
     "citation used as a noun (\"in [12]\") — name the authors, or use \\citet"),
    ("as-subject",
     re.compile(r"\\cite(?:p)?" + _OPT + r"[^}]*\}\s+(?:show|shows|showed|propose|proposes|proposed|"
                r"demonstrate|demonstrates|demonstrated|introduce|introduces|introduced|report|reports|"
                r"reported|argue|argues|argued|find|finds|found|present|presents|presented|use|uses|used)\b"),
     "a parenthetical citation is the grammatical subject — use \\citet{...}"),
    ("no-tie",
     re.compile(r"[A-Za-z0-9)\]] \\cite(?:p)?" + _OPT),
     "a breakable space before \\cite — use `~\\cite` so the bracket cannot start a line"),
]


def in_text_mechanics(docs: list[tuple[str, str]]) -> dict[str, list[tuple[str, int, str]]]:
    found: dict[str, list[tuple[str, int, str]]] = {k: [] for k, _, _ in MECHANICS}
    found["stack"] = []
    for p, txt in docs:
        for i, line in enumerate(T.strip_comments(txt).split("\n"), 1):
            for m in CITE_MACRO.finditer(line):
                n = len([k for k in m.group(1).split(",") if k.strip()])
                if n >= 4:
                    found["stack"].append((p, i, f"{n} keys in one bracket: {line.strip()[:100]}"))
            for name, rx, _msg in MECHANICS:
                if rx.search(line):
                    found[name].append((p, i, line.strip()[:100]))
    return found


MECHANICS_MSG = {k: msg for k, _, msg in MECHANICS}
MECHANICS_MSG["stack"] = "four or more citations in one bracket — discuss them, or the claim is too vague to need any"


# ---------------------------------------------------------------- layer 3 worklist
def load_bearing_sentences(docs: list[tuple[str, str]], all_sections: bool = False) -> list[dict]:
    """Every sentence that carries a citation in the abstract / intro / related work.

    Returns [{"section", "keys", "sentence", "file"}], de-duplicated. These are the
    citations that a reviewer checks first, and the ones Layer 3 must cover.
    """
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def harvest(section: str, body: str, path: str) -> None:
        marked = CITE_MACRO.sub(lambda m: " CITEMARK(" + ",".join(
            k.strip() for k in m.group(1).split(",") if k.strip()) + ") ", body)
        prose = T.to_prose(marked)
        for s in T.sentences(prose):
            keys = [k for grp in re.findall(r"CITEMARK\(([^)]*)\)", s) for k in grp.split(",") if k]
            if not keys:
                continue
            clean = re.sub(r"\s*CITEMARK\(([^)]*)\)", lambda m: " [" + m.group(1) + "]", s)
            clean = re.sub(r"\s+([.,;:])", r"\1", " ".join(clean.split()))
            sig = (",".join(sorted(set(keys))), norm_title(clean)[:120])
            if sig in seen:
                continue
            seen.add(sig)
            rows.append({"section": section, "keys": sorted(set(keys)),
                         "sentence": clean, "file": os.path.basename(path)})

    for path, txt in docs:
        raw = T.strip_comments(txt)
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, re.S)
        if m:
            harvest("abstract", m.group(1), path)
        current, bearing = "front matter", all_sections
        secs = T.split_sections(raw)
        if not secs and all_sections:
            harvest("document", raw, path)
        for lvl, title, body in secs:
            if lvl in ("section", "chapter"):
                current = title
                bearing = all_sections or bool(LOAD_BEARING_SECTIONS.search(title))
            if bearing:
                harvest(current, body, path)
    return rows


def ledger_layer3(path: str) -> dict[str, str]:
    """Parse the 'Citation layer-3 log' table of LEDGER.md -> {key: location}."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return {}
    m = re.search(r"^#+\s*.*(?:layer[- ]?3|claim support).*$", text, re.I | re.M)
    if not m:
        return {}
    block = text[m.end():]
    nxt = re.search(r"^#+\s", block, re.M)
    if nxt:
        block = block[: nxt.start()]
    covered: dict[str, str] = {}
    for line in block.split("\n"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in ("key", "---", "") or set(cells[0]) <= {"-", ":"}:
            continue
        key = cells[0].strip("`")
        where = cells[2]
        if where and where not in ("—", "-", "?", "[TBD]"):
            covered[key] = where
    return covered


# ---------------------------------------------------------------- profiles
def year_profile(entries: list[dict], this_year: int) -> dict:
    years = [y for y in (entry_year(e) for e in entries) if y]
    if not years:
        return {}
    recent = sum(1 for y in years if y >= this_year - 2)
    return {
        "n": len(years),
        "oldest": min(years),
        "newest": max(years),
        "median": sorted(years)[len(years) // 2],
        "recent_pct": round(100 * recent / len(years), 1),
    }


def self_citation_rate(entries: list[dict], authors: list[str]) -> tuple[int, list[str]]:
    mine = {a.strip().lower() for a in authors if a.strip()}
    hits = [e["key"] for e in entries if mine & set(surnames(e["fields"].get("author", "")))]
    return len(hits), hits


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib", help="path to refs.bib")
    ap.add_argument("--report", help="write a markdown report here")
    ap.add_argument("--offline", action="store_true", help="skip all network lookups")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="non-zero exit unless the gate passes (default)")
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    ap.add_argument("--mailto", default=os.environ.get("CROSSREF_MAILTO", ""),
                    help="contact email for the Crossref polite pool")
    ap.add_argument("--tex", nargs="*", default=[],
                    help="tex files: uncited entries, unresolved keys, in-text mechanics, Layer-3 worklist")
    ap.add_argument("--ledger", help="LEDGER.md whose 'Citation layer-3 log' table records claim support")
    ap.add_argument("--all-sections", action="store_true",
                    help="treat every cited sentence as load-bearing, not only abstract/intro/related")
    ap.add_argument("--authors", default="",
                    help="comma-separated surnames of the manuscript's authors, for the self-citation rate")
    ap.add_argument("--cache", help="JSON file to cache API responses across runs")
    ap.add_argument("--replay", help="JSON file of recorded responses; never touches the network")
    ap.add_argument("--no-retraction-check", dest="retraction", action="store_false", default=True,
                    help="skip the per-DOI retraction lookup")
    ap.add_argument("--verbose", "-v", action="store_true", help="log every lookup to stderr")
    args = ap.parse_args(argv)

    why = T.sniff_binary(args.bib)
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

    try:
        replay = load_replay(args.replay)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    this_year = _dt.date.today().year
    net = Net(UA, enabled=not args.offline, mailto=args.mailto, cache_path=args.cache,
              replay=replay, verbose=args.verbose)
    results = []
    for e in entries:
        struct = structural(e, this_year)
        status, rec, notes, flags = resolve(net, e, args.retraction)
        results.append({"entry": e, "status": status, "record": rec,
                        "notes": notes, "structural": struct, "flags": flags})
    net.save()

    dups = find_duplicates(entries)
    keys = {e["key"] for e in entries}
    docs = read_tex(args.tex) if args.tex else []
    cited = cited_keys(docs) if docs else set()
    uncited = sorted(keys - cited) if cited else []
    unresolved = sorted(cited - keys) if cited else []
    mech = in_text_mechanics(docs) if docs else {}
    worklist = load_bearing_sentences(docs, args.all_sections) if docs else []
    covered = ledger_layer3(args.ledger) if args.ledger else {}
    bearing_keys = sorted({k for row in worklist for k in row["keys"]})
    uncovered = [k for k in bearing_keys if k not in covered] if args.ledger else []
    ledger_unknown = sorted(k for k in covered if k not in keys) if args.ledger else []

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    upgrades = [r for r in results if r["flags"].get("upgrade")]

    offline = net.blocked or args.offline
    layer3_checked = bool(args.ledger and docs)
    gate_ok = (
        counts.get("VERIFIED", 0) == len(results)
        and not dups
        and not unresolved
        and not upgrades
        and not any(r["structural"] for r in results)
        and not uncovered
    )
    if offline:
        verdict = "BLOCKED: network unavailable — structural checks only. Gate 2 CANNOT pass."
    elif gate_ok and layer3_checked:
        verdict = "PASS — layers 1 and 2 clear; every load-bearing citation has a ledger location (layer 3)."
    elif gate_ok:
        verdict = ("PASS on layers 1 and 2. Layer 3 (claim support) was not checked — pass "
                   "--ledger paper/LEDGER.md once the worklist below is logged.")
    else:
        verdict = "FAIL — see findings below. Gate 2 does not pass."

    net_state = net.state
    lines = [
        "# Citation integrity report",
        "",
        f"- Source: `{args.bib}`  ·  {len(entries)} entries",
        f"- Network: {net_state}",
        "- " + "  ·  ".join(f"**{k}** {v}" for k, v in sorted(counts.items())),
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    problems = [r for r in results if r["status"] != "VERIFIED" or r["notes"] or r["structural"]]
    if problems:
        lines += ["## Findings", ""]
        order = {"RETRACTED": 0, "UNVERIFIED": 1, "MISMATCH": 2, "OFFLINE": 3, "VERIFIED": 4}
        for r in sorted(problems, key=lambda x: order.get(x["status"], 9)):
            e = r["entry"]
            lines.append(f"### `{e['key']}` — {r['status']}  (line {e['line']})")
            t = e["fields"].get("title", "(no title)")
            lines.append(f"*{t[:140]}*")
            if r["status"] == "UNVERIFIED":
                lines.append("- **No matching record in any database. Treat as fabricated "
                             "until the author supplies the PDF.**")
                if r["flags"].get("nearest"):
                    lines.append(f"- nearest title found, rejected (author/year disagree): "
                                 f"\"{r['flags']['nearest'][:110]}\"")
            if r["status"] == "OFFLINE":
                lines.append("- Not checked against a database (no network).")
            for n in r["notes"]:
                lines.append(f"- metadata: {n}")
            for s in r["structural"]:
                lines.append(f"- structure: {s}")
            if r["record"]:
                lines.append(f"- matched via {r['record']['source']}"
                             + (f", DOI `{r['record']['doi']}`" if r["record"].get("doi") else ""))
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

    if docs:
        total_mech = sum(len(v) for v in mech.values())
        lines += ["## In-text mechanics (non-blocking)", ""]
        if not total_mech:
            lines.append("No mechanical defects found in the cited sentences.")
        for name, hits in mech.items():
            if not hits:
                continue
            lines.append(f"- **{name}** × {len(hits)} — {MECHANICS_MSG[name]}")
            for p, i, txt in hits[:4]:
                lines.append(f"    - `{os.path.basename(p)}:{i}` {txt}")
            if len(hits) > 4:
                lines.append(f"    - … and {len(hits) - 4} more")
        lines.append("")

    lines += ["## Layer 3 — claim support (manual, and required)", ""]
    if docs:
        scope = "every cited sentence" if args.all_sections else "abstract, introduction, related work"
        lines += [f"Load-bearing citations ({scope}): {len(bearing_keys)} key(s) in "
                  f"{len(worklist)} sentence(s). For each row open the source, find the",
                  "sentence/table/figure that supports the claim, and record it in the ledger's",
                  "`Citation layer-3 log` as `| key | claim | where |`.", ""]
        if args.ledger:
            lines.append(f"Ledger `{args.ledger}`: {len(covered)} key(s) logged, "
                         f"**{len(uncovered)} load-bearing key(s) uncovered**"
                         + (f": {', '.join('`' + k + '`' for k in uncovered[:20])}" if uncovered else "") + ".")
            if ledger_unknown:
                lines.append(f"Logged keys not in the .bib: {', '.join('`' + k + '`' for k in ledger_unknown)}.")
            lines.append("")
        if worklist:
            lines += ["| Section | Keys | Sentence | Ledger |", "|---|---|---|---|"]
            for row in worklist[:200]:
                ok = "✓" if args.ledger and all(k in covered for k in row["keys"]) else (
                    "**open**" if args.ledger else "")
                lines.append(f"| {row['section'][:28]} | {', '.join('`' + k + '`' for k in row['keys'])} | "
                             f"{row['sentence'][:160].replace('|', '/')} | {ok} |")
            if len(worklist) > 200:
                lines.append(f"| … | | {len(worklist) - 200} more | |")
            lines.append("")
    else:
        lines += ["Layers 1 and 2 cannot tell you whether a source says what you claim it says.",
                  "Pass `--tex main.tex sections/*.tex` to extract the load-bearing citations",
                  "into a worklist, and `--ledger LEDGER.md` to check which are already logged.",
                  "A citation you have not opened is not a citation.", ""]

    yp = year_profile(entries, this_year)
    lines += ["## Profile", ""]
    if yp:
        lines.append(f"- Years: {yp['oldest']}–{yp['newest']}, median {yp['median']}; "
                     f"{yp['recent_pct']}% from the last three years"
                     + (" — low for a fast-moving area; check the last two cycles of the target venue."
                        if yp["recent_pct"] < 20 else "."))
    if args.authors:
        n_self, self_keys = self_citation_rate(entries, args.authors.split(","))
        pct = round(100 * n_self / len(entries), 1)
        lines.append(f"- Self-citations: {n_self}/{len(entries)} ({pct}%)"
                     + (" — above 20% reads as padding; keep only the ones the argument needs."
                        if pct > 20 else "."))
    if upgrades:
        lines.append(f"- Preprints with a published version: {len(upgrades)} — "
                     + ", ".join("`" + r["entry"]["key"] + "`" for r in upgrades[:10]))
    lines.append("")

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
