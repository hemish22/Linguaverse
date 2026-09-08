#!/usr/bin/env bash
#
# run-dev.sh — start the LinguaLens dev stack (FastAPI backend + Vite frontend).
#
# Prereqs:
#   - .venv with `pip install -r requirements.txt`
#   - GROQ_API_KEY set in .env
#   - frontend/ scaffolded (npm install done once)
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# --- 1) API key check -------------------------------------------------------

if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example to .env and set GROQ_API_KEY first."
  exit 1
fi

if grep -Eq '^GROQ_API_KEY=your_.*_here$|^GROQ_API_KEY=$' .env; then
  echo "ERROR: GROQ_API_KEY is still a placeholder in .env. Set a real key first."
  exit 1
fi

# --- 2) Backend (FastAPI on :8000, backgrounded) ----------------------------

PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -x "$PYTHON" ]; then
  echo "ERROR: $PYTHON not found. Create it with: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [ ! -f api.py ]; then
  echo "ERROR: api.py not found at repo root — the FastAPI backend hasn't been added yet."
  exit 1
fi

echo "Starting FastAPI backend on http://localhost:8000 (docs at /docs)..."
"$ROOT/.venv/bin/uvicorn" api:app --reload --port 8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT

# --- 3) Frontend (Vite on :5173) --------------------------------------------

if [ ! -d frontend ]; then
  echo ""
  echo "WARNING: frontend/ not found (Pam is still building it)."
  echo "Backend is running in the background — Ctrl-C to stop it."
  wait "$BACKEND_PID"
  exit 0
fi

cd frontend
if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo ""
echo "Starting Vite dev server on http://localhost:5173 ..."
exec npm run dev
