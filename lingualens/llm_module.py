"""
llm_module.py — LLM interaction for LinguaLens

Uses Google Gemini (gemini-2.5-flash) to:
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
        _model = genai.GenerativeModel("gemini-2.5-flash")
    return _model


def _build_prompt(text: str, target_language: str, difficulty: str) -> str:
    """
    Build the prompt template for text simplification and translation.

    Args:
        text: The OCR-extracted text to process.
        target_language: The language for translation output.
        difficulty: The target audience reading level (e.g. Child, Student, Professional).

    Returns:
        Formatted prompt string.
    """
    prompt = f"""You are an expert at making complex information accessible.

Analyze the following text that was extracted from an image (it may be a medicine label, 
government document, signboard, instruction manual, research paper, or similar).

Your task:
1. **Detected Language**: Identify the primary language(s) of the original text.
2. **AI Simplified Explanation**: Rewrite the text tailored for a {difficulty}. Avoid jargon and technical terms. If the text contains medical, legal, or technical content, explain what it means in practical terms for a {difficulty}.
3. **Key Points**: List 3-5 important takeaways using this format:
   - What this document is: [description]
   - Information required/present: [details]
   - Actions to take: [actions]
4. **Translation**: Translate your simplified explanation into {target_language}. Make sure the translation is natural and easy to read.

Format your response EXACTLY like this (use these exact headers):

## Detected Language
[Language name]

## AI Simplified Explanation
[Your simple explanation tailored for a {difficulty}]

## Key Points
- What this document is: [description]
- Information present: [details]
- Actions to take: [actions]

## Translation ({target_language})
[Your translated explanation here]

---

Text to analyze:
\"\"\"
{text}
\"\"\"
"""
    return prompt


def simplify_and_translate(text: str, target_language: str = "Hindi", difficulty: str = "Student") -> dict:
    """
    Send extracted text to Gemini for simplification and translation.

    Args:
        text: The OCR-extracted text to process.
        target_language: Target language for translation (English, Hindi, or Tamil).
        difficulty: Target reading level.

    Returns:
        Dictionary with keys:
        - 'detected_language': Guessed language of original text
        - 'explanation': Simple explanation of the text
        - 'key_points': Key points as a string
        - 'translation': Translated explanation
        - 'full_response': Complete raw response from the LLM
    """
    if not text or not text.strip():
        return {
            "detected_language": "Unknown",
            "explanation": "No text was provided to analyze.",
            "key_points": "",
            "translation": "",
            "full_response": "",
        }

    model = _get_model()
    prompt = _build_prompt(text, target_language, difficulty)

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
            "detected_language": "Unknown",
            "explanation": error_msg,
            "key_points": "",
            "translation": "",
            "full_response": error_msg,
        }


def _parse_response(response_text: str, target_language: str) -> dict:
    import re
    
    # Use regex to robustly parse sections regardless of spacing
    detected_lang_match = re.search(r'## Detected Language\s*\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)
    explanation_match = re.search(r'## (?:(?:AI )?Simplified Explanation|Simple Explanation)\s*\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)
    key_points_match = re.search(r'## Key Points\s*\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)
    translation_match = re.search(r'## Translation.*?\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)

    explanation = explanation_match.group(1).strip() if (explanation_match and explanation_match.group(1)) else ""
    key_points = key_points_match.group(1).strip() if (key_points_match and key_points_match.group(1)) else ""
    translation = translation_match.group(1).strip() if (translation_match and translation_match.group(1)) else ""
    detected_lang = detected_lang_match.group(1).strip() if (detected_lang_match and detected_lang_match.group(1)) else "Unknown"

    if not explanation and not key_points and not translation:
        explanation = str(response_text).strip() if response_text else ""
        
    return {
        "detected_language": detected_lang,
        "explanation": explanation,
        "key_points": key_points,
        "translation": translation,
    }
