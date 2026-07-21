from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models import PrescriptionStatus

from .constants import AI_DISCLAIMER


class PrescriptionExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    medicine_names: list[str]
    dosage_text: list[str]
    frequency_text: list[str]
    raw_ocr_text: str


class PrescriptionExtractionResponse(PrescriptionExtraction):
    id: int
    baby_id: int
    status: Literal[PrescriptionStatus.PENDING_REVIEW]
    ai_disclaimer: Literal["Extracted text requires pharmacist/doctor review."] = (
        AI_DISCLAIMER
    )


class PrescriptionReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal[PrescriptionStatus.REVIEWED, PrescriptionStatus.FLAGGED]
    note: str = Field(min_length=1, max_length=5000)


class PrescriptionReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: PrescriptionStatus
    reviewer_id: int
    reviewer_note: str
