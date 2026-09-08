import { useCallback, useEffect, useState } from "react"
import {
  BadgeAlert,
  Copy,
  Check,
  FileText,
  Languages,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Markdown } from "./Markdown"
import { AudioPlayer } from "./AudioPlayer"
import type { AnalysisResult, TargetLanguage } from "@/lib/types"

interface ResultsViewProps {
  ocrText: string
  confidence: number
  ocrPages?: number | null
  analysis: AnalysisResult
  targetLanguage: TargetLanguage
}

export function ResultsView({
  ocrText,
  confidence,
  ocrPages,
  analysis,
  targetLanguage,
}: ResultsViewProps) {
  const [copiedText, setCopiedText] = useState(false)

  useEffect(() => {
    if (!copiedText) return
    const t = setTimeout(() => setCopiedText(false), 1600)
    return () => clearTimeout(t)
  }, [copiedText])

  const copyOcr = useCallback(() => {
    navigator.clipboard.writeText(ocrText).then(() => setCopiedText(true))
  }, [ocrText])

  const original = analysis.explanation
  const translation = analysis.translation
  const mainAudioText = translation || original

  return (
    <section aria-label="Analysis results" className="space-y-6">
      <AudioPlayer text={mainAudioText} language={targetLanguage} prefetch label="Listen to the explanation" />

      {/* OCR text */}
      <Card>
        <CardHeader className="flex-row items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2">
            <FileText className="size-4 text-vermilion" aria-hidden />
            Extracted text
          </CardTitle>
          <Button variant="ghost" size="icon-sm" onClick={copyOcr} aria-label="Copy extracted text">
            {copiedText ? <Check className="text-emerald-500" /> : <Copy />}
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <span>
              OCR confidence
              <span className="ml-1.5 inline-flex items-center gap-1 text-foreground/80">
                {confidence >= 0.7 ? (
                  <Badge variant="default" className="bg-emerald-600/15 text-emerald-700 dark:text-emerald-400">
                    {(confidence * 100).toFixed(0)}%
                  </Badge>
                ) : (
                  <Badge variant="default" className="bg-amber-600/15 text-amber-700 dark:text-amber-400">
                    {(confidence * 100).toFixed(0)}%
                  </Badge>
                )}
              </span>
            </span>
            {typeof ocrPages === "number" && (
              <span>
                · {ocrPages} {ocrPages === 1 ? "page" : "pages"}
              </span>
            )}
            <span className="inline-flex items-center gap-1">
              <Languages className="size-3.5" aria-hidden />
              Detected&nbsp;language: {analysis.detected_language || "—"}
            </span>
            {confidence < 0.5 && (
              <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400">
                <BadgeAlert className="size-3.5" aria-hidden />
                Low confidence — text may be inaccurate.
              </span>
            )}
          </div>

          {confidence < 0.7 ? (
            <Progress value={Math.round(confidence * 100)} className="mb-4" aria-label={`OCR confidence ${confidence.toFixed(0)} percent`} />
          ) : null}

          <div className="max-h-72 overflow-y-auto rounded-xl bg-muted/50 p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap">
            {ocrText}
          </div>
        </CardContent>
      </Card>

      {/* Explanation + translation side-by-side */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="lg:h-full">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-vermilion" aria-hidden />
              {targetLanguage === "English" ? "Explanation" : "Explanation (original)"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown>{original}</Markdown>
            {analysis.key_points?.trim() && (
              <>
                <Separator className="my-4" />
                <p className="mb-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Key points
                </p>
                <Markdown>{analysis.key_points}</Markdown>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="lg:h-full">
          <CardHeader className="flex-row items-center justify-between gap-2">
            <CardTitle className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-amber" aria-hidden />
              {targetLanguage === "English"
                ? "Translation"
                : `Translation (${targetLanguage === "Hindi" ? "हिंदी" : "தமிழ்"})`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Markdown>{translation || original}</Markdown>
            {analysis.translated_key_points?.trim() && targetLanguage !== "English" && (
              <>
                <Separator className="my-4" />
                <p className="mb-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase">
                  Key points
                </p>
                <Markdown>{analysis.translated_key_points}</Markdown>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  )
}