"""Tests for LinguaLens utility and LLM parsing helpers."""

import pytest


# NOTE: importing llm_module depends on a Gemini SDK being installed. Jim is
# migrating this module from `google-generativeai` to `google-genai`; the tests
# below only exercise pure helpers and should remain valid across that change.

def _clean_for_tts(text):
    from utils import clean_for_tts
    return clean_for_tts(text)


class TestCleanForTts:
    def test_strips_markdown_tokens(self):
        assert _clean_for_tts("**bold** *italic* #header `code`") == "bold italic header code"

    def test_strips_bullets(self):
        assert _clean_for_tts("- item one\n- item two") == "item one\nitem two"
        assert _clean_for_tts("• bullet") == "bullet"

    def test_replaces_loose_dashes(self):
        assert _clean_for_tts("a - b") == "a, b"

    def test_returns_empty_for_empty_input(self):
        assert _clean_for_tts("") == ""
        assert _clean_for_tts(None) == ""


class TestParseResponse:
    def _parse(self, text, target_language="English"):
        from llm_module import _parse_response
        return _parse_response(text, target_language)

    def test_parses_all_sections(self):
        sample = (
            "## Detected Language\nHindi\n\n"
            "## Original Explanation\nQuick summary body\n\n"
            "## Translated Explanation (English)\nTranslated body\n"
        )
        result = self._parse(sample, "English")
        assert result["detected_language"] == "Hindi"
        assert result["explanation"] == "Quick summary body"
        assert result["translation"] == "Translated body"

    def test_missing_translation_falls_back_to_unknown(self):
        sample = "## Detected Language\nTamil\n\n## Original Explanation\nbody\n"
        result = self._parse(sample, "Hindi")
        assert result["detected_language"] == "Tamil"
        assert result["explanation"] == "body"
        assert result["translation"] == ""

    def test_no_sections_returns_whole_text_as_explanation(self):
        result = self._parse("just some raw text", "English")
        assert result["explanation"] == "just some raw text"
        assert result["detected_language"] == "Unknown"

    def test_empty_input(self):
        result = self._parse("", "English")
        assert result["detected_language"] == "Unknown"
        assert result["explanation"] == ""
        assert result["translation"] == ""
