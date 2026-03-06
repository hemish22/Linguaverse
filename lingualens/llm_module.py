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
2. **Original Explanation**: Restructure and simplify the text tailord for a {difficulty}.
   - Use simple, short sentences.
   - Highlight important keywords using **bold text**.
   - Output EXACTLY the 4 sections requested below (Quick Summary, Key Points, Steps to Complete, Important Note).
   - If a section doesn't apply (e.g. no steps to complete), just leave it blank or omit it smoothly.
3. **Translated Explanation**: Translate the entire restructured explanation into {target_language}. Maintain the same sections, icons, short sentences, and bold keywords.

Format your response EXACTLY like this (use these exact headers):

## Detected Language
[Language name]

## Original Explanation
📄 **Quick Summary**
---
[2 simple, short sentences]

💡 **Key Points**
---
* **[Keyword]** - [Short explanation]
* **[Keyword]** - [Short explanation]

📝 **Steps to Complete**
---
1. [Step 1]
2. [Step 2]

⚠️ **Important Note**
---
[Critical warning or note]

## Translated Explanation ({target_language})
📄 **[Translated 'Quick Summary' title]**
---
[Translated summary sentences]

💡 **[Translated 'Key Points' title]**
---
* **[Translated Keyword]** - [Translated short explanation]

...and so on for the rest of the sections. Maintain the exact formatting.

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
        - 'key_points': Key points as a string
        - 'translated_key_points': Translated key points
        - 'explanation': Detailed simple explanation of the text
        - 'translation': Translated detailed explanation
        - 'full_response': Complete raw response from the LLM
    """
    if not text or not text.strip():
        return {
            "detected_language": "Unknown",
            "key_points": "",
            "translated_key_points": "",
            "explanation": "No text was provided to analyze.",
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
            "key_points": "",
            "translated_key_points": "",
            "explanation": error_msg,
            "translation": "",
            "full_response": error_msg,
        }


def _parse_response(response_text: str, target_language: str) -> dict:
    import re
    
    # Use regex to robustly parse sections regardless of spacing
    detected_lang_match = re.search(r'## Detected Language\s*\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)
    explanation_match = re.search(r'## Original Explanation\s*\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)
    translation_match = re.search(r'## Translated Explanation.*?\n(.*?)(?=\n##|$)', response_text, re.DOTALL | re.IGNORECASE)

    explanation = explanation_match.group(1).strip() if (explanation_match and explanation_match.group(1)) else ""
    translation = translation_match.group(1).strip() if (translation_match and translation_match.group(1)) else ""
    detected_lang = detected_lang_match.group(1).strip() if (detected_lang_match and detected_lang_match.group(1)) else "Unknown"

    if not explanation and not translation:
        explanation = str(response_text).strip() if response_text else ""
        
    return {
        "detected_language": detected_lang,
        "explanation": explanation,
        "translation": translation,
    }


def generate_suggested_questions(document_text: str, target_language: str = "English") -> list:
    """
    Generate 3 practical suggested questions about the document.

    Args:
        document_text: The OCR-extracted text.
        target_language: Language for the suggested questions.

    Returns:
        A list of up to 3 question strings.
    """
    if not document_text or not document_text.strip():
        return []

    model = _get_model()
    prompt = f"""Based on the following document text, generate exactly 3 short, practical questions
that a user might want to ask about this document.

Document text:
\"\"\"
{document_text}
\"\"\"

Return ONLY the 3 questions, one per line, in {target_language}.
No numbering, no bullets, no extra text.
Keep each question under 12 words."""

    try:
        response = model.generate_content(prompt)
        questions = [q.strip() for q in response.text.strip().split("\n") if q.strip()]
        return questions[:3]
    except Exception:
        return []


def answer_question(document_text: str, target_language: str, question_text: str = None, audio_bytes: bytes = None) -> str:
    """
    Answers a user's question about the document text using Gemini.
    Supports either text or audio input.
    """
    if not document_text.strip():
        return "Please upload a document first."
        
    if not question_text and not audio_bytes:
        return "Please provide a question."

    model = _get_model()
    
    prompt = f"""You are an incredibly helpful assistant helping users understand documents.

Document text:
\"\"\"
{document_text}
\"\"\"

User question:
{question_text if question_text else '(Please listen to the attached audio question)'}

Rules:
1. Answer using ONLY the information in the document.
2. If the answer is not present, say exactly: "The document does not mention this."
3. Explain clearly, simply, and directly.
4. IMPORTANT: You must provide your final answer in the following language: {target_language}.
"""

    contents = [prompt]
    if audio_bytes:
        contents.append({
            "mime_type": "audio/wav",
            "data": audio_bytes
        })
        
    try:
        response = model.generate_content(contents)
        return response.text.strip()
    except Exception as e:
        return f"Error communicating with Gemini API: {str(e)}"
