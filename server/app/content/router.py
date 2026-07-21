from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ContentItem, ContentType
from ..schemas import ContentItemSchema

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("", response_model=list[ContentItemSchema])
def list_content(
    age_months: Annotated[int, Query(ge=0, le=216)],
    db: Annotated[Session, Depends(get_db)],
    content_type: Annotated[ContentType | None, Query(alias="type")] = None,
) -> list[ContentItem]:
    """Return items whose inclusive age range contains ``age_months``."""
    statement = select(ContentItem).where(
        ContentItem.age_min_months <= age_months,
        ContentItem.age_max_months >= age_months,
    )
    if content_type is not None:
        statement = statement.where(ContentItem.type == content_type)

    return list(
        db.scalars(statement.order_by(ContentItem.type, ContentItem.title)).all()
    )
