from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.training_job import JobStatus, ModelType


class TrainRequest(BaseModel):
    dataset_id: UUID
    model_type: ModelType = ModelType.logistic_regression
    # Defaults to the last column of the CSV when omitted
    target_column: str | None = Field(default=None, min_length=1, max_length=255)
    hyperparameters: dict[str, float | int | str] = Field(default_factory=dict)


class TrainingJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dataset_id: UUID
    owner_id: UUID
    model_type: ModelType
    target_column: str | None
    hyperparameters: dict
    status: JobStatus
    error: str | None
    mlflow_run_id: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
