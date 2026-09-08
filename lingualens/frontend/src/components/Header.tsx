import { ScanSearch } from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"

export function Header({ backendUp }: { backendUp: boolean }) {
  return (
    <header className="flex items-center justify-between border-b border-border/70 bg-background/80 px-4 py-2 backdrop-blur-sm md:px-6">
      <div className="flex items-center gap-2.5">
        <div className="lens-motif flex size-9 items-center justify-center rounded-full border border-vermilion/30 bg-card">
          <ScanSearch className="size-4.5 text-vermilion" />
        </div>
        <div className="leading-tight">
          <div className="text-base font-bold tracking-tight">LinguaLens</div>
          <div className="text-[0.7rem] text-muted-foreground">
            Every document, in your language.
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <span
          role="status"
          className="hidden items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground sm:inline-flex"
        >
          <span
            aria-hidden
            className={`size-1.5 rounded-full ${backendUp ? "bg-emerald-500" : "bg-vermilion"}`}
          />
          {backendUp ? "API online" : "API offline"}
        </span>
        <ThemeToggle />
      </div>
    </header>
  )
}