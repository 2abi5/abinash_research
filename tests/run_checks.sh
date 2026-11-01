#!/usr/bin/env bash
# Run every checker against the fixtures. A checker that finds nothing has regressed.
set -u
cd "$(dirname "$0")/.." || exit 1
S=skills/research-pro/scripts
F=tests/fixtures
OUT=$(mktemp)
TL=$(mktemp -d)
pass=0; fail=0

expect_findings() {   # name, expected-exit, command...
  local name="$1" want="$2"; shift 2
  "$@" >"$OUT" 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    printf "  ok       %-40s (exit %s)\n" "$name" "$got"; pass=$((pass+1))
  else
    printf "  REGRESS  %-40s (exit %s, wanted %s)\n" "$name" "$got" "$want"
    sed 's/^/             /' "$OUT" | head -12; fail=$((fail+1))
  fi
}

expect_output() {     # name, fixed-string the output must contain, command...
  local name="$1" needle="$2"; shift 2
  "$@" >"$OUT" 2>&1
  if grep -qF -- "$needle" "$OUT"; then
    printf "  ok       %-40s (says \"%s\")\n" "$name" "$needle"; pass=$((pass+1))
  else
    printf "  REGRESS  %-40s (never says \"%s\")\n" "$name" "$needle"
    sed 's/^/             /' "$OUT" | head -12; fail=$((fail+1))
  fi
}

echo "== fixtures: every checker must report findings =="
expect_findings "verify_citations (offline)" 1 python3 $S/verify_citations.py $F/refs.bib --offline --tex $F/paper.tex
expect_findings "prose_metrics (slop)"       1 python3 $S/prose_metrics.py $F/slop.tex
expect_findings "venue_check (acl-arr)"      1 python3 $S/venue_check.py --venue acl-arr --paper $F/bad_paper.tex
expect_findings "latex_lint (sins)"          1 python3 $S/latex_lint.py $F/latex_sins.tex
expect_findings "figure_audit (figs)"        1 python3 $S/figure_audit.py $F/figs
expect_findings "score_readiness (gated)"    1 python3 $S/score_readiness.py $F/readiness_filled.json --venue neurips

echo "== clean inputs: these must pass =="
expect_findings "exemplar_profile (build)"   0 python3 $S/exemplar_profile.py $F/exemplar1.tex
expect_findings "repo_scan"                  0 python3 $S/repo_scan.py $F/repo
expect_findings "score_readiness --template" 0 python3 $S/score_readiness.py --template --venue neurips
expect_findings "venue_check --list"         0 python3 $S/venue_check.py --list --venue neurips --paper $F/bad_paper.tex

echo "== citations against recorded database answers (replay: no network needed) =="
BROKEN=(python3 $S/verify_citations.py $F/refs.bib --replay $F/cite_replay.json --tex $F/paper_mechanics.tex --ledger $F/ledger_layer3.md --authors "He,Panta")
expect_findings "verify_citations (replay, broken bib)"  1 "${BROKEN[@]}"
expect_output   "  ... flags the retracted entry"        "RETRACTED" "${BROKEN[@]}"
expect_output   "  ... rejects the near-miss title"      "nearest title found, rejected" "${BROKEN[@]}"
expect_output   "  ... finds the published version"      "a published version exists" "${BROKEN[@]}"
expect_output   "  ... lists uncovered layer-3 keys"     "2 load-bearing key(s) uncovered" "${BROKEN[@]}"
expect_output   "  ... flags a citation stack"           "four or more citations in one bracket" "${BROKEN[@]}"
expect_output   "  ... flags a cite after the period"    "after-period" "${BROKEN[@]}"
expect_output   "  ... reports the self-citation rate"   "Self-citations: 2/7" "${BROKEN[@]}"
expect_findings "verify_citations (replay, clean PASS)" 0 python3 $S/verify_citations.py $F/refs_clean.bib --replay $F/cite_replay.json --tex $F/paper_clean.tex --ledger $F/ledger_clean.md
expect_output   "  ... says layer 3 is covered"          "every load-bearing citation has a ledger location" python3 $S/verify_citations.py $F/refs_clean.bib --replay $F/cite_replay.json --tex $F/paper_clean.tex --ledger $F/ledger_clean.md
expect_output   "  ... without --ledger, says layer 3 unchecked" "Layer 3 (claim support) was not checked" python3 $S/verify_citations.py $F/refs_clean.bib --replay $F/cite_replay.json --tex $F/paper_clean.tex
expect_findings "verify_citations bad replay file"       2 python3 $S/verify_citations.py $F/refs_clean.bib --replay $F/notjson.json

echo "== literature scanner (replay and offline re-rank) =="
SCAN=(python3 $S/lit_scan.py --seed W2000000001 --seed 10.1000/routing.2021 --search "sparse expert routing" --since 2019 --sentinels "10.1000/edge.2025,10.1000/missing.2020" --replay $F/lit_replay.json --out "$TL/lit")
expect_findings "lit_scan (replay)"                      0 "${SCAN[@]}"
expect_output   "  ... ranks multi-seed candidates first" "3 candidate(s) connected to two or more seeds" "${SCAN[@]}"
expect_output   "  ... flags the retracted candidate"    "RETRACTED" "${SCAN[@]}"
expect_output   "  ... reports sentinel recall"          "sentinel recall: 1/2" "${SCAN[@]}"
expect_output   "  ... keeps a hand-edited map.md"       "map.md kept" "${SCAN[@]}"
expect_findings "lit_scan --from-json"                   0 python3 $S/lit_scan.py --from-json $F/lit_scan_dump.json --out "$TL/lit2"
expect_findings "lit_scan malformed dump"                2 python3 $S/lit_scan.py --from-json $F/notjson.json --out "$TL/lit3"
expect_findings "lit_scan no arguments"                  2 python3 $S/lit_scan.py

echo "== clean prose must pass, and the rewrite stages must behave =="
expect_findings "prose_metrics (clean2, all pass)" 0 python3 $S/prose_metrics.py $F/clean2.tex
expect_findings "prose_metrics (clean, 1 FAIL)"    1 python3 $S/prose_metrics.py $F/clean.tex
expect_findings "prose_metrics (overcorrected)"    1 python3 $S/prose_metrics.py $F/overcorrected.tex
expect_output   "  ... warns choppiness"           "[WARN] choppiness" python3 $S/prose_metrics.py $F/overcorrected.tex
expect_output   "  ... warns em-dash density"      "[WARN] em-dash density" python3 $S/prose_metrics.py $F/overcorrected.tex
expect_output   "  ... warns contrastive negation" "[WARN] contrastive negation" python3 $S/prose_metrics.py $F/overcorrected.tex
expect_output   "  ... warns repeated openers"     "[WARN] repeated sentence openers" python3 $S/prose_metrics.py $F/overcorrected.tex
expect_output   "  ... warns closing summary"      "[WARN] section-closing summaries" python3 $S/prose_metrics.py $F/overcorrected.tex
expect_findings "prose_metrics --compare"          0 python3 $S/prose_metrics.py $F/clean2.tex --compare $F/slop.tex
expect_output   "  ... shows the delta table"      "sentence-length stdev" python3 $S/prose_metrics.py $F/clean2.tex --compare $F/slop.tex
expect_findings "prose_metrics --paragraphs"       0 python3 $S/prose_metrics.py $F/clean2.tex --paragraphs
expect_findings "prose_metrics --section (match)"  1 python3 $S/prose_metrics.py $F/slop.tex --section introduction
expect_findings "prose_metrics --section (none)"   2 python3 $S/prose_metrics.py $F/clean2.tex --section nomatch

echo "== hostile inputs: clean errors, never a traceback =="
expect_findings "prose_metrics on a PDF"           2 python3 $S/prose_metrics.py $F/figs/teaser_good.pdf
expect_findings "verify_citations on a PDF"        2 python3 $S/verify_citations.py $F/figs/teaser_good.pdf --offline
expect_findings "score_readiness malformed json"   2 python3 $S/score_readiness.py $F/notjson.json
expect_findings "score_readiness missing file"     2 python3 $S/score_readiness.py $F/nope.json
expect_findings "latex_lint unbalanced brace"      1 python3 $S/latex_lint.py $F/unbalanced.tex
expect_findings "figure_audit corrupt pdf"         1 python3 $S/figure_audit.py $F/corrupt.pdf

echo "== scaffold round-trip =="
T=$(mktemp -d)
expect_findings "new_paper scaffold"         0 python3 $S/new_paper.py --title "Test Paper" --venue neurips --out "$T/paper"
expect_findings "scaffold lint (its [TBD])"  1 python3 $S/latex_lint.py "$T/paper/main.tex" --venue neurips

# The generated Makefile must point at the real scripts directory, whichever way the
# skill was installed (global, plugin, or cloned into the project). A hardcoded
# repo-relative path silently breaks `make check` for every global install.
MK_S=$(grep -m1 '^S ' "$T/paper/Makefile" | sed 's/.*?= *//')
case "$MK_S" in
  /*) RESOLVED="$MK_S" ;;
   *) RESOLVED="$T/paper/$MK_S" ;;
esac
if [ -f "$RESOLVED/verify_citations.py" ]; then
  printf "  ok       %-40s (S=%s)\n" "scaffold Makefile script path" "${MK_S%%/skills*}..."; pass=$((pass+1))
else
  printf "  REGRESS  %-40s (S=%s does not resolve)\n" "scaffold Makefile script path" "$MK_S"; fail=$((fail+1))
fi
rm -rf "$T" "$TL" "$OUT"

echo
echo "$pass ok, $fail regressed"
[ "$fail" = 0 ] || exit 1
