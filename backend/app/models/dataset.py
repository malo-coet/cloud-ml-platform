import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatasetFormat(enum.StrEnum):
    csv = "csv"
    parquet = "parquet"
    zip = "zip"
    image = "image"


class Dataset(Base):
    """Metadata of an uploaded dataset — the file itself lives in object storage."""

    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", "version", name="uq_datasets_owner_name_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    format: Mapped[DatasetFormat] = mapped_column(Enum(DatasetFormat, name="dataset_format"))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    version: Mapped[int] = mapped_column(default=1)
    s3_key: Mapped[str] = mapped_column(String(1024), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
