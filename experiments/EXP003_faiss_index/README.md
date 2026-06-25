# EXP003 — FAISS Index Type vs. Recall

**Status:** planned  
**Date started:** —  
**Author:** Chuck Wiley

## Question

Which FAISS index type gives acceptable recall for NetWeave's node embedding similarity search at current and projected node counts (<5K nodes)?

## Hypothesis

HNSW will give the best recall/speed tradeoff at 5K nodes, while flat indices are sufficient at current scale (<500 nodes) and simpler to maintain.

## Success criterion

Winning index achieves Recall@10 ≥ 0.90 at 5K nodes with query latency < 10ms.

## Variants tested

| Variant | Key parameters |
|---------|----------------|
| flat_l2 | IndexFlatL2 — exact search |
| flat_ip | IndexFlatIP — inner product (cosine if normalized) |
| ivf_flat | IVF16,Flat — 16 clusters |
| hnsw | HNSW32 — hierarchical graph index |

## Scale simulation

Each variant tested at: 500 / 1K / 2K / 5K nodes (synthetic embeddings used for padding).

## Results

| Variant | Recall@10 @5K | Latency (ms) | Build time (ms) | Notes |
|---------|--------------|--------------|-----------------|-------|
| (not yet run) | — | — | — | — |

## Decision

**Winner:** —  
**Decision:** planned  
**MLflow run ID:** —  
**Date of decision:** —

## Production change (if VALIDATED)

File: `netweave/src/expand.py`  
Function: Index type selection in v2 build.  
Citation: `# Validated in EXP003 — see netweave-lab/experiments/EXP003_faiss_index/`
