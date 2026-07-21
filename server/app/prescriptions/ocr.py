from io import BytesIO

import pymupdf
import pytesseract
from PIL import Image, UnidentifiedImageError


class OCRProcessingError(ValueError):
    pass


def _ocr_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image.convert("RGB")).strip()


def extract_text(data: bytes, content_type: str) -> str:
    try:
        if content_type == "application/pdf":
            document = pymupdf.open(stream=data, filetype="pdf")
            pages = []
            for page in document:
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                with Image.open(BytesIO(pixmap.tobytes("png"))) as image:
                    pages.append(_ocr_image(image))
            text = "\n\n".join(page for page in pages if page)
        else:
            with Image.open(BytesIO(data)) as image:
                text = _ocr_image(image)
    except (UnidentifiedImageError, pymupdf.FileDataError) as exc:
        raise OCRProcessingError("The uploaded file could not be decoded.") from exc

    if not text.strip():
        raise OCRProcessingError("No text could be extracted from the uploaded file.")
    return text
