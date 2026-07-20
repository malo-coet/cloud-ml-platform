"""create training jobs table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "training_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Uuid(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "model_type",
            sa.Enum("logistic_regression", "random_forest", name="model_type"),
            nullable=False,
        ),
        sa.Column("target_column", sa.String(length=255), nullable=True),
        sa.Column("hyperparameters", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "completed", "failed", name="job_status"),
            nullable=False,
        ),
        sa.Column("error", sa.String(length=2000), nullable=True),
        sa.Column("mlflow_run_id", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_training_jobs_dataset_id"), "training_jobs", ["dataset_id"])
    op.create_index(op.f("ix_training_jobs_owner_id"), "training_jobs", ["owner_id"])
    op.create_index(op.f("ix_training_jobs_status"), "training_jobs", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_training_jobs_status"), table_name="training_jobs")
    op.drop_index(op.f("ix_training_jobs_owner_id"), table_name="training_jobs")
    op.drop_index(op.f("ix_training_jobs_dataset_id"), table_name="training_jobs")
    op.drop_table("training_jobs")
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="model_type").drop(op.get_bind(), checkfirst=True)
