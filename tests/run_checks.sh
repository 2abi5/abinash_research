#!/usr/bin/env bash
# Run every checker against the fixtures. A checker that finds nothing has regressed.
set -u
cd "$(dirname "$0")/.." || exit 1
S=skills/research-pro/scripts
F=tests/fixtures
pass=0; fail=0

expect_findings() {   # name, expected-exit, command...
  local name="$1" want="$2"; shift 2
  "$@" >/tmp/rp_check.out 2>&1
  local got=$?
  if [ "$got" = "$want" ]; then
    printf "  ok       %-34s (exit %s)\n" "$name" "$got"; pass=$((pass+1))
  else
    printf "  REGRESS  %-34s (exit %s, wanted %s)\n" "$name" "$got" "$want"
    sed 's/^/             /' /tmp/rp_check.out | head -12; fail=$((fail+1))
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

echo "== scaffold round-trip =="
T=$(mktemp -d)
expect_findings "new_paper scaffold"         0 python3 $S/new_paper.py --title "Test Paper" --venue neurips --out "$T/paper"
expect_findings "scaffold lint (its [TBD])"  1 python3 $S/latex_lint.py "$T/paper/main.tex" --venue neurips
rm -rf "$T"

echo
echo "$pass ok, $fail regressed"
[ "$fail" = 0 ] || exit 1
