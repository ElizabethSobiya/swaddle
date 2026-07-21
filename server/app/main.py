from fastapi import FastAPI

from .assistant.router import router as assistant_router
from .config import get_settings

app = FastAPI(title="BabyCare AI Platform API", version="0.1.0")
app.include_router(assistant_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    get_settings()
    return {"status": "ok"}
