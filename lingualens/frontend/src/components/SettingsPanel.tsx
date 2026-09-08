import { Languages, SlidersHorizontal } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import type { Difficulty, SourcePreset, TargetLanguage } from "@/lib/types"

interface SettingsPanelProps {
  sourcePreset: SourcePreset
  targetLanguage: TargetLanguage
  difficulty: Difficulty
  onChange: (patch: {
    sourcePreset?: SourcePreset
    targetLanguage?: TargetLanguage
    difficulty?: Difficulty
  }) => void
  disabled?: boolean
}

export function SettingsPanel({
  sourcePreset,
  targetLanguage,
  difficulty,
  onChange,
  disabled,
}: SettingsPanelProps) {
  return (
    <section
      aria-label="Explanation settings"
      className="rounded-2xl border border-border bg-card p-4 shadow-xs md:p-5"
    >
      <div className="mb-4 flex items-center gap-2">
        <SlidersHorizontal className="size-4 text-vermilion" aria-hidden />
        <h2 className="text-sm font-semibold tracking-tight">
          How should we explain it?
        </h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="space-y-1.5">
          <Label htmlFor="source-preset">Text in your image</Label>
          <Select
            value={sourcePreset}
            onValueChange={(v) => onChange({ sourcePreset: v as SourcePreset })}
            disabled={disabled}
          >
            <SelectTrigger id="source-preset" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="English & Hindi">English &amp; Hindi</SelectItem>
              <SelectItem value="English & Tamil">English &amp; Tamil</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="target-language">Output language</Label>
          <Select
            value={targetLanguage}
            onValueChange={(v) => onChange({ targetLanguage: v as TargetLanguage })}
            disabled={disabled}
          >
            <SelectTrigger id="target-language" className="w-full">
              <Languages data-icon="inline-start" className="text-muted-foreground" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="English">English</SelectItem>
              <SelectItem value="Hindi">हिंदी (Hindi)</SelectItem>
              <SelectItem value="Tamil">தமிழ் (Tamil)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="difficulty">Explain for</Label>
          <Select
            value={difficulty}
            onValueChange={(v) => onChange({ difficulty: v as Difficulty })}
            disabled={disabled}
          >
            <SelectTrigger id="difficulty" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Child">Child (12 years old)</SelectItem>
              <SelectItem value="Student">Student</SelectItem>
              <SelectItem value="Professional">Professional</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </section>
  )
}