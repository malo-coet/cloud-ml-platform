from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from trainer.config import settings
from trainer.models import TrainingJob

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def claim_next_job(session: Session) -> TrainingJob | None:
    """Atomically pick the oldest queued job and mark it running.

    FOR UPDATE SKIP LOCKED makes this safe with several worker replicas:
    two workers can never claim the same job.
    """
    stmt = (
        select(TrainingJob)
        .where(TrainingJob.status == "queued")
        .order_by(TrainingJob.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = session.scalars(stmt).first()
    if job is not None:
        job.status = "running"
        job.started_at = datetime.now(UTC)
        session.commit()
    return job
