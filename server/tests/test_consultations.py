from datetime import UTC, datetime
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import ConsultationSlot, SlotStatus


def slot(status: SlotStatus = SlotStatus.AVAILABLE) -> ConsultationSlot:
    return ConsultationSlot(
        id=7,
        pediatrician_name="Dr. Asha Menon",
        slot_time=datetime(2026, 7, 22, 9, 0, tzinfo=UTC),
        status=status,
    )


def test_lists_consultation_slots() -> None:
    session = MagicMock()
    session.scalars.return_value.all.return_value = [slot()]
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = TestClient(app).get("/api/consultations/slots")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["pediatrician_name"] == "Dr. Asha Menon"
    assert response.json()[0]["status"] == "available"


def test_books_available_slot_and_returns_confirmation() -> None:
    consultation_slot = slot()
    session = MagicMock()
    session.scalar.return_value = consultation_slot
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = TestClient(app).post("/api/consultations/book", json={"slot_id": 7})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["confirmation_id"] == "CONS-000007"
    assert response.json()["status"] == "booked"
    session.commit.assert_called_once()


def test_booking_missing_slot_returns_not_found() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = TestClient(app).post("/api/consultations/book", json={"slot_id": 99})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    session.commit.assert_not_called()


def test_booking_booked_slot_returns_conflict() -> None:
    session = MagicMock()
    session.scalar.return_value = slot(SlotStatus.BOOKED)
    app.dependency_overrides[get_db] = lambda: session
    try:
        response = TestClient(app).post("/api/consultations/book", json={"slot_id": 7})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    session.commit.assert_not_called()
