from app.assistant.service import OpenAIClient

from .constants import (
    AI_DISCLAIMER,
    PRESCRIPTION_EXTRACTION_MODEL,
    PRESCRIPTION_EXTRACTION_SYSTEM_PROMPT,
)
from .schemas import PrescriptionExtraction


def structure_prescription(
    client: OpenAIClient, raw_ocr_text: str
) -> PrescriptionExtraction:
    response = client.responses.parse(
        model=PRESCRIPTION_EXTRACTION_MODEL,
        reasoning={"effort": "none"},
        input=[
            {"role": "system", "content": PRESCRIPTION_EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": raw_ocr_text},
        ],
        text_format=PrescriptionExtraction,
    )
    result = response.output_parsed
    if result is None:
        raise ValueError("The model did not return a structured response.")
    if not isinstance(result, PrescriptionExtraction):
        result = PrescriptionExtraction.model_validate(result)
    return result.model_copy(update={"raw_ocr_text": raw_ocr_text})


def stored_extraction(result: PrescriptionExtraction) -> dict[str, object]:
    return {
        **result.model_dump(mode="json"),
        "ai_disclaimer": AI_DISCLAIMER,
    }
