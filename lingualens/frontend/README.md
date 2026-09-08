# LinguaLens frontend

React + Vite + TypeScript frontend for **LinguaLens** — replaces the legacy
Streamlit UI. OCR → AI simplify/translate → TTS → Q&A, all in one page.

## Stack

- [Vite](https://vite.dev) 8 + React 19 + TypeScript (strict)
- [Tailwind CSS](https://tailwindcss.com) v4 + [shadcn/ui](https://ui.shadcn.com) (base-ui)
- Custom brand theme: "Paper & Ink" (light) / "Midnight Lens" (dark), built on the
  original LinguaLens Navy/Red/Orange/Yellow palette — warm paper background,
  ink-navy text, vermilion action color, amber highlights, and a lens-aperture motif.
- [react-markdown](https://github.com/remarkjs/react-markdown) for LLM output

## Requirements

- Node 26 / npm 12 (project scaffolded and verified with these)
- A running LinguaLens FastAPI backend (default `http://localhost:8000`)

## Run it

```bash
npm install
cp .env.example .env     # optional — VITE_API_URL already defaults to :8000
npm run dev              # http://localhost:5173
```

Production build + preview:

```bash
npm run build            # tsc + vite build → dist/
npm run preview
```

Backend URL comes from `VITE_API_URL` (default `http://localhost:8000`).

## Features

- Image or PDF upload + drag-and-drop + webcam capture, or paste text directly
  (PDFs show a file card with name + size instead of a thumbnail)
- "Try a sample" demo buttons load two preset forms (Hindi Form 7, English Form 8)
  shipped as PDFs in `public/demo/` — same staged-file flow as an upload, no pipeline special-casing
- Settings: image text language (English & Hindi / English & Tamil),
  output language (English / Hindi / Tamil), difficulty (Child / Student / Professional)
- OCR text + confidence shown with extracted text (copy button); PDFs add a
  `· N pages` note beside the confidence
- Result panel: original explanation + translation side-by-side, key points,
  detected language
- TTS audio player: prefetches the explanation audio (instant play), playback
  controls (play/pause, scrubbable seek bar, restart, 0.75–2× speed), reused
  for Q&A answers (`AudioPlayer.tsx` + base-ui `Slider`); fetches MP3 from
  `/api/tts`
- Q&A: suggested questions, typed questions, voice questions (MediaRecorder →
  `/api/ask`), chat-style conversation history
- Loading / empty / error states; responsive layout; accessible labels,
  keyboard-navigable dropzone, `aria-live` announcements

## Structure

```
src/
  lib/types.ts          API response types
  lib/api.ts            fetch wrappers for the /api contract (VITE_API_URL)
  components/
    Header.tsx          brand bar + API health dot + theme toggle
    Hero.tsx            intro / lens motif
    InputPanel.tsx      Upload / Webcam / Paste tabs
    SettingsPanel.tsx   the three selects
    ResultsView.tsx     OCR text + confidence + explanation/translation + audio player
    QaPanel.tsx         suggested / typed / voice Q&A + conversation + answer audio
    AudioPlayer.tsx     shared TTS player (play/pause, seek, restart, speed, prefetch)
    Markdown.tsx        safe LLM output renderer
    ErrorBoundary.tsx   catches render errors (friendly fallback instead of blank page)
    ui/                 shadcn/ui components
```

## API contract consumed

From `board.md` (base `VITE_API_URL`):

| Endpoint | Purpose |
| --- | --- |
| `POST /api/ocr` | multipart image or PDF → `{ text, confidence, pages }` |
| `POST /api/analyze` | `{ text, target_language, difficulty }` → result |
| `POST /api/suggest` | `{ document_text, target_language }` → `{ questions }` |
| `POST /api/ask` | typed or audio question → `{ answer }` |
| `POST /api/tts` | `{ text, language }` → `audio/mpeg` |
| `GET /api/health` | liveness for the status dot |