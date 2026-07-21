from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from openai import OpenAI, OpenAIError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assistant.service import OpenAIClient
from app.config import get_settings
from app.database import get_db
from app.models import Baby, Product, SymptomQuery

from .constants import RECENT_CONTEXT_DAYS, RECENT_QUERY_LIMIT
from .schemas import ProductRecommendationResponse
from .service import ai_rerank, calculate_age_months, rank_products

router = APIRouter(prefix="/api/products", tags=["products"])


def get_optional_openai_client() -> OpenAI | None:
    api_key = get_settings().openai_api_key
    return OpenAI(api_key=api_key) if api_key else None


@router.get("/recommend", response_model=ProductRecommendationResponse)
def recommend_products(
    baby_id: Annotated[int, Query(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    client: Annotated[OpenAIClient | None, Depends(get_optional_openai_client)],
    include_ai: Annotated[bool, Query()] = True,
) -> ProductRecommendationResponse:
    baby = db.get(Baby, baby_id)
    if baby is None:
        raise HTTPException(status_code=404, detail="Baby not found.")
    age_months = calculate_age_months(baby.dob)

    cutoff = datetime.now(UTC) - timedelta(days=RECENT_CONTEXT_DAYS)
    recent_queries = list(
        db.scalars(
            select(SymptomQuery)
            .where(
                SymptomQuery.baby_id == baby_id,
                SymptomQuery.created_at >= cutoff,
            )
            .order_by(SymptomQuery.created_at.desc())
            .limit(RECENT_QUERY_LIMIT)
        )
    )
    products = list(
        db.scalars(
            select(Product).where(
                Product.age_min_months <= age_months,
                Product.age_max_months >= age_months,
            )
        )
    )
    symptom_context = [query.symptoms for query in recent_queries]
    rule_based = rank_products(products, age_months, symptom_context)

    explained = None
    unavailable_reason = None
    if include_ai and not rule_based:
        explained = []
    elif include_ai and client is None:
        unavailable_reason = "OPENAI_API_KEY is not configured."
    elif include_ai:
        try:
            explained = ai_rerank(client, rule_based, age_months, symptom_context)
        except (OpenAIError, ValueError):
            unavailable_reason = "GPT-5.6 re-ranking was unavailable."

    return ProductRecommendationResponse(
        baby_id=baby_id,
        age_months=age_months,
        recent_symptom_queries_used=len(recent_queries),
        rule_based=rule_based,
        ai_explained=explained,
        ai_unavailable_reason=unavailable_reason,
    )
