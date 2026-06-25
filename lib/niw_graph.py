import networkx as nx
import pandas as pd
from collections import Counter


def load_graph(nodes_path: str, edges_path: str) -> nx.DiGraph:
    """
    Load nodes.parquet and edges.parquet into a NetworkX DiGraph.
    Node attributes: all columns from nodes.parquet keyed on node_id.
    Edge attributes: tie_strength, role_fit, intro_likelihood, composite.
    domain_score is NOT stored on edges — it is computed at query time.
    """
    nodes_df = pd.read_parquet(nodes_path)
    edges_df = pd.read_parquet(edges_path)

    G = nx.DiGraph()

    for _, row in nodes_df.iterrows():
        node_id = row["node_id"]
        attrs = row.drop("node_id").to_dict()
        # Normalize to Python list — parquet may return pyarrow array or ndarray
        attrs["domain_tags"] = list(attrs.get("domain_tags", []) or [])
        G.add_node(node_id, **attrs)

    for _, row in edges_df.iterrows():
        G.add_edge(
            row["source"],
            row["target"],
            tie_strength=float(row.get("tie_strength", 0.0)),
            role_fit=float(row.get("role_fit", 0.0)),
            intro_likelihood=float(row.get("intro_likelihood", 0.0)),
            composite=float(row.get("composite", 0.0)),
        )

    return G


def graph_summary(G: nx.DiGraph) -> dict:
    """
    Return dict with: n_nodes, n_edges, density, avg_degree,
    domain_tag_distribution, seniority_distribution.
    Used as sanity check at top of every experiment.
    """
    domain_tag_distribution = Counter(
        tag
        for _, d in G.nodes(data=True)
        for tag in d.get("domain_tags", [])
    )
    seniority_distribution = Counter(
        d.get("seniority", "unknown")
        for _, d in G.nodes(data=True)
    )
    degrees = [deg for _, deg in G.degree()]
    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "density": nx.density(G),
        "avg_degree": sum(degrees) / len(degrees) if degrees else 0.0,
        "domain_tag_distribution": dict(domain_tag_distribution),
        "seniority_distribution": dict(seniority_distribution),
    }


def filter_by_domain(G: nx.DiGraph, tags: list[str]) -> nx.DiGraph:
    """
    Return subgraph containing only nodes whose domain_tags
    overlap with the provided tags list.
    Returns a read-only view — call .copy() on the result if you need to mutate.
    """
    tag_set = set(tags)
    matching = [
        n for n, d in G.nodes(data=True)
        if set(d.get("domain_tags", [])) & tag_set
    ]
    return G.subgraph(matching)


def export_graphml(G: nx.DiGraph, path: str) -> None:
    """
    Export graph to GraphML format for Gephi import.
    Flattens list attributes (domain_tags) to pipe-delimited strings.
    """
    H = G.copy()

    for _, data in H.nodes(data=True):
        for key, val in list(data.items()):
            if isinstance(val, list):
                data[key] = "|".join(str(v) for v in val)
            elif val is None:
                data[key] = ""

    for _, _, data in H.edges(data=True):
        for key, val in list(data.items()):
            if isinstance(val, list):
                data[key] = "|".join(str(v) for v in val)
            elif val is None:
                data[key] = ""

    nx.write_graphml(H, path)
