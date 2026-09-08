# LinguaLens backend — FastAPI (Hugging Face Spaces, Docker SDK)
#
# Note: first boot downloads EasyOCR detection/recognition models (~64MB) and
# loads PyTorch, which needs ~1GB+ RAM once the app starts — expect a slow
# cold start. HF Spaces free tier provides 16GB RAM.
# Storage/image soft limit on HF is 10GB — well within our needs.

FROM python:3.11-slim

# OS libraries required by EasyOCR / OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app and the backend python modules
COPY api.py .
COPY ocr_module.py llm_module.py utils.py pdf_extract.py .

# Hugging Face Spaces expects the app on port 7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-7860}"]