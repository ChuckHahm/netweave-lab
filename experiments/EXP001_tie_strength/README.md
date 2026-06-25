# EXP001 — Tie Strength Decay Function

**Status:** planned  
**Date started:** —  
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

| Variant | NDCG@10 | Notes |
|---------|---------|-------|
| (not yet run) | — | — |

## Decision

**Winner:** —  
**Margin over baseline:** —  
**Decision:** planned  
**MLflow run ID:** —  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/edges.py`  
Function: `tie_strength()`  
Change: Update decay function and parameters to the winning variant.  
Citation: `# Validated in EXP001 — see netweave-lab/experiments/EXP001_tie_strength/`
