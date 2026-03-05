# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0 — Working Prototype

## Must-Haves (from SPEC)

- [ ] OCR text extraction from images
- [ ] LLM-powered simplification and explanation
- [ ] Multilingual translation (English, Hindi, Tamil)
- [ ] Streamlit UI with upload + webcam
- [ ] Clean modular project structure

## Phases

### Phase 1: Project Scaffolding & OCR Module
**Status**: ⬜ Not Started
**Objective**: Set up project structure, dependencies, and build the OCR extraction module
**Deliverables**:
- `requirements.txt` with all dependencies
- `ocr_module.py` with `extract_text()` function using EasyOCR
- `utils.py` with shared utilities (image processing, config loading)
- Basic project structure in place

### Phase 2: LLM Processing Module
**Status**: ⬜ Not Started
**Objective**: Build the LLM interaction module for text simplification, explanation, and translation
**Deliverables**:
- `llm_module.py` with functions for simplification and translation
- Prompt templates for explanation generation
- Gemini API integration with error handling
- `.env` configuration for API keys

### Phase 3: Streamlit UI & Integration
**Status**: ⬜ Not Started
**Objective**: Build the complete Streamlit frontend and wire all modules together
**Deliverables**:
- `app.py` — full Streamlit application
- Image upload and webcam capture
- Language selection dropdown
- Display panels for extracted text, explanation, and translation
- Optional TTS playback with gTTS

### Phase 4: Polish & Documentation
**Status**: ⬜ Not Started
**Objective**: Final testing, error handling improvements, README, and run instructions
**Deliverables**:
- README.md with setup and run instructions
- Error handling for edge cases (no text found, API failures)
- Code comments and docstrings
- Final verification of end-to-end flow
