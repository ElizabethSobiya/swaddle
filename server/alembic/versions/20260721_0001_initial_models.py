"""Create BabyCare core tables.

Revision ID: 20260721_0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260721_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = sa.Enum(
    "parent", "pediatrician", "reviewer", name="userrole", native_enum=False
)
prescription_status = sa.Enum(
    "pending", "reviewed", "flagged", name="prescriptionstatus", native_enum=False
)
content_type = sa.Enum(
    "rhyme", "video", "sound", "activity", name="contenttype", native_enum=False
)
slot_status = sa.Enum("available", "booked", name="slotstatus", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("age_min_months", sa.Integer(), nullable=False),
        sa.Column("age_max_months", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(80)), nullable=False),
    )
    op.create_index("ix_products_category", "products", ["category"])

    op.create_table(
        "content_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", content_type, nullable=False),
        sa.Column("title", sa.String(255), nullable=False, unique=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("age_min_months", sa.Integer(), nullable=False),
        sa.Column("age_max_months", sa.Integer(), nullable=False),
    )

    op.create_table(
        "consultation_slots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pediatrician_name", sa.String(255), nullable=False),
        sa.Column("slot_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", slot_status, nullable=False),
    )
    op.create_index(
        "ix_consultation_slots_slot_time",
        "consultation_slots",
        ["slot_time"],
        unique=True,
    )

    op.create_table(
        "babies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("dob", sa.Date(), nullable=False),
        sa.Column("sex", sa.String(30), nullable=False),
    )
    op.create_index("ix_babies_user_id", "babies", ["user_id"])

    op.create_table(
        "symptom_queries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "baby_id",
            sa.Integer(),
            sa.ForeignKey("babies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column("age_months", sa.Integer(), nullable=False),
        sa.Column("ai_response", sa.JSON(), nullable=False),
        sa.Column("alert_level", sa.String(30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_symptom_queries_baby_id", "symptom_queries", ["baby_id"])

    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "baby_id",
            sa.Integer(),
            sa.ForeignKey("babies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_url", sa.String(2048), nullable=False),
        sa.Column("extracted_text", sa.JSON(), nullable=False),
        sa.Column("status", prescription_status, nullable=False),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_prescriptions_baby_id", "prescriptions", ["baby_id"])
    op.create_index("ix_prescriptions_reviewer_id", "prescriptions", ["reviewer_id"])


def downgrade() -> None:
    op.drop_table("prescriptions")
    op.drop_table("symptom_queries")
    op.drop_table("babies")
    op.drop_table("consultation_slots")
    op.drop_table("content_items")
    op.drop_table("products")
    op.drop_table("users")
