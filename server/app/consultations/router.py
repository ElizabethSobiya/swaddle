from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConsultationSlot, SlotStatus

from .schemas import (
    ConsultationBookingConfirmation,
    ConsultationBookingRequest,
    ConsultationSlotResponse,
)

router = APIRouter(prefix="/api/consultations", tags=["consultations"])


@router.get("/slots", response_model=list[ConsultationSlotResponse])
def list_consultation_slots(
    db: Annotated[Session, Depends(get_db)],
) -> list[ConsultationSlot]:
    return list(
        db.scalars(select(ConsultationSlot).order_by(ConsultationSlot.slot_time)).all()
    )


@router.post(
    "/book",
    response_model=ConsultationBookingConfirmation,
    status_code=status.HTTP_201_CREATED,
)
def book_consultation(
    payload: ConsultationBookingRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ConsultationBookingConfirmation:
    # Roadmap: real-time video and 24-hour live consultations are explicitly out of
    # scope for this build; this endpoint only reserves a scheduled slot.
    slot = db.scalar(
        select(ConsultationSlot)
        .where(ConsultationSlot.id == payload.slot_id)
        .with_for_update()
    )
    if slot is None:
        raise HTTPException(status_code=404, detail="Consultation slot not found.")
    if slot.status != SlotStatus.AVAILABLE:
        raise HTTPException(
            status_code=409, detail="Consultation slot is already booked."
        )

    slot.status = SlotStatus.BOOKED
    db.commit()
    db.refresh(slot)

    return ConsultationBookingConfirmation(
        confirmation_id=f"CONS-{slot.id:06d}",
        slot_id=slot.id,
        pediatrician_name=slot.pediatrician_name,
        slot_time=slot.slot_time,
        status=slot.status,
        message="Consultation slot booked successfully.",
    )
