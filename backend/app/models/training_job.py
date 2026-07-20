import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelType(enum.StrEnum):
    logistic_regression = "logistic_regression"
    random_forest = "random_forest"


class JobStatus(enum.StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class TrainingJob(Base):
    """A training request and its lifecycle — executed by the training service."""

    __tablename__ = "training_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    model_type: Mapped[ModelType] = mapped_column(Enum(ModelType, name="model_type"))
    target_column: Mapped[str | None] = mapped_column(String(255), default=None)
    hyperparameters: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.queued, index=True
    )
    error: Mapped[str | None] = mapped_column(String(2000), default=None)
    mlflow_run_id: Mapped[str | None] = mapped_column(String(64), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
