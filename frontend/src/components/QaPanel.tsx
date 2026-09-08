import { useEffect, useRef, useState } from "react"
import { AlertCircle, Mic, MicOff, Send, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Markdown } from "./Markdown"
import { AudioPlayer } from "./AudioPlayer"
import type { ChatEntry, TargetLanguage } from "@/lib/types"

interface QaPanelProps {
  suggestedQuestions: string[]
  chatHistory: ChatEntry[]
  onAskText: (question: string) => Promise<void>
  onAskVoice: (audio: Blob) => Promise<void>
  busy: boolean
  targetLanguage: TargetLanguage
}

export function QaPanel({
  suggestedQuestions,
  chatHistory,
  onAskText,
  onAskVoice,
  busy,
  targetLanguage,
}: QaPanelProps) {
  const [question, setQuestion] = useState("")
  const [recording, setRecording] = useState(false)
  const [recentError, setRecentError] = useState<string | null>(null)
  const recorderRef = useRef<{ stop: () => Promise<Blob | null>; cancel: () => void } | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }, [chatHistory.length])

  async function submitText() {
    const q = question.trim()
    if (!q || busy) return
    setQuestion("")
    setRecentError(null)
    try {
      await onAskText(q)
    } catch (e) {
      setRecentError(e instanceof Error ? e.message : "Question failed")
    }
  }

  async function submitSuggested(q: string) {
    if (busy) return
    setRecentError(null)
    try {
      await onAskText(q)
    } catch (e) {
      setRecentError(e instanceof Error ? e.message : "Question failed")
    }
  }

  async function toggleRecording() {
    if (recording) {
      const blob = await recorderRef.current?.stop()
      setRecording(false)
      if (blob) {
        setRecentError(null)
        try {
          await onAskVoice(blob)
        } catch (e) {
          setRecentError(e instanceof Error ? e.message : "Voice question failed")
        }
      }
      return
    }
    try {
      const r = await startRecording()
      recorderRef.current = r
      setRecording(true)
    } catch {
      setRecentError("Microphone access was denied. Use typed questions instead.")
    }
  }

  return (
    <section aria-label="Ask questions about this document" className="space-y-5">
      {suggestedQuestions.length > 0 && (
        <div className="space-y-2">
          <p className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            <Sparkles className="size-3.5" aria-hidden />
            Suggested questions
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, i) => (
              <Button
                key={i}
                variant="secondary"
                size="sm"
                onClick={() => submitSuggested(q)}
                disabled={busy}
                className="h-auto whitespace-normal text-left"
              >
                {q}
              </Button>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <p className="flex items-center gap-1.5 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
          <Send className="size-3.5" aria-hidden />
          Ask in any language — type or speak
        </p>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
          <Textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                submitText()
              }
            }}
            placeholder="e.g. What documents are required? · इस फॉर्म में क्या भरना है? · இதில் என்ன நிரப்ப வேண்டும்?"
            className="min-h-16 flex-1"
            rows={2}
            disabled={busy}
            aria-label="Type your question"
          />
          <div className="flex shrink-0 gap-2">
            <Button
              onClick={submitText}
              disabled={!question.trim() || busy}
              className="flex-1 sm:flex-none"
            >
              <Send data-icon="inline-start" />
              Ask
            </Button>
            <Button
              variant={recording ? "destructive" : "secondary"}
              onClick={toggleRecording}
              disabled={busy && !recording}
              aria-pressed={recording}
              title={recording ? "Stop and send recording" : "Record a voice question"}
            >
              {recording ? <MicOff /> : <Mic />}
              <span className="hidden sm:inline">{recording ? "Send voice" : "Voice"}</span>
            </Button>
          </div>
        </div>
        {recording && (
          <p className="flex items-center gap-2 text-xs font-medium text-vermilion">
            <span className="size-2 animate-pulse rounded-full bg-vermilion" aria-hidden />
            Recording… tap “Send voice” when finished.
          </p>
        )}
        {recentError && (
          <Alert variant="destructive" className="py-2">
            <AlertCircle className="size-4" aria-hidden />
            <AlertTitle className="text-sm">Couldn’t answer</AlertTitle>
            <AlertDescription className="text-xs">{recentError}</AlertDescription>
          </Alert>
        )}
      </div>

      {chatHistory.length > 0 && (
        <div className="space-y-4">
          <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Conversation
          </p>
          <ol className="space-y-4">
            {chatHistory.map((msg, i) => (
              <li
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-xs sm:max-w-[75%] ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card ring-1 ring-foreground/10"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="space-y-2">
                      <Markdown>{msg.content}</Markdown>
                      <AudioPlayer
                        text={msg.content}
                        language={targetLanguage}
                        label="Listen to this answer"
                        compact
                      />
                    </div>
                  ) : (
                    <p className="leading-relaxed">{msg.content}</p>
                  )}
                </div>
              </li>
            ))}
          </ol>
          <div ref={endRef} aria-hidden />
        </div>
      )}
    </section>
  )
}

async function startRecording(): Promise<{
  stop: () => Promise<Blob | null>
  cancel: () => void
}> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
    ? "audio/webm;codecs=opus"
    : MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : ""
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
  const chunks: BlobPart[] = []
  recorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunks.push(e.data)
  }
  const stopped = new Promise<Blob | null>((resolve) => {
    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop())
      resolve(chunks.length ? new Blob(chunks, { type: mimeType || "audio/webm" }) : null)
    }
  })
  recorder.start()
  return {
    stop: async () => {
      recorder.stop()
      return stopped
    },
    cancel: () => {
      recorder.stop()
      stream.getTracks().forEach((t) => t.stop())
    },
  }
}