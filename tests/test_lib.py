import os
import pytest
import networkx as nx
from lib.niw_metrics import ndcg_at_k, precision_at_k, rank_correlation, build_ground_truth
from lib.niw_graph import graph_summary, filter_by_domain, export_graphml


@pytest.fixture
def sample_graph():
    """5-node synthetic DiGraph for lib sanity tests."""
    G = nx.DiGraph()
    G.add_node("n1", name="Alice", seniority="executive", domain_tags=["biotech", "investor"])
    G.add_node("n2", name="Bob", seniority="director", domain_tags=["medical_diagnostics"])
    G.add_node("n3", name="Carol", seniority="manager", domain_tags=["software"])
    G.add_node("n4", name="Dave", seniority="founder", domain_tags=["biotech"])
    G.add_node("n5", name="Eve", seniority="ic", domain_tags=["investor", "fintech"])
    G.add_edge("n1", "n2", tie_strength=0.9, role_fit=0.8, intro_likelihood=0.7, composite=0.8)
    G.add_edge("n2", "n3", tie_strength=0.5, role_fit=0.4, intro_likelihood=0.6, composite=0.5)
    G.add_edge("n3", "n4", tie_strength=0.3, role_fit=0.6, intro_likelihood=0.4, composite=0.4)
    G.add_edge("n4", "n5", tie_strength=0.7, role_fit=0.5, intro_likelihood=0.8, composite=0.7)
    return G


def test_ndcg_perfect():
    ranked = ["a", "b", "c"]
    relevant = {"a", "b", "c"}
    assert ndcg_at_k(ranked, relevant, k=3) == pytest.approx(1.0)


def test_ndcg_empty_relevant():
    assert ndcg_at_k(["a", "b"], set(), k=2) == 0.0


def test_ndcg_no_overlap():
    assert ndcg_at_k(["a", "b"], {"c", "d"}, k=2) == 0.0


def test_precision_at_k():
    ranked = ["a", "b", "c", "d"]
    relevant = {"a", "c"}
    assert precision_at_k(ranked, relevant, k=4) == pytest.approx(0.5)


def test_rank_correlation_identical():
    lst = ["a", "b", "c", "d"]
    assert rank_correlation(lst, lst) == pytest.approx(1.0)


def test_build_ground_truth(sample_graph):
    # n1: executive, ["biotech","investor"] vs goal ["biotech","investor"] → Jaccard 1.0 ✓
    # n4: founder, ["biotech"] vs goal ["biotech","investor"] → Jaccard 0.5 ✓
    # n2: director, ["medical_diagnostics"] → Jaccard 0.0 ✗
    # n5: ic (not senior) → ✗
    goal_tags = ["biotech", "investor"]
    result = build_ground_truth(sample_graph, goal_tags)
    assert "n1" in result
    assert "n4" in result
    assert "n2" not in result
    assert "n3" not in result
    assert "n5" not in result


def test_graph_summary_keys(sample_graph):
    summary = graph_summary(sample_graph)
    for key in ["n_nodes", "n_edges", "density", "avg_degree",
                "domain_tag_distribution", "seniority_distribution"]:
        assert key in summary
    assert summary["n_nodes"] == 5
    assert summary["n_edges"] == 4


def test_filter_by_domain(sample_graph):
    sub = filter_by_domain(sample_graph, ["biotech"])
    assert "n1" in sub.nodes  # has biotech
    assert "n4" in sub.nodes  # has biotech
    assert "n3" not in sub.nodes  # software only


def test_export_graphml_no_exception(sample_graph, tmp_path):
    path = str(tmp_path / "test.graphml")
    export_graphml(sample_graph, path)
    assert os.path.exists(path)
    content = open(path).read()
    # List attrs should have been pipe-joined
    assert "biotech" in content
