import { Badge } from "@/components/ui/badge"
import type { LeaderboardEntry } from "@/types"
import { formatScore, scorePercent, scoreTone } from "@/lib/score"
import { cn } from "@/lib/utils"

interface LeaderboardProps {
  entries: LeaderboardEntry[]
  compact?: boolean
}

function ScoreCell({ score, isAverage }: { score: number; isAverage: boolean }) {
  const tone = scoreTone(score)
  const percent = scorePercent(score)

  return (
    <div className="flex items-center justify-end gap-2">
      <div className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-muted sm:block">
        <div
          className={cn(
            "h-full rounded-full",
            isAverage && "bg-muted-foreground/50",
            !isAverage && tone === "above" && "bg-primary",
            !isAverage && tone === "below" && "bg-muted-foreground/70"
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
      <Badge
        variant={isAverage ? "outline" : tone === "above" ? "default" : "secondary"}
        className="min-w-12 justify-center tabular-nums"
      >
        {formatScore(score)}
      </Badge>
    </div>
  )
}

export function Leaderboard({ entries, compact = false }: LeaderboardProps) {
  const rankedEntries = entries.filter((entry) => !entry.is_average)
  const averageEntry = entries.find((entry) => entry.is_average)

  return (
    <div className="overflow-hidden rounded-lg border">
      <div
        className={cn(
          "grid grid-cols-[2.5rem_1fr_7rem] items-center border-b bg-muted/40 px-3 font-medium text-muted-foreground",
          compact ? "py-1 text-xs" : "py-1.5 text-xs"
        )}
      >
        <span>#</span>
        <span>Contributor</span>
        <span className="text-right">Score</span>
      </div>
      <div className="divide-y">
        {rankedEntries.map((entry) => (
          <div
            key={`${entry.contributor}-${entry.rank}`}
            className={cn(
              "grid grid-cols-[2.5rem_1fr_7rem] items-center px-3",
              compact ? "py-1 text-xs" : "py-1.5 text-sm"
            )}
          >
            <span className="tabular-nums text-muted-foreground">{entry.rank}</span>
            <span className="truncate font-medium">{entry.contributor}</span>
            <ScoreCell score={entry.score} isAverage={false} />
          </div>
        ))}
        {averageEntry ? (
          <div
            className={cn(
              "grid grid-cols-[2.5rem_1fr_7rem] items-center bg-muted/20 px-3 text-muted-foreground",
              compact ? "py-1 text-xs" : "py-1.5 text-sm"
            )}
          >
            <span>—</span>
            <span className="truncate font-medium">{averageEntry.contributor}</span>
            <ScoreCell score={averageEntry.score} isAverage />
          </div>
        ) : null}
      </div>
    </div>
  )
}
