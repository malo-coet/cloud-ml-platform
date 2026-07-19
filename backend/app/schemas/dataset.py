from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.dataset import DatasetFormat


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    filename: str
    format: DatasetFormat
    size_bytes: int
    version: int
    created_at: datetime


class DatasetDownload(BaseModel):
    url: str
    expires_in: int
