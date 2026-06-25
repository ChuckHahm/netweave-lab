# EXP005 — Graph Layout Readability for Introduction Paths

**Status:** planned  
**Date started:** —  
**Author:** Chuck Wiley

## Question

Which Cytoscape layout algorithm makes introduction path structure most readable for a client deliverable?

## Hypothesis

Hierarchical layout will win because introduction paths are directional (source → intermediary → target), which maps naturally to a top-down hierarchy. Force-directed may cluster too aggressively.

## Setup required

Requires Cytoscape Desktop running on localhost:1234. Run `p4c.cytoscape_ping()` to confirm before executing layout cells.

If Cytoscape is unavailable: use Gephi fallback — `export_graphml(G, "experiments/EXP005_layout_readability/graph.graphml")` and open manually with ForceAtlas2 + LinLog mode.

## Layouts compared

| Layout | Algorithm |
|--------|-----------|
| force-directed | COSE — default, good for medium graphs |
| hierarchical | Good for path structure |
| circular | Good for cluster visibility |
| kamada-kawai | Good for small graphs, path clarity |
| prefuse-force-directed | ForceAtlas2 equivalent in Cytoscape |

## Evaluation (qualitative)

Rate each layout 1–5 on:
- Introduction path legibility
- Cluster separation
- Node label readability

## Results

| Layout | Path legibility | Cluster sep | Label readability | Notes |
|--------|----------------|-------------|-------------------|-------|
| (not yet run) | — | — | — | — |

## Decision

**Winner:** —  
**Decision:** planned (qualitative)  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/query.py`  
Function: Default layout parameter when pushing output to Cytoscape for client review.  
Citation: `# Validated in EXP005 — see netweave-lab/experiments/EXP005_layout_readability/`
