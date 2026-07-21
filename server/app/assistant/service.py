import re
from typing import Protocol

from .constants import DISCLAIMER, SYMPTOM_CHECK_MODEL, SYMPTOM_CHECK_SYSTEM_PROMPT
from .schemas import AlertLevel, SymptomCheckRequest, SymptomCheckResponse


class ResponsesAPI(Protocol):
    def parse(self, **kwargs: object) -> object: ...


class OpenAIClient(Protocol):
    responses: ResponsesAPI


GENERAL_RED_FLAG_PATTERNS = (
    r"\b(difficulty|trouble|struggling)\s+(breathing|to breathe)\b",
    r"\b(shortness of breath|cannot breathe|can't breathe)\b",
    r"\b(blue|grey|gray)\s+(lips|skin|face)\b",
    r"\b(lethargic|lethargy|unresponsive|cannot wake|can't wake|hard to wake)\b",
    r"\b(seizure|convulsion)\b",
    r"\bstiff neck\b",
    r"\buncontrolled bleeding\b",
    r"\b(no wet diaper|not urinating|severe dehydration)\b",
    r"\b(purple rash|rapidly worsening|seriously unwell)\b",
)


def contains_red_flag(request: SymptomCheckRequest) -> bool:
    symptoms = request.symptoms.casefold()
    if request.age_months < 3 and re.search(r"\b(fever|temperature)\b", symptoms):
        return True
    return any(re.search(pattern, symptoms) for pattern in GENERAL_RED_FLAG_PATTERNS)


def check_symptoms(
    client: OpenAIClient, request: SymptomCheckRequest
) -> SymptomCheckResponse:
    response = client.responses.parse(
        model=SYMPTOM_CHECK_MODEL,
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": SYMPTOM_CHECK_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Baby age: {request.age_months} months. "
                    f"Reported symptoms: {request.symptoms}"
                ),
            },
        ],
        text_format=SymptomCheckResponse,
    )
    result = response.output_parsed
    if result is None:
        raise ValueError("The model did not return a structured response.")
    if not isinstance(result, SymptomCheckResponse):
        result = SymptomCheckResponse.model_validate(result)

    updates: dict[str, object] = {"disclaimer": DISCLAIMER}
    if contains_red_flag(request):
        updates["alert_level"] = AlertLevel.HIGH
    return result.model_copy(update=updates)
