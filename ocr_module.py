"""
ocr_module.py — OCR text extraction for LinguaLens

Uses Tesseract (via pytesseract) to extract text from images. No PyTorch
dependency, which keeps the backend small enough for Render's free tier.
"""

import pytesseract
import numpy as np
from PIL import Image
from utils import preprocess_image


# Maps the Streamlit/API preset to a Tesseract language string.
# Only 'eng' is installed locally; 'hin'/'tam' packs are apt-installed in the
# Docker image (Dwight). 'eng' is always included as a fallback base.
_LANG_MAP = {
    "English & Tamil": "eng+tam",
    "English & Hindi": "eng+hin",
    "English": "eng",
}


def _resolve_langs(source_language_preset: str) -> str:
    preset = (source_language_preset or "").strip()
    if "Tamil" in preset and "Hindi" not in preset:
        return _LANG_MAP["English & Tamil"]
    if "Hindi" in preset:
        return _LANG_MAP["English & Hindi"]
    return _LANG_MAP["English"]


def extract_text(image, source_language_preset="English & Hindi") -> tuple[str, float]:
    """
    Extract text and average confidence from an image using Tesseract.

    Args:
        image: Can be a PIL Image, numpy array, or file path string.
        source_language_preset: The string from the UI/API selectbox indicating
            the expected text ('English & Hindi', 'English & Tamil', or similar).

    Returns:
        Tuple containing:
        - Extracted text as a single string, joined by newlines. Empty string if no text is found.
        - Average confidence score (float between 0 and 1).
    """
    # Convert input to a numpy array if needed
    if isinstance(image, str):
        # File path provided
        img_array = np.array(Image.open(image).convert("RGB"))
    elif isinstance(image, Image.Image):
        # PIL Image provided
        img_array = preprocess_image(image)
    elif isinstance(image, np.ndarray):
        img_array = image
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")

    langs = _resolve_langs(source_language_preset)

    # Pull per-word data so we can compute a real average confidence.
    data = pytesseract.image_to_data(
        img_array, lang=langs, output_type=pytesseract.Output.DICT
    )

    confidences = [c for c in data.get("conf", []) if isinstance(c, (int, float)) and c >= 0]
    words = [w for w in data.get("text", []) if w and w.strip()]

    if not words or not confidences:
        return "", 0.0

    # Keep the low-confidence filtering spirit: drop words below ~20%.
    valid = [
        (w.strip(), float(c) / 100.0)
        for w, c in zip(data.get("text", []), data.get("conf", []))
        if w.strip() and isinstance(c, (int, float)) and c >= 20
    ]

    if not valid:
        return "", 0.0

    extracted_lines = [text for text, _ in valid]
    avg_confidence = float(sum(conf for _, conf in valid) / len(valid))

    return "\n".join(extracted_lines), avg_confidence