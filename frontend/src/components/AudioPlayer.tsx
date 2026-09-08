import { useCallback, useEffect, useRef, useState } from "react"
import { AudioLines, LoaderCircle, Pause, Play, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { cn } from "cn"
import { fetchTts } from "@/lib/api"
import type { TargetLanguage } from "@/lib/types"

const SPEEDS = [0.75, 1, 1.25, 1.5, 2]

interface AudioPlayerProps {
  text: string
  language: TargetLanguage
  label?: string
  prefetch?: boolean
  compact?: boolean
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds <= 0) return "0:00"
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0")
  return `${m}:${s}`
}

export function AudioPlayer({
  text,
  language,
  label = "Listen",
  prefetch = false,
  compact = false,
}: AudioPlayerProps) {
  const [ready, setReady] = useState(false)
  const [preparing, setPreparing] = useState(prefetch)
  const [playing, setPlaying] = useState(false)
  const [current, setCurrent] = useState(0)
  const [duration, setDuration] = useState(0)
  const [speed, setSpeed] = useState(1)
  const [error, setError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement | null>(null)
  const urlRef = useRef<string | null>(null)

  const dispose = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.removeAttribute("src")
      audioRef.current.load()
      audioRef.current = null
    }
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current)
      urlRef.current = null
    }
    setCurrent(0)
    setDuration(0)
    setPlaying(false)
    setReady(false)
  }, [])

  const ensureAudio = useCallback((src: string) => {
    if (audioRef.current) return audioRef.current
    const audio = new Audio(src)
    audio.playbackRate = speed
    audio.addEventListener("loadedmetadata", () => {
      setDuration(Number.isFinite(audio.duration) ? audio.duration : 0)
    })
    audio.addEventListener("timeupdate", () => setCurrent(audio.currentTime))
    audio.addEventListener("ended", () => setPlaying(false))
    audio.addEventListener("error", () => {
      setPlaying(false)
      setError("Audio couldn’t play. Try again.")
    })
    audioRef.current = audio
    return audio
  }, [speed])

  const play = useCallback(async () => {
    setError(null)
    let src = urlRef.current
    if (!src) {
      setPreparing(true)
      try {
        const blob = await fetchTts(text, language)
        if (urlRef.current) URL.revokeObjectURL(urlRef.current)
        src = URL.createObjectURL(blob)
        urlRef.current = src
        setReady(true)
      } catch (e) {
        setPreparing(false)
        setError(e instanceof Error ? e.message : "TTS unavailable")
        return
      }
      setPreparing(false)
    }
    if (!src) return
    const audio = ensureAudio(src)
    try {
      await audio.play()
      setPlaying(true)
    } catch {
      setError("Audio couldn’t start. Try again.")
    }
  }, [text, language, ensureAudio])

  const toggle = useCallback(() => {
    if (playing) {
      audioRef.current?.pause()
      setPlaying(false)
      return
    }
    void play()
  }, [playing, play])

  const restart = useCallback(() => {
    const audio = audioRef.current
    if (audio) {
      audio.currentTime = 0
      setCurrent(0)
      void audio
        .play()
        .then(() => setPlaying(true))
        .catch(() => {})
      return
    }
    void play()
  }, [play])

  const seek = useCallback((value: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = value
      setCurrent(value)
    }
  }, [])

  const changeSpeed = useCallback((next: number) => {
    setSpeed(next)
    if (audioRef.current) audioRef.current.playbackRate = next
  }, [])

  // Reset on source change; prefetch when requested so the first play is instant.
  useEffect(() => {
    dispose()
    setError(null)
    if (!prefetch) {
      setPreparing(false)
      return
    }
    let cancelled = false
    setPreparing(true)
    fetchTts(text, language)
      .then((blob) => {
        if (cancelled) return
        const u = URL.createObjectURL(blob)
        urlRef.current = u
        setReady(true)
      })
      .catch(() => {
        if (!cancelled) setError("Couldn’t prepare audio — play will fetch on demand.")
      })
      .finally(() => {
        if (!cancelled) setPreparing(false)
      })
    return () => {
      cancelled = true
    }
  }, [text, language, prefetch, dispose])

  useEffect(() => dispose, [dispose])

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-xl border border-border bg-muted/40 shadow-xs",
        compact ? "px-3 py-2" : "p-3 sm:p-4",
      )}
    >
      <div
        className={cn(
          "flex shrink-0 items-center justify-center rounded-full ring-2 ring-vermilion/25",
          compact ? "size-7" : "size-9",
        )}
        aria-hidden
      >
        {preparing && !ready ? (
          <LoaderCircle className="size-4 animate-spin text-vermilion" />
        ) : (
          <AudioLines className={cn("text-vermilion", compact ? "size-3.5" : "size-4")} />
        )}
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        <Button
          variant="default"
          size="icon-sm"
          onClick={toggle}
          disabled={preparing && !ready}
          aria-label={playing ? "Pause audio" : "Play audio"}
          title={label}
        >
          {playing ? <Pause /> : <Play />}
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={restart}
          disabled={!ready}
          aria-label="Restart audio"
          title="Restart audio"
        >
          <RotateCcw />
        </Button>
      </div>

      <div className="min-w-0 flex-1">
        <Slider
          min={0}
          max={duration || 1}
          step={0.1}
          value={Math.min(current, duration || 1)}
          onValueChange={seek}
          disabled={!duration}
          aria-label="Audio position"
        />
        <div
          className={cn(
            "mt-0.5 flex items-center justify-between tabular-nums text-muted-foreground",
            compact ? "text-[9px]" : "text-[11px]",
          )}
        >
          <span>{formatTime(current)}</span>
          {preparing && !ready ? (
            <span className="flex items-center gap-1">
              <LoaderCircle className="size-3 animate-spin" aria-hidden />
              <span className={compact ? "hidden sm:inline" : ""}>preparing audio…</span>
            </span>
          ) : (
            <span>{formatTime(duration)}</span>
          )}
        </div>
      </div>

      <div
        className="flex shrink-0 items-center gap-0.5"
        role="group"
        aria-label="Playback speed"
      >
        {SPEEDS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => changeSpeed(s)}
            aria-pressed={speed === s}
            disabled={!ready}
            className={cn(
              "rounded-md px-1.5 py-0.5 text-[10px] font-medium transition-colors tabular-nums focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-hidden disabled:opacity-40",
              speed === s
                ? "bg-vermilion text-white"
                : "text-muted-foreground hover:bg-card hover:text-foreground",
            )}
            title={`${s}× speed`}
          >
            {s}x
          </button>
        ))}
      </div>

      {error && (
        <span
          className="max-w-40 shrink-0 truncate text-[11px] text-destructive"
          role="alert"
          title={error}
        >
          {error}
        </span>
      )}
    </div>
  )
}