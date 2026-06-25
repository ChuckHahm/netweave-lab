# EXP006 — Path-Finding Algorithm Comparison

**Status:** planned  
**Date started:** —  
**Author:** Chuck Wiley

## Question

Which path-finding algorithm surfaces the highest-quality introduction paths in the NetWeave graph?

## Hypothesis

Dijkstra with inverted composite weights will produce the best paths because it globally optimizes across the entire path, while top_k_neighbors will underperform on multi-hop targets.

## Success criterion

Winning algorithm achieves mean path composite ≥ 0.65 across 10 target nodes with path length ≤ 2 hops.

## Setup required

Set `CHUCK_NODE_ID` environment variable before running:
```bash
export CHUCK_NODE_ID="your_node_id"
```

Manually select 10 target nodes (known-hard-to-reach) and label whether each path passes through a trusted intermediary.

## Variants tested

| Variant | Key parameters |
|---------|----------------|
| dijkstra | Inverted composite weight, global path optimization |
| astar | domain_score heuristic + inverted composite weight |
| top_k_neighbors | Top-k predecessors of target by tie_strength |

## Results

| Variant | Mean path composite | Mean path length | Trusted intermediary % | Notes |
|---------|--------------------|-----------------|-----------------------|-------|
| (not yet run) | — | — | — | — |

## Decision

**Winner:** —  
**Decision:** planned  
**MLflow run ID:** —  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/query.py`  
Function: Path-finding function used in the goal-driven query engine.  
Citation: `# Validated in EXP006 — see netweave-lab/experiments/EXP006_pathfinding_algos/`
