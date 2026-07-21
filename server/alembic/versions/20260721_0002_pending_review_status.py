"""Rename pending prescription status to pending_review.

Revision ID: 20260721_0002
Revises: 20260721_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260721_0002"
down_revision: str | None = "20260721_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

old_status = sa.Enum(
    "pending", "reviewed", "flagged", name="prescriptionstatus", native_enum=False
)
new_status = sa.Enum(
    "pending_review",
    "reviewed",
    "flagged",
    name="prescriptionstatus",
    native_enum=False,
)


def upgrade() -> None:
    op.alter_column(
        "prescriptions",
        "status",
        existing_type=old_status,
        type_=new_status,
        existing_nullable=False,
    )
    op.execute(
        sa.text(
            "UPDATE prescriptions SET status = 'pending_review' "
            "WHERE status = 'pending'"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE prescriptions SET status = 'pending' "
            "WHERE status = 'pending_review'"
        )
    )
    op.alter_column(
        "prescriptions",
        "status",
        existing_type=new_status,
        type_=old_status,
        existing_nullable=False,
    )
