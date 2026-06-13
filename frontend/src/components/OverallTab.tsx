import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { OverallView } from "@/types"
import { Leaderboard } from "./Leaderboard"

interface OverallTabProps {
  overall: OverallView
}

export function OverallTab({ overall }: OverallTabProps) {
  return (
    <div className="flex flex-col gap-3">
      <Card size="sm">
        <CardHeader>
          <CardTitle>{overall.name}</CardTitle>
          <CardDescription>{overall.definition}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">{overall.interpretation}</p>
        </CardContent>
      </Card>

      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Leaderboard</h3>
        <Leaderboard entries={overall.leaderboard} />
      </section>

      <Separator />

      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Category Summary</h3>
        <div className="grid gap-2 lg:grid-cols-3">
          {overall.categories.map((category) => {
            const averageEntry = category.leaderboard.find((entry) => entry.is_average)
            const topEntry = category.leaderboard.find((entry) => !entry.is_average)

            return (
              <Card key={category.key} size="sm">
                <CardHeader>
                  <CardTitle>{category.name}</CardTitle>
                  <CardDescription>{category.definition}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-2 text-xs">
                  <p className="text-muted-foreground">{category.interpretation}</p>
                  {topEntry ? (
                    <p>
                      Top: <span className="font-medium">{topEntry.contributor}</span> (
                      {topEntry.score.toFixed(2)})
                    </p>
                  ) : null}
                  {averageEntry ? (
                    <p className="text-muted-foreground">
                      Average: {averageEntry.score.toFixed(2)}
                    </p>
                  ) : null}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>
    </div>
  )
}
