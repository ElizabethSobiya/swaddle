from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import ContentItem, ContentType


def content_item(**overrides: object) -> ContentItem:
    values = {
        "id": 1,
        "type": ContentType.ACTIVITY,
        "title": "Primary Color Tone Match",
        "url": "game://color-sound/primary",
        "age_min_months": 12,
        "age_max_months": 36,
        "config": {"game_type": "color_sound_match", "pairs": []},
    }
    values.update(overrides)
    return ContentItem(**values)


def client_returning(items: list[ContentItem]) -> TestClient:
    session = MagicMock()
    session.scalars.return_value.all.return_value = items
    app.dependency_overrides[get_db] = lambda: session
    return TestClient(app)


def test_content_returns_serialized_game_config() -> None:
    client = client_returning([content_item()])
    try:
        response = client.get("/api/content?age_months=18&type=activity")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["config"]["game_type"] == "color_sound_match"


def test_content_type_is_optional() -> None:
    client = client_returning(
        [
            content_item(
                type=ContentType.RHYME, config=None, url="https://example.test/a.ogg"
            )
        ]
    )
    try:
        response = client.get("/api/content?age_months=6")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["type"] == "rhyme"


def test_content_rejects_invalid_age_and_type() -> None:
    client = client_returning([])
    try:
        negative_age = client.get("/api/content?age_months=-1")
        invalid_type = client.get("/api/content?age_months=12&type=book")
    finally:
        app.dependency_overrides.clear()

    assert negative_age.status_code == 422
    assert invalid_type.status_code == 422
