# Ledger — <paper short name>

venue: <slug> | deadline: YYYY-MM-DD | stage: S<n> | updated: YYYY-MM-DD

## Story spine
1. TASK      — We study <input> → <output>, in the setting of <scope>.
2. GAP       — Prior methods <what they do>. They fail when <condition>, **because** <technical reason>.
3. INSIGHT   — <the one observation that makes the failure fixable>
4. METHOD    — We <mechanism>, which <property that addresses the reason>.
5. EVIDENCE  — On <datasets>, <delta> vs <strongest baseline>; <ablation> isolates <mechanism>.
6. SO WHAT   — A reader now knows <transferable knowledge>.

## Contribution claims
| # | Claim (one sentence, falsifiable) | Type | Evidence | Location | Status |
|---|---|---|---|---|---|
| C1 | | empirical | | | needs-evidence |
| C2 | | causal | | | needs-evidence |

Type: empirical · causal · theoretical · comparative · generality · efficiency
Status: supported · needs-evidence · unsupported

## Claim strength check
For each claim, the highest rung the evidence actually supports:
`5 X causes Y · 4 X improves Y by N% on D · 3 X improves Y on D · 2 X associated with Y · 1 X may help Y`
Rung 1 does not belong in an abstract.

## Evidence plan
| Claim | Experiment | Datasets | Baselines | Metric | Could falsify? | Status |
|---|---|---|---|---|---|---|
| C1 | | | | | yes | NEEDS EXPERIMENT |

## Provenance (every table cell, three hops)
| Table/Figure · cell | results/ file | config | commit |
|---|---|---|---|
| Tab.2 Ours top-1 | results/imagenet/ours_seed{0,1,2}.json | configs/imagenet/ours.yaml | a3f9c21 |

## Citation layer-3 log (claim support)
| Key | Claim it supports | Where in the source |
|---|---|---|
| kim2024 | per-layer routing commits before context resolves | §3.1, Fig. 2 |

## Terminology (fix once, never drift)
| Concept | The one name we use | Defined at |
|---|---|---|

## Gates
| Gate | Stage | Status | Blocking issues |
|---|---|---|---|
| G1 claim/evidence | S4 | not run | |
| G2 citations | S6 | not run | |
| G3 venue compliance | S8 | not run | |
| G4 readiness | S9 | not run | |

A gate that has not been run is not passed.

## Open items
- [ ] `[AUTHOR DECISION]`
- [ ] `[NEEDS EXPERIMENT]`
- [ ] `[NEEDS SOURCE]`
