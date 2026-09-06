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


def test_readiness_check() -> None:
    response = client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_readiness_check_reports_unavailable_database(monkeypatch) -> None:
    def fail() -> None:
        raise OSError("database is unreachable")

    monkeypatch.setattr("app.main.engine.connect", fail)

    response = client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "down"}
