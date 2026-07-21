import json
import re
from datetime import date

from app.assistant.service import OpenAIClient
from app.models import Product

from .constants import PRODUCT_RERANK_MODEL, PRODUCT_RERANK_SYSTEM_PROMPT
from .schemas import (
    AIExplainedProduct,
    AIRerankResult,
    RuleBasedProduct,
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def calculate_age_months(dob: date, today: date | None = None) -> int:
    current = today or date.today()
    months = (current.year - dob.year) * 12 + current.month - dob.month
    if current.day < dob.day:
        months -= 1
    return max(months, 0)


def _tokens(value: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(value.casefold()))


def rank_products(
    products: list[Product], age_months: int, symptom_context: list[str]
) -> list[RuleBasedProduct]:
    context_tokens = _tokens(" ".join(symptom_context))
    ranked = []
    for product in products:
        span = max(product.age_max_months - product.age_min_months, 1)
        midpoint = (product.age_min_months + product.age_max_months) / 2
        age_fit = max(0.0, 1 - abs(age_months - midpoint) / (span / 2 + 1))
        matched_tags = sorted(
            tag for tag in product.tags if _tokens(tag) & context_tokens
        )
        score = round(age_fit * 10 + len(matched_tags) * 5, 3)
        ranked.append(
            RuleBasedProduct(
                id=product.id,
                name=product.name,
                category=product.category,
                age_min_months=product.age_min_months,
                age_max_months=product.age_max_months,
                price=product.price,
                tags=product.tags,
                score=score,
                matched_tags=matched_tags,
            )
        )
    return sorted(ranked, key=lambda item: (-item.score, item.name.casefold()))


def _one_sentence(value: str) -> str:
    compact = " ".join(value.split())
    match = re.search(r"[.!?]", compact)
    if match:
        return compact[: match.end()]
    return f"{compact}."


def ai_rerank(
    client: OpenAIClient,
    rule_based: list[RuleBasedProduct],
    age_months: int,
    symptom_context: list[str],
) -> list[AIExplainedProduct]:
    payload = {
        "age_months": age_months,
        "recent_symptom_context": symptom_context,
        "eligible_products": [item.model_dump(mode="json") for item in rule_based],
    }
    response = client.responses.parse(
        model=PRODUCT_RERANK_MODEL,
        reasoning={"effort": "low"},
        input=[
            {"role": "system", "content": PRODUCT_RERANK_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        text_format=AIRerankResult,
    )
    result = response.output_parsed
    if result is None:
        raise ValueError("The model did not return a structured response.")
    if not isinstance(result, AIRerankResult):
        result = AIRerankResult.model_validate(result)

    by_id = {item.id: item for item in rule_based}
    ordered = []
    seen = set()
    for ai_item in result.products:
        if ai_item.product_id not in by_id or ai_item.product_id in seen:
            continue
        seen.add(ai_item.product_id)
        ordered.append((by_id[ai_item.product_id], ai_item.explanation))
    for item in rule_based:
        if item.id not in seen:
            ordered.append(
                (
                    item,
                    f"This product matches the {age_months}-month age range.",
                )
            )

    return [
        AIExplainedProduct(
            **item.model_dump(),
            ai_rank=index,
            explanation=_one_sentence(explanation),
        )
        for index, (item, explanation) in enumerate(ordered, start=1)
    ]
