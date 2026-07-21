from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RuleBasedProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    age_min_months: int
    age_max_months: int
    price: Decimal
    tags: list[str]
    score: float
    matched_tags: list[str]


class AIRerankItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: int
    explanation: str = Field(min_length=1, max_length=280)


class AIRerankResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    products: list[AIRerankItem]


class AIExplainedProduct(RuleBasedProduct):
    ai_rank: int
    explanation: str


class ProductRecommendationResponse(BaseModel):
    baby_id: int
    age_months: int
    recent_symptom_queries_used: int
    rule_based: list[RuleBasedProduct]
    ai_explained: list[AIExplainedProduct] | None
    ai_unavailable_reason: str | None = None
