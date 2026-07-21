from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import SlotStatus


class ConsultationSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pediatrician_name: str
    slot_time: datetime
    status: SlotStatus


class ConsultationBookingRequest(BaseModel):
    slot_id: int = Field(gt=0)


class ConsultationBookingConfirmation(BaseModel):
    confirmation_id: str
    slot_id: int
    pediatrician_name: str
    slot_time: datetime
    status: SlotStatus
    message: str
