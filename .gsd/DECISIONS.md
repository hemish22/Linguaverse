# DECISIONS.md — Architecture Decision Records

## ADR-001: Use EasyOCR over PaddleOCR
**Date**: 2026-03-05
**Status**: Accepted
**Context**: User suggested EasyOCR or PaddleOCR. EasyOCR has simpler installation, better Python integration, and supports multiple languages out of the box.
**Decision**: Use EasyOCR for text extraction.

## ADR-002: Use Gemini API for LLM
**Date**: 2026-03-05
**Status**: Accepted
**Context**: User suggested Gemini or OpenAI. Gemini offers a generous free tier suitable for hackathon prototypes.
**Decision**: Use Google Gemini API via `google-generativeai` SDK.

## ADR-003: Streamlit for Frontend
**Date**: 2026-03-05
**Status**: Accepted
**Context**: User specified Streamlit. It's ideal for rapid Python-based UI prototyping.
**Decision**: Use Streamlit as the sole frontend framework.
