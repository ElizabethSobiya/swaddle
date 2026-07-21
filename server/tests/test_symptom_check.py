from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.assistant.constants import DISCLAIMER, SYMPTOM_CHECK_MODEL
from app.assistant.router import get_openai_client
from app.assistant.schemas import AlertLevel, SymptomCheckResponse
from app.database import get_db
from app.main import app


def response_for(level: AlertLevel) -> SymptomCheckResponse:
    return SymptomCheckResponse(
        possible_causes=["A common minor viral illness or environmental irritation"],
        home_care=["Offer frequent fluids and monitor closely"],
        red_flags=["Seek care now if breathing becomes difficult"],
        alert_level=level,
        disclaimer=DISCLAIMER,
    )


def request_with_mock(
    model_response: SymptomCheckResponse, symptoms: str, age_months: int
) -> tuple[object, MagicMock, MagicMock]:
    openai_client = MagicMock()
    openai_client.responses.parse.return_value = SimpleNamespace(
        output_parsed=model_response
    )
    db = MagicMock()
    app.dependency_overrides[get_openai_client] = lambda: openai_client
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    response = client.post(
        "/api/assistant/symptom-check",
        json={"baby_id": 1, "symptoms": symptoms, "age_months": age_months},
    )
    app.dependency_overrides.clear()
    return response, openai_client, db


def test_low_alert_response() -> None:
    response, openai_client, db = request_with_mock(
        response_for(AlertLevel.LOW), "Mild runny nose and playful", 8
    )

    assert response.status_code == 200
    assert response.json()["alert_level"] == "low"
    assert response.json()["disclaimer"] == DISCLAIMER
    called_model = openai_client.responses.parse.call_args.kwargs["model"]
    assert called_model == SYMPTOM_CHECK_MODEL
    db.commit.assert_called_once()


def test_medium_alert_response() -> None:
    response, _, _ = request_with_mock(
        response_for(AlertLevel.MEDIUM), "Persistent cough but breathing normally", 14
    )

    assert response.status_code == 200
    assert response.json()["alert_level"] == "medium"


def test_high_alert_response_from_model() -> None:
    response, _, _ = request_with_mock(
        response_for(AlertLevel.HIGH), "Child appears seriously unwell", 18
    )

    assert response.status_code == 200
    assert response.json()["alert_level"] == "high"


def test_fever_under_three_months_forces_high_alert() -> None:
    response, _, _ = request_with_mock(
        response_for(AlertLevel.LOW), "Fever since this morning", 2
    )

    assert response.status_code == 200
    assert response.json()["alert_level"] == "high"


def test_difficulty_breathing_forces_high_alert() -> None:
    response, openai_client, _ = request_with_mock(
        response_for(AlertLevel.MEDIUM), "Difficulty breathing and poor feeding", 7
    )

    assert response.status_code == 200
    assert response.json()["alert_level"] == "high"
    prompt = openai_client.responses.parse.call_args.kwargs["input"][0]["content"]
    assert "Never suggest or mention specific medicines" in prompt


def test_symptom_check_rejects_invalid_payload_without_calling_model() -> None:
    openai_client = MagicMock()
    app.dependency_overrides[get_openai_client] = lambda: openai_client
    app.dependency_overrides[get_db] = lambda: MagicMock()
    try:
        response = TestClient(app).post(
            "/api/assistant/symptom-check",
            json={"baby_id": 0, "symptoms": "", "age_months": -1},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert fields == {"baby_id", "symptoms", "age_months"}
    openai_client.responses.parse.assert_not_called()


def test_symptom_check_returns_bad_gateway_for_invalid_model_output() -> None:
    openai_client = MagicMock()
    openai_client.responses.parse.return_value = SimpleNamespace(output_parsed=None)
    db = MagicMock()
    app.dependency_overrides[get_openai_client] = lambda: openai_client
    app.dependency_overrides[get_db] = lambda: db
    try:
        response = TestClient(app).post(
            "/api/assistant/symptom-check",
            json={"baby_id": 1, "symptoms": "Mild cough", "age_months": 8},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    db.commit.assert_not_called()
