import math
import numpy as np
import networkx as nx


def ndcg_at_k(ranked_list: list[str], relevant_set: set[str], k: int = 10) -> float:
    """
    Normalized Discounted Cumulative Gain at k.
    Primary ranking quality metric across all experiments.
    ranked_list: node_ids in ranked order (best first)
    relevant_set: ground truth node_ids that are genuinely relevant
    """
    if not relevant_set:
        return 0.0

    k = min(k, len(ranked_list))

    dcg = sum(
        1.0 / math.log2(i + 2)
        for i, node in enumerate(ranked_list[:k])
        if node in relevant_set
    )

    ideal_hits = min(k, len(relevant_set))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))

    return dcg / idcg if idcg > 0 else 0.0


def precision_at_k(ranked_list: list[str], relevant_set: set[str], k: int = 10) -> float:
    """
    Fraction of top-k results that are in relevant_set.
    Secondary metric — simpler to interpret than NDCG.
    """
    if not ranked_list:
        return 0.0
    k = min(k, len(ranked_list))
    return len(set(ranked_list[:k]) & relevant_set) / k


def rank_correlation(list_a: list[str], list_b: list[str]) -> float:
    """
    Spearman rank correlation between two ranked node lists.
    Uses the intersection of both lists for comparison.
    """
    set_b = set(list_b)
    shared = [n for n in list_a if n in set_b]
    if len(shared) < 2:
        return 0.0

    rank_a = np.array([list_a.index(n) for n in shared], dtype=float)
    rank_b = np.array([list_b.index(n) for n in shared], dtype=float)

    # Pearson correlation on ranks = Spearman rank correlation
    ra, rb = rank_a - rank_a.mean(), rank_b - rank_b.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float(np.dot(ra, rb) / denom) if denom > 0 else 0.0


def build_ground_truth(G: nx.DiGraph, goal_tags: list[str]) -> set[str]:
    """
    Construct a ground truth relevant set by selecting nodes where:
    - domain_tags overlap with goal_tags (Jaccard >= 0.5)
    - seniority in [executive, director, founder]
    Used as the relevant_set for NDCG/precision evaluation when
    no human-labeled ground truth exists.
    """
    goal_set = set(goal_tags)
    senior_levels = {"executive", "director", "founder"}
    result = set()

    for node_id, data in G.nodes(data=True):
        tags = set(data.get("domain_tags", []))
        seniority = data.get("seniority", "")

        if tags and goal_set:
            jaccard = len(tags & goal_set) / len(tags | goal_set)
        else:
            jaccard = 0.0

        if jaccard >= 0.5 and seniority in senior_levels:
            result.add(node_id)

    return result
