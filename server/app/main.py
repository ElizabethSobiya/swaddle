from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .assistant.router import router as assistant_router
from .config import get_settings
from .consultations.router import router as consultations_router
from .content.router import router as content_router
from .prescriptions.router import router as prescriptions_router
from .products.router import router as products_router

settings = get_settings()
app = FastAPI(title="Swaddle API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
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
    get_settings()
    return {"status": "ok"}
