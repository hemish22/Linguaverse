# 🔍 LinguaLens

**AI-powered image text extraction, simplification, and translation.**

Upload an image containing complex text (medicine labels, government documents, signboards, research papers, etc.) and get simple, easy-to-understand explanations in your language.

---

## ✨ Features

- **📸 Image Input** — Upload images or capture from webcam
- **🔤 OCR Extraction** — Automatically extracts text using EasyOCR
- **🧠 AI Simplification** — Gemini AI explains complex text in plain language
- **🌐 Multilingual** — Translations in English, Hindi, and Tamil
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
# Edit .env and add your Gemini API key
```

Get a free API key at: https://aistudio.google.com/apikey

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
lingualens/
├── app.py              # Streamlit UI application
├── ocr_module.py       # EasyOCR text extraction
├── llm_module.py       # Gemini API simplification & translation
├── utils.py            # Shared utilities (config, TTS, image processing)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # This file
```

## 🔧 Architecture

```
User uploads image
       │
       ▼
┌─────────────┐
│  OCR Module  │  ← EasyOCR (English, Hindi, Tamil)
│ extract_text │
└──────┬──────┘
       │ extracted text
       ▼
┌──────────────────┐
│   LLM Module     │  ← Gemini 2.0 Flash
│ simplify_and_    │
│ translate        │
└──────┬───────────┘
       │ explanation + translation
       ▼
┌──────────────────┐
│  Streamlit UI    │  ← Display results + TTS
│  app.py          │
└──────────────────┘
```

## 🌐 Supported Languages

| Language | OCR | Translation | TTS |
|----------|-----|-------------|-----|
| English  | ✅  | ✅          | ✅  |
| Hindi    | ✅  | ✅          | ✅  |
| Tamil    | ✅  | ✅          | ✅  |

## 📋 Requirements

- Python 3.9+
- Gemini API key (free tier available)
- Internet connection (for API calls and TTS)

---

Built with ❤️ using Streamlit, EasyOCR, and Google Gemini
