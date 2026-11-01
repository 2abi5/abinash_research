#!/usr/bin/env python3
"""Expand seed papers into a ranked candidate list for a scoping scan (stage S2).

Give it the two to five papers closest to your idea. It pulls, from OpenAlex:

  backward   every work each seed cites            (the field the seeds stand on)
  forward    every work that cites each seed       (what came after -- including
                                                    the paper that scooped you)
  search     optional keyword search, recorded verbatim with date and hit count

and ranks the union by how many seeds each candidate is connected to, then by
citations. A paper connected to three of your four seeds is almost certainly one
you must read; a paper connected to one seed with four citations usually is not.

It also reports the two numbers the methodology asks for and nobody computes:

  saturation   how many *new* candidates each successive seed added -- the stop
               rule is "stop when a new seed adds nothing you had not seen"
  recall       with --sentinels, whether known-relevant papers were reached at all;
               a sentinel your seeds do not reach means the seeds are wrong

Outputs (in --out, default lit/):
  candidates.md   the ranked table, search record, saturation and recall
  scan.json       everything, for --from-json re-ranking offline
  map.md          the S2 map skeleton (Mechanism / Assumption / Fails when /
                  Baseline?) pre-filled with the top candidates. Never overwritten.

This produces *leads*, not a reference list. Every candidate must still be opened
and read at the depth its role requires (references/03-literature-review.md), and
every one that is cited must pass verify_citations.py.

OpenAlex needs no key. Pass --mailto for the polite pool. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

from _netlib import NOT_FOUND, Net, load_replay
from _netlib import q as _q
from _netlib import qp as _qp

UA = "research-pro-lit-scan/1.0 (literature scoping; academic use)"
OA = "https://api.openalex.org"
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,referenced_works,"
          "authorships,primary_location,open_access,type,is_retracted")
PER_PAGE = 100
ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5})(v\d+)?$", re.I)
DOI_RE = re.compile(r"10\.\d{4,9}/\S+")


# ---------------------------------------------------------------- identifiers
def classify(seed: str) -> tuple[str, str]:
    """('openalex', 'W…') | ('doi', '10.…') | ('title', text)."""
    s = seed.strip()
    m = re.search(r"(W\d{6,})\b", s)
    if s.upper().startswith("W") and m or "openalex.org/W" in s:
        return "openalex", m.group(1)
    m = ARXIV_RE.match(s)
    if m:
        return "doi", f"10.48550/arXiv.{m.group(1)}"
    m = DOI_RE.search(s)
    if m:
        return "doi", m.group(0).rstrip(".),")
    return "title", s


def short_id(openalex_url: str) -> str:
    return (openalex_url or "").rsplit("/", 1)[-1]


def clean_doi(d: str) -> str:
    d = (d or "").strip()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d, flags=re.I)
    return d.lower()


def compact(work: dict) -> dict:
    auths = work.get("authorships") or []
    first = ""
    if auths:
        first = ((auths[0].get("author") or {}).get("display_name") or "")
    src = (work.get("primary_location") or {}).get("source") or {}
    oa = work.get("open_access") or {}
    return {
        "id": short_id(work.get("id", "")),
        "doi": clean_doi(work.get("doi") or ""),
        "title": work.get("title") or work.get("display_name") or "(untitled)",
        "year": work.get("publication_year"),
        "venue": src.get("display_name") or "",
        "cited_by": work.get("cited_by_count") or 0,
        "first_author": first,
        "n_authors": len(auths),
        "type": work.get("type") or "",
        "oa_url": oa.get("oa_url") or "",
        "retracted": bool(work.get("is_retracted")),
        "referenced_works": [short_id(w) for w in (work.get("referenced_works") or [])],
    }


# ---------------------------------------------------------------- OpenAlex
class OpenAlex:
    def __init__(self, net: Net):
        self.net = net
        self.batch_filter_ok: bool | None = None  # unknown until first try

    def _url(self, path: str, **params) -> str:
        if self.net.mailto:
            params["mailto"] = self.net.mailto
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v not in (None, ""))
        return f"{OA}{path}" + (f"?{qs}" if qs else "")

    def work(self, ident: str) -> dict | None:
        d = self.net.get(self._url(f"/works/{_qp(ident)}"))
        return compact(d) if isinstance(d, dict) and d.get("id") else None

    def by_title(self, title: str) -> dict | None:
        d = self.net.get(self._url("/works", filter=f"title.search:{_q(title[:250])}",
                                   **{"per-page": 1}, select=SELECT))
        if isinstance(d, dict) and d.get("results"):
            return compact(d["results"][0])
        return None

    def many(self, ids: list[str]) -> dict[str, dict]:
        """Fetch many works by OpenAlex id, batched by 50 when the API allows, one by one otherwise."""
        out: dict[str, dict] = {}
        ids = [i for i in dict.fromkeys(ids) if i]
        i = 0
        while i < len(ids):
            chunk = ids[i:i + 50]
            got = None
            if self.batch_filter_ok is not False:
                d = self.net.get(self._url("/works", filter="ids.openalex:" + "|".join(chunk),
                                           **{"per-page": 50}, select=SELECT))
                if isinstance(d, dict) and isinstance(d.get("results"), list):
                    self.batch_filter_ok = True
                    got = {compact(w)["id"]: compact(w) for w in d["results"]}
                elif self.batch_filter_ok is None:
                    # The filter spelling was refused: not a network failure. Fall back to one-by-one.
                    self.batch_filter_ok = False
                    if d is None:
                        self.net.forgive_one_failure()
            if got is None:
                got = {}
                for wid in chunk:
                    if self.net.offline:
                        break
                    w = self.work(wid)
                    if w:
                        got[w["id"]] = w
            out.update(got)
            i += 50
        return out

    def citing(self, wid: str, limit: int, since: int | None) -> tuple[list[dict], int]:
        """Works that cite `wid`, most-cited first. Returns (works, total_count)."""
        flt = f"cites:{wid}" + (f",publication_year:>{since - 1}" if since else "")
        cursor, out, total = "*", [], 0
        while cursor and len(out) < limit:
            d = self.net.get(self._url("/works", filter=flt, sort="cited_by_count:desc",
                                       **{"per-page": min(PER_PAGE, limit - len(out))},
                                       cursor=cursor, select=SELECT))
            if not isinstance(d, dict):
                break
            total = (d.get("meta") or {}).get("count", total) or total
            out += [compact(w) for w in d.get("results") or []]
            cursor = (d.get("meta") or {}).get("next_cursor")
        return out[:limit], total

    def search(self, query: str, limit: int, since: int | None,
               types: str) -> tuple[list[dict], int]:
        flt = ",".join(x for x in [f"from_publication_date:{since}-01-01" if since else "",
                                   f"type:{types}" if types else ""] if x)
        cursor, out, total = "*", [], 0
        while cursor and len(out) < limit:
            d = self.net.get(self._url("/works", search=_q(query), filter=flt or None,
                                       sort="relevance_score:desc",
                                       **{"per-page": min(PER_PAGE, limit - len(out))},
                                       cursor=cursor, select=SELECT))
            if not isinstance(d, dict):
                break
            total = (d.get("meta") or {}).get("count", total) or total
            out += [compact(w) for w in d.get("results") or []]
            cursor = (d.get("meta") or {}).get("next_cursor")
        return out[:limit], total


def resolve_seed(oa: OpenAlex, seed: str) -> tuple[dict | None, str]:
    kind, val = classify(seed)
    if kind == "openalex":
        return oa.work(val), kind
    if kind == "doi":
        return oa.work(f"doi:{val}"), kind
    return oa.by_title(val), kind


# ---------------------------------------------------------------- ranking
def rank(works: dict[str, dict], edges: list[dict], seed_ids: list[str]) -> list[dict]:
    """Candidates ordered by seed connections, then `both`, then citations, then recency.

    No year filter here: --since is applied when fetching forward citations and search
    results. A seed's own references are kept whatever their age, because a 2015 paper
    cited by all four seeds is the foundation the gap statement must acknowledge.
    """
    links: dict[str, set] = {}
    dirs: dict[str, set] = {}
    for e in edges:
        links.setdefault(e["work"], set()).add(e["seed"])
        dirs.setdefault(e["work"], set()).add(e["direction"])
    rows = []
    for wid, w in works.items():
        if wid in seed_ids:
            continue
        d = dirs.get(wid, set())
        direction = "both" if {"backward", "forward"} <= d else (
            "cites seed" if "forward" in d else ("cited by seed" if "backward" in d else "search"))
        rows.append({**w, "links": len(links.get(wid, ())), "direction": direction})
    rows.sort(key=lambda r: (-r["links"], -(r["direction"] == "both"), -r["cited_by"],
                             -(r["year"] or 0)))
    return rows


def saturation(order: list[str], edges: list[dict]) -> list[tuple[str, int, int, int]]:
    """Per seed, in order: (seed, backward, forward, new-to-the-set)."""
    seen: set[str] = set()
    out = []
    for sid in order:
        mine = [e for e in edges if e["seed"] == sid]
        back = sum(1 for e in mine if e["direction"] == "backward")
        fwd = sum(1 for e in mine if e["direction"] == "forward")
        new = {e["work"] for e in mine} - seen
        seen |= {e["work"] for e in mine}
        out.append((sid, back, fwd, len(new)))
    return out


def sentinel_recall(sentinels: list[str], works: dict[str, dict]) -> tuple[list[str], list[str]]:
    dois = {w["doi"] for w in works.values() if w.get("doi")}
    ids = set(works)
    found, missing = [], []
    for s in sentinels:
        kind, val = classify(s)
        hit = (kind == "openalex" and val in ids) or (kind == "doi" and val.lower() in dois)
        (found if hit else missing).append(s)
    return found, missing


# ---------------------------------------------------------------- output
def md_escape(s: str) -> str:
    return (s or "").replace("|", "/").replace("\n", " ")


def write_candidates(path: str, dump: dict, rows: list[dict], sat, recall, max_rows: int) -> None:
    today = dump["generated"]
    L = [f"# Literature scan — {today}", ""]
    L += ["## Seeds", ""]
    for s in dump["seeds"]:
        L.append(f"- `{s['id']}` {s['first_author']} {s['year']} — *{md_escape(s['title'])[:100]}* "
                 f"({s['venue'] or s['type']}; cited by {s['cited_by']})")
    L += ["", "## Search record", "", "| DB | String / filter | Date run | Hits |", "|---|---|---|---|"]
    for r in dump["search_record"]:
        L.append(f"| {r['db']} | `{md_escape(r['query'])}` | {r['date']} | {r['hits']} |")
    L += ["", "## Saturation (stop rule)", "",
          "| Seed | Backward refs | Forward cites fetched | New candidates added |",
          "|---|---|---|---|"]
    for sid, back, fwd, new in sat:
        L.append(f"| `{sid}` | {back} | {fwd} | **{new}** |")
    L += ["", "Stop adding seeds when a new seed adds nothing you had not already seen. "
          "If the last row is still large, the scan has not converged.", ""]
    if recall is not None:
        found, missing = recall
        n = len(found) + len(missing)
        L += ["## Sentinel recall", "",
              f"{len(found)}/{n} known-relevant papers reached by the seeds."]
        if missing:
            L.append("Not reached (add as a seed, or your seeds sit in the wrong neighbourhood): "
                     + ", ".join(f"`{m}`" for m in missing))
        L.append("")
    L += [f"## Candidates — top {min(max_rows, len(rows))} of {len(rows)}", "",
          "Ranked by seed connections, then citations. `both` = cites a seed *and* is cited by one.", "",
          "| # | Links | Relation | Year | Cited by | First author | Title | Venue | ID |",
          "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:max_rows], 1):
        ident = f"doi:{r['doi']}" if r["doi"] else r["id"]
        flag = " ⚠ RETRACTED" if r.get("retracted") else ""
        L.append(f"| {i} | {r['links']} | {r['direction']} | {r['year'] or '?'} | {r['cited_by']} | "
                 f"{md_escape(r['first_author'])} | {md_escape(r['title'])[:90]}{flag} | "
                 f"{md_escape(r['venue'])[:40]} | `{ident}` |")
    L += ["", "Every row is a lead. Open it; decide WHY / HOW / WHAT depth; fill `map.md`.", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def write_map(path: str, rows: list[dict], top: int) -> bool:
    if os.path.exists(path):
        return False
    L = ["# Literature map", "",
         "One row per paper you actually read. `Fails when` is the column the gap statement is",
         "written from; `Baseline?` becomes the main results table. Depth: WHY (read fully),",
         "HOW (method + protocol), WHAT (abstract, figures, conclusion).", "",
         "| Paper | Year | Venue | Depth | Mechanism | Assumption it needs | Fails when | Baseline? | Verified (key) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows[:top]:
        who = (r["first_author"].split()[-1] if r["first_author"] else "?") + ("+" if r["n_authors"] > 1 else "")
        L.append(f"| {who} — {md_escape(r['title'])[:60]} | {r['year'] or '?'} | {md_escape(r['venue'])[:30]} "
                 f"| | | | | | `[NEEDS SOURCE]` |")
    L += ["", "Add rows found by snowballing by hand. Replace `[NEEDS SOURCE]` with the .bib key once",
          "`verify_citations.py` has resolved the entry.", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return True


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", action="append", default=[],
                    help="DOI, arXiv id, OpenAlex W-id, or a title (repeatable; 2–5 is right)")
    ap.add_argument("--search", action="append", default=[],
                    help="keyword query, repeatable; recorded verbatim with date and hit count")
    ap.add_argument("--since", type=int,
                    help="forward citations and search results published before this year are ignored; "
                         "the seeds' own references are always kept")
    ap.add_argument("--max", type=int, default=60, help="rows in candidates.md (default 60)")
    ap.add_argument("--forward-max", type=int, default=200, help="citing works fetched per seed")
    ap.add_argument("--search-max", type=int, default=100, help="results fetched per search query")
    ap.add_argument("--types", default="article|preprint", help="OpenAlex work types for --search")
    ap.add_argument("--sentinels", default="", help="comma-separated DOIs/W-ids that MUST be reached")
    ap.add_argument("--map-top", type=int, default=25, help="rows pre-filled in map.md")
    ap.add_argument("--out", default="lit", help="output directory (default lit/)")
    ap.add_argument("--from-json", help="re-rank a previous scan.json offline; no network")
    ap.add_argument("--mailto", default=os.environ.get("OPENALEX_MAILTO", ""))
    ap.add_argument("--cache", help="JSON cache of API responses")
    ap.add_argument("--replay", help="recorded responses; never touches the network")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    today = _dt.date.today().isoformat()
    sentinels = [s.strip() for s in args.sentinels.split(",") if s.strip()]

    if args.from_json:
        try:
            with open(args.from_json, encoding="utf-8") as fh:
                dump = json.load(fh)
            works, edges = dump["works"], dump["edges"]
            seed_ids = [s["id"] for s in dump["seeds"]]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            print(f"error: cannot read scan dump {args.from_json}: {exc}", file=sys.stderr)
            return 2
        net = None
    else:
        if not args.seed and not args.search:
            ap.error("give at least one --seed or --search (or --from-json)")
        try:
            replay = load_replay(args.replay)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        net = Net(UA, mailto=args.mailto, cache_path=args.cache, replay=replay, verbose=args.verbose)
        oa = OpenAlex(net)
        dump = {"generated": today, "seeds": [], "works": {}, "edges": [], "search_record": [],
                "args": {"since": args.since, "seeds": args.seed, "search": args.search}}
        works: dict[str, dict] = dump["works"]
        edges: list[dict] = dump["edges"]
        seed_ids: list[str] = []

        lookup_errors = 0
        for s in args.seed:
            failures_before = net.failures
            w, kind = resolve_seed(oa, s)
            if net.offline:
                break
            if w is None:
                if net.failures > failures_before:
                    lookup_errors += 1
                    print(f"  could not reach OpenAlex for seed: {s}", file=sys.stderr)
                else:
                    print(f"  seed not found in OpenAlex (clean 404): {s}", file=sys.stderr)
                continue
            if kind == "title":
                print(f"  seed resolved by title search — confirm it is the right paper: "
                      f"{w['first_author']} {w['year']} \"{w['title'][:70]}\"", file=sys.stderr)
            dump["seeds"].append(w)
            seed_ids.append(w["id"])
            works[w["id"]] = w
            print(f"  seed {w['id']}: {w['first_author']} {w['year']} — {w['title'][:70]}", file=sys.stderr)

            back = oa.many(w["referenced_works"])
            for wid, bw in back.items():
                works.setdefault(wid, bw)
                edges.append({"seed": w["id"], "work": wid, "direction": "backward"})
            fwd, total = oa.citing(w["id"], args.forward_max, args.since)
            for fw in fwd:
                works.setdefault(fw["id"], fw)
                edges.append({"seed": w["id"], "work": fw["id"], "direction": "forward"})
            dump["search_record"].append({"db": "OpenAlex", "query": f"cites:{w['id']}"
                                          + (f" since {args.since}" if args.since else ""),
                                          "date": today, "hits": total})
            print(f"    {len(back)} backward · {len(fwd)}/{total} forward", file=sys.stderr)

        for qtext in args.search:
            if net.offline:
                break
            res, total = oa.search(qtext, args.search_max, args.since, args.types)
            for r in res:
                works.setdefault(r["id"], r)
            dump["search_record"].append({"db": "OpenAlex", "query": f"search={qtext!r}"
                                          + (f" since {args.since}" if args.since else "")
                                          + (f" type:{args.types}" if args.types else ""),
                                          "date": today, "hits": total})
            print(f"  search {qtext!r}: {len(res)}/{total}", file=sys.stderr)

        net.save()
        if net.offline or (not seed_ids and lookup_errors):
            print("BLOCKED: OpenAlex is unreachable (api.openalex.org). Nothing was scanned.\n"
                  "Do the expansion by hand — seeds' reference lists backward, 'cited by' forward —\n"
                  "and record each query, date, and hit count in the search record.", file=sys.stderr)
            return 1
        if not seed_ids and not args.search:
            print("error: no seed could be resolved.", file=sys.stderr)
            return 1

    rows = rank(works, edges, seed_ids)
    sat = saturation(seed_ids, edges)
    recall = sentinel_recall(sentinels, works) if sentinels else None

    os.makedirs(args.out, exist_ok=True)
    cand = os.path.join(args.out, "candidates.md")
    write_candidates(cand, dump, rows, sat, recall, args.max)
    if not args.from_json:
        with open(os.path.join(args.out, "scan.json"), "w", encoding="utf-8") as fh:
            json.dump(dump, fh, indent=1)
    wrote_map = write_map(os.path.join(args.out, "map.md"), rows, args.map_top)

    print(f"# Literature scan — {len(dump['seeds'])} seed(s), {len(rows)} candidates")
    print(f"- network: {net.state if net else 'from-json (offline re-rank)'}")
    print("- saturation: " + "; ".join(f"{sid} +{new}" for sid, _b, _f, new in sat))
    if recall is not None:
        print(f"- sentinel recall: {len(recall[0])}/{len(recall[0]) + len(recall[1])}"
              + (f" — missing {', '.join(recall[1])}" if recall[1] else ""))
    multi = sum(1 for r in rows if r["links"] >= 2)
    retracted = [r for r in rows if r.get("retracted")]
    print(f"- {multi} candidate(s) connected to two or more seeds — read these first")
    if retracted:
        print(f"- {len(retracted)} candidate(s) are RETRACTED — cite only to discuss the retraction")
    print(f"- wrote {cand}" + (f", {os.path.join(args.out, 'scan.json')}" if not args.from_json else "")
          + (f", {os.path.join(args.out, 'map.md')}" if wrote_map else " (map.md kept — fill it by hand)"))
    for i, r in enumerate(rows[:10], 1):
        print(f"  {i:>2}. [{r['links']}] {r['year'] or '?'} {r['first_author'][:18]:18} {r['title'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
