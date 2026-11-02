# Worked example — from the literature map to the gap statement

The map is not a reading log. It is the instrument that writes Introduction
paragraph 2 and the Related Work groupings. This example runs the scanner on a
recorded, **entirely fictional** neighbourhood (every paper, author, DOI and count
below is invented; `10.1000/…` is the DOI handbook's example prefix), fills the map,
and then reads the gap off it.

## 1. The scan

```bash
S=skills/research-pro/scripts
python3 $S/lit_scan.py --seed W2000000001 --seed 10.1000/routing.2021 \
        --search "sparse expert routing" --since 2019 \
        --sentinels 10.1000/edge.2025,10.1000/missing.2020 \
        --replay tests/fixtures/lit_replay.json --out lit/
```

Two seeds: the closest prior work (per-layer routing, 2021) and the strongest
baseline (global gating, 2023). The report's first two tables answer "did I stop too
early?" and "did I look in the right place?":

```
| Seed          | Backward refs | Forward cites fetched | New candidates added |
| W2000000001   | 5             | 4                     | 9                    |
| W2000000002   | 4             | 3                     | 4                    |

Sentinel recall: 1/2 known-relevant papers reached by the seeds.
Not reached: 10.1000/missing.2020
```

The second seed added four candidates the first had not reached; a third seed would
tell you whether the scan has converged. One sentinel was not reached by either seed:
either it is not in this neighbourhood after all, or the seeds are wrong. Decide
which before writing a word.

Then the ranked candidates (abridged):

```
| # | Links | Relation      | Year | Cited by | First author  | Title                                            |
| 1 | 2     | cited by seed | 2015 | 6900     | Soon-Ho Han   | Learning Which Weights to Keep                   |
| 2 | 2     | cited by seed | 2022 | 3100     | M. Ferreira   | Switching Experts for Trillion-Parameter Models  |
| 3 | 2     | cites seed    | 2024 | 31       | Priya Nair    | Late-Commitment Gating for Vision Transformers   |
| 5 | 1     | cited by seed | 2017 | 5200     | Noa Shalev    | Sparsely-Gated Expert Layers at Scale            |
| 8 | 1     | cites seed    | 2022 | 120      | Lea Fischer   | Token-Level Routing Is Not Enough                |
| 9 | 1     | cited by seed | 2024 | 40       | Jiwon Kim     | Magnitude Pruning Needs Structure                |
| 11| 1     | cites seed    | 2021 | 9        | Tomasz Nowak  | Gradient Echo Regularisation …  ⚠ RETRACTED      |
```

Reading order follows the `Links` column, not `Cited by`. Row 3 is the one that
matters most and the one a citation count would have buried: 31 citations, 2024,
connected to both seeds, and the title says it is attacking the same failure. That is
either your closest competitor or your scoop. Open it first.

Row 11 is a trap for anyone who copies a baseline from a related-work section.

## 2. Depth, then reading notes

| Paper | Depth | Why |
|---|---|---|
| Okafor 2021 (seed) | WHY | defines per-layer routing; its §6 limitations name the failure |
| Menon 2023 (seed) | HOW | strongest baseline; exact protocol needed for the table |
| Nair 2024 | HOW | closest competitor; concurrent-ish |
| Fischer 2022 | HOW | a variant of the mechanism with the same failure |
| Kim 2024, Han 2015 | HOW | the pruning line; Kim is the current baseline there |
| Shalev 2017, Ferreira 2022 | WHAT | foundations; cite in the intro, do not compare |
| Berg 2023 (survey) | WHAT | pointer to evidence, never evidence |

Reading notes for the WHY and HOW papers, each with a location for every claim you
will later make about it (`templates/lit-review.md`). Without them, step 3 is
guesswork that a reviewer who wrote one of these papers will catch.

## 3. The filled map

| Paper | Year | Venue | Depth | Mechanism | Assumption it needs | Fails when | Baseline? |
|---|---|---|---|---|---|---|---|
| Okafor+ | 2021 | NeurIPS | WHY | per-layer router, top-1 dispatch | the expert choice is decidable from the token state at layer ℓ | the class is disambiguated after ℓ (their §6, −1.9 pts, Tab. 5) | yes, Tab. 2 row 2 |
| Fischer+ | 2022 | ICLR | HOW | per-token router, shared across layers | token identity predicts the expert | context-dependent inputs; same late-signal failure (Fig. 2) | yes, Tab. 2 row 3 |
| Menon+ | 2023 | ICML | HOW | one gate on mean-pooled context | mean pooling preserves the discriminative signal | rare inputs averaged out by the pool (their Tab. 4, long-tail split) | yes, Tab. 2 row 4 (strongest) |
| Nair+ | 2024 | NeurIPS | HOW | gate at the last third of the network | the signal has arrived by layer 2L/3 | latency budget forbids running 2L/3 densely (+11% latency, Tab. 4) | yes, Tab. 2 row 5 |
| Han+ | 2015 | NeurIPS | HOW | magnitude pruning, static | weight magnitude ≈ importance | importance is input-dependent | yes, Tab. 2 row 1 |
| Kim+ | 2024 | CVPR | HOW | structured magnitude pruning | same, plus a structure prior | same; and the structure prior is dataset-specific (§5.3) | yes, Tab. 2 row 1 (replaces Han) |
| Berg+ | 2023 | CSUR | WHAT | survey | — | — | no: survey |

Every `Fails when` cell names a **condition** and a **location**. "Limited accuracy"
would not be allowed in this column.

## 4. Read down the column

Cover everything but `Fails when`:

```
class disambiguated after the routing layer
same late-signal failure
rare inputs averaged out by the pool
latency forbids running 2L/3 densely
importance is input-dependent
same; structure prior is dataset-specific
```

Six failures, one shape. Every method decides *where to spend compute* using
information that is available at the point of decision, and every failure is a case
where the information that matters **has not arrived yet** (per-layer, per-token) or
was **destroyed on the way** (mean pooling) or arrives **too late to be cheap**
(late gate). Pruning is the degenerate case: it decides once, before any input.

That sentence is the gap. Notice that it is a *mechanism*, not a complaint, and that
it already tells the reader what a solution would have to do: see the discriminative
signal before committing, without averaging it away and without paying for the dense
prefix.

## 5. The two places it goes

**Introduction, paragraph 2** (a chain ending in the reason; compare
`02-gap-paragraph.md`, version C):

> Conditional computation reduces inference cost by activating a subset of a model's
> parameters per input. The dominant approach gates each layer independently
> \citep{okafor2021routing,fischer2022token}: a small router at layer $\ell$ scores
> the experts available there and dispatches the token. This works when the
> information that determines the right expert is present at $\ell$. It is not, for
> inputs whose class is disambiguated late; \citet{okafor2021routing} measure a
> 1.9-point loss on exactly those classes. Pooling the sequence before gating
> \citep{menon2023global} sees the whole input but averages the rare cases away, and
> deferring the gate \citep{nair2024late} sees them but pays for the dense prefix.
> The missing quantity is not router capacity. It is **information that has not
> arrived, kept intact, at a point where acting on it is still cheap.**

Every citation in that paragraph has a `Fails when` cell behind it with a location,
which is the row that goes into the ledger's layer-3 log.

**Related Work** (two groupings by mechanism, each ending in the shared limit and the
distinction; see `04-related-work.md`):

> *Routing by local evidence.* Per-layer \citep{okafor2021routing} and per-token
> \citep{fischer2022token} routers score experts from the state available where the
> decision is made. They are cheap because they never look ahead, and they fail for
> the same reason: a class that separates at layer 9 cannot be routed at layer 4. We
> route from a pooled summary instead, so no decision is made before the signal exists.
>
> *Routing by global evidence.* \citet{menon2023global} gate once from mean-pooled
> context, which sees the full input but, as their long-tail split shows (Tab. 4),
> averages rare inputs toward the common experts. \citet{nair2024late} defer the gate
> to the last third of the network and recover the rare cases at an 11% latency cost.
> Closest to ours is the former; we differ in pooling with a learned attention summary
> rather than the mean, which keeps the rare signal, at the cost of one extra
> forward pass over the summary.

The closest competitor is named, credited, and given a number. The distinction
sentence is checkable and concedes a cost.

## 6. The test

Cover your method. Read the Introduction paragraph alone. Can a reader state, in one
sentence, what a solution would have to do? If yes, the map did its job. If not, the
`Fails when` column has a cell that names a symptom instead of a condition. Fix the
cell, not the prose.

## Reproduce

```bash
python3 skills/research-pro/scripts/lit_scan.py --from-json tests/fixtures/lit_scan_dump.json \
        --sentinels 10.1000/edge.2025,10.1000/missing.2020 --out /tmp/lit-example
```
