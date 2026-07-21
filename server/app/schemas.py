from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import ContentType, PrescriptionStatus, SlotStatus, UserRole


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSchema(Schema):
    id: int
    email: EmailStr
    role: UserRole
    hashed_password: str


class BabySchema(Schema):
    id: int
    user_id: int
    name: str
    dob: date
    sex: str


class SymptomQuerySchema(Schema):
    id: int
    baby_id: int
    symptoms: str
    age_months: int = Field(ge=0)
    ai_response: dict[str, Any]
    alert_level: str
    created_at: datetime


class PrescriptionSchema(Schema):
    id: int
    baby_id: int
    file_url: str
    extracted_text: dict[str, Any]
    status: PrescriptionStatus
    reviewer_id: int | None
    reviewer_note: str | None


class ProductSchema(Schema):
    id: int
    name: str
    category: str
    age_min_months: int = Field(ge=0)
    age_max_months: int = Field(ge=0)
    price: Decimal = Field(ge=0)
    tags: list[str]


class ContentItemSchema(Schema):
    id: int
    type: ContentType
    title: str
    url: str
    age_min_months: int = Field(ge=0)
    age_max_months: int = Field(ge=0)


class ConsultationSlotSchema(Schema):
    id: int
    pediatrician_name: str
    slot_time: datetime
    status: SlotStatus
