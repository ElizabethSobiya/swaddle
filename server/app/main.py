import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .assistant.router import router as assistant_router
from .config import get_settings
from .consultations.router import router as consultations_router
from .content.router import router as content_router
from .database import engine
from .prescriptions.router import router as prescriptions_router
from .products.router import router as products_router

logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(title="Swaddle API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(assistant_router)
app.include_router(prescriptions_router)
app.include_router(products_router)
app.include_router(content_router)
app.include_router(consultations_router)


@app.get("/")
def api_index() -> dict[str, str]:
    return {
        "name": "Swaddle API",
        "status": "running",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Liveness: the process is up and its configuration parsed."""
    get_settings()
    return {"status": "ok"}


@app.get("/api/health/ready")
def readiness_check() -> JSONResponse:
    """Readiness: the process can also reach its database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - exercised only against a broken database
        logger.exception("Readiness check failed: database is unreachable")
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "database": "down"}
        )
    return JSONResponse(content={"status": "ok", "database": "up"})
