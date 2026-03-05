"""
utils.py — Shared utilities for LinguaLens

Provides:
- Environment configuration loading (API keys)
- Text-to-speech audio generation via gTTS
- Image preprocessing helpers
"""

import os
import io
import re
from dotenv import load_dotenv
from gtts import gTTS
from PIL import Image
import numpy as np


def load_config():
    """
    Load environment variables from .env file.
    Returns the Gemini API key or raises an error if not found.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Please create a .env file with: GEMINI_API_KEY=your_key_here"
        )
    return api_key


# Mapping of language names to gTTS language codes
LANGUAGE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
}


def clean_for_tts(text: str) -> str:
    """
    Remove markdown formatting like bullets and bolding so the TTS 
    doesn't read out "dash" or "asterisk".
    """
    if not text:
        return ""
    # Remove bold, italics, headers, code blocks
    text = re.sub(r'[*_#`]', '', text)
    # Remove bullet points at the start of lines
    text = re.sub(r'^[-\•]\s+', '', text, flags=re.MULTILINE)
    # Replace remaining loose dashes
    text = text.replace(' - ', ', ')
    return text.strip()


def text_to_speech(text: str, language: str = "English") -> bytes:
    """
    Convert text to speech audio using gTTS.

    Args:
        text: The text to convert to speech.
        language: Language name (English, Hindi, or Tamil).

    Returns:
        Audio data as bytes (MP3 format).
    """
    text = clean_for_tts(text)
    lang_code = LANGUAGE_MAP.get(language, "en")
    tts = gTTS(text=text, lang=lang_code)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a numpy array suitable for EasyOCR.

    Args:
        image: PIL Image object.

    Returns:
        Numpy array (RGB format).
    """
    # Ensure image is in RGB mode (EasyOCR expects this)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)
