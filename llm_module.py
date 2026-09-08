"""
llm_module.py — LLM interaction for LinguaLens

Uses a Groq-hosted text model (openai/gpt-oss-120b) to:
- Simplify complex text into plain language
- Generate key points
- Translate explanations into the target language
Audio questions are transcribed with Groq's Whisper model first,
because Groq's chat models are text-only (not multimodal).
"""

import os
from groq import Groq
from utils import load_config


# The Groq chat model used for all completions.
# NOTE: gpt-oss-120b is a reasoning model — its response carries a `reasoning`
# field AND a `content` field. Read ONLY `message.content`, and never set a
# small max_tokens (reasoning tokens are spent first, so a low cap yields
# empty content). Overridable via the GROQ_MODEL env var.
_MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Whisper model used to transcribe audio questions.
_AUDIO_MODEL = "whisper-large-v3"

# Configure the Groq API on module load
_client = None


def _get_client():
    """
    Lazily initialize and return the Groq client.
    Configures the API key on first call.
    """
    global _client
    if _client is None:
        _client = Groq(api_key=load_config())
    return _client


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
2. **Original Explanation**: Restructure and simplify the text tailored for a {difficulty}.
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
    Send extracted text to the LLM for simplification and translation.

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

    client = _get_client()
    prompt = _build_prompt(text, target_language, difficulty)

    try:
        response = client.chat.completions.create(
            model=_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        full_text = response.choices[0].message.content or ""

        # Parse the structured response into sections
        result = _parse_response(full_text, target_language)
        result["full_response"] = full_text
        return result

    except Exception as e:
        error_msg = "Sorry, we couldn't reach the AI assistant. Please check your internet connection and API key, then try again."
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

    key_points = _extract_key_points(explanation)
    translated_key_points = _extract_key_points(translation)

    return {
        "detected_language": detected_lang,
        "key_points": key_points,
        "translated_key_points": translated_key_points,
        "explanation": explanation,
        "translation": translation,
    }


def _extract_key_points(section_text: str) -> str:
    """
    Extract the 'Key Points' bullet list from inside a section (explanation or
    translation). Returns the raw bullet lines, or an empty string if none found.
    """
    import re
    if not section_text:
        return ""

    match = re.search(r'💡\s*\*?\*?\s*Key Points\s*\*?\*?\s*---?\s*\n(.*?)(?=\n📝|\n⚠️|\n##|$)', section_text, re.DOTALL | re.IGNORECASE)
    if match and match.group(1):
        return match.group(1).strip()
    return ""


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

    client = _get_client()
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
        response = client.chat.completions.create(
            model=_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content or ""
        questions = [q.strip() for q in text.strip().split("\n") if q.strip()]
        return questions[:3]
    except Exception:
        return []


def answer_question(document_text: str, target_language: str, question_text: str = None, audio_bytes: bytes = None) -> str:
    """
    Answers a user's question about the document text.

    Accepts either typed text or an audio clip. Because Groq's chat models are
    text-only, an audio question is transcribed with Whisper first, then the
    transcribed text is answered. The document text is never sent to Whisper.
    """
    if not document_text or not document_text.strip():
        return "Please upload a document first."

    if not question_text and not audio_bytes:
        return "Please provide a question."

    client = _get_client()

    # Transcribe audio before asking the chat model (text-only model).
    if audio_bytes and not question_text:
        try:
            transcription = client.audio.transcriptions.create(
                model=_AUDIO_MODEL,
                file=("question.wav", audio_bytes),
            )
            question_text = transcription.text.strip()
        except Exception:
            return "Sorry, I couldn't understand the audio question. Please try speaking again or type your question."

    if not question_text:
        return "Please provide a question."

    prompt = f"""You are an incredibly helpful assistant helping users understand documents.

Document text:
\"\"\"
{document_text}
\"\"\"

User question:
{question_text}

Rules:
1. Answer using ONLY the information in the document.
2. If the answer is not present, say exactly: "The document does not mention this."
3. Explain clearly, simply, and directly.
4. IMPORTANT: You must provide your final answer in the following language: {target_language}.
"""

    try:
        response = client.chat.completions.create(
            model=_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception:
        return "Sorry, I couldn't process that question right now. Please try again."
