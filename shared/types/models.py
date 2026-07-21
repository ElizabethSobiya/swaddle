"""Pydantic mirrors of the platform's shared TypeScript interfaces."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(word.capitalize() for word in rest)


class SharedModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True
    )


class CareCategory(StrEnum):
    FEEDING = "feeding"
    SLEEP = "sleep"
    DIAPER = "diaper"
    NOTE = "note"


class BabyProfile(SharedModel):
    id: str
    name: str
    birth_date: date


class CareEntry(SharedModel):
    id: str
    baby_id: str
    category: CareCategory
    occurred_at: datetime
    notes: str | None = None


class ContentType(StrEnum):
    RHYME = "rhyme"
    VIDEO = "video"
    SOUND = "sound"
    ACTIVITY = "activity"


class ContentItem(SharedModel):
    id: int
    type: ContentType
    title: str
    url: str
    age_min_months: int
    age_max_months: int
    config: dict[str, Any] | None = None
