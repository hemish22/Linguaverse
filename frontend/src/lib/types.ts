export type TargetLanguage = "English" | "Hindi" | "Tamil"

export type Difficulty = "Child" | "Student" | "Professional"

export type SourcePreset = "English & Hindi" | "English & Tamil"

export interface OcrResponse {
  text: string
  confidence: number
  pages: number | null
}

export interface AnalysisResult {
  detected_language: string
  explanation: string
  translation: string
  key_points: string
  translated_key_points: string
}

export interface SuggestResponse {
  questions: string[]
}

export interface AskResponse {
  answer: string
}

export interface ChatEntry {
  role: "user" | "assistant"
  content: string
}

export type UiState =
  | { status: "idle" }
  | { status: "loading"; step: string }
  | { status: "error"; message: string }