# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision

LinguaLens is an AI-powered image-to-explanation system. Users upload images containing text (medicine labels, government documents, signboards, research papers, etc.), and the system extracts, simplifies, and translates the text into plain language across multiple languages — making complex information accessible to non-expert users.

## Goals

1. **OCR Extraction** — Accurately extract text from uploaded images using EasyOCR
2. **Intelligent Simplification** — Use an LLM (Gemini) to simplify and explain complex text for non-expert users
3. **Multilingual Translation** — Translate explanations into English, Hindi, and Tamil
4. **Accessible UI** — Provide a clean Streamlit interface with image upload, webcam capture, and language selection
5. **Audio Output** — Optional text-to-speech using gTTS for spoken explanations

## Non-Goals (Out of Scope)

- Real-time video stream processing
- User authentication or account management
- Persistent storage / database backend
- Deployment to production cloud (prototype only)
- Support for more than 3 languages in v1
- PDF or document file upload (images only)

## Users

**Non-expert individuals** who encounter complex text in daily life:
- Patients reading medicine labels
- Citizens reading government documents
- Travelers reading foreign signboards
- Students reading research papers or technical instructions

## Constraints

- **Technical**: Python-only stack; Streamlit for frontend; must work locally
- **API**: Requires a Gemini API key (user-provided via `.env`)
- **Timeline**: Hackathon prototype — single milestone, rapid delivery
- **Languages**: v1 supports English, Hindi, Tamil only

## Success Criteria

- [ ] User can upload an image and see extracted text
- [ ] User can capture image from webcam
- [ ] Extracted text is simplified into plain-language explanation
- [ ] Explanation is translated into user-selected language
- [ ] Optional TTS plays the explanation aloud
- [ ] Project runs locally with `pip install -r requirements.txt && streamlit run app.py`
