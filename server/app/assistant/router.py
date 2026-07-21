from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from openai import APIConnectionError, APITimeoutError, OpenAI
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import SymptomQuery

from .schemas import SymptomCheckRequest, SymptomCheckResponse
from .service import OpenAIClient, check_symptoms

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


def get_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )


@router.post(
    "/symptom-check",
    response_model=SymptomCheckResponse,
    status_code=status.HTTP_200_OK,
)
def symptom_check(
    payload: SymptomCheckRequest,
    client: Annotated[OpenAIClient, Depends(get_openai_client)],
    db: Annotated[Session, Depends(get_db)],
) -> SymptomCheckResponse:
    try:
        result = check_symptoms(client, payload)
    except APITimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The symptom assistant timed out. Please try again.",
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The symptom assistant is temporarily unavailable.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The assistant returned an invalid response.",
        ) from exc

    db.add(
        SymptomQuery(
            baby_id=payload.baby_id,
            symptoms=payload.symptoms,
            age_months=payload.age_months,
            ai_response=result.model_dump(mode="json"),
            alert_level=result.alert_level.value,
        )
    )
    db.commit()
    return result
