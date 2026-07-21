from pathlib import Path
from typing import Annotated
from urllib.parse import quote

import pytesseract
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.assistant.router import get_openai_client
from app.assistant.service import OpenAIClient
from app.database import get_db
from app.models import Baby, Prescription, PrescriptionStatus, User

from .auth import get_current_reviewer
from .constants import AI_DISCLAIMER, MAX_UPLOAD_BYTES, SUPPORTED_CONTENT_TYPES
from .ocr import OCRProcessingError, extract_text
from .schemas import (
    PrescriptionExtractionResponse,
    PrescriptionReviewRequest,
    PrescriptionReviewResponse,
)
from .service import stored_extraction, structure_prescription

router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.post("/extract", response_model=PrescriptionExtractionResponse)
def extract_prescription(
    baby_id: Annotated[int, Form(gt=0)],
    file: Annotated[UploadFile, File()],
    client: Annotated[OpenAIClient, Depends(get_openai_client)],
    db: Annotated[Session, Depends(get_db)],
) -> PrescriptionExtractionResponse:
    if db.get(Baby, baby_id) is None:
        raise HTTPException(status_code=404, detail="Baby not found.")
    content_type = file.content_type or ""
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Upload an image or PDF.")
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The upload exceeds 10 MB.")

    try:
        raw_text = extract_text(data, content_type)
        extraction = structure_prescription(client, raw_text)
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=503, detail="Tesseract OCR is unavailable."
        ) from exc
    except OCRProcessingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail="The extraction model returned invalid data."
        ) from exc

    filename = Path(file.filename or "prescription").name
    prescription = Prescription(
        baby_id=baby_id,
        file_url=f"local-upload:///{quote(filename)}",
        extracted_text=stored_extraction(extraction),
        status=PrescriptionStatus.PENDING_REVIEW,
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return PrescriptionExtractionResponse(
        id=prescription.id,
        baby_id=prescription.baby_id,
        status=prescription.status,
        **extraction.model_dump(),
        ai_disclaimer=AI_DISCLAIMER,
    )


@router.patch("/{prescription_id}/review", response_model=PrescriptionReviewResponse)
def review_prescription(
    prescription_id: int,
    payload: PrescriptionReviewRequest,
    reviewer: Annotated[User, Depends(get_current_reviewer)],
    db: Annotated[Session, Depends(get_db)],
) -> PrescriptionReviewResponse:
    prescription = db.get(Prescription, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found.")
    prescription.status = PrescriptionStatus(payload.status)
    prescription.reviewer_id = reviewer.id
    prescription.reviewer_note = payload.note
    db.commit()
    db.refresh(prescription)
    return PrescriptionReviewResponse.model_validate(prescription)
