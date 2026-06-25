# NetWeave Intelligence Workbench (NIW) — Lab Spec
## Claude Code Project Document

---

## Purpose and Philosophy

The NIW is a **research harness**, not a production system. Its job is to run
controlled experiments on graph design decisions so that the best-validated
choices can be merged into the production NetWeave pipeline (`netweave/`).

The discipline that keeps this useful:
- Every experiment produces a **logged, reproducible result**
- Every validated decision produces **exactly one pull request** to `netweave/src/`
- The lab never becomes the product — it exists to inform the product

This document is the operating contract for `netweave-lab/`. Claude Code should
treat it as the authoritative specification for all scaffolding, notebooks, and
tooling in this project.

---

## Relationship to Production Code

```
netweave-lab/          ← YOU ARE HERE (this spec)
    experiments/       ← notebooks that test design alternatives
    results/           ← logged MLflow runs, comparison tables
    shared/            ← read-only symlink to netweave/data/processed/

netweave/              ← production pipeline (separate Claude Code project)
    src/               ← functions updated ONLY after NIW validation
    CLAUDE.md          ← production spec (see NETWEAVE_GRAPH.md)
```

Data flows one way: `netweave-lab` reads from `netweave/data/processed/` as
input. It never writes back. Production code changes are made manually after
a NIW experiment is declared validated.

---

## Repository Layout

```
netweave-lab/
├── CLAUDE.md                        ← this file
├── requirements.txt
├── mlflow.db                        ← local MLflow tracking store (auto-created)
├── shared/                          ← symlink or copy of netweave/data/processed/
│   ├── nodes.parquet
│   └── edges.parquet
├── experiments/
│   ├── EXP001_tie_strength/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   ├── EXP002_domain_classifier/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   ├── EXP003_faiss_index/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   ├── EXP004_llm_enrichment/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   ├── EXP005_layout_readability/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   ├── EXP006_pathfinding_algos/
│   │   ├── notebook.ipynb
│   │   └── README.md
│   └── EXP007_second_degree/
│       ├── notebook.ipynb
│       └── README.md
├── templates/
│   ├── experiment_template.ipynb    ← copy this to start any new experiment
│   └── experiment_readme.md        ← copy this for each experiment README
├── lib/
│   ├── niw_graph.py                 ← shared graph-loading utilities
│   ├── niw_metrics.py               ← shared evaluation metric functions
│   ├── niw_viz.py                   ← shared visualization helpers
│   └── niw_mlflow.py                ← shared MLflow logging helpers
└── dashboard/
    └── compare.ipynb                ← cross-experiment comparison dashboard
```

---

## Tech Stack

```
python           3.11+
jupyterlab       4.x          — primary UI
networkx         3.x          — graph construction and algorithms
pandas           2.x          — node/edge tables
pyarrow          — parquet I/O
matplotlib       3.x          — static plots
panel            1.x          — interactive parameter sliders in notebooks
mlflow           2.x          — experiment tracking and run comparison
py4cytoscape     1.x          — Python ↔ Cytoscape Desktop bridge
faiss-cpu        1.x          — vector index experiments
sentence-transformers         — node embedding generation
anthropic        — Claude API calls for enrichment experiments
scikit-learn     — cosine similarity, classification metrics
pytest           — sanity tests on shared lib functions
```

Install all: `pip install jupyterlab networkx pandas pyarrow matplotlib panel
mlflow py4cytoscape faiss-cpu sentence-transformers anthropic scikit-learn pytest`

External tools (install separately, not via pip):
- **Cytoscape Desktop** — download from cytoscape.org; must be running for
  py4cytoscape calls to work. Launch before running EXP005.
- **Gephi** — download from gephi.org; used for ForceAtlas2 on large graphs.
  NIW exports GraphML files; Gephi is opened manually.

---

## Experiment Registry

All planned experiments are listed here. Add new experiments by appending to
this table. Never reuse an experiment ID.

| ID     | Question being tested                                    | Primary tool       | Status  |
|--------|----------------------------------------------------------|--------------------|---------|
| EXP001 | Which tie-strength decay function ranks intros best?     | NetworkX + Panel   | planned |
| EXP002 | Does Claude API enrichment add signal over keywords?     | Anthropic API      | planned |
| EXP003 | Which FAISS index type gives best recall at <5K nodes?   | FAISS + NetworkX   | planned |
| EXP004 | Does LLM-generated employer_desc improve domain tags?    | Anthropic API      | planned |
| EXP005 | Which graph layout best reveals intro path structure?    | py4cytoscape       | planned |
| EXP006 | Which path-finding algo produces highest-quality intros? | NetworkX           | planned |
| EXP007 | What OSINT signals best predict second-degree relevance? | Brave + NetworkX   | planned |

---

## Standard Experiment Structure

Every experiment notebook follows this exact cell structure. Claude Code must
use this structure when scaffolding any new experiment notebook.

### Cell 1 — Experiment header (markdown)
```markdown
# EXP00N — [Short title]

**Question:** [One sentence — the design decision being tested]
**Hypothesis:** [What you expect to find and why]
**Success criterion:** [Specific measurable threshold that would validate the hypothesis]
**Production impact:** [Which function in netweave/src/ would change if validated]
**Author:** Chuck Wiley  **Date:** YYYY-MM-DD
```

### Cell 2 — Imports and MLflow setup
```python
import mlflow
import mlflow.tracking
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lib.niw_graph import load_graph
from lib.niw_metrics import ndcg_at_k, precision_at_k
from lib.niw_mlflow import start_run, log_result

EXPERIMENT_ID = "EXP00N"
EXPERIMENT_NAME = "[Short title]"
mlflow.set_experiment(EXPERIMENT_NAME)
```

### Cell 3 — Load data
```python
# Always load from shared/ — never modify source data
G = load_graph(
    nodes_path="shared/nodes.parquet",
    edges_path="shared/edges.parquet"
)
print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
```

### Cell 4 — Define variants
```python
# Each variant is one value of the design parameter being tested
variants = {
    "variant_A": {"param": value_A},
    "variant_B": {"param": value_B},
    "variant_C": {"param": value_C},
}
```

### Cell 5 — Run experiment loop
```python
results = []
for variant_name, params in variants.items():
    with mlflow.start_run(run_name=f"{EXPERIMENT_ID}_{variant_name}"):
        mlflow.log_params(params)

        # --- YOUR EXPERIMENT CODE HERE ---
        ranked_contacts = run_variant(G, **params)
        # ---------------------------------

        score = evaluate(ranked_contacts)
        mlflow.log_metric("ndcg_at_10", score)
        results.append({"variant": variant_name, "score": score, **params})
        print(f"{variant_name}: {score:.4f}")

results_df = pd.DataFrame(results).sort_values("score", ascending=False)
```

### Cell 6 — Visualize comparison
```python
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(results_df["variant"], results_df["score"])
ax.set_xlabel("NDCG@10")
ax.set_title(f"{EXPERIMENT_ID}: {EXPERIMENT_NAME}")
plt.tight_layout()
plt.savefig(f"experiments/{EXPERIMENT_ID}/results.png", dpi=150)
plt.show()
```

### Cell 7 — Decision (markdown)
```markdown
## Result and Decision

**Winner:** variant_X (score: N.NN)
**Margin over baseline:** +N.NN
**Decision:** [VALIDATED | INCONCLUSIVE | REJECTED]

**If VALIDATED — production change:**
File: `netweave/src/[filename].py`
Function: `[function_name]`
Change: [one sentence description of what changes]
Notebook citation to add as comment: `# Validated in EXP00N — see netweave-lab/experiments/EXP00N/`
```

---

## Shared Library Specifications

Claude Code must implement these four modules in `lib/` before scaffolding
any experiment notebooks. They are the foundation every experiment depends on.

### lib/niw_graph.py

```python
def load_graph(nodes_path: str, edges_path: str) -> nx.DiGraph:
    """
    Load nodes.parquet and edges.parquet into a NetworkX DiGraph.
    Node attributes: all columns from nodes.parquet keyed on node_id.
    Edge attributes: tie_strength, role_fit, intro_likelihood, composite.
    domain_score is NOT stored on edges — it is computed at query time.
    """

def graph_summary(G: nx.DiGraph) -> dict:
    """
    Return dict with: n_nodes, n_edges, density, avg_degree,
    domain_tag_distribution, seniority_distribution.
    Used as sanity check at top of every experiment.
    """

def filter_by_domain(G: nx.DiGraph, tags: list[str]) -> nx.DiGraph:
    """
    Return subgraph containing only nodes whose domain_tags
    overlap with the provided tags list.
    """

def export_graphml(G: nx.DiGraph, path: str) -> None:
    """
    Export graph to GraphML format for Gephi import.
    Flatten list attributes (domain_tags) to pipe-delimited strings.
    """
```

### lib/niw_metrics.py

```python
def ndcg_at_k(ranked_list: list[str], relevant_set: set[str], k: int = 10) -> float:
    """
    Normalized Discounted Cumulative Gain at k.
    Primary ranking quality metric across all experiments.
    ranked_list: node_ids in ranked order (best first)
    relevant_set: ground truth node_ids that are genuinely relevant
    """

def precision_at_k(ranked_list: list[str], relevant_set: set[str], k: int = 10) -> float:
    """
    Fraction of top-k results that are in relevant_set.
    Secondary metric — simpler to interpret than NDCG.
    """

def rank_correlation(list_a: list[str], list_b: list[str]) -> float:
    """
    Spearman rank correlation between two ranked node lists.
    Used to compare how similar two variant rankings are.
    """

def build_ground_truth(G: nx.DiGraph, goal_tags: list[str]) -> set[str]:
    """
    Construct a ground truth relevant set by selecting nodes where:
    - domain_tags overlap with goal_tags (Jaccard >= 0.5)
    - seniority in [executive, director, founder]
    Used as the relevant_set for NDCG/precision evaluation when
    no human-labeled ground truth exists.
    """
```

### lib/niw_viz.py

```python
def plot_ranked_contacts(ranked_df: pd.DataFrame, title: str, top_n: int = 15) -> None:
    """
    Horizontal bar chart of top_n contacts with composite score.
    Color bars by domain_tag (one color per tag from a fixed palette).
    Save to calling experiment's results/ subfolder automatically.
    """

def plot_score_distribution(G: nx.DiGraph, score_attr: str) -> None:
    """
    Histogram of a given edge or node attribute across the full graph.
    Used to inspect score distributions before and after parameter changes.
    """

def plot_variant_comparison(results_df: pd.DataFrame, metric: str) -> None:
    """
    Side-by-side bar chart comparing variants on a given metric.
    Standard output for Cell 6 of every experiment.
    """

def push_to_cytoscape(G: nx.DiGraph, style: str = "default") -> None:
    """
    Push graph to running Cytoscape Desktop instance via py4cytoscape.
    Requires Cytoscape to be running on localhost:1234 (default CyREST port).
    Maps composite edge weight to edge width and domain_tag to node color.
    Silently skips (with warning) if Cytoscape is not running.
    """
```

### lib/niw_mlflow.py

```python
def start_run(experiment_id: str, variant_name: str, params: dict) -> mlflow.ActiveRun:
    """
    Convenience wrapper for mlflow.start_run that auto-logs:
    - experiment_id, variant_name, timestamp
    - graph stats (n_nodes, n_edges) from shared/
    - python version and key package versions
    Returns the active run context manager.
    """

def log_result(run: mlflow.ActiveRun, metrics: dict, artifacts: list[str]) -> None:
    """
    Log metrics dict and a list of artifact file paths to the active run.
    Prints a one-line summary: EXP00N | variant_X | metric=N.NN
    """

def compare_runs(experiment_name: str, metric: str = "ndcg_at_10") -> pd.DataFrame:
    """
    Pull all runs for an experiment from MLflow and return a sorted DataFrame.
    Used in Cell 6 and in the cross-experiment comparison dashboard.
    """
```

---

## Experiment Specifications

Detailed specs for each of the seven planned experiments. Claude Code should
use these as the implementation guide when scaffolding each notebook.

---

### EXP001 — Tie Strength Decay Function

**Question:** Which decay function best models relationship warmth from connection
recency data?

**Variants to test:**

```python
import math

def exponential_decay(days: int, half_life: int) -> float:
    return math.exp(-0.693 * days / half_life)

variants = {
    "exp_180":  lambda d: exponential_decay(d, 180),
    "exp_365":  lambda d: exponential_decay(d, 365),   # production baseline
    "exp_730":  lambda d: exponential_decay(d, 730),
    "linear":   lambda d: max(0, 1 - (d / 1095)),      # 3-year linear decay
    "step":     lambda d: 1.0 if d <= 180 else 0.6 if d <= 540 else 0.3,
}
```

**Evaluation:** For each variant, re-score all edges, re-run the LipoNexus query
("Find MASLD investors and clinical partners"), compute NDCG@10 against
`build_ground_truth(G, ["medical_diagnostics", "biotech", "investor"])`.

**Panel slider (add after loop):** Build an interactive slider for half_life
(90–1095 days) that re-renders the ranked contact list in real time. This
gives intuition beyond the metric numbers.

```python
import panel as pn
pn.extension()

half_life_slider = pn.widgets.IntSlider(name="Half-life (days)", start=90, end=1095, step=30, value=365)

@pn.depends(half_life_slider)
def ranked_output(half_life):
    scores = {nid: exponential_decay(G.nodes[nid].get("recency_days", 999), half_life)
              for nid in G.nodes}
    top = sorted(scores, key=scores.get, reverse=True)[:10]
    return pn.pane.DataFrame(pd.DataFrame([(n, f"{scores[n]:.3f}") for n in top],
                             columns=["node_id", "tie_strength"]))

pn.Column(half_life_slider, ranked_output).servable()
```

**Production impact:** `netweave/src/edges.py` → `tie_strength()` function.

---

### EXP002 — Domain Classifier: Keyword vs. Claude API

**Question:** Does calling the Claude API for node classification produce
meaningfully better domain tags than keyword matching alone?

**Variants to test:**
- `keyword_only` — existing taxonomy.py keyword classifier
- `claude_zero_shot` — Claude API with company + position, no examples
- `claude_few_shot` — Claude API with 6 labeled examples in the prompt
- `claude_few_shot_brave` — Claude API + Brave Search employer description

**Evaluation protocol:**
1. Hand-label 30 nodes (5 per domain) as ground truth. Store in
   `experiments/EXP002/ground_truth.json`.
2. Run each classifier on all 30 nodes.
3. Compute: precision, recall, F1 per domain tag; overall accuracy; API cost.
4. Log all four metrics + cost per node to MLflow.

**Cost tracking (critical):** Log `cost_per_node_usd` as an MLflow metric.
Claude API enrichment must justify its cost with measurable F1 improvement.
If `claude_zero_shot` F1 < `keyword_only` F1 + 0.05, keyword_only wins.

**Production impact:** `netweave/src/taxonomy.py` → `classify_node()` function.

---

### EXP003 — FAISS Index Type vs. Recall

**Question:** Which FAISS index type gives acceptable recall for NetWeave's
node embedding similarity search at current and projected node counts?

**Context:** When second-degree expansion is added in v2, FAISS will be used
to find second-degree candidates similar to high-scoring first-degree nodes.
The right index type depends on node count and acceptable recall/speed tradeoff.

**Variants to test:**

```python
import faiss
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Build embeddings from node text: "{company} {position} {domain_tags}"
node_texts = [...]
embeddings = encoder.encode(node_texts).astype("float32")
d = embeddings.shape[1]  # 384 for MiniLM

variants = {
    "flat_l2":     faiss.IndexFlatL2(d),
    "flat_ip":     faiss.IndexFlatIP(d),         # inner product (cosine if normalized)
    "ivf_flat":    faiss.index_factory(d, "IVF16,Flat"),
    "hnsw":        faiss.index_factory(d, "HNSW32"),
}
```

**Evaluation:** For each index, run 20 random query nodes and measure:
- Recall@10 (fraction of true top-10 nearest neighbors found)
- Query latency (ms)
- Index build time (ms)
- Memory footprint (MB)

**Scale simulation:** Run at 500, 1K, 2K, and 5K synthetic nodes (pad real
nodes with synthetic embeddings) to project performance at second-degree scale.

**Production impact:** `netweave/src/expand.py` → index type selection in v2 build.

---

### EXP004 — LLM Enrichment Signal Value

**Question:** Does the `employer_desc` field generated by Claude API during
node enrichment (Step 2) improve downstream query ranking quality?

**Variants to test:**
- `no_desc` — nodes enriched with keyword classifier only, no employer_desc
- `with_desc` — nodes enriched with Claude-generated employer_desc included
  in the embedding used for domain_score computation

**Evaluation:** Re-embed all nodes under each variant. Re-run the LipoNexus
query. Compute NDCG@10. Also compute rank_correlation between variants to
measure how much the ranking actually changes.

**Key question to answer:** Does employer_desc add signal, or does it add
noise that hurts ranking? If rank_correlation > 0.95, the descriptions are
not changing the ranking meaningfully — not worth the API cost.

**Production impact:** `netweave/src/enrich.py` → decision on whether
employer_desc is included in embedding input.

---

### EXP005 — Graph Layout Readability for Introduction Paths

**Question:** Which Cytoscape layout algorithm makes introduction path
structure most readable for a client deliverable?

**Setup:** This experiment requires Cytoscape Desktop running on localhost.
Run `push_to_cytoscape(G)` from `lib/niw_viz.py` to load the graph, then
apply layouts programmatically via py4cytoscape.

**Layouts to compare:**

```python
import py4cytoscape as p4c

layouts = [
    "force-directed",        # COSE — default, good for medium graphs
    "hierarchical",          # good for showing path structure
    "circular",              # good for showing clusters
    "kamada-kawai",          # good for small graphs, path clarity
    "prefuse-force-directed", # ForceAtlas2 equivalent in Cytoscape
]

for layout in layouts:
    p4c.layout_network(layout)
    p4c.export_image(f"experiments/EXP005/{layout}.png", type="PNG", resolution=150)
```

**Evaluation:** This experiment is **qualitative**, not metric-driven.
After generating images, rate each layout on:
- Introduction path legibility (1–5)
- Cluster separation (1–5)
- Node label readability (1–5)

Log ratings as MLflow metrics. Winner is the layout used in client deliverables.

**Edge weight visualization:** Map `composite` edge weight to edge width
(thin = weak, thick = strong) and `domain_tags[0]` to node color before
exporting. This is the visual style that should carry into production reports.

**Production impact:** `netweave/src/query.py` → default layout parameter
when pushing output to Cytoscape for client review.

**Note:** If Cytoscape Desktop is unavailable, export GraphML via
`export_graphml()` and open manually in Gephi. Use ForceAtlas2 with
LinLog mode on for the Gephi variant.

---

### EXP006 — Path-Finding Algorithm Comparison

**Question:** Which path-finding algorithm surfaces the highest-quality
introduction paths in the NetWeave graph?

**Variants to test:**

```python
import networkx as nx

source = CHUCK_NODE_ID  # set from env

def dijkstra_path(G, target):
    # Invert composite weight (higher = shorter path)
    G_inv = G.copy()
    for u, v, d in G_inv.edges(data=True):
        d["inv_weight"] = 1 - d.get("composite", 0.5)
    return nx.dijkstra_path(G_inv, source, target, weight="inv_weight")

def astar_path(G, target):
    # A* with domain_score heuristic
    def heuristic(u, v):
        return 1 - G.nodes[v].get("domain_score", 0)
    G_inv = G.copy()
    for u, v, d in G_inv.edges(data=True):
        d["inv_weight"] = 1 - d.get("composite", 0.5)
    return nx.astar_path(G_inv, source, target, heuristic=heuristic, weight="inv_weight")

def top_k_neighbors(G, target, k=3):
    # Simple: return top-k neighbors of target ranked by tie_strength
    neighbors = list(G.predecessors(target))
    return sorted(neighbors, key=lambda n: G[n][target].get("tie_strength", 0), reverse=True)[:k]

variants = {
    "dijkstra":         dijkstra_path,
    "astar":            astar_path,
    "top_k_neighbors":  top_k_neighbors,
}
```

**Evaluation:** Run each algorithm against 10 target nodes (manually selected
as known-hard-to-reach contacts). Score each path on:
- Path composite weight (product of edge composites along path)
- Path length (fewer hops = better, max 3)
- Whether path passes through a known trusted intermediary (manual binary label)

**Production impact:** `netweave/src/query.py` → path-finding function used
in the goal-driven query engine.

---

### EXP007 — Second-Degree Node Signal Quality

**Question:** Which OSINT signals most reliably predict that a second-degree
node (connection of a connection) is relevant to a given client goal?

**Context:** This experiment is forward-looking — it informs the v2 design
of `netweave/src/expand.py`. It requires manual collection of a small
second-degree node sample as test data.

**Setup:** Manually pull 20 second-degree nodes via LinkedIn profile inspection
for 3–5 of your highest-scoring first-degree connections. Label each as
relevant or not-relevant to the LipoNexus goal. Store in
`experiments/EXP007/second_degree_sample.json`.

**OSINT signal variants to test:**

```python
signal_extractors = {
    "title_keyword":   lambda node: keyword_match(node["position"]),
    "employer_match":  lambda node: jaccard(node["employer_tags"], goal_tags),
    "patent_signal":   lambda node: bool(node.get("patent_count", 0)),
    "grant_signal":    lambda node: bool(node.get("sbir_grant", False)),
    "embedding_sim":   lambda node: cosine_sim(node["embedding"], goal_embedding),
    "combined":        lambda node: weighted_combination(node, goal_tags),
}
```

**Evaluation:** For each signal, compute precision and recall against
the 20-node ground truth sample. The winning signal combination becomes
the relevance scorer in v2 second-degree expansion.

**Production impact:** `netweave/src/expand.py` → second-degree relevance
scoring function (v2 implementation).

---

## Cross-Experiment Comparison Dashboard

`dashboard/compare.ipynb` is a standing notebook that pulls all MLflow run
results and displays a cross-experiment summary. It does not run experiments —
it only reads results.

```python
# dashboard/compare.ipynb — structure

# Cell 1: Load all experiment results
client = mlflow.tracking.MlflowClient()
all_runs = {}
for exp_name in ["EXP001", "EXP002", "EXP003", "EXP004", "EXP006"]:
    exp = client.get_experiment_by_name(exp_name)
    runs = client.search_runs(exp.experiment_id, order_by=["metrics.ndcg_at_10 DESC"])
    all_runs[exp_name] = pd.DataFrame([{
        "variant": r.data.tags.get("mlflow.runName"),
        "ndcg_at_10": r.data.metrics.get("ndcg_at_10"),
        "status": r.data.tags.get("decision", "pending"),
        **r.data.params
    } for r in runs])

# Cell 2: Winners table
winners = {exp: df.iloc[0] for exp, df in all_runs.items() if not df.empty}
pd.DataFrame(winners).T[["variant", "ndcg_at_10", "status"]]

# Cell 3: Production change log
# Manual markdown cell — updated after each VALIDATED decision
```

---

## Merge Protocol — Lab to Production

When an experiment is declared VALIDATED, follow this exact sequence:

1. **Update experiment README.md** with:
   - Final decision and winning variant parameters
   - The MLflow run ID of the winning run
   - Date of decision

2. **Open the production `netweave/src/` file** that needs to change.

3. **Make the minimal change** — only the function identified in the experiment
   spec. No refactoring, no opportunistic improvements.

4. **Add a citation comment** immediately above the changed code:
   ```python
   # Validated: EXP001 (exp_365 half-life) — see netweave-lab/experiments/EXP001/
   # NDCG@10: 0.847 vs baseline 0.803 (+0.044)
   ```

5. **Update `dashboard/compare.ipynb`** production change log cell.

6. **Run `pytest netweave/tests/`** — all tests must pass before considering
   the merge complete.

---

## First Run Checklist

Before running any experiment:

- [ ] Install all packages: `pip install -r requirements.txt`
- [ ] Copy or symlink `netweave/data/processed/` → `netweave-lab/shared/`
- [ ] Set env vars: `ANTHROPIC_API_KEY`, `BRAVE_API_KEY`, `CHUCK_LINKEDIN_URL`
- [ ] Run `mlflow ui` and confirm dashboard opens at localhost:5000
- [ ] Run `python -c "from lib.niw_graph import load_graph; G = load_graph('shared/nodes.parquet', 'shared/edges.parquet'); print(G)"` — confirm graph loads
- [ ] Run `pytest lib/` — all shared library tests green
- [ ] For EXP005 only: launch Cytoscape Desktop and confirm `p4c.cytoscape_ping()` returns OK

**Start with EXP001** — it requires no API calls, runs fast, and validates
the entire experiment scaffolding before spending any budget.

---

## Known Constraints

- MLflow runs locally (SQLite backend). Do not deploy a remote tracking server
  until node count exceeds 10K or multiple team members need concurrent access.
- py4cytoscape requires Cytoscape Desktop running locally. If unavailable,
  EXP005 falls back to Gephi GraphML export — document the fallback in the
  experiment README.
- Ground truth for NDCG evaluation is synthetic (build_ground_truth) unless
  manually labeled. Treat NDCG scores as relative comparisons between variants,
  not absolute quality measures.
- EXP007 requires manual data collection. Allocate 2–3 hours for the
  second-degree node labeling before running the notebook.
- API costs: EXP002 and EXP004 make Claude API calls. Budget ~$2–5 for a
  full experiment run on a 500-node graph. Log cost_per_node_usd to MLflow.
