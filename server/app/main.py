from fastapi import FastAPI

from .assistant.router import router as assistant_router
from .config import get_settings
from .content.router import router as content_router
from .prescriptions.router import router as prescriptions_router
from .products.router import router as products_router

app = FastAPI(title="BabyCare AI Platform API", version="0.1.0")
app.include_router(assistant_router)
app.include_router(prescriptions_router)
app.include_router(products_router)
app.include_router(content_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    get_settings()
    return {"status": "ok"}
