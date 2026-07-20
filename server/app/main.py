from fastapi import FastAPI

from .config import get_settings

app = FastAPI(title="BabyCare AI Platform API", version="0.1.0")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    get_settings()
    return {"status": "ok"}

