import type { LeaderboardEntry } from "@/types"
import { cn } from "@/lib/utils"
import { ScoreAxis } from "./ScoreAxis"

interface LeaderboardProps {
  entries: LeaderboardEntry[]
  compact?: boolean
}

export function Leaderboard({ entries, compact = false }: LeaderboardProps) {
  const rankedEntries = entries.filter((entry) => !entry.is_average)
  const averageEntry = entries.find((entry) => entry.is_average)

  return (
    <div className="overflow-hidden rounded-md ring-1 ring-border/70">
      <div
        className={cn(
          "grid grid-cols-[2rem_1fr_auto] items-center border-b border-border/70 bg-muted/30 px-3",
          compact ? "py-1.5" : "py-2"
        )}
      >
        <span className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
          #
        </span>
        <span className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
          Contributor
        </span>
        <span className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
          Score
        </span>
      </div>
      <div>
        {rankedEntries.map((entry) => (
          <div
            key={`${entry.contributor}-${entry.rank}`}
            className={cn(
              "grid grid-cols-[2rem_1fr_auto] items-center border-b border-border/40 px-3 last:border-b-0",
              compact ? "py-1.5" : "py-2"
            )}
          >
            <span className="font-mono text-xs tabular-nums text-muted-foreground">
              {entry.rank}
            </span>
            <span className="truncate text-sm">{entry.contributor}</span>
            <ScoreAxis score={entry.score} compact={compact} />
          </div>
        ))}
        {averageEntry ? (
          <div
            className={cn(
              "grid grid-cols-[2rem_1fr_auto] items-center bg-muted/20 px-3",
              compact ? "py-1.5" : "py-2"
            )}
          >
            <span className="font-mono text-xs text-muted-foreground/60">—</span>
            <span className="truncate text-sm text-muted-foreground">
              {averageEntry.contributor}
            </span>
            <ScoreAxis score={averageEntry.score} isAverage compact={compact} />
          </div>
        ) : null}
      </div>
    </div>
  )
}
