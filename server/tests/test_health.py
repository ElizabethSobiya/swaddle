from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_index() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Swaddle API",
        "status": "running",
        "health": "/api/health",
        "docs": "/docs",
    }


def test_health_check() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
