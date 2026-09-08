"""
ocr_module.py — OCR text extraction for LinguaLens

Uses EasyOCR to extract text from images. The reader is lazily initialized
to avoid loading heavy models on every call.
"""

import sys
import easyocr
import numpy as np
from PIL import Image
from utils import preprocess_image


# Module-level reader instances (lazy-loaded to avoid memory bloat)
_readers = {}


def _get_reader(lang_code="hi"):
    """
    Lazily initialize and return the EasyOCR reader.
    Supports English-only, Hindi, and Tamil text detection.
    Maintains separate readers for mutually-exclusive language models (like Hindi vs Tamil).
    """
    global _readers
    
    if lang_code not in _readers:
        if lang_code == "en":
            lang_list = ["en"]
        elif lang_code == "ta":
            # EasyOCR doesn't allow combining Tamil ('ta') with Hindi ('hi'). They must run in separate readers.
            lang_list = ["en", "ta"]
        else:
            lang_list = ["en", "hi"]

        # Auto-detect GPU: macOS has no CUDA-backed PyTorch, so force CPU there.
        gpu = sys.platform != "darwin"
        _readers[lang_code] = easyocr.Reader(
            lang_list,
            gpu=gpu
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

    # Determine the language code from the UI preset.
    # "English & X" presets load English plus the detected script; a pure
    # "English" preset now loads the lightweight English-only reader.
    preset = source_language_preset
    if "Tamil" in preset and "Hindi" not in preset:
        lang_code = "ta"
    elif "Hindi" in preset:
        lang_code = "hi"
    else:
        lang_code = "en"

    reader = _get_reader(lang_code)

    # Run OCR — returns list of (bbox, text, confidence) tuples
    results = reader.readtext(img_array)

    if not results:
        return "", 0.0

    # Extract text. Use a tiny floor (0.05) that only drops near-garbage
    # glyphs; anything above it is surfaced rather than silently thrown away,
    # so low-confidence text still reaches the user. The returned average
    # confidence honestly reflects the quality of what was extracted.
    valid_results = [(text, conf) for (_, text, conf) in results if conf > 0.05]
    
    if not valid_results:
        return "", 0.0
        
    extracted_lines = [text for text, _ in valid_results]
    avg_confidence = float(sum(conf for _, conf in valid_results) / len(valid_results))

    return "\n".join(extracted_lines), avg_confidence
