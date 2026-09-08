import { useCallback, useEffect, useState } from "react"
import {
  CheckCircle2,
  LoaderCircle,
  MessageCircleQuestion,
  RefreshCcw,
  ScanText,
  XCircle,
} from "lucide-react"
import { Header } from "./components/Header"
import { Hero } from "./components/Hero"
import { InputPanel, type InputPayload } from "./components/InputPanel"
import { SettingsPanel } from "./components/SettingsPanel"
import { ResultsView } from "./components/ResultsView"
import { QaPanel } from "./components/QaPanel"
import { Badge } from "./components/ui/badge"
import { Button } from "./components/ui/button"
import { Card, CardContent } from "./components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert"
import { FileText } from "lucide-react"
import { healthCheck, analyzeText, ocrFile, askTypedQuestion, askVoiceQuestion, suggestQuestions } from "./lib/api"
import type {
  AnalysisResult,
  ChatEntry,
  Difficulty,
  SourcePreset,
  TargetLanguage,
} from "./lib/types"

interface StagedFile extends InputPayload {
  size: number
}

type Phase =
  | { stage: "setup" }
  | { stage: "loading"; step: string }
  | { stage: "results" }
  | { stage: "error"; message: string }

export default function App() {
  const [backendUp, setBackendUp] = useState(false)
  const [phase, setPhase] = useState<Phase>({ stage: "setup" })

  const [sourcePreset, setSourcePreset] = useState<SourcePreset>("English & Hindi")
  const [targetLanguage, setTargetLanguage] = useState<TargetLanguage>("Hindi")
  const [difficulty, setDifficulty] = useState<Difficulty>("Student")

  const [file, setFile] = useState<StagedFile | null>(null)
  const [directText, setDirectText] = useState("")

  const [ocrText, setOcrText] = useState("")
  const [confidence, setConfidence] = useState(0)
  const [ocrPages, setOcrPages] = useState<number | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [chatHistory, setChatHistory] = useState<ChatEntry[]>([])
  const [qaBusy, setQaBusy] = useState(false)

  useEffect(() => {
    let alive = true
    healthCheck().then((up) => alive && setBackendUp(up))
    return () => {
      alive = false
    }
  }, [])

  const handleFile = useCallback(
    (payload: InputPayload) => {
      setFile({ ...payload, size: payload.blob.size })
      setDirectText("")
    },
    [],
  )

  const handleDirectText = useCallback((text: string) => {
    setDirectText(text)
    setFile(null)
  }, [])

  const onChangeSettings = useCallback(
    (patch: {
      sourcePreset?: SourcePreset
      targetLanguage?: TargetLanguage
      difficulty?: Difficulty
    }) => {
      if (patch.sourcePreset) setSourcePreset(patch.sourcePreset)
      if (patch.targetLanguage) setTargetLanguage(patch.targetLanguage)
      if (patch.difficulty) setDifficulty(patch.difficulty)
    },
    [],
  )

  const runAnalysis = useCallback(async () => {
    setPhase({ stage: "loading", step: "Reading your document…" })
    setChatHistory([])
    setSuggestedQuestions([])
    setAnalysis(null)
    try {
      let text = directText
      let conf = 1
      if (directText) {
        setPhase({ stage: "loading", step: "Preparing your text…" })
      } else if (file) {
        const label = file.kind === "pdf" ? "document" : "image"
        setPhase({
          stage: "loading",
          step: `Extracting text from the ${label} (OCR)…`,
        })
        const ocr = await ocrFile(file.blob, sourcePreset, file.name)
        text = ocr.text
        conf = ocr.confidence
        setOcrPages(ocr.pages ?? null)
      } else {
        setPhase({ stage: "setup" })
        return
      }

      if (!text || !text.trim()) {
        setPhase({
          stage: "error",
          message: "No text was detected. Try a clearer image, a different source preset, or paste the text directly.",
        })
        return
      }

      setOcrText(text)
      setConfidence(conf)
      setPhase({ stage: "loading", step: "Simplifying and translating with AI…" })
      const result = await analyzeText(text, targetLanguage, difficulty)
      setAnalysis(result)

      setPhase({ stage: "loading", step: "Generating suggested questions…" })
      try {
        const questions = await suggestQuestions(text, targetLanguage)
        setSuggestedQuestions(questions)
      } catch {
        setSuggestedQuestions([])
      }

      setPhase({ stage: "results" })
    } catch (e) {
      setPhase({
        stage: "error",
        message: e instanceof Error ? e.message : "Something went wrong while analyzing.",
      })
    }
  }, [file, directText, sourcePreset, targetLanguage, difficulty])

  const askText = useCallback(
    async (q: string) => {
      if (!ocrText) return
      setQaBusy(true)
      try {
        setChatHistory((h) => [...h, { role: "user", content: q }])
        const answer = await askTypedQuestion(ocrText, targetLanguage, q)
        setChatHistory((h) => [...h, { role: "assistant", content: answer }])
      } finally {
        setQaBusy(false)
      }
    },
    [ocrText, targetLanguage],
  )

  const askVoice = useCallback(
    async (audio: Blob) => {
      if (!ocrText) return
      setQaBusy(true)
      try {
        setChatHistory((h) => [...h, { role: "user", content: "🎤 Voice question" }])
        const answer = await askVoiceQuestion(ocrText, targetLanguage, audio)
        setChatHistory((h) => [...h, { role: "assistant", content: answer }])
      } finally {
        setQaBusy(false)
      }
    },
    [ocrText, targetLanguage],
  )

  const resetAll = useCallback(() => {
    setFile(null)
    setDirectText("")
    setOcrText("")
    setConfidence(0)
    setOcrPages(null)
    setAnalysis(null)
    setSuggestedQuestions([])
    setChatHistory([])
    setPhase({ stage: "setup" })
  }, [])

  const hasDocumentInput = Boolean(file || directText)
  const showInputCard = phase.stage === "setup" || phase.stage === "error"
  const isLoading = phase.stage === "loading"

  return (
    <div className="flex min-h-svh flex-col">
      <Header backendUp={backendUp} />

      <Hero />

      <main className="mx-auto w-full max-w-5xl flex-1 space-y-6 px-4 pb-16">
        {phase.stage === "loading" && (
          <LoadingPanel step={phase.step} />
        )}

        {phase.stage === "error" && (
          <Alert variant="destructive">
            <XCircle className="size-4" aria-hidden />
            <AlertTitle className="text-sm font-semibold">Analysis could not be completed</AlertTitle>
            <AlertDescription>{phase.message}</AlertDescription>
          </Alert>
        )}

        {showInputCard && (
          <Card className="shadow-xs">
            <CardContent className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <ScanText className="size-4 text-vermilion" aria-hidden />
                  <h2 className="text-sm font-semibold tracking-tight">1 · Add your document</h2>
                </div>
                {hasDocumentInput && (
                  <Button variant="ghost" size="sm" onClick={resetAll}>
                    <RefreshCcw data-icon="inline-start" />
                    Start over
                  </Button>
                )}
              </div>

              <InputPanel onImage={handleFile} onText={handleDirectText} disabled={false} />

              {file && file.kind === "image" && (
                <figure className="flex items-start gap-4">
                  <img
                    src={file.dataUrl}
                    alt="The image you uploaded to analyze"
                    className="max-h-56 w-auto rounded-xl border border-border object-contain shadow-sm"
                  />
                  <figcaption className="py-1 text-xs text-muted-foreground">
                    {file.name}
                    <br />
                    Ready to analyze.
                  </figcaption>
                </figure>
              )}

              {file && file.kind === "pdf" && (
                <div className="flex items-center gap-4 rounded-xl border border-border bg-muted/40 p-4">
                  <div className="lens-motif flex size-12 shrink-0 items-center justify-center rounded-lg bg-card">
                    <FileText className="size-6 text-vermilion" aria-hidden />
                  </div>
                  <div className="min-w-0 text-sm">
                    <p className="truncate font-semibold">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(0)} KB · PDF — ready to analyze.
                    </p>
                  </div>
                </div>
              )}
              {directText && (
                <Badge variant="secondary" className="justify-self-start">
                  Using pasted text ({directText.length} characters)
                </Badge>
              )}
            </CardContent>
          </Card>
        )}

        {showInputCard && (
          <SettingsPanel
            sourcePreset={sourcePreset}
            targetLanguage={targetLanguage}
            difficulty={difficulty}
            onChange={onChangeSettings}
            disabled={false}
          />
        )}

        {(hasDocumentInput && (showInputCard || phase.stage === "results")) && (
          <Button
            size="lg"
            className="w-full"
            onClick={runAnalysis}
            disabled={isLoading}
          >
            {isLoading ? (
              <LoaderCircle className="animate-spin" />
            ) : (
              <MessageCircleQuestion data-icon="inline-start" />
            )}
            {analysis && phase.stage === "results" ? "Re-run analysis" : "Analyze document"}
          </Button>
        )}

        {phase.stage === "results" && analysis && (
          <>
            <ResultsView
              ocrText={ocrText}
              confidence={confidence}
              ocrPages={ocrPages}
              analysis={analysis}
              targetLanguage={targetLanguage}
            />

            <Card className="shadow-xs">
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <MessageCircleQuestion className="size-4 text-vermilion" aria-hidden />
                  <h2 className="text-sm font-semibold tracking-tight">
                    Ask questions about this document
                  </h2>
                </div>
                <QaPanel
                  suggestedQuestions={suggestedQuestions}
                  chatHistory={chatHistory}
                  onAskText={askText}
                  onAskVoice={askVoice}
                  busy={qaBusy}
                  targetLanguage={targetLanguage}
                />
              </CardContent>
            </Card>
          </>
        )}
      </main>

      <footer className="border-t border-border/70 py-4 text-center text-xs text-muted-foreground">
        LinguaLens · OCR → AI explain → translate → listen · Built by Hemish Jain &amp; Anukool Kashyap
      </footer>
    </div>
  )
}

function LoadingPanel({ step }: { step: string }) {
  return (
    <Card className="shadow-xs">
      <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
        <LoaderCircle className="size-8 animate-spin text-vermilion" aria-hidden />
        <p className="text-sm font-semibold">{step}</p>
        <p className="text-xs text-muted-foreground" aria-live="polite">
          This can take a few seconds while the AI works.
        </p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <ScanText className="size-3.5" aria-hidden />
          <span>OCR</span> ·
          <MessageCircleQuestion className="size-3.5" aria-hidden />
          <span>Simplify</span> ·
          <CheckCircle2 className="size-3.5" aria-hidden />
          <span>Translate</span>
        </div>
      </CardContent>
    </Card>
  )
}