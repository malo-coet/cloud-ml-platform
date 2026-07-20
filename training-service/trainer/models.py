"""Read/update mappings of the shared tables.

The backend owns the schema (Alembic migrations); this service only reads
datasets and updates the jobs it processes. Enum columns are declared with
their PostgreSQL type names so comparisons bind with the right type, but
values stay plain strings on the Python side.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_dataset_format = Enum("csv", "parquet", "zip", "image", name="dataset_format")
_model_type = Enum("logistic_regression", "random_forest", name="model_type")
_job_status = Enum("queued", "running", "completed", "failed", name="job_status")


class Base(DeclarativeBase):
    pass


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(_dataset_format)
    version: Mapped[int]
    s3_key: Mapped[str] = mapped_column(String(1024))


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    dataset_id: Mapped[uuid.UUID]
    owner_id: Mapped[uuid.UUID]
    model_type: Mapped[str] = mapped_column(_model_type)
    target_column: Mapped[str | None] = mapped_column(String(255))
    hyperparameters: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(_job_status)
    error: Mapped[str | None] = mapped_column(String(2000))
    mlflow_run_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
