import type {
  AnalysisResult,
  AskResponse,
  Difficulty,
  OcrResponse,
  SourcePreset,
  SuggestResponse,
  TargetLanguage,
} from "./types"

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

export class ApiError extends Error {
  status?: number

  constructor(
    message: string,
    status?: number,
  ) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

async function parseJson<T>(res: Response): Promise<T> {
  let body: unknown
  try {
    body = await res.json()
  } catch {
    body = null
  }
  if (!res.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : `Request failed (${res.status})`
    throw new ApiError(detail, res.status)
  }
  return body as T
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/health`)
    if (!res.ok) return false
    const data = await parseJson<{ status: string }>(res)
    return data.status === "ok"
  } catch {
    return false
  }
}

export async function ocrFile(
  file: File | Blob,
  sourceLanguagePreset: SourcePreset,
  filename: string,
): Promise<OcrResponse> {
  const form = new FormData()
  form.append("file", file, filename)
  form.append("source_language_preset", sourceLanguagePreset)
  const res = await fetch(`${API_URL}/api/ocr`, { method: "POST", body: form })
  return parseJson<OcrResponse>(res)
}

export async function analyzeText(
  text: string,
  targetLanguage: TargetLanguage,
  difficulty: Difficulty,
): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, target_language: targetLanguage, difficulty }),
  })
  return parseJson<AnalysisResult>(res)
}

export async function suggestQuestions(
  documentText: string,
  targetLanguage: TargetLanguage,
): Promise<string[]> {
  const res = await fetch(`${API_URL}/api/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      document_text: documentText,
      target_language: targetLanguage,
    }),
  })
  const data = await parseJson<SuggestResponse>(res)
  return data.questions ?? []
}

export async function askTypedQuestion(
  documentText: string,
  targetLanguage: TargetLanguage,
  questionText: string,
): Promise<string> {
  const res = await fetch(`${API_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      document_text: documentText,
      target_language: targetLanguage,
      question_text: questionText,
    }),
  })
  const data = await parseJson<AskResponse>(res)
  return data.answer
}

export async function askVoiceQuestion(
  documentText: string,
  targetLanguage: TargetLanguage,
  audio: Blob,
): Promise<string> {
  const ext = audio.type === "audio/webm" ? "webm" : "mp3"
  const form = new FormData()
  form.append("document_text", documentText)
  form.append("target_language", targetLanguage)
  form.append("audio", audio, `question.${ext}`)
  const res = await fetch(`${API_URL}/api/ask`, { method: "POST", body: form })
  const data = await parseJson<AskResponse>(res)
  return data.answer
}

export async function fetchTts(
  text: string,
  language: TargetLanguage,
): Promise<Blob> {
  const res = await fetch(`${API_URL}/api/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  })
  if (!res.ok) {
    throw new ApiError(`TTS failed (${res.status})`, res.status)
  }
  return res.blob()
}