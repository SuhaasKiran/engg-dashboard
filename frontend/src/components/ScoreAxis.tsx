import { formatScore, scoreTone } from "@/lib/score"
import { cn } from "@/lib/utils"

interface ScoreAxisProps {
  score: number
  isAverage?: boolean
  compact?: boolean
}

/** Signature element: score plotted on a 0–1 axis with 0.5 baseline. */
export function ScoreAxis({ score, isAverage = false, compact = false }: ScoreAxisProps) {
  const tone = scoreTone(score)
  const position = Math.min(Math.max(score * 100, 0), 100)

  return (
    <div
      className={cn(
        "flex items-center gap-2.5",
        compact ? "min-w-[5.5rem]" : "min-w-[6.5rem]"
      )}
    >
      <div
        className={cn(
          "relative shrink-0 overflow-visible",
          compact ? "h-3 w-14" : "h-3.5 w-16"
        )}
        aria-hidden
      >
        <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-border" />
        <div
          className="absolute top-0 bottom-0 w-px bg-accent/40"
          style={{ left: "50%" }}
        />
        <div
          className={cn(
            "absolute top-1/2 size-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-background",
            isAverage && "bg-muted-foreground/60",
            !isAverage && tone === "above" && "bg-primary shadow-[0_0_6px_var(--primary)]",
            !isAverage && tone === "below" && "bg-muted-foreground"
          )}
          style={{ left: `${position}%` }}
        />
      </div>
      <span
        className={cn(
          "font-mono tabular-nums tracking-tight",
          compact ? "text-[11px]" : "text-xs",
          isAverage ? "text-muted-foreground" : "text-foreground"
        )}
      >
        {formatScore(score)}
      </span>
    </div>
  )
}
