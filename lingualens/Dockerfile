# LinguaLens backend — FastAPI (Render, free tier)
#
# The backend uses Tesseract (via pytesseract) — no PyTorch/EasyOCR — so the
# image is light (~few hundred MB) and fits Render's free 512MB RAM plan.

FROM python:3.11-slim

# Tesseract binary + language packs (English + Hindi + Tamil)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-tam \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app and the backend python modules
COPY api.py .
COPY ocr_module.py llm_module.py utils.py pdf_extract.py .

EXPOSE 8000

# Render injects $PORT (fallback 8000 for local runs)
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]