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


def extract_text(image, source_language_preset="English & Hindi") -> tuple[str, float]:
    """
    Extract text and average confidence from an image using EasyOCR.

    Args:
        image: Can be a PIL Image, numpy array, or file path string.
        source_language_preset: The string from the Streamlit selectbox indicating the expected text.

    Returns:
        Tuple containing:
        - Extracted text as a single string, joined by newlines. Returns empty string if no text is found.
        - Average confidence score (float between 0 and 1).
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
        return "", 0.0

    # Extract text and calculate average confidence
    valid_results = [(text, conf) for (_, text, conf) in results if conf > 0.2]
    
    if not valid_results:
        return "", 0.0
        
    extracted_lines = [text for text, _ in valid_results]
    avg_confidence = float(sum(conf for _, conf in valid_results) / len(valid_results))

    return "\n".join(extracted_lines), avg_confidence
