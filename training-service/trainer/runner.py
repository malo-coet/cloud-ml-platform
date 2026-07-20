import logging
from datetime import UTC, datetime
from io import BytesIO

import boto3
import mlflow
import pandas as pd
from sqlalchemy.orm import Session

from trainer.config import settings
from trainer.models import Dataset, TrainingJob
from trainer.pipeline import TrainResult, train_dataframe

logger = logging.getLogger(__name__)

_s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)


def _load_dataframe(dataset: Dataset) -> pd.DataFrame:
    response = _s3.get_object(Bucket=settings.s3_datasets_bucket, Key=dataset.s3_key)
    return pd.read_csv(BytesIO(response["Body"].read()))


def _log_to_mlflow(dataset: Dataset, job: TrainingJob, result: TrainResult) -> str:
    """Record the run in MLflow and register the model in the Model Registry."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(dataset.name)
    run_name = f"{job.model_type}-v{dataset.version}"
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(result.params)
        mlflow.log_param("dataset_version", dataset.version)
        mlflow.log_metrics(result.metrics)
        mlflow.sklearn.log_model(
            result.model,
            name="model",
            registered_model_name=f"{dataset.name}-classifier",
        )
    return run.info.run_id


def process_job(session: Session, job: TrainingJob) -> None:
    """Run one claimed job end to end and persist its outcome."""
    try:
        dataset = session.get(Dataset, job.dataset_id)
        if dataset is None:
            raise ValueError("Dataset no longer exists")

        df = _load_dataframe(dataset)
        result = train_dataframe(
            df,
            model_type=job.model_type,
            target_column=job.target_column,
            hyperparameters=job.hyperparameters,
        )
        job.mlflow_run_id = _log_to_mlflow(dataset, job, result)
        job.status = "completed"
        logger.info("job %s completed — metrics: %s", job.id, result.metrics)
    except Exception as exc:  # noqa: BLE001 — a failed job must never kill the worker
        job.status = "failed"
        job.error = str(exc)[:2000]
        logger.exception("job %s failed", job.id)
    finally:
        job.finished_at = datetime.now(UTC)
        session.commit()
