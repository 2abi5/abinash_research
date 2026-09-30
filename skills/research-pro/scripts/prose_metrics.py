#!/usr/bin/env python3
"""Measure the machine-register tells described in references/12-prose-quality.md.

Reports banned phrases with line numbers, sentence-length variance, hedge density,
transition-opener density, nominalisation and passive rates, tricolons, and empty
topic sentences. Thresholds come from that reference file.

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
    "it is important to note", "it is worth noting", "it should be noted",
    "it should be emphasized", "it is crucial to", "one must consider",
    "plays a crucial role", "plays a vital role", "plays a key role",
    "plays a significant role", "serves as a", "stands as a",
    "sheds light on", "paves the way", "opens new avenues", "opens the door",
    "in the realm of", "in the context of today", "when it comes to",
    "in today's rapidly evolving", "in an era of", "in the ever-evolving",
    "in recent years, there has been growing interest",
    "in recent years, there has been increasing interest",
    "a testament to", "a wide range of", "a variety of", "a plethora of",
    "a myriad of", "a host of", "delve into", "delves into", "delving into",
    "at the forefront of", "cutting-edge", "state-of-the-art approach",
    "it is well known that", "as we all know", "needless to say",
    "the landscape of", "navigate the complexities", "unlock the potential",
    "harness the power", "usher in", "revolutionize", "game-changer",
    "first and foremost", "last but not least",
]

BANNED_WORDS = [
    "leverage", "leverages", "leveraging", "leveraged", "utilize", "utilizes",
    "utilizing", "utilized", "utilization", "underscore", "underscores",
    "underscoring", "pivotal", "crucial", "vital", "paramount", "realm",
    "tapestry", "symphony", "cornerstone", "myriad", "plethora", "holistic",
    "seamless", "seamlessly", "comprehensive", "intricate", "meticulous",
    "meticulously", "nuanced", "multifaceted", "robustly", "foster", "fostering",
    "elevate", "elevating", "showcase", "showcases", "showcasing",
    "groundbreaking", "novel", "innovative", "cutting", "transformative",
    "unparalleled", "unprecedented",
]

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
                      "although", "despite"]

EMPTY_TOPIC = [r"^in this (section|subsection|chapter)",
               r"^this (section|subsection|chapter) (describes|presents|discusses|introduces|provides)",
               r"^we (now|first|next|then) (describe|present|discuss|introduce)",
               r"^(first|second|third|finally),? we (describe|present|discuss)",
               r"^there (are|is) (several|many|a number of)",
               r"^it is (well[- ])?(known|established) that"]

NOMINALISATION = re.compile(
    r"\b\w{4,}(?:tion|sion|ment|ance|ence|ity|ness|ization|isation)s?\b", re.I)
PASSIVE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|has been|have been|had been)\s+"
    r"(?:\w+ly\s+)?(\w+(?:ed|en|wn|ne|nt))\b", re.I)
EXPLETIVE = re.compile(r"\b(?:it is|it was|there is|there are|there was|there were)\b", re.I)
TRICOLON = re.compile(r"\b\w+,\s+\w+,?\s+and\s+\w+\b")

THRESHOLDS = {
    "banned_total": 0,
    "sentence_len_stdev_min": 8.0,
    "paragraphs_without_short_sentence_pct_max": 25.0,
    "transition_opener_pct_max": 25.0,
    "paragraphs_over_two_hedges_max": 0,
    "empty_topic_sentences_max": 0,
    "mean_sentence_len_max": 30.0,
    "passive_pct_max": 40.0,
}


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


def analyse(path: str) -> dict:
    raw = T.read_with_inputs(path)
    body = T.body_only(T.strip_comments(raw))
    prose = T.to_prose(body)
    raw_lines = T.strip_comments(raw).split("\n")

    sents = T.sentences(prose)
    lens = [len(T.words(s)) for s in sents]
    paras = T.paragraphs(prose)
    all_words = T.words(prose)
    nwords = max(len(all_words), 1)

    para_stats = []
    for p in paras:
        ps = T.sentences(p)
        plens = [len(T.words(s)) for s in ps]
        hedge_n = sum(len(re.findall(rf"\b{re.escape(h)}\b", p, re.I)) for h in HEDGES)
        first = ps[0] if ps else ""
        opener = T.words(first)[0].lower() if T.words(first) else ""
        empty = any(re.search(pat, first.strip(), re.I) for pat in EMPTY_TOPIC)
        para_stats.append({
            "sentences": len(ps),
            "min_sentence_len": min(plens) if plens else 0,
            "hedges": hedge_n,
            "opener": opener,
            "transition_opener": opener in TRANSITION_OPENERS,
            "empty_topic": empty,
            "first_sentence": first[:130],
        })

    npar = max(len(para_stats), 1)
    no_short = [p for p in para_stats if p["min_sentence_len"] >= 10]
    trans = [p for p in para_stats if p["transition_opener"]]
    hedgy = [p for p in para_stats if p["hedges"] > 2]
    empties = [p for p in para_stats if p["empty_topic"]]

    return {
        "file": path,
        "words": len(all_words),
        "sentences": len(sents),
        "paragraphs": len(paras),
        "banned_phrases": find_in_lines(raw_lines, BANNED_PHRASES, whole_word=False),
        "banned_words": find_in_lines(raw_lines, BANNED_WORDS, whole_word=True),
        "sentence_len_mean": round(statistics.mean(lens), 1) if lens else 0,
        "sentence_len_stdev": round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
        "sentence_len_max": max(lens) if lens else 0,
        "short_sentences_pct": round(100 * sum(1 for x in lens if x < 10) / max(len(lens), 1), 1),
        "long_sentences_pct": round(100 * sum(1 for x in lens if x > 35) / max(len(lens), 1), 1),
        "paragraphs_without_short_sentence_pct": round(100 * len(no_short) / npar, 1),
        "transition_opener_pct": round(100 * len(trans) / npar, 1),
        "paragraphs_over_two_hedges": len(hedgy),
        "empty_topic_sentences": [p["first_sentence"] for p in empties],
        "nominalisation_per_100w": round(100 * len(NOMINALISATION.findall(prose)) / nwords, 1),
        "passive_pct": round(100 * len(PASSIVE.findall(prose)) / max(len(sents), 1), 1),
        "expletive_openers": len(EXPLETIVE.findall(prose)),
        "tricolons": len(TRICOLON.findall(prose)),
        "first_person_per_100w": round(
            100 * len(re.findall(r"\b(?:we|our|ours|us)\b", prose, re.I)) / nwords, 1),
        "_paras": para_stats,
    }


def verdict(m: dict) -> list[tuple[str, str, str]]:
    """Return [(status, check, detail)]."""
    out = []
    nb = len(m["banned_phrases"]) + len(m["banned_words"])
    out.append(("FAIL" if nb else "PASS", "banned phrases/words",
                f"{nb} hit(s) — target {THRESHOLDS['banned_total']}"))
    sd = m["sentence_len_stdev"]
    out.append(("PASS" if sd >= THRESHOLDS["sentence_len_stdev_min"] else "FAIL",
                "sentence-length variance",
                f"stdev {sd} — target >= {THRESHOLDS['sentence_len_stdev_min']} "
                f"(mean {m['sentence_len_mean']}, max {m['sentence_len_max']})"))
    v = m["paragraphs_without_short_sentence_pct"]
    out.append(("PASS" if v <= THRESHOLDS["paragraphs_without_short_sentence_pct_max"] else "FAIL",
                "short sentence per paragraph",
                f"{v}% of paragraphs have no sentence under 10 words — target <= "
                f"{THRESHOLDS['paragraphs_without_short_sentence_pct_max']}%"))
    v = m["transition_opener_pct"]
    out.append(("PASS" if v <= THRESHOLDS["transition_opener_pct_max"] else "FAIL",
                "transition openers",
                f"{v}% of paragraphs open with a transition adverb — target <= "
                f"{THRESHOLDS['transition_opener_pct_max']}%"))
    v = m["paragraphs_over_two_hedges"]
    out.append(("PASS" if v <= THRESHOLDS["paragraphs_over_two_hedges_max"] else "FAIL",
                "hedge stacking", f"{v} paragraph(s) with more than two hedges — target 0"))
    v = len(m["empty_topic_sentences"])
    out.append(("PASS" if v <= THRESHOLDS["empty_topic_sentences_max"] else "FAIL",
                "empty topic sentences", f"{v} found — target 0"))
    v = m["sentence_len_mean"]
    out.append(("PASS" if v <= THRESHOLDS["mean_sentence_len_max"] else "WARN",
                "mean sentence length",
                f"{v} words — over {THRESHOLDS['mean_sentence_len_max']} is hard to read"))
    v = m["passive_pct"]
    out.append(("PASS" if v <= THRESHOLDS["passive_pct_max"] else "WARN",
                "passive voice",
                f"~{v} passive constructions per 100 sentences — acceptable in Methods, "
                f"not in Introduction"))
    out.append(("INFO", "nominalisation", f"{m['nominalisation_per_100w']} per 100 words — "
                "high values flatten the prose; turn nouns back into verbs"))
    out.append(("INFO", "tricolons", f"{m['tricolons']} three-item lists"))
    out.append(("INFO", "expletive openers",
                f"{m['expletive_openers']} 'it is / there are' constructions"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", help="main .tex file (\\input files are followed)")
    ap.add_argument("--json", action="store_true", help="emit raw metrics as JSON")
    ap.add_argument("--max-hits", type=int, default=25, help="banned hits to list")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="non-zero exit on any FAIL (default)")
    ap.add_argument("--no-strict", dest="strict", action="store_false")
    args = ap.parse_args(argv)

    m = analyse(args.tex)
    if m["words"] == 0:
        print(f"error: no prose found in {args.tex}", file=sys.stderr)
        return 2

    if args.json:
        m.pop("_paras", None)
        print(json.dumps(m, indent=2))
        return 0

    checks = verdict(m)
    fails = [c for c in checks if c[0] == "FAIL"]

    print(f"# Prose quality — {m['file']}")
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

    print("\n## What this cannot measure\n")
    print("  Emptiness. For every paragraph, ask: what does the reader now know that")
    print("  they did not before? If the answer is 'that this topic is important',")
    print("  delete the paragraph. Then read the whole thing aloud.")

    if args.strict and fails:
        print(f"\nFAIL — {len(fails)} check(s) failed.")
        return 1
    print("\nPASS — no blocking prose defects found by measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
