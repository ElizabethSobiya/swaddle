from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.assistant.router import get_openai_client
from app.database import get_db
from app.main import app
from app.models import Prescription, PrescriptionStatus, UserRole
from app.prescriptions.auth import get_current_reviewer
from app.prescriptions.constants import AI_DISCLAIMER, PRESCRIPTION_EXTRACTION_MODEL
from app.prescriptions.schemas import PrescriptionExtraction


def extraction_dependencies() -> tuple[MagicMock, MagicMock]:
    openai_client = MagicMock()
    openai_client.responses.parse.return_value = SimpleNamespace(
        output_parsed=PrescriptionExtraction(
            medicine_names=["Amoxycillin"],
            dosage_text=["125 mg"],
            frequency_text=["twice daily"],
            raw_ocr_text="model must not control this value",
        )
    )
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=1)

    def assign_id(prescription: Prescription) -> None:
        prescription.id = 42

    db.refresh.side_effect = assign_id
    app.dependency_overrides[get_openai_client] = lambda: openai_client
    app.dependency_overrides[get_db] = lambda: db
    return openai_client, db


def test_extract_prescription_structures_and_saves_pending_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_ocr = "Amoxycillin 125 mg twice daily"
    monkeypatch.setattr(
        "app.prescriptions.router.extract_text", lambda _data, _type: raw_ocr
    )
    openai_client, db = extraction_dependencies()

    response = TestClient(app).post(
        "/api/prescriptions/extract",
        data={"baby_id": "1"},
        files={"file": ("rx.png", b"image bytes", "image/png")},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "pending_review"
    assert response.json()["raw_ocr_text"] == raw_ocr
    assert response.json()["ai_disclaimer"] == AI_DISCLAIMER
    request = openai_client.responses.parse.call_args.kwargs
    assert request["model"] == PRESCRIPTION_EXTRACTION_MODEL
    assert request["reasoning"] == {"effort": "none"}
    saved = db.add.call_args.args[0]
    assert saved.status == PrescriptionStatus.PENDING_REVIEW
    assert saved.extracted_text["ai_disclaimer"] == AI_DISCLAIMER


def test_extract_rejects_unsupported_file_type() -> None:
    extraction_dependencies()
    response = TestClient(app).post(
        "/api/prescriptions/extract",
        data={"baby_id": "1"},
        files={"file": ("rx.txt", b"text", "text/plain")},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 415


def test_review_allows_reviewer_to_flag_with_note() -> None:
    prescription = Prescription(
        id=7,
        baby_id=1,
        file_url="local-upload:///rx.png",
        extracted_text={},
        status=PrescriptionStatus.PENDING_REVIEW,
    )
    db = MagicMock()
    db.get.return_value = prescription
    reviewer = SimpleNamespace(id=9, role=UserRole.REVIEWER)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_reviewer] = lambda: reviewer

    response = TestClient(app).patch(
        "/api/prescriptions/7/review",
        json={"status": "flagged", "note": "Please verify the strength."},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": 7,
        "status": "flagged",
        "reviewer_id": 9,
        "reviewer_note": "Please verify the strength.",
    }


def test_review_rejects_parent_role() -> None:
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=3, role=UserRole.PARENT)
    app.dependency_overrides[get_db] = lambda: db

    response = TestClient(app).patch(
        "/api/prescriptions/7/review",
        headers={"X-User-Id": "3"},
        json={"status": "reviewed", "note": "Looks accurate."},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_review_rejects_pending_review_status() -> None:
    reviewer = SimpleNamespace(id=9, role=UserRole.REVIEWER)
    app.dependency_overrides[get_current_reviewer] = lambda: reviewer
    app.dependency_overrides[get_db] = lambda: MagicMock()

    response = TestClient(app).patch(
        "/api/prescriptions/7/review",
        json={"status": "pending_review", "note": "Not a review outcome."},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 422
