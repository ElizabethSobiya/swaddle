from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_options() -> dict[str, Any]:
    settings = get_settings()
    options: dict[str, Any] = {"pool_pre_ping": True}
    # SQLite (tests) uses a pool that rejects the sizing arguments below.
    if settings.database_url.startswith("postgresql"):
        options.update(
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            # Managed Postgres providers drop idle connections; recycle first.
            pool_recycle=settings.db_pool_recycle_seconds,
        )
    return options


engine = create_engine(get_settings().database_url, **_engine_options())
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
