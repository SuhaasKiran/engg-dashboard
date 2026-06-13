import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { SubMetricView } from "@/types"
import { Leaderboard } from "./Leaderboard"

interface SubMetricCardProps {
  subMetric: SubMetricView
}

export function SubMetricCard({ subMetric }: SubMetricCardProps) {
  return (
    <Card size="sm" className="min-w-0 ring-foreground/8">
      <CardHeader className="gap-1">
        <CardTitle className="font-heading text-sm leading-snug">{subMetric.name}</CardTitle>
        <CardDescription className="text-xs leading-relaxed">
          {subMetric.definition}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2.5">
        <p className="text-xs leading-relaxed text-muted-foreground/80">
          {subMetric.interpretation}
        </p>
        <Leaderboard entries={subMetric.leaderboard} compact />
      </CardContent>
    </Card>
  )
}
