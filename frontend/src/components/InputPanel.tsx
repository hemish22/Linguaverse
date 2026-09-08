import { useRef, useState } from "react"
import {
  Camera,
  FileText,
  ImageIcon,
  LoaderCircle,
  UploadCloud,
  X,
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

export interface InputPayload {
  kind: "image" | "pdf"
  dataUrl?: string
  blob: Blob
  name: string
}

interface InputPanelProps {
  onImage: (payload: InputPayload) => void
  onText: (text: string) => void
  disabled?: boolean
}

export function InputPanel({ onImage, onText, disabled }: InputPanelProps) {
  const [tab, setTab] = useState("upload")
  const fileRef = useRef<HTMLInputElement>(null)

  return (
    <Tabs value={tab} onValueChange={setTab} className="flex flex-col">
      <TabsList className="w-full">
        <TabsTrigger value="upload">
          <UploadCloud data-icon="inline-start" />
          Upload
        </TabsTrigger>
        <TabsTrigger value="camera">
          <Camera data-icon="inline-start" />
          Webcam
        </TabsTrigger>
        <TabsTrigger value="text">
          <FileText data-icon="inline-start" />
          Paste text
        </TabsTrigger>
      </TabsList>

      <TabsContent value="upload">
        <Dropzone
          onImage={onImage}
          onClick={() => fileRef.current?.click()}
          disabled={disabled}
        />
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,application/pdf,.pdf"
          className="hidden"
          aria-hidden
          tabIndex={-1}
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleDroppedFile(file, onImage)
            e.target.value = ""
          }}
        />
        <DemoRow onImage={onImage} disabled={disabled} />
      </TabsContent>

      <TabsContent value="camera" className="mt-4">
        <WebcamCapture onImage={onImage} disabled={disabled} />
      </TabsContent>

      <TabsContent value="text" className="mt-4">
        <TextInput onText={onText} disabled={disabled} />
      </TabsContent>
    </Tabs>
  )
}

function handleDroppedFile(file: File, onImage: (p: InputPayload) => void) {
  if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
    onImage({
      kind: "pdf",
      blob: file,
      name: file.name,
    })
    return
  }
  if (file.type.startsWith("image/")) {
    readImageFile(file, onImage)
  }
}

function readImageFile(file: File, onImage: (p: InputPayload) => void) {
  const reader = new FileReader()
  reader.onload = () => {
    onImage({
      kind: "image",
      dataUrl: String(reader.result),
      blob: file,
      name: file.name,
    })
  }
  reader.readAsDataURL(file)
}

function Dropzone({
  onImage,
  onClick,
  disabled,
}: {
  onImage: (p: InputPayload) => void
  onClick: () => void
  disabled?: boolean
}) {
  const [dragOver, setDragOver] = useState(false)
  return (
    <div
      className={cn(
        "mt-4 flex min-h-56 cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-10 text-center transition-colors",
        dragOver
          ? "border-vermilion bg-vermilion/5"
          : "border-border bg-card hover:border-vermilion/50",
        disabled && "pointer-events-none opacity-50",
      )}
      role="button"
      tabIndex={0}
      aria-label="Upload an image or PDF, or drag and drop one here"
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick()
        }
      }}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        const file = e.dataTransfer.files?.[0]
        if (file) handleDroppedFile(file, onImage)
      }}
    >
      <div className="lens-motif flex size-16 items-center justify-center rounded-full border border-vermilion/30">
        <ImageIcon className="size-7 text-vermilion" />
      </div>
      <div className="space-y-1">
        <p className="text-sm font-semibold">
          {dragOver ? "Release to add your file" : "Drop an image or PDF, or click to browse"}
        </p>
        <p className="text-xs text-muted-foreground">
          JPG, PNG, WEBP or PDF — a label, form, signboard, manual or page
        </p>
      </div>
      <Button type="button" variant="secondary" size="sm" className="pointer-events-none">
        Choose file
      </Button>
    </div>
  )
}

function WebcamCapture({
  onImage,
  disabled,
}: {
  onImage: (p: InputPayload) => void
  disabled?: boolean
}) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [streamActive, setStreamActive] = useState(false)
  const [capturing, setCapturing] = useState(false)

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      setStreamActive(true)
    } catch {
      /* camera permission denied — surface as empty state text */
    }
  }

  function stopCamera() {
    const stream = videoRef.current?.srcObject as MediaStream | null
    stream?.getTracks().forEach((t) => t.stop())
    if (videoRef.current) videoRef.current.srcObject = null
    setStreamActive(false)
  }

  function capture() {
    const video = videoRef.current
    if (!video || !video.videoWidth) return
    setCapturing(true)
    const canvas = document.createElement("canvas")
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext("2d")?.drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) {
        onImage({
          kind: "image",
          dataUrl: canvas.toDataURL("image/jpeg", 0.9),
          blob,
          name: "webcam-capture.jpg",
        })
      }
      setCapturing(false)
    }, "image/jpeg", 0.9)
  }

  if (!streamActive) {
    return (
      <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card px-6 py-8 text-center">
        <Camera className="size-8 text-muted-foreground" />
        <p className="text-sm font-semibold">Capture a photo from your webcam</p>
        <p className="max-w-xs text-xs text-muted-foreground">
          Point your camera at a document, label or sign and take a snapshot.
        </p>
        <Button type="button" onClick={startCamera} disabled={disabled}>
          Enable camera
        </Button>
        <p className="text-xs text-muted-foreground" aria-live="polite">
          Camera access is requested only when you enable it.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="relative overflow-hidden rounded-2xl border border-border bg-black">
        <video ref={videoRef} playsInline muted className="aspect-[4/3] w-full object-cover" />
      </div>
      <div className="flex items-center justify-center gap-2">
        <Button type="button" variant="secondary" onClick={stopCamera}>
          <X data-icon="inline-start" /> Stop camera
        </Button>
        <Button type="button" onClick={capture} disabled={capturing}>
          {capturing ? (
            <LoaderCircle className="animate-spin" data-icon="inline-start" />
          ) : (
            <Camera data-icon="inline-start" />
          )}
          {capturing ? "Capturing…" : "Take photo"}
        </Button>
      </div>
    </div>
  )
}

const DEMOS = [
  { key: "Form_7_Hindi", label: "Hindi form · Form 7" },
  { key: "Form_8_English", label: "English form · Form 8" },
]

function DemoRow({
  onImage,
  disabled,
}: {
  onImage: (p: InputPayload) => void
  disabled?: boolean
}) {
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function loadDemo(key: string) {
    setError(null)
    setLoading(key)
    try {
      const res = await fetch(`/demo/${key}.pdf`)
      if (!res.ok) throw new Error("Couldn’t load the sample form")
      const blob = await res.blob()
      const file = new File([blob], `${key}.pdf`, { type: "application/pdf" })
      onImage({ kind: "pdf", blob: file, name: file.name })
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn’t load the sample form")
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="mt-4 rounded-xl border border-border bg-muted/30 px-4 py-3">
      <div className="flex flex-wrap items-center justify-center gap-2">
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="lens-motif size-1.5 rounded-full bg-vermilion" aria-hidden />
          No document handy? Try a sample
        </span>
        {DEMOS.map((d) => (
          <Button
            key={d.key}
            type="button"
            variant="outline"
            size="sm"
            onClick={() => loadDemo(d.key)}
            disabled={disabled || loading !== null}
            aria-busy={loading === d.key}
          >
            {loading === d.key && (
              <LoaderCircle className="animate-spin" data-icon="inline-start" />
            )}
            {d.label}
          </Button>
        ))}
      </div>
      {error && (
        <p className="mt-2 text-center text-xs text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

function TextInput({
  onText,
  disabled,
}: {
  onText: (text: string) => void
  disabled?: boolean
}) {
  const [value, setValue] = useState("")
  return (
    <div className="space-y-3">
      <Textarea
        placeholder="Type or paste the complex text you want LinguaLens to explain…"
        rows={6}
        value={value}
        disabled={disabled}
        onChange={(e) => setValue(e.target.value)}
        aria-label="Text to explain"
      />
      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="secondary"
          onClick={() => setValue("")}
          disabled={!value || disabled}
        >
          Clear
        </Button>
        <Button
          type="button"
          onClick={() => onText(value.trim())}
          disabled={!value.trim() || disabled}
        >
          <FileText data-icon="inline-start" />
          Explain this text
        </Button>
      </div>
    </div>
  )
}