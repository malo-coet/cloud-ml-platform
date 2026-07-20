from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.api.routes.datasets import _get_accessible_dataset
from app.models.dataset import DatasetFormat
from app.models.training_job import TrainingJob
from app.models.user import UserRole
from app.schemas.training_job import TrainingJobRead, TrainRequest

router = APIRouter(prefix="/train", tags=["training"])


@router.post("", response_model=TrainingJobRead, status_code=status.HTTP_202_ACCEPTED)
def request_training(payload: TrainRequest, user: CurrentUser, db: DbSession) -> TrainingJob:
    """Queue a training job — the training service picks it up asynchronously."""
    dataset = _get_accessible_dataset(payload.dataset_id, user, db)
    if dataset.format != DatasetFormat.csv:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only CSV datasets can be trained on for now",
        )
    job = TrainingJob(
        dataset_id=dataset.id,
        owner_id=user.id,
        model_type=payload.model_type,
        target_column=payload.target_column,
        hyperparameters=payload.hyperparameters,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[TrainingJobRead])
def list_training_jobs(
    user: CurrentUser, db: DbSession, skip: int = 0, limit: int = 50
) -> list[TrainingJob]:
    """Your training jobs, newest first."""
    stmt = (
        select(TrainingJob)
        .where(TrainingJob.owner_id == user.id)
        .order_by(TrainingJob.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
    )
    return list(db.scalars(stmt))


@router.get("/{job_id}", response_model=TrainingJobRead)
def read_training_job(job_id: UUID, user: CurrentUser, db: DbSession) -> TrainingJob:
    job = db.get(TrainingJob, job_id)
    if job is None or (job.owner_id != user.id and user.role != UserRole.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
