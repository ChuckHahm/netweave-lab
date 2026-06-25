import os
import sys
import time
import importlib.metadata
import mlflow
import mlflow.tracking
import pandas as pd

MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


def _pkg_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def start_run(experiment_id: str, variant_name: str, params: dict) -> mlflow.ActiveRun:
    """
    Convenience wrapper for mlflow.start_run that auto-logs:
    - experiment_id, variant_name, timestamp
    - graph stats (n_nodes, n_edges) from shared/
    - python version and key package versions
    Returns the active run context manager.
    """
    mlflow.set_experiment(experiment_id)
    run = mlflow.start_run(run_name=f"{experiment_id}_{variant_name}")

    mlflow.log_params(params)
    mlflow.set_tags({
        "experiment_id": experiment_id,
        "variant_name": variant_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "python_version": sys.version.split()[0],
        "networkx_version": _pkg_version("networkx"),
        "pandas_version": _pkg_version("pandas"),
        "mlflow_version": _pkg_version("mlflow"),
        "anthropic_version": _pkg_version("anthropic"),
    })

    # Log graph row counts if shared/ data is available
    try:
        import pyarrow.parquet as pq
        nodes_path, edges_path = "shared/nodes.parquet", "shared/edges.parquet"
        if os.path.exists(nodes_path) and os.path.exists(edges_path):
            mlflow.log_params({
                "n_nodes": pq.read_table(nodes_path).num_rows,
                "n_edges": pq.read_table(edges_path).num_rows,
            })
    except Exception:
        pass

    return run


def log_result(run: mlflow.ActiveRun, metrics: dict, artifacts: list[str]) -> None:
    """
    Log metrics dict and a list of artifact file paths to the active run.
    Prints a one-line summary: EXP00N | variant_X | metric=N.NN
    """
    mlflow.log_metrics(metrics)

    for path in artifacts:
        if os.path.exists(path):
            mlflow.log_artifact(path)

    run_name = getattr(run.info, "run_name", None) or getattr(run, "info", {})
    summary = " | ".join(
        f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"
        for k, v in metrics.items()
    )
    print(f"{run_name} | {summary}")


def compare_runs(experiment_name: str, metric: str = "ndcg_at_10") -> pd.DataFrame:
    """
    Pull all runs for an experiment from MLflow and return a sorted DataFrame.
    Used in Cell 6 and in the cross-experiment comparison dashboard.
    Returns an empty DataFrame if the experiment does not exist yet.
    """
    client = mlflow.tracking.MlflowClient()
    exp = client.get_experiment_by_name(experiment_name)

    if exp is None:
        return pd.DataFrame()

    runs = client.search_runs(
        exp.experiment_id,
        order_by=[f"metrics.{metric} DESC"],
    )

    return pd.DataFrame([{
        "run_id": r.info.run_id,
        "variant": r.data.tags.get("mlflow.runName"),
        metric: r.data.metrics.get(metric),
        **r.data.params,
    } for r in runs])
