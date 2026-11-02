# Literature review artifacts

Copy the blocks you need into `lit/`. `lit_scan.py` writes the first three for a
scoping scan; the rest are filled by hand. Every table here is something a reviewer
of a systematic review will ask to see, and something a reviewer of a method paper
will notice the absence of.

## Search record

One row per query actually run. Verbatim string, date, hit count. Scholar counts too,
labelled as a snowball tool.

| DB | String / filter | Date run | Hits | Notes |
|---|---|---|---|---|
| OpenAlex | `cites:W2000000001 since 2019` | 2026-09-30 | 412 | forward arm, seed 1 |
| ACM DL | `("chest radiograph" OR "chest x-ray") AND (transformer OR "vision transformer") AND (classif*)` | 2026-09-30 | 388 | title/abstract fields |
| Google Scholar | `"late commitment" routing experts` | 2026-09-30 | ~1,200 | snowball only; first 5 pages screened |

## Sentinels

Papers the search must retrieve. A string that misses them is a wrong string.

| Sentinel | Why it must appear | Retrieved by |
|---|---|---|
| 10.1000/known.2024 | the closest prior work | OpenAlex forward arm; ACM string |
| 10.1000/baseline.2023 | strongest baseline | **not retrieved**: ACM string lacks "gating" synonym; fixed 2026-10-01 |

## Screening log (PRISMA counts)

```
Identified:              n =          (per database, as in the search record)
Duplicates removed:      n =
Title/abstract screened: n =          → excluded          (reasons not required)
Full text assessed:      n =          → excluded          (reasons required, below)
Included:                n =
Snowball additions:      n =          (listed, with how found)
Final:                   n =
```

Full-text exclusions, with reason codes decided in the protocol:

| Record | Reason code | Note |
|---|---|---|
| Kim 2023 | WRONG-OUTCOME | reports latency only |
| Liu 2022 | NO-COMPARATOR | single arm |
| Nair 2024 | NOT-RETRIEVABLE | paywalled, author did not respond (requested 2026-09-12) |

Codes: WRONG-POPULATION · WRONG-TECHNIQUE · WRONG-OUTCOME · NO-COMPARATOR ·
INSUFFICIENT-REPORTING · NOT-RETRIEVABLE · DUPLICATE-STUDY · OTHER (explain)

Screener agreement (two screeners, title/abstract stage): κ = ____ on n = ____ records.

## The map (scoping scan)

| Paper | Year | Venue | Depth | Mechanism | Assumption it needs | Fails when | Baseline? | Verified (key) |
|---|---|---|---|---|---|---|---|---|
| Kim+ | 2024 | CVPR | HOW | magnitude pruning | weight magnitude ~ importance | discriminative signal is input-dependent | yes, Tab. 2 | kim2024pruning |
| Okafor+ | 2021 | NeurIPS | WHY | per-layer routing | expert choice decidable at layer ℓ | class disambiguated after ℓ | yes, Tab. 2 | okafor2021routing |
| Berg+ | 2023 | CSUR | WHAT | survey | — | — | no: survey | berg2023survey |

Depth: WHY (read fully, incl. limitations) · HOW (method + protocol, exact settings) ·
WHAT (abstract, figures, conclusion) · hand (found by snowballing, not by the protocol).
`Fails when` must name a condition, not a mood. `Baseline? = no` needs a reason in the cell.

## Reading note (one per WHY / HOW paper)

```markdown
### okafor2021routing — Okafor et al., NeurIPS 2021   [verified: crossref 2026-09-30]
Claim (theirs, one sentence):  per-layer gating matches dense accuracy at 2x fewer FLOPs on ImageNet.
Mechanism:                     router at each layer scores that layer's experts from the token state; top-1 dispatch.
Evidence:                      Tab. 2 (ImageNet-1k, ViT-B, 3 seeds); Fig. 4 (FLOPs vs top-1).
Assumption / scope:            the information that picks the expert is present at layer ℓ (§3.1, stated).
Fails when (from their text):  §6 limitations: "late-disambiguated classes" lose 1.9 points (Tab. 5).
Protocol details for our table: 300 epochs, AdamW, 224 px, batch 1024, top-1 on val (§5.1).
Relevance to us:               WHY paper. Their §6 names our gap. Baseline row 2 in our Tab. 2.
Quote worth keeping:           "the router must commit before the features that distinguish ... exist" (§6, p. 8)
Layer-3 rows this supports:    | okafor2021routing | per-layer routing commits before context resolves | §3.1, §6 Tab. 5 |
```

Everything in "Relevance" and "Fails when" must point at a location. That location is
what goes into the ledger's layer-3 log when the paper is cited.

## Extraction row (systematic review)

| Key | Year | Venue | Peer-reviewed | Population / dataset | n | Technique | Comparator | Outcome metric | Effect (dispersion) | Funding | Code | RoB: selection | RoB: measurement | RoB: reporting |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | yes/no/preprint | | | | | | | | url/none | low/some/high | | |

Pilot the columns on five included papers before extracting the rest.

## Synthesis matrix

Rows: included papers. Columns: the themes or mechanisms the review is organised by.
Cells: what the paper contributes to that theme, with a location. Write each synthesis
paragraph **down a column**.

| Paper | Theme A: when per-layer routing fails | Theme B: cost of global context | Theme C: evaluation protocol gaps |
|---|---|---|---|
| Okafor 2021 | names late-disambiguation (§6, −1.9 pts Tab. 5) | — | single dataset |
| Nair 2024 | reproduces the failure on ADE20K (Tab. 3) | +11% latency at batch 1 (Tab. 4) | 3 seeds reported |
| Fischer 2022 | token-level variant, same failure (Fig. 2) | — | no seeds reported |

Column paragraph skeleton:

```
1. Claim the column supports, one sentence.
2. Evidence: ≥ 2 studies, settings and numbers, with locations.
3. Disagreement, and what plausibly explains it (population, protocol, scale).
4. What the column does not show.
```

## Update log

| Date | Search re-run from | New records | Screened in | Changes to conclusions |
|---|---|---|---|---|
| 2026-09-30 | 2026-05-01 | 61 | 4 | none; Nair 2024 added to Theme B |
