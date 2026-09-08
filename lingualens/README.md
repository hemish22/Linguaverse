# 🔍 LinguaLens

**AI-powered image text extraction, simplification, and translation.**

Upload an image containing complex text (medicine labels, government documents, signboards, research papers, etc.) and get simple, easy-to-understand explanations in your language.

---

## ✨ Features

- **📄 Image / PDF Input** — Upload images, capture from webcam, or drop in a PDF (digital PDFs use their text layer; scanned PDFs are rendered and OCR'd)
- **🔤 OCR Extraction** — Automatically extracts text using EasyOCR
- **🧠 AI Simplification** — GROQ AI explains complex text in plain language
- **🌐 Multilingual** — Translations in English, Hindi, and Tamil
- **🎤 Voice Questions** — Ask follow-up questions by voice (transcribed with Groq `whisper-large-v3`)
- **🔊 Text-to-Speech** — Listen to explanations with gTTS

## 🚀 Quick Start

### 1. Clone and navigate

```bash
cd lingualens
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

```bash
cp .env.example .env
# Edit .env and add your GROQ API key (as GROQ_API_KEY)
```

Get a free API key at: https://console.groq.com/keys

### 4. Run locally (React + FastAPI)

```bash
# Start both the FastAPI backend (:8000) and the Vite dev server (:5173)
./run-dev.sh
```

Or start them separately:

```bash
# Backend — FastAPI at http://localhost:8000/docs
.venv/bin/uvicorn api:app --reload --port 8000
```

```bash
# Frontend — Vite dev server at http://localhost:5173
cd frontend && npm install && npm run dev
```

> **Legacy UI:** the original Streamlit app (`app.py`) still runs at `http://localhost:8501` via `streamlit run app.py` and is kept as a legacy/alternate interface while the React frontend supersedes it.

---

## 📁 Project Structure

```
lingualens/
├── api.py               # FastAPI backend (wraps ocr/llm/utils)
├── frontend/            # React + Vite + TypeScript + Tailwind + shadcn/ui
├── app.py               # Legacy Streamlit UI (alternate)
├── ocr_module.py        # EasyOCR text extraction
├── llm_module.py        # Groq API simplification & translation
├── utils.py             # Shared utilities (config, TTS, image processing)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── run-dev.sh           # Start backend + frontend together
├── tests/               # pytest test suite
└── README.md            # This file
```

## 🔧 Architecture

```
        ┌────────────────────────────────────────────┐
        │   React + Vite + TS + Tailwind + shadcn/ui  │  → Vite dev server (:5173)
        │   frontend/                                 │     (VITE_API_URL, default http://localhost:8000)
        └──────────────────────┬─────────────────────┘
                               │  JSON / multipart
                               ▼
        ┌────────────────────────────────────────────┐
        │   FastAPI backend  api.py (:8000)           │  → /api/ocr /api/analyze /api/suggest
        │   CORS open to Vite dev origin              │    /api/ask /api/tts /api/health
        └──────────┬──────────────┬──────────────┬────┘
                   ▼              ▼              ▼
        ┌──────────────┐  ┌──────────────────┐  ┌───────────┐
        │  EasyOCR      │  │  Groq            │  │  gTTS     │
        │  extract_text │  │  openai/gpt-oss- │  │  TTS      │
        │  (en+hi/en+ta)│  │  120b · whisper- │  └───────────┘
        └──────────────┘  │  large-v3         │
                          └──────────────────┘
```

The React frontend calls the FastAPI backend, which reuses the existing `ocr_module.py` / `llm_module.py` / `utils.py` modules. CORS is open to the Vite dev origin. The legacy `app.py` Streamlit UI is kept as an alternate interface.

## API endpoints

Base: `http://localhost:8000`. Full interactive docs at `/docs`.

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/api/ocr` | multipart `file` (image **or** PDF), `source_language_preset` | `{ text, confidence, pages }` |
| POST | `/api/analyze` | json `{ text, target_language, difficulty }` | `{ detected_language, explanation, translation, key_points, translated_key_points }` |
| POST | `/api/suggest` | json `{ document_text, target_language }` | `{ questions: string[] }` |
| POST | `/api/ask` | multipart `document_text`, `target_language`, optional `question_text`, `audio` | `{ answer: str }` |
| POST | `/api/tts` | json `{ text, language }` | binary `audio/mpeg` |
| GET | `/api/health` | — | `{ status: "ok" }` |

Languages: `English | Hindi | Tamil`. Difficulty: `Child | Student | Professional`.

## 🌐 Supported Languages

| Language | OCR | Translation | TTS |
|----------|-----|-------------|-----|
| English  | ✅  | ✅          | ✅  |
| Hindi    | ✅  | ✅          | ✅  |
| Tamil    | ✅  | ✅          | ✅  |

## 📋 Requirements

- Python 3.9+
- Node.js 18+ (for the React/Vite frontend)
- GROQ API key (free tier available)
- Internet connection (for API calls and TTS)

---

Built with ❤️ using React, FastAPI, EasyOCR, GROQ, and gTTS
