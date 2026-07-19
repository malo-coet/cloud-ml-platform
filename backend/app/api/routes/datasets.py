from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.models.dataset import Dataset, DatasetFormat
from app.models.user import User, UserRole
from app.schemas.dataset import DatasetDownload, DatasetRead
from app.services.storage import Storage

router = APIRouter(prefix="/datasets", tags=["datasets"])

_EXTENSION_FORMATS = {
    ".csv": DatasetFormat.csv,
    ".parquet": DatasetFormat.parquet,
    ".zip": DatasetFormat.zip,
    ".png": DatasetFormat.image,
    ".jpg": DatasetFormat.image,
    ".jpeg": DatasetFormat.image,
}

DOWNLOAD_URL_TTL_SECONDS = 900


def _get_accessible_dataset(dataset_id: UUID, user: User, db: Session) -> Dataset:
    """Fetch a dataset the user owns (admins can access everything).

    Returns 404 rather than 403 for foreign datasets to avoid leaking their existence.
    """
    dataset = db.get(Dataset, dataset_id)
    if dataset is None or (dataset.owner_id != user.id and user.role != UserRole.admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return dataset


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    user: CurrentUser,
    db: DbSession,
    storage: Storage,
    file: UploadFile,
    name: Annotated[str | None, Form(min_length=1, max_length=255)] = None,
) -> Dataset:
    """Upload a dataset file. Re-uploading under the same name creates a new version."""
    filename = Path(file.filename or "upload").name
    dataset_format = _EXTENSION_FORMATS.get(Path(filename).suffix.lower())
    if dataset_format is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type — allowed: .csv, .parquet, .zip, .png, .jpg, .jpeg",
        )

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)
    if size_bytes == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    dataset_name = (name or Path(filename).stem).strip().replace("/", "-")
    latest_version = db.scalar(
        select(func.max(Dataset.version)).where(
            Dataset.owner_id == user.id, Dataset.name == dataset_name
        )
    )
    version = (latest_version or 0) + 1
    s3_key = f"{user.id}/{dataset_name}/v{version}/{filename}"

    storage.upload(file.file, s3_key, content_type=file.content_type)
    dataset = Dataset(
        owner_id=user.id,
        name=dataset_name,
        filename=filename,
        format=dataset_format,
        size_bytes=size_bytes,
        version=version,
        s3_key=s3_key,
    )
    db.add(dataset)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        storage.delete(s3_key)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Concurrent upload of the same dataset — please retry",
        ) from None
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetRead])
def list_datasets(
    user: CurrentUser, db: DbSession, skip: int = 0, limit: int = 50
) -> list[Dataset]:
    """List your own datasets, newest first (every version is a separate entry)."""
    stmt = (
        select(Dataset)
        .where(Dataset.owner_id == user.id)
        .order_by(Dataset.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
    )
    return list(db.scalars(stmt))


@router.get("/{dataset_id}", response_model=DatasetRead)
def read_dataset(dataset_id: UUID, user: CurrentUser, db: DbSession) -> Dataset:
    return _get_accessible_dataset(dataset_id, user, db)


@router.get("/{dataset_id}/download", response_model=DatasetDownload)
def download_dataset(
    dataset_id: UUID, user: CurrentUser, db: DbSession, storage: Storage
) -> DatasetDownload:
    """Return a short-lived presigned URL — the file is served by object storage directly."""
    dataset = _get_accessible_dataset(dataset_id, user, db)
    url = storage.presigned_download_url(
        dataset.s3_key, dataset.filename, expires_in=DOWNLOAD_URL_TTL_SECONDS
    )
    return DatasetDownload(url=url, expires_in=DOWNLOAD_URL_TTL_SECONDS)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: UUID, user: CurrentUser, db: DbSession, storage: Storage
) -> None:
    dataset = _get_accessible_dataset(dataset_id, user, db)
    storage.delete(dataset.s3_key)
    db.delete(dataset)
    db.commit()
