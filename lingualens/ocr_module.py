"""
ocr_module.py — OCR text extraction for LinguaLens

Uses EasyOCR to extract text from images. The reader is lazily initialized
to avoid loading heavy models on every call.
"""

import easyocr
import numpy as np
from PIL import Image
from utils import preprocess_image


# Module-level reader instances (lazy-loaded to avoid memory bloat)
_readers = {}


def _get_reader(lang_code="hi"):
    """
    Lazily initialize and return the EasyOCR reader.
    Supports English, Hindi, and Tamil text detection.
    Maintains separate readers for mutually-exclusive language models (like Hindi vs Tamil).
    """
    global _readers
    
    # EasyOCR doesn't allow combining Tamil ('ta') with Hindi ('hi'). They must run in separate readers.
    if lang_code not in _readers:
        lang_list = ["en", "ta"] if lang_code == "ta" else ["en", "hi"]
        
        # gpu=True will use GPU if available, falls back to CPU otherwise
        _readers[lang_code] = easyocr.Reader(
            lang_list,
            gpu=True
        )
        
    return _readers[lang_code]


def extract_text(image, source_language_preset="English & Hindi") -> str:
    """
    Extract text from an image using EasyOCR.

    Args:
        image: Can be a PIL Image, numpy array, or file path string.
        source_language_preset: The string from the Streamlit selectbox indicating the expected text.

    Returns:
        Extracted text as a single string, with detected lines
        joined by newlines. Returns empty string if no text is found.
    """
    # Convert input to numpy array if needed
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

    # Determine the primary language code from the UI preset
    lang_code = "ta" if "Tamil" in source_language_preset else "hi"

    reader = _get_reader(lang_code)

    # Run OCR — returns list of (bbox, text, confidence) tuples
    results = reader.readtext(img_array)

    if not results:
        return ""

    # Extract text from results and join with newlines
    extracted_lines = [text for (_, text, confidence) in results if confidence > 0.2]

    return "\n".join(extracted_lines)
