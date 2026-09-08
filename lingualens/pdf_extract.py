"""
pdf_extract.py — PDF text extraction for LinguaLens.

Uses PyMuPDF (`pymupdf`) to pull embedded text from PDF pages. Pages with no
usable text layer are rendered to images and OCR'd via ocr_module.extract_text.
"""

import io

import pymupdf
from PIL import Image
import numpy as np

from ocr_module import extract_text


# A page counts as having a real text layer if it yields at least this many
# non-whitespace characters; otherwise it is treated as a scanned page.
_TEXT_LAYER_MIN_CHARS = 10

# Rendering resolution for scanned pages (DPI).
OCR_DPI = 200


def extract_pdf(data: bytes, source_language_preset: str = "English & Hindi") -> tuple[str, float, int]:
    """
    Extract text from a PDF (embedded text layer + OCR fallback for scanned pages).

    Args:
        data: Raw PDF bytes.
        source_language_preset: Language hint passed on to ocr_module.extract_text.

    Returns:
        Tuple (full_text, confidence, page_count):
        - full_text: Concatenated page text, pages joined by a blank line.
        - confidence: 1.0 if everything came from the text layer, else the
          average of the OCR'd pages' confidences.
        - page_count: Number of pages in the PDF.
    """
    doc = pymupdf.open(stream=data, filetype="pdf")

    page_texts: list[str] = []
    ocr_confidences: list[float] = []

    for page in doc:
        raw = page.get_text() or ""
        stripped = raw.strip()

        if len(stripped) >= _TEXT_LAYER_MIN_CHARS:
            # Real embedded text layer — keep it directly.
            page_texts.append(stripped)
            continue

        # No/sparse text layer: render to an image and OCR it.
        pix = page.get_pixmap(dpi=OCR_DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img_array = np.array(img)
        text, confidence = extract_text(img_array, source_language_preset)
        if text.strip():
            page_texts.append(text.strip())
            ocr_confidences.append(confidence)

    full_text = "\n\n".join(page_texts).strip()
    page_count = doc.page_count

    if ocr_confidences:
        confidence = float(sum(ocr_confidences) / len(ocr_confidences))
    else:
        confidence = 1.0 if full_text else 0.0

    return full_text, confidence, page_count