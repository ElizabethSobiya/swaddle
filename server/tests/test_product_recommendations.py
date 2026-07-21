from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Product
from app.products.constants import PRODUCT_RERANK_MODEL
from app.products.router import get_optional_openai_client
from app.products.schemas import AIRerankItem, AIRerankResult
from app.products.service import calculate_age_months, rank_products


def product(
    product_id: int,
    name: str,
    age_min: int,
    age_max: int,
    tags: list[str],
) -> Product:
    return Product(
        id=product_id,
        name=name,
        category="care",
        age_min_months=age_min,
        age_max_months=age_max,
        price=Decimal("19.99"),
        tags=tags,
    )


def test_calculate_age_months_accounts_for_day_of_month() -> None:
    assert calculate_age_months(date(2026, 1, 20), date(2026, 7, 19)) == 5
    assert calculate_age_months(date(2026, 1, 20), date(2026, 7, 20)) == 6


def test_rule_ranking_combines_age_fit_and_tag_overlap() -> None:
    closer_age = product(1, "General Care", 0, 12, ["washable"])
    symptom_match = product(2, "Nasal Care", 0, 24, ["nasal", "gentle"])

    ranked = rank_products(
        [closer_age, symptom_match], 6, ["Baby has nasal congestion"]
    )

    assert ranked[0].id == 2
    assert ranked[0].matched_tags == ["nasal"]


def recommendation_dependencies(include_client: bool) -> tuple[MagicMock, MagicMock]:
    db = MagicMock()
    db.get.return_value = SimpleNamespace(id=1, dob=date(2026, 1, 1))
    recent_query = SimpleNamespace(symptoms="nasal congestion")
    products = [
        product(1, "Nasal Aspirator", 0, 24, ["nasal", "gentle"]),
        product(2, "Soft Bib", 0, 24, ["washable"]),
    ]
    db.scalars.side_effect = [iter([recent_query]), iter(products)]
    openai_client = MagicMock()
    openai_client.responses.parse.return_value = SimpleNamespace(
        output_parsed=AIRerankResult(
            products=[
                AIRerankItem(
                    product_id=2,
                    explanation="It fits the baby's age and is easy to wash.",
                ),
                AIRerankItem(
                    product_id=1,
                    explanation="Its nasal tag overlaps the recent context.",
                ),
            ]
        )
    )
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_optional_openai_client] = (
        (lambda: openai_client) if include_client else (lambda: None)
    )
    return db, openai_client


def test_endpoint_returns_rule_based_without_ai() -> None:
    _, openai_client = recommendation_dependencies(include_client=False)

    response = TestClient(app).get("/api/products/recommend?baby_id=1&include_ai=false")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()["rule_based"]) == 2
    assert response.json()["ai_explained"] is None
    assert response.json()["ai_unavailable_reason"] is None
    openai_client.responses.parse.assert_not_called()


def test_endpoint_returns_ai_ranking_beside_rule_ranking() -> None:
    _, openai_client = recommendation_dependencies(include_client=True)

    response = TestClient(app).get("/api/products/recommend?baby_id=1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["rule_based"][0]["id"] == 1
    assert [item["id"] for item in body["ai_explained"]] == [2, 1]
    assert all(item["explanation"].endswith(".") for item in body["ai_explained"])
    request = openai_client.responses.parse.call_args.kwargs
    assert request["model"] == PRODUCT_RERANK_MODEL
    assert request["reasoning"] == {"effort": "low"}


def test_endpoint_preserves_rules_when_ai_is_not_configured() -> None:
    recommendation_dependencies(include_client=False)

    response = TestClient(app).get("/api/products/recommend?baby_id=1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()["rule_based"]) == 2
    assert response.json()["ai_explained"] is None
    assert "OPENAI_API_KEY" in response.json()["ai_unavailable_reason"]
