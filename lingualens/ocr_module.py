"""
ocr_module.py — OCR text extraction for LinguaLens

Uses EasyOCR to extract text from images. The reader is lazily initialized
to avoid loading heavy models on every call.
"""

import easyocr
import numpy as np
from PIL import Image
from utils import preprocess_image


# Module-level reader instance (lazy-loaded)
_reader = None


def _get_reader():
    """
    Lazily initialize and return the EasyOCR reader.
    Supports English, Hindi, and Tamil text detection.
    The reader is cached at module level to avoid repeated model loading.
    """
    global _reader
    if _reader is None:
        # Initialize with multilingual support
        # gpu=True will use GPU if available, falls back to CPU otherwise
        _reader = easyocr.Reader(
            ["en", "hi", "ta"],
            gpu=True
        )
    return _reader


def extract_text(image) -> str:
    """
    Extract text from an image using EasyOCR.

    Args:
        image: Can be a PIL Image, numpy array, or file path string.

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

    reader = _get_reader()

    # Run OCR — returns list of (bbox, text, confidence) tuples
    results = reader.readtext(img_array)

    if not results:
        return ""

    # Extract text from results and join with newlines
    extracted_lines = [text for (_, text, confidence) in results if confidence > 0.2]

    return "\n".join(extracted_lines)
