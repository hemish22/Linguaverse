"""
llm_module.py — LLM interaction for LinguaLens

Uses Google Gemini (gemini-2.0-flash) to:
- Simplify complex text into plain language
- Generate key points
- Translate explanations into the target language
"""

import google.generativeai as genai
from utils import load_config


# Configure the Gemini API on module load
_api_key = None
_model = None


def _get_model():
    """
    Lazily initialize and return the Gemini model.
    Configures the API key on first call.
    """
    global _api_key, _model
    if _model is None:
        _api_key = load_config()
        genai.configure(api_key=_api_key)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model


def _build_prompt(text: str, target_language: str) -> str:
    """
    Build the prompt template for text simplification and translation.

    Args:
        text: The OCR-extracted text to process.
        target_language: The language for translation output.

    Returns:
        Formatted prompt string.
    """
    prompt = f"""You are an expert at making complex information accessible to everyone.

Analyze the following text that was extracted from an image (it may be a medicine label, 
government document, signboard, instruction manual, research paper, or similar).

Your task:
1. **Simple Explanation**: Rewrite the text in simple, everyday language that a non-expert 
   can easily understand. Avoid jargon and technical terms. If the text contains medical, 
   legal, or technical content, explain what it means in practical terms.

2. **Key Points**: List the 3-5 most important takeaways as bullet points.

3. **Translation**: Translate your simple explanation into {target_language}. 
   Make sure the translation is natural and easy to read, not a literal word-for-word translation.

Format your response EXACTLY like this (use these exact headers):

## Simple Explanation
[Your simple explanation here]

## Key Points
- [Point 1]
- [Point 2]
- [Point 3]

## Translation ({target_language})
[Your translated explanation here]

---

Text to analyze:
\"\"\"
{text}
\"\"\"
"""
    return prompt


def simplify_and_translate(text: str, target_language: str = "Hindi") -> dict:
    """
    Send extracted text to Gemini for simplification and translation.

    Args:
        text: The OCR-extracted text to process.
        target_language: Target language for translation (English, Hindi, or Tamil).

    Returns:
        Dictionary with keys:
        - 'explanation': Simple explanation of the text
        - 'key_points': Key points as a string
        - 'translation': Translated explanation
        - 'full_response': Complete raw response from the LLM
    """
    if not text or not text.strip():
        return {
            "explanation": "No text was provided to analyze.",
            "key_points": "",
            "translation": "",
            "full_response": "",
        }

    model = _get_model()
    prompt = _build_prompt(text, target_language)

    try:
        response = model.generate_content(prompt)
        full_text = response.text

        # Parse the structured response into sections
        result = _parse_response(full_text, target_language)
        result["full_response"] = full_text
        return result

    except Exception as e:
        error_msg = f"Error communicating with Gemini API: {str(e)}"
        return {
            "explanation": error_msg,
            "key_points": "",
            "translation": "",
            "full_response": error_msg,
        }


def _parse_response(response_text: str, target_language: str) -> dict:
    """
    Parse the LLM response into structured sections.

    Looks for the markdown headers:
    - ## Simple Explanation
    - ## Key Points
    - ## Translation

    Args:
        response_text: Raw text response from the LLM.
        target_language: The target language (used to identify translation section).

    Returns:
        Dictionary with 'explanation', 'key_points', and 'translation' keys.
    """
    explanation = ""
    key_points = ""
    translation = ""

    # Split by ## headers and extract sections
    sections = response_text.split("## ")

    for section in sections:
        section_lower = section.lower().strip()

        if section_lower.startswith("simple explanation"):
            # Everything after the header line
            lines = section.split("\n", 1)
            explanation = lines[1].strip() if len(lines) > 1 else ""

        elif section_lower.startswith("key points"):
            lines = section.split("\n", 1)
            key_points = lines[1].strip() if len(lines) > 1 else ""

        elif section_lower.startswith("translation"):
            lines = section.split("\n", 1)
            translation = lines[1].strip() if len(lines) > 1 else ""

    # Fallback: if parsing failed, return the full response as explanation
    if not explanation and not key_points and not translation:
        explanation = response_text
        
    return {
        "explanation": explanation,
        "key_points": key_points,
        "translation": translation,
    }
