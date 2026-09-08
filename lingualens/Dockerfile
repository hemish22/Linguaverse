# LinguaLens backend — FastAPI (Render)
#
# Note: the first boot downloads EasyOCR detection/recognition models (~64MB)
# and loads PyTorch, which needs ~1GB+ RAM once the app starts.

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
COPY ocr_module.py llm_module.py utils.py .

EXPOSE 8000

# Render provides $PORT (defaults to 8000 locally)
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
