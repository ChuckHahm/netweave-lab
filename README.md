# NetWeave Intelligence Workbench (NIW)

A research harness for running controlled experiments on graph design decisions. Validated results feed the production [NetWeave](../netweave/) pipeline.

## What this is

The NIW runs seven experiments that test specific design alternatives — decay functions, classifiers, index types, layout algorithms, pathfinding approaches — and logs every run to MLflow so results are reproducible and comparable. The best-validated choice from each experiment becomes a pull request to `netweave/src/`.

Data flows one way: NIW reads from `netweave/data/processed/`, never writes back.

## Experiments

| ID | Question | Tool | Status |
|----|----------|------|--------|
| EXP001 | Which tie-strength decay function ranks intros best? | NetworkX + Panel | planned |
| EXP002 | Does Claude API enrichment add signal over keywords? | Anthropic API | planned |
| EXP003 | Which FAISS index type gives best recall at <5K nodes? | FAISS + NetworkX | planned |
| EXP004 | Does LLM-generated employer_desc improve domain tags? | Anthropic API | planned |
| EXP005 | Which graph layout best reveals intro path structure? | py4cytoscape | planned |
| EXP006 | Which path-finding algo produces highest-quality intros? | NetworkX | planned |
| EXP007 | What OSINT signals best predict second-degree relevance? | Brave + NetworkX | planned |

## Structure

```
experiments/      — one notebook + README per experiment
lib/              — shared utilities (graph loading, metrics, viz, MLflow)
templates/        — copy these to start a new experiment
dashboard/        — cross-experiment comparison notebook
shared/           — symlink to netweave/data/processed/ (read-only)
```

## Setup

```bash
pip install jupyterlab networkx pandas pyarrow matplotlib panel mlflow \
            py4cytoscape faiss-cpu sentence-transformers anthropic \
            scikit-learn pytest
```

External tools (install separately):
- **Cytoscape Desktop** — cytoscape.org (required for EXP005)
- **Gephi** — gephi.org (fallback for EXP005 if Cytoscape unavailable)

Environment variables:
```bash
export ANTHROPIC_API_KEY=...
export BRAVE_API_KEY=...
export CHUCK_LINKEDIN_URL=...
```

## Running experiments

Start with **EXP001** — no API calls, fast, validates the full scaffolding:

```bash
# Symlink or copy processed data
ln -s ../netweave/data/processed/ shared/

# Start MLflow tracking UI
mlflow ui  # opens at localhost:5000

# Run sanity tests
pytest lib/

# Launch JupyterLab
jupyter lab
```

Then open `experiments/EXP001_tie_strength/notebook.ipynb`.

## Merge protocol

When an experiment is declared **VALIDATED**:

1. Update the experiment `README.md` with the winning variant, MLflow run ID, and date
2. Make the minimal change to the identified function in `netweave/src/`
3. Add a citation comment above the changed code:
   ```python
   # Validated: EXP001 (exp_365 half-life) — see netweave-lab/experiments/EXP001/
   # NDCG@10: 0.847 vs baseline 0.803 (+0.044)
   ```
4. Update `dashboard/compare.ipynb` production change log
5. Run `pytest netweave/tests/` — all tests must pass
