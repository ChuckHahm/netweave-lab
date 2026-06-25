# EXP007 — Second-Degree Node Signal Quality

**Status:** planned  
**Date started:** —  
**Author:** Chuck Wiley

## Question

Which OSINT signals most reliably predict that a second-degree node (connection of a connection) is relevant to a given client goal?

## Hypothesis

The combined embedding_sim + employer_match signal will outperform individual signals because no single signal is sufficient — domain match alone misses seniority, and title keywords miss non-standard titles.

## Setup required

Before running: manually pull 20 second-degree nodes via LinkedIn for 3–5 of your highest-scoring first-degree connections. Label each as relevant/not-relevant to the LipoNexus goal.

Store labeled data in: `experiments/EXP007_second_degree/second_degree_sample.json`

Format:
```json
[{"node_id": "n001", "relevant": true, "position": "...", "employer": "..."}]
```

Estimated time for manual labeling: 2–3 hours.

## Variants tested

| Variant | Signal |
|---------|--------|
| title_keyword | Keyword match on position |
| employer_match | Jaccard of employer tags vs. goal tags |
| patent_signal | Boolean: has patents |
| grant_signal | Boolean: has SBIR grant |
| embedding_sim | Cosine similarity of node embedding to goal embedding |
| combined | Weighted combination of all above |

## Results

| Variant | Precision | Recall | Notes |
|---------|-----------|--------|-------|
| (not yet run) | — | — | — |

## Decision

**Winner:** —  
**Decision:** planned  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/expand.py`  
Function: Second-degree relevance scoring function (v2 implementation).  
Citation: `# Validated in EXP007 — see netweave-lab/experiments/EXP007_second_degree/`
