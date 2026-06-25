import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx


def plot_ranked_contacts(
    ranked_df: pd.DataFrame,
    title: str,
    top_n: int = 15,
    output_dir: str = ".",
) -> None:
    """
    Horizontal bar chart of top_n contacts with composite score.
    Color bars by domain_tag (one color per tag from tab10 palette).
    Saves PNG to output_dir automatically.
    """
    df = ranked_df.head(top_n).copy()

    all_tags = df["domain_tags"].apply(
        lambda x: x[0] if isinstance(x, list) and x else "unknown"
    )
    unique_tags = sorted(all_tags.unique())
    palette = cm.tab10.colors
    tag_to_color = {tag: palette[i % len(palette)] for i, tag in enumerate(unique_tags)}
    colors = [tag_to_color[tag] for tag in all_tags]

    label_col = "name" if "name" in df.columns else df.columns[0]
    score_col = "composite" if "composite" in df.columns else df.columns[-1]

    fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.4)))
    ax.barh(df[label_col], df[score_col], color=colors)
    ax.set_xlabel(score_col)
    ax.set_title(title)
    ax.invert_yaxis()
    plt.tight_layout()

    filename = f"{title.replace(' ', '_').replace('/', '-')}.png"
    plt.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.show()


def plot_score_distribution(G: nx.DiGraph, score_attr: str) -> None:
    """
    Histogram of a given edge or node attribute across the full graph.
    Used to inspect score distributions before and after parameter changes.
    """
    node_vals = [
        d.get(score_attr)
        for _, d in G.nodes(data=True)
        if d.get(score_attr) is not None
    ]

    if node_vals:
        vals = node_vals
        source = "node"
    else:
        vals = [
            d.get(score_attr)
            for _, _, d in G.edges(data=True)
            if d.get(score_attr) is not None
        ]
        source = "edge"

    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]

    if not vals:
        print(f"No values found for attribute '{score_attr}'")
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(vals, bins=30, edgecolor="white")
    ax.set_xlabel(score_attr)
    ax.set_ylabel("count")
    ax.set_title(f"Distribution of {source} attribute: {score_attr}")
    plt.tight_layout()
    plt.show()


def plot_variant_comparison(results_df: pd.DataFrame, metric: str) -> None:
    """
    Side-by-side bar chart comparing variants on a given metric.
    Standard output for Cell 6 of every experiment.
    """
    df = results_df.sort_values(metric, ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(df["variant"], df[metric])
    ax.set_xlabel(metric)
    ax.set_title(f"Variant Comparison — {metric}")
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()


def push_to_cytoscape(G: nx.DiGraph, style: str = "default") -> None:
    """
    Push graph to running Cytoscape Desktop instance via py4cytoscape.
    Requires Cytoscape to be running on localhost:1234 (default CyREST port).
    Maps composite edge weight to edge width and domain_tag to node color.
    Silently skips (with warning) if Cytoscape is not running.
    """
    try:
        import py4cytoscape as p4c
        p4c.cytoscape_ping()

        node_data = [
            {
                "id": str(n),
                "label": str(n),
                "domain_tag": (d.get("domain_tags", ["unknown"]) or ["unknown"])[0],
            }
            for n, d in G.nodes(data=True)
        ]
        edge_data = [
            {"source": str(u), "target": str(v), "composite": d.get("composite", 0.5)}
            for u, v, d in G.edges(data=True)
        ]

        p4c.create_network_from_data_frames(
            nodes=pd.DataFrame(node_data),
            edges=pd.DataFrame(edge_data),
            title="NIW Graph",
            collection="NIW",
        )

        # Map composite [0, 1] → edge width [1, 8]
        p4c.set_edge_line_width_mapping(
            "composite", [0.0, 1.0], [1.0, 8.0], mapping_type="c"
        )

        # Map domain_tag → node color (discrete)
        unique_tags = list({
            (d.get("domain_tags") or ["unknown"])[0]
            for _, d in G.nodes(data=True)
        })
        palette = [
            "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
            "#a65628", "#f781bf", "#999999", "#a6cee3", "#b2df8a",
        ]
        tag_colors = [palette[i % len(palette)] for i in range(len(unique_tags))]
        p4c.set_node_color_mapping("domain_tag", unique_tags, tag_colors, mapping_type="d")

    except Exception as e:
        warnings.warn(f"Cytoscape unavailable — skipping push: {e}")
