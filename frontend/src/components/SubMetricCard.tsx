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
    <Card size="sm" className="min-w-0">
      <CardHeader>
        <CardTitle>{subMetric.name}</CardTitle>
        <CardDescription>{subMetric.definition}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <p className="text-xs text-muted-foreground">{subMetric.interpretation}</p>
        <Leaderboard entries={subMetric.leaderboard} compact />
      </CardContent>
    </Card>
  )
}
