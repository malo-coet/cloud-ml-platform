"""Read-only client for the MLflow REST API.

Uses plain HTTP calls instead of the mlflow package to keep the API image small.
"""

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_TIMEOUT = 10.0


def _request(method: str, path: str, **kwargs) -> dict:
    url = f"{settings.mlflow_tracking_uri.rstrip('/')}/api/2.0/mlflow/{path}"
    try:
        response = httpx.request(method, url, timeout=_TIMEOUT, **kwargs)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MLflow tracking server is unavailable",
        ) from exc
    return response.json()


def list_runs(limit: int = 50) -> list[dict]:
    """Latest runs across every experiment, with their params and metrics."""
    experiments = _request(
        "GET", "experiments/search", params={"max_results": 200}
    ).get("experiments", [])
    if not experiments:
        return []
    names = {e["experiment_id"]: e["name"] for e in experiments}
    body = {
        "experiment_ids": list(names),
        "max_results": min(limit, 100),
        "order_by": ["attributes.start_time DESC"],
    }
    runs = _request("POST", "runs/search", json=body).get("runs", [])
    return [
        {
            "run_id": run["info"]["run_id"],
            "run_name": run["info"].get("run_name"),
            "experiment": names.get(run["info"]["experiment_id"]),
            "status": run["info"]["status"],
            "start_time": run["info"].get("start_time"),
            "end_time": run["info"].get("end_time"),
            "metrics": {m["key"]: m["value"] for m in run.get("data", {}).get("metrics", [])},
            "params": {p["key"]: p["value"] for p in run.get("data", {}).get("params", [])},
        }
        for run in runs
    ]


def list_registered_models() -> list[dict]:
    """Models in the MLflow Model Registry with their latest versions."""
    models = _request(
        "GET", "registered-models/search", params={"max_results": 100}
    ).get("registered_models", [])
    return [
        {
            "name": model["name"],
            "created_at": model.get("creation_timestamp"),
            "last_updated_at": model.get("last_updated_timestamp"),
            "latest_versions": [
                {
                    "version": version["version"],
                    "stage": version.get("current_stage"),
                    "run_id": version.get("run_id"),
                    "status": version.get("status"),
                }
                for version in model.get("latest_versions", [])
            ],
        }
        for model in models
    ]
