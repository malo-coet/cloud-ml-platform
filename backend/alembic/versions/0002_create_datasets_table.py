"""create datasets table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column(
            "format",
            sa.Enum("csv", "parquet", "zip", "image", name="dataset_format"),
            nullable=False,
        ),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("s3_key", sa.String(length=1024), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("owner_id", "name", "version", name="uq_datasets_owner_name_version"),
    )
    op.create_index(op.f("ix_datasets_owner_id"), "datasets", ["owner_id"])
    op.create_index(op.f("ix_datasets_name"), "datasets", ["name"])


def downgrade() -> None:
    op.drop_index(op.f("ix_datasets_name"), table_name="datasets")
    op.drop_index(op.f("ix_datasets_owner_id"), table_name="datasets")
    op.drop_table("datasets")
    sa.Enum(name="dataset_format").drop(op.get_bind(), checkfirst=True)
