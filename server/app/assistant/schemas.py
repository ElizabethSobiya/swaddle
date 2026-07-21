from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .constants import DISCLAIMER


class AlertLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SymptomCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baby_id: int = Field(gt=0)
    symptoms: str = Field(min_length=1, max_length=5000)
    age_months: int = Field(ge=0, le=216)


class SymptomCheckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    possible_causes: list[str]
    home_care: list[str]
    red_flags: list[str]
    alert_level: AlertLevel
    disclaimer: Literal["This is not medical advice."] = DISCLAIMER
