from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.services import mlflow_client

router = APIRouter(tags=["experiments"])


@router.get("/experiments")
def list_experiments(_: CurrentUser, limit: int = 50) -> list[dict]:
    """Latest MLflow runs (all experiments) with params and metrics."""
    return mlflow_client.list_runs(limit=limit)


@router.get("/models")
def list_models(_: CurrentUser) -> list[dict]:
    """Models registered in the MLflow Model Registry."""
    return mlflow_client.list_registered_models()
