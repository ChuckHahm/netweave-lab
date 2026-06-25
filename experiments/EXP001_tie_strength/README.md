# EXP001 — Tie Strength Decay Function

**Status:** INCONCLUSIVE  
**Date run:** 2026-06-25  
**Author:** Chuck Wiley

## Question

Which tie-strength decay function best models relationship warmth from connection recency data?

## Hypothesis

An exponential decay with a half-life of ~365 days will outperform linear and step functions because human relationship warmth decays continuously rather than in discrete steps, and 1 year represents a natural "touch cycle" for professional networks.

## Success criterion

Winning variant achieves NDCG@10 ≥ 0.80 against `build_ground_truth(G, ["medical_diagnostics", "biotech", "investor"])`, with margin ≥ 0.03 over the second-best variant.

## Variants tested

| Variant | Key parameters |
|---------|----------------|
| exp_180 | Exponential, half-life=180 days |
| exp_365 | Exponential, half-life=365 days (production baseline) |
| exp_730 | Exponential, half-life=730 days |
| linear | Linear decay over 3 years (1095 days) |
| step | 1.0 if ≤180d, 0.6 if ≤540d, 0.3 otherwise |

## Results

| Variant | NDCG@10 | P@10 |
|---------|---------|------|
| exp_180 | 0.1312 | 0.10 |
| exp_365 | 0.1312 | 0.10 |
| exp_730 | 0.1312 | 0.10 |
| linear  | 0.1312 | 0.10 |
| step    | 0.1312 | 0.10 |

All variants tied. See `results.png` for the comparison chart.

## Decision

**Winner:** none (all tied)  
**Margin over baseline:** 0.000  
**Decision:** INCONCLUSIVE  
**Date of decision:** 2026-06-25

**Root cause:** 4 of 5 ground-truth nodes have recency_days in the 3,753–5,726 range and rank 895–1443 under every decay function. Only one relevant node (42 days) reaches top-10, at rank 5 identically across all variants. Decay shape is irrelevant when recency alone cannot surface domain-relevant contacts.

**Structural finding:** `tie_strength` (recency) is a weak primary ranking signal for domain-specific intro queries. The `composite` score is what surfaces old-but-relevant contacts.

**Follow-up:** Re-run EXP001 using `composite` as the ranking signal so the experiment tests decay shape within the weighted formula rather than in isolation.

## Production change

**None.** Retain `exp_365` as the production default (least aggressive; penalizes old contacts least).
