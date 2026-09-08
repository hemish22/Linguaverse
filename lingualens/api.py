"""
api.py — FastAPI backend for LinguaLens.

Exposes the existing LinguaLens python logic over HTTP for the React frontend.
Reuses ocr_module, llm_module, and utils without modifying them.
"""

import io

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from PIL import Image

from ocr_module import extract_text
from pdf_extract import extract_pdf
from llm_module import (
    simplify_and_translate,
    generate_suggested_questions,
    answer_question,
)
from utils import text_to_speech


app = FastAPI(title="LinguaLens API")

# Allow the Vite dev origins (and React defaults). Open in dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str
    target_language: str = "Hindi"
    difficulty: str = "Student"


class SuggestRequest(BaseModel):
    document_text: str
    target_language: str = "English"


class TTSRequest(BaseModel):
    text: str
    language: str = "English"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ocr")
async def ocr(
    file: UploadFile = File(...),
    source_language_preset: str = Form("English & Hindi"),
):
    data = await file.read()

    is_pdf = file.content_type == "application/pdf" or (file.filename or "").lower().endswith(".pdf")
    if is_pdf:
        text, confidence, pages = extract_pdf(data, source_language_preset)
        return {"text": text, "confidence": confidence, "pages": pages}

    image = Image.open(io.BytesIO(data))
    text, confidence = extract_text(image, source_language_preset)
    return {"text": text, "confidence": confidence, "pages": None}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    result = simplify_and_translate(req.text, req.target_language, req.difficulty)
    return {
        "detected_language": result.get("detected_language", "Unknown"),
        "explanation": result.get("explanation", ""),
        "translation": result.get("translation", ""),
        "key_points": result.get("key_points", ""),
        "translated_key_points": result.get("translated_key_points", ""),
    }


@app.post("/api/suggest")
def suggest(req: SuggestRequest):
    questions = generate_suggested_questions(req.document_text, req.target_language)
    return {"questions": questions}


@app.post("/api/ask")
async def ask(
    document_text: str = Form(...),
    target_language: str = Form("Hindi"),
    question_text: str = Form(None),
    audio: UploadFile = File(None),
):
    audio_bytes = None
    if audio is not None:
        audio_bytes = await audio.read()
    answer = answer_question(
        document_text,
        target_language,
        question_text=question_text,
        audio_bytes=audio_bytes,
    )
    return {"answer": answer}


@app.post("/api/tts")
def tts(req: TTSRequest):
    audio_bytes = text_to_speech(req.text, req.language)
    return Response(content=audio_bytes, media_type="audio/mpeg")
