from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(StrEnum):
    PARENT = "parent"
    PEDIATRICIAN = "pediatrician"
    REVIEWER = "reviewer"


class PrescriptionStatus(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    FLAGGED = "flagged"


class ContentType(StrEnum):
    RHYME = "rhyme"
    VIDEO = "video"
    SOUND = "sound"
    ACTIVITY = "activity"


class SlotStatus(StrEnum):
    AVAILABLE = "available"
    BOOKED = "booked"


def enum_values(enum: type[StrEnum]) -> list[str]:
    return [member.value for member in enum]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, values_callable=enum_values, native_enum=False)
    )
    hashed_password: Mapped[str] = mapped_column(String(255))

    babies: Mapped[list["Baby"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reviewed_prescriptions: Mapped[list["Prescription"]] = relationship(
        back_populates="reviewer", foreign_keys="Prescription.reviewer_id"
    )


class Baby(Base):
    __tablename__ = "babies"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    dob: Mapped[date] = mapped_column(Date)
    sex: Mapped[str] = mapped_column(String(30))

    user: Mapped[User] = relationship(back_populates="babies")
    symptom_queries: Mapped[list["SymptomQuery"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    prescriptions: Mapped[list["Prescription"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )


class SymptomQuery(Base):
    __tablename__ = "symptom_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"), index=True
    )
    symptoms: Mapped[str] = mapped_column(Text)
    age_months: Mapped[int] = mapped_column(Integer)
    ai_response: Mapped[dict[str, Any]] = mapped_column(JSON)
    alert_level: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    baby: Mapped[Baby] = relationship(back_populates="symptom_queries")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"), index=True
    )
    file_url: Mapped[str] = mapped_column(String(2048))
    extracted_text: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[PrescriptionStatus] = mapped_column(
        SqlEnum(PrescriptionStatus, values_callable=enum_values, native_enum=False),
        default=PrescriptionStatus.PENDING,
    )
    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby: Mapped[Baby] = relationship(back_populates="prescriptions")
    reviewer: Mapped[User | None] = relationship(
        back_populates="reviewed_prescriptions", foreign_keys=[reviewer_id]
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    age_min_months: Mapped[int] = mapped_column(Integer)
    age_max_months: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(80)), default=list)


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ContentType] = mapped_column(
        SqlEnum(ContentType, values_callable=enum_values, native_enum=False)
    )
    title: Mapped[str] = mapped_column(String(255), unique=True)
    url: Mapped[str] = mapped_column(String(2048))
    age_min_months: Mapped[int] = mapped_column(Integer)
    age_max_months: Mapped[int] = mapped_column(Integer)


class ConsultationSlot(Base):
    __tablename__ = "consultation_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    pediatrician_name: Mapped[str] = mapped_column(String(255))
    slot_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), unique=True, index=True
    )
    status: Mapped[SlotStatus] = mapped_column(
        SqlEnum(SlotStatus, values_callable=enum_values, native_enum=False),
        default=SlotStatus.AVAILABLE,
    )
