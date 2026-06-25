# EXP002 — Domain Classifier: Keyword vs. Claude API

**Status:** planned  
**Date started:** —  
**Author:** Chuck Wiley

## Question

Does calling the Claude API for node classification produce meaningfully better domain tags than keyword matching alone?

## Hypothesis

Claude few-shot will outperform keyword-only by ≥5 F1 points on multi-label domain classification, but the cost per node will determine whether the improvement justifies API usage.

## Success criterion

`claude_zero_shot` F1 ≥ `keyword_only` F1 + 0.05 (otherwise keyword_only wins regardless of absolute scores). Log `cost_per_node_usd` to MLflow.

## Setup required

Before running: create `experiments/EXP002_domain_classifier/ground_truth.json` with 30 hand-labeled nodes (5 per domain). Format:
```json
{"node_id": "n001", "domain_tags": ["biotech", "investor"]}
```

## Variants tested

| Variant | Key parameters |
|---------|----------------|
| keyword_only | Existing taxonomy.py keyword classifier |
| claude_zero_shot | Claude API with company + position, no examples |
| claude_few_shot | Claude API with 6 labeled examples in prompt |
| claude_few_shot_brave | Claude API + Brave Search employer description |

## Results

| Variant | F1 | cost_per_node_usd | Notes |
|---------|----|--------------------|-------|
| (not yet run) | — | — | — |

## Decision

**Winner:** —  
**Decision:** planned  
**MLflow run ID:** —  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/taxonomy.py`  
Function: `classify_node()`  
Citation: `# Validated in EXP002 — see netweave-lab/experiments/EXP002_domain_classifier/`
