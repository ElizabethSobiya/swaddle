from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole


def get_current_reviewer(
    db: Annotated[Session, Depends(get_db)],
    x_user_id: Annotated[int | None, Header()] = None,
) -> User:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required.",
        )
    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    if user.role != UserRole.REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer role is required.",
        )
    return user
