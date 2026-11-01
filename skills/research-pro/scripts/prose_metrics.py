#!/usr/bin/env python3
"""Measure the machine-register tells described in references/12-prose-quality.md.

Blocking checks (FAIL under --strict): banned phrases and words, sentence-length
variance, a short sentence per paragraph, transition-opener density, hedge
stacking, empty topic sentences.

Advisory checks (WARN, never change the exit code): em-dash density, contrastive
negation ("not X, but Y"), repeated sentence openers, uniform paragraph length,
section-closing summaries, roadmap sentences, rhetorical questions, choppiness
(the over-corrected register), and over-used words by rate.

Modes:
  prose_metrics.py main.tex                 the report
  prose_metrics.py main.tex --paragraphs    one row per paragraph, for the rewrite loop
  prose_metrics.py new.tex --compare old.tex  metric deltas between two versions
  prose_metrics.py main.tex --section intro   only sections whose title matches

This finds patterns. It cannot find emptiness -- for every paragraph still ask
"what does the reader now know that they did not before?"

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys

import _textlib as T

BANNED_PHRASES = [
    "it is important to note", "it is worth noting", "it's worth noting", "it should be noted",
    "it should be emphasized", "it is crucial to", "one must consider",
    "plays a crucial role", "plays a vital role", "plays a key role",
    "plays a significant role", "plays a pivotal role", "serves as a", "stands as a",
    "sheds light on", "shed light on", "paves the way", "pave the way", "opens new avenues",
    "opens the door", "in the realm of", "in the context of today", "when it comes to",
    "in today's rapidly evolving", "in an era of", "in the ever-evolving", "in the digital age",
    "in recent years, there has been growing interest",
    "in recent years, there has been increasing interest",
    "with the advent of", "the advent of", "with the rapid development", "rapid advancement",
    "has garnered significant attention", "has garnered", "has gained traction", "has emerged as a",
    "a testament to", "a wide range of", "a variety of", "a plethora of",
    "a myriad of", "a host of", "delve into", "delves into", "delving into",
    "at the forefront of", "cutting-edge", "state-of-the-art approach",
    "it is well known that", "as we all know", "needless to say",
    "the landscape of", "navigate the complexities", "unlock the potential",
    "harness the power", "usher in", "revolutionize", "game-changer", "paradigm shift",
    "first and foremost", "last but not least", "in essence", "at its core",
    "sets the stage", "lays the groundwork", "a step forward", "a significant step",
    "aligns with", "resonates with", "stands out as", "double-edged sword",
    "to address this gap", "to bridge this gap", "bridge the gap", "fill this gap",
    "promising avenue", "promising direction", "fertile ground",
]

BANNED_WORDS = [
    "leverage", "leverages", "leveraging", "leveraged", "utilize", "utilizes",
    "utilizing", "utilized", "utilization", "underscore", "underscores",
    "underscoring", "pivotal", "crucial", "crucially", "vital", "paramount", "realm",
    "tapestry", "symphony", "cornerstone", "myriad", "plethora", "holistic",
    "seamless", "seamlessly", "comprehensive", "intricate", "meticulous",
    "meticulously", "nuanced", "multifaceted", "robustly", "foster", "fostering",
    "elevate", "elevating", "showcase", "showcases", "showcasing",
    "groundbreaking", "novel", "innovative", "cutting", "transformative",
    "unparalleled", "unprecedented", "streamline", "streamlined", "streamlining",
    "garner", "garnered", "embark", "beacon", "testament", "synergy", "synergistic",
    "landscape", "revolutionary", "remarkable", "remarkably",
]

# Counted per 1000 words. Not banned -- each is a normal word -- but a rate above the
# threshold is the signature of prose that reaches for the same soft verb every time.
OVERUSED = {
    "enhance": 2.0, "enhances": 2.0, "enhanced": 2.0, "enhancing": 2.0,
    "ensure": 2.0, "ensures": 2.0, "ensuring": 2.0,
    "various": 2.0, "numerous": 1.5, "effectively": 1.5, "efficiently": 1.5,
    "significantly": 2.5, "greatly": 1.0, "truly": 0.5, "highly": 2.0, "extremely": 1.0,
    "in order to": 1.5, "aims to": 1.5, "serves to": 1.0, "allows us to": 1.5,
    "overall": 1.5, "ultimately": 1.0, "specifically": 2.5, "particularly": 2.5,
}

HEDGES = ["may", "might", "could", "can potentially", "possibly", "perhaps",
          "somewhat", "relatively", "arguably", "appears to", "seems to",
          "suggests that", "tends to", "in some cases", "to some extent",
          "generally", "typically", "often", "potentially", "likely",
          "it is possible that", "we believe", "we think"]

TRANSITION_OPENERS = ["moreover", "furthermore", "additionally", "consequently",
                      "therefore", "thus", "hence", "however", "nevertheless",
                      "nonetheless", "in addition", "on the other hand",
                      "in contrast", "similarly", "likewise", "overall",
                      "in summary", "notably", "importantly", "specifically",
                      "indeed", "accordingly", "subsequently", "while",
                      "although", "despite", "crucially", "interestingly"]

EMPTY_TOPIC = [r"^in this (section|subsection|chapter)",
               r"^this (section|subsection|chapter) (describes|presents|discusses|introduces|provides|outlines)",
               r"^we (now|first|next|then) (describe|present|discuss|introduce)",
               r"^(first|second|third|finally),? we (describe|present|discuss)",
               r"^there (are|is) (several|many|a number of)",
               r"^it is (well[- ])?(known|established) that"]

CLOSING_SUMMARY = re.compile(
    r"^(?:in summary|to summarize|to summarise|overall|taken together|in conclusion|in short|"
    r"to sum up|altogether|to conclude|this section (?:has )?(?:described|presented|showed|introduced))\b", re.I)
ROADMAP = re.compile(
    r"^(?:in this (?:section|paper|work|article),? we (?:will )?(?:first|describe|present|introduce|propose|outline))"
    r"|(?:\bfirst\b.{3,80}\bthen\b.{3,80}\bfinally\b)", re.I)
CONTRASTIVE = [
    re.compile(r"\bnot\s+(?:just|merely|only|simply)\b", re.I),
    re.compile(r"\bnot\b[^.;:!?]{1,60}?,\s*but\b", re.I),
    re.compile(r"\b(?:is|are|was|were|it's|isn't|aren't)\s+(?:not|n't)\b[^.;:!?]{1,40}?\brather\b", re.I),
    re.compile(r"\brather than (?:simply|merely|just)\b", re.I),
]
EM_DASH = re.compile(r"—|(?<!-)---(?!-)|\s--\s")
NOMINALISATION = re.compile(
    r"\b\w{4,}(?:tion|sion|ment|ance|ence|ity|ness|ization|isation)s?\b", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|has been|have been|had been)\s+"
    r"(?:\w+ly\s+)?(\w+(?:ed|en|wn|ne|nt))\b", re.I)
EXPLETIVE = re.compile(r"\b(?:it is|it was|there is|there are|there was|there were)\b", re.I)
TRICOLON = re.compile(r"\b\w+,\s+\w+,?\s+and\s+\w+\b")
PLACEHOLDERS = {"cite", "ref", "math"}

THRESHOLDS = {
    "banned_total": 0,
    "sentence_len_stdev_min": 8.0,
    "paragraphs_without_short_sentence_pct_max": 25.0,
    "transition_opener_pct_max": 25.0,
    "paragraphs_over_two_hedges_max": 0,
    "empty_topic_sentences_max": 0,
    "mean_sentence_len_max": 30.0,
    "passive_pct_max": 40.0,
    # advisory
    "em_dash_per_100w_max": 0.5,
    "contrastive_per_100s_max": 5.0,
    "opener_runs_max": 0,
    "para_len_stdev_min": 0.8,
    "closing_summaries_max": 0,
    "rhetorical_per_1000w_max": 1.0,
    "choppy_mean_len_min": 12.0,
    "choppy_under7_pct_max": 25.0,
}

COMPARE_KEYS = [
    ("banned_total", "banned hits", "lower"),
    ("sentence_len_mean", "mean sentence length", None),
    ("sentence_len_stdev", "sentence-length stdev", "higher"),
    ("paragraphs_without_short_sentence_pct", "paragraphs w/o short sentence %", "lower"),
    ("transition_opener_pct", "transition openers %", "lower"),
    ("paragraphs_over_two_hedges", "hedge-stacked paragraphs", "lower"),
    ("empty_topic_count", "empty topic sentences", "lower"),
    ("em_dash_per_100w", "em-dashes / 100 words", "lower"),
    ("contrastive_per_100s", "contrastive negations / 100 sentences", "lower"),
    ("opener_runs", "repeated-opener runs", "lower"),
    ("nominalisation_per_100w", "nominalisations / 100 words", "lower"),
    ("passive_pct", "passive / 100 sentences", None),
    ("words", "words", None),
]


def find_in_lines(raw_lines: list[str], needles: list[str], whole_word: bool) -> list[dict]:
    hits = []
    for i, line in enumerate(raw_lines, 1):
        low = line.lower()
        for nd in needles:
            if whole_word:
                if re.search(rf"\b{re.escape(nd)}\b", low):
                    hits.append({"line": i, "match": nd, "text": line.strip()[:120]})
            elif nd in low:
                hits.append({"line": i, "match": nd, "text": line.strip()[:120]})
    return hits


def select_sections(body: str, pattern: str) -> str:
    """Keep only the sections whose title matches `pattern` (case-insensitive)."""
    rx = re.compile(pattern, re.I)
    keep, current_ok = [], False
    for lvl, title, sec_body in T.split_sections(body):
        if lvl in ("section", "chapter"):
            current_ok = bool(rx.search(title))
        elif not current_ok and rx.search(title):
            current_ok = True  # a matching subsection inside a non-matching section
        if current_ok:
            keep.append(sec_body)
    return "\n\n".join(keep)


def opener_of(sentence: str) -> str:
    for w in T.words(sentence):
        lw = w.lower()
        if lw not in PLACEHOLDERS:
            return lw
    return ""


def closing_summaries(body: str) -> list[str]:
    """Last-paragraph openers that merely restate a non-concluding section."""
    found = []
    for lvl, title, sec_body in T.split_sections(body):
        if lvl not in ("section", "chapter"):
            continue
        if re.search(r"conclusion|summary|abstract|discussion", title, re.I):
            continue
        paras = T.paragraphs(T.to_prose(sec_body))
        if len(paras) < 2:
            continue
        last = T.sentences(paras[-1])
        if last and CLOSING_SUMMARY.search(last[0].strip()):
            found.append(f"[{title[:30]}] {last[0][:110]}")
    return found


def analyse(path: str, section: str | None = None) -> dict:
    raw = T.read_with_inputs(path)
    body = T.body_only(T.strip_comments(raw))
    if section:
        body = select_sections(body, section)
    prose = T.to_prose(body)
    raw_lines = T.strip_comments(raw).split("\n") if not section else T.strip_comments(body).split("\n")

    sents = T.sentences(prose)
    lens = [len(T.words(s)) for s in sents]
    paras = T.paragraphs(prose)
    all_words = T.words(prose)
    nwords = max(len(all_words), 1)
    nsents = max(len(sents), 1)

    para_stats = []
    opener_runs = 0
    for idx, p in enumerate(paras, 1):
        ps = T.sentences(p)
        plens = [len(T.words(s)) for s in ps]
        hedge_n = sum(len(re.findall(rf"\b{re.escape(h)}\b", p, re.I)) for h in HEDGES)
        first = ps[0] if ps else ""
        opener = opener_of(first)
        empty = any(re.search(pat, first.strip(), re.I) for pat in EMPTY_TOPIC)
        openers = [opener_of(s) for s in ps]
        run, best = 1, 1
        for a, b in zip(openers, openers[1:]):
            run = run + 1 if (a and a == b) else 1
            best = max(best, run)
        if best >= 3:
            opener_runs += 1
        para_stats.append({
            "n": idx,
            "sentences": len(ps),
            "lengths": plens,
            "min_sentence_len": min(plens) if plens else 0,
            "hedges": hedge_n,
            "opener": opener,
            "transition_opener": opener in TRANSITION_OPENERS,
            "empty_topic": empty,
            "opener_run": best,
            "first_sentence": first[:130],
        })

    npar = max(len(para_stats), 1)
    no_short = [p for p in para_stats if p["min_sentence_len"] >= 10]
    trans = [p for p in para_stats if p["transition_opener"]]
    hedgy = [p for p in para_stats if p["hedges"] > 2]
    empties = [p for p in para_stats if p["empty_topic"]]
    para_lens = [p["sentences"] for p in para_stats]

    banned_phrases = find_in_lines(raw_lines, BANNED_PHRASES, whole_word=False)
    banned_words = find_in_lines(raw_lines, BANNED_WORDS, whole_word=True)
    overused = {}
    low = prose.lower()
    for term, thr in OVERUSED.items():
        n = len(re.findall(rf"\b{re.escape(term)}\b", low))
        rate = round(1000 * n / nwords, 2)
        if n >= 2 and rate > thr:
            overused[term] = {"count": n, "per_1000w": rate, "threshold": thr}

    contrastive = sum(len(rx.findall(prose)) for rx in CONTRASTIVE)
    em = len(EM_DASH.findall(prose))
    questions = sum(1 for s in sents if s.rstrip().endswith("?"))
    roadmaps = sum(1 for s in sents if ROADMAP.search(s.strip()))
    under7 = sum(1 for x in lens if x < 7)

    return {
        "file": path,
        "section_filter": section,
        "words": len(all_words),
        "sentences": len(sents),
        "paragraphs": len(paras),
        "banned_phrases": banned_phrases,
        "banned_words": banned_words,
        "banned_total": len(banned_phrases) + len(banned_words),
        "overused": overused,
        "sentence_len_mean": round(statistics.mean(lens), 1) if lens else 0,
        "sentence_len_stdev": round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
        "sentence_len_max": max(lens) if lens else 0,
        "short_sentences_pct": round(100 * sum(1 for x in lens if x < 10) / nsents, 1),
        "under7_pct": round(100 * under7 / nsents, 1),
        "long_sentences_pct": round(100 * sum(1 for x in lens if x > 35) / nsents, 1),
        "paragraphs_without_short_sentence_pct": round(100 * len(no_short) / npar, 1),
        "transition_opener_pct": round(100 * len(trans) / npar, 1),
        "paragraphs_over_two_hedges": len(hedgy),
        "empty_topic_sentences": [p["first_sentence"] for p in empties],
        "empty_topic_count": len(empties),
        "para_len_stdev": round(statistics.pstdev(para_lens), 2) if len(para_lens) > 1 else 0,
        "opener_runs": opener_runs,
        "em_dashes": em,
        "em_dash_per_100w": round(100 * em / nwords, 2),
        "contrastive": contrastive,
        "contrastive_per_100s": round(100 * contrastive / nsents, 1),
        "closing_summaries": closing_summaries(body),
        "roadmaps": roadmaps,
        "rhetorical_questions": questions,
        "rhetorical_per_1000w": round(1000 * questions / nwords, 2),
        "nominalisation_per_100w": round(100 * len(NOMINALISATION.findall(prose)) / nwords, 1),
        "passive_pct": round(100 * len(PASSIVE.findall(prose)) / nsents, 1),
        "expletive_openers": len(EXPLETIVE.findall(prose)),
        "tricolons": len(TRICOLON.findall(prose)),
        "first_person_per_100w": round(
            100 * len(re.findall(r"\b(?:we|our|ours|us)\b", prose, re.I)) / nwords, 1),
        "_paras": para_stats,
    }


def verdict(m: dict) -> list[tuple[str, str, str]]:
    """Return [(status, check, detail)]. FAIL blocks; WARN and INFO never do."""
    th = THRESHOLDS
    out = []
    nb = m["banned_total"]
    out.append(("FAIL" if nb else "PASS", "banned phrases/words",
                f"{nb} hit(s) — target {th['banned_total']}"))
    sd = m["sentence_len_stdev"]
    out.append(("PASS" if sd >= th["sentence_len_stdev_min"] else "FAIL",
                "sentence-length variance",
                f"stdev {sd} — target >= {th['sentence_len_stdev_min']} "
                f"(mean {m['sentence_len_mean']}, max {m['sentence_len_max']})"))
    v = m["paragraphs_without_short_sentence_pct"]
    out.append(("PASS" if v <= th["paragraphs_without_short_sentence_pct_max"] else "FAIL",
                "short sentence per paragraph",
                f"{v}% of paragraphs have no sentence under 10 words — target <= "
                f"{th['paragraphs_without_short_sentence_pct_max']}%"))
    v = m["transition_opener_pct"]
    out.append(("PASS" if v <= th["transition_opener_pct_max"] else "FAIL",
                "transition openers",
                f"{v}% of paragraphs open with a transition adverb — target <= "
                f"{th['transition_opener_pct_max']}%"))
    v = m["paragraphs_over_two_hedges"]
    out.append(("PASS" if v <= th["paragraphs_over_two_hedges_max"] else "FAIL",
                "hedge stacking", f"{v} paragraph(s) with more than two hedges — target 0"))
    v = m["empty_topic_count"]
    out.append(("PASS" if v <= th["empty_topic_sentences_max"] else "FAIL",
                "empty topic sentences", f"{v} found — target 0"))

    v = m["sentence_len_mean"]
    out.append(("PASS" if v <= th["mean_sentence_len_max"] else "WARN",
                "mean sentence length",
                f"{v} words — over {th['mean_sentence_len_max']} is hard to read"))
    choppy = (m["sentences"] >= 6 and (m["sentence_len_mean"] < th["choppy_mean_len_min"]
                                       or m["under7_pct"] > th["choppy_under7_pct_max"]))
    out.append(("WARN" if choppy else "PASS", "choppiness (over-correction)",
                f"mean {m['sentence_len_mean']} words, {m['under7_pct']}% of sentences under 7 words — "
                f"staccato prose is the other machine register"))
    v = m["passive_pct"]
    out.append(("PASS" if v <= th["passive_pct_max"] else "WARN",
                "passive voice",
                f"~{v} passive constructions per 100 sentences — acceptable in Methods, "
                f"not in Introduction"))
    v = m["em_dash_per_100w"]
    out.append(("WARN" if (m["em_dashes"] >= 3 and v > th["em_dash_per_100w_max"]) else "PASS",
                "em-dash density",
                f"{m['em_dashes']} em-dashes, {v} per 100 words — above {th['em_dash_per_100w_max']} "
                f"reads as generated; most become a comma, a colon, or a new sentence"))
    v = m["contrastive_per_100s"]
    out.append(("WARN" if (m["contrastive"] >= 2 and v > th["contrastive_per_100s_max"]) else "PASS",
                "contrastive negation",
                f"{m['contrastive']} 'not X, but Y' frames, {v} per 100 sentences — say what it is"))
    v = m["opener_runs"]
    out.append(("WARN" if v > th["opener_runs_max"] else "PASS",
                "repeated sentence openers",
                f"{v} paragraph(s) with three or more consecutive sentences starting on the same word"))
    uniform = m["paragraphs"] >= 4 and m["para_len_stdev"] < th["para_len_stdev_min"]
    out.append(("WARN" if uniform else "PASS", "paragraph-length variance",
                f"stdev {m['para_len_stdev']} sentences across {m['paragraphs']} paragraphs — "
                f"equal-length paragraphs read as generated"))
    v = len(m["closing_summaries"])
    out.append(("WARN" if v > th["closing_summaries_max"] else "PASS",
                "section-closing summaries",
                f"{v} section(s) end on a paragraph that restates the section — cut them"))
    rm = m["roadmaps"]
    out.append(("WARN" if rm > max(1, m["words"] // 1500) else "PASS", "roadmap sentences",
                f"{rm} 'in this section we first… then… finally' sentence(s) — one per paper is plenty"))
    v = m["rhetorical_per_1000w"]
    out.append(("WARN" if (m["rhetorical_questions"] >= 2 and v > th["rhetorical_per_1000w_max"]) else "PASS",
                "rhetorical questions",
                f"{m['rhetorical_questions']} question(s), {v} per 1000 words — answer them as statements"))
    ov = m["overused"]
    out.append(("WARN" if ov else "PASS", "over-used words (by rate)",
                (", ".join(f"{k} ×{d['count']}" for k, d in sorted(ov.items(), key=lambda kv: -kv[1]['count']))
                 if ov else "none above threshold")))

    out.append(("INFO", "nominalisation", f"{m['nominalisation_per_100w']} per 100 words — "
                "high values flatten the prose; turn nouns back into verbs"))
    out.append(("INFO", "tricolons", f"{m['tricolons']} three-item lists"))
    out.append(("INFO", "expletive openers",
                f"{m['expletive_openers']} 'it is / there are' constructions"))
    out.append(("INFO", "first person", f"{m['first_person_per_100w']} we/our per 100 words"))
    return out


def print_paragraphs(m: dict) -> None:
    print(f"\n## Paragraphs — {m['file']}\n")
    print("  #   sents  lengths                         min  hedges  opener        flags")
    for p in m["_paras"]:
        flags = []
        if p["transition_opener"]:
            flags.append("T:transition-opener")
        if p["empty_topic"]:
            flags.append("E:empty-topic")
        if p["hedges"] > 2:
            flags.append("H:hedge-stack")
        if p["min_sentence_len"] >= 10:
            flags.append("N:no-short-sentence")
        if p["opener_run"] >= 3:
            flags.append("R:repeated-opener")
        lens = ",".join(str(x) for x in p["lengths"])
        print(f"  {p['n']:<3} {p['sentences']:<6} {lens[:30]:<31} {p['min_sentence_len']:<4} "
              f"{p['hedges']:<7} {p['opener'][:12]:<13} {' '.join(flags)}")
        print(f"      → {p['first_sentence'][:100]}")
    print("\n  Flags: T opens on a transition adverb · E announces its topic instead of its claim ·")
    print("  H more than two hedges · N no sentence under 10 words · R three+ sentences open alike.")


def print_compare(before: dict, after: dict) -> None:
    print(f"\n## Compare — before: {before['file']}  →  after: {after['file']}\n")
    print(f"  {'metric':38} {'before':>9} {'after':>9} {'delta':>9}  ")
    for key, label, better in COMPARE_KEYS:
        b, a = before.get(key, 0), after.get(key, 0)
        d = round(a - b, 2)
        mark = ""
        if better and d != 0:
            good = (d < 0) if better == "lower" else (d > 0)
            mark = "better" if good else "WORSE"
        print(f"  {label:38} {b:>9} {a:>9} {d:>+9}  {mark}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", help="main .tex file (\\input files are followed)")
    ap.add_argument("--json", action="store_true", help="emit raw metrics as JSON")
    ap.add_argument("--paragraphs", action="store_true", help="per-paragraph table for the rewrite loop")
    ap.add_argument("--compare", metavar="BEFORE.tex", help="show metric deltas against an earlier version")
    ap.add_argument("--section", metavar="REGEX", help="measure only sections whose title matches")
    ap.add_argument("--max-hits", type=int, default=25, help="banned hits to list")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="non-zero exit on any FAIL (default)")
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    for path in [args.tex] + ([args.compare] if args.compare else []):
        why = T.sniff_binary(path)
        if why:
            print(f"error: {why}", file=sys.stderr)
            return 2

    m = analyse(args.tex, args.section)
    if m["words"] == 0:
        where = f" in sections matching /{args.section}/" if args.section else ""
        print(f"error: no prose found in {args.tex}{where}", file=sys.stderr)
        return 2

    if args.json:
        m.pop("_paras", None)
        print(json.dumps(m, indent=2))
        return 0

    checks = verdict(m)
    fails = [c for c in checks if c[0] == "FAIL"]
    warns = [c for c in checks if c[0] == "WARN"]

    scope = f"  (sections matching /{args.section}/)" if args.section else ""
    print(f"# Prose quality — {m['file']}{scope}")
    print(f"\n{m['words']} words · {m['sentences']} sentences · {m['paragraphs']} paragraphs\n")
    for status, name, detail in checks:
        print(f"  [{status:4}] {name:32} {detail}")

    hits = ([("phrase", h) for h in m["banned_phrases"]]
            + [("word", h) for h in m["banned_words"]])
    if hits:
        print(f"\n## Banned phrases and words ({len(hits)})\n")
        for kind, h in hits[: args.max_hits]:
            print(f"  {h['line']:>5}: {kind:6} \"{h['match']}\"   | {h['text']}")
        if len(hits) > args.max_hits:
            print(f"  ... and {len(hits) - args.max_hits} more")

    if m["empty_topic_sentences"]:
        print("\n## Empty topic sentences — replace with the paragraph's claim\n")
        for s in m["empty_topic_sentences"][:10]:
            print(f"  - {s}")
    if m["closing_summaries"]:
        print("\n## Section-closing summaries — the reader just read the section\n")
        for s in m["closing_summaries"][:10]:
            print(f"  - {s}")

    if args.paragraphs:
        print_paragraphs(m)
    if args.compare:
        before = analyse(args.compare, args.section)
        print_compare(before, m)

    print("\n## What this cannot measure\n")
    print("  Emptiness. For every paragraph, ask: what does the reader now know that")
    print("  they did not before? If the answer is 'that this topic is important',")
    print("  delete the paragraph. Then read the whole thing aloud.")

    if args.strict and fails:
        print(f"\nFAIL — {len(fails)} check(s) failed" + (f", {len(warns)} warning(s)." if warns else "."))
        return 1
    print(f"\nPASS — no blocking prose defects found by measurement"
          + (f"; {len(warns)} warning(s) to read." if warns else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
