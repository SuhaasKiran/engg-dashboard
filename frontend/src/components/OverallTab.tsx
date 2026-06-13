import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { OverallView } from "@/types"
import { CategoryIntro } from "./CategoryIntro"
import { Leaderboard } from "./Leaderboard"
import { SectionLabel } from "./SectionLabel"

interface OverallTabProps {
  overall: OverallView
}

export function OverallTab({ overall }: OverallTabProps) {
  return (
    <div className="flex flex-col gap-5">
      <CategoryIntro
        name={overall.name}
        definition={overall.definition}
        interpretation={overall.interpretation}
      />

      <section className="flex flex-col gap-2">
        <SectionLabel>Leaderboard</SectionLabel>
        <Leaderboard entries={overall.leaderboard} />
      </section>

      <Separator className="bg-border/60" />

      <section className="flex flex-col gap-3">
        <SectionLabel>Categories</SectionLabel>
        <div className="grid gap-3 lg:grid-cols-3">
          {overall.categories.map((category) => {
            const averageEntry = category.leaderboard.find((entry) => entry.is_average)
            const topEntry = category.leaderboard.find((entry) => !entry.is_average)

            return (
              <Card key={category.key} size="sm" className="ring-foreground/8">
                <CardHeader className="gap-1">
                  <CardTitle className="font-heading text-base">{category.name}</CardTitle>
                  <CardDescription className="line-clamp-2 text-xs leading-relaxed">
                    {category.definition}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-2">
                  <p className="text-xs leading-relaxed text-muted-foreground/80">
                    {category.interpretation}
                  </p>
                  {topEntry ? (
                    <p className="font-mono text-xs">
                      <span className="text-muted-foreground">Top </span>
                      {topEntry.contributor}
                      <span className="text-muted-foreground"> · </span>
                      {topEntry.score.toFixed(2)}
                    </p>
                  ) : null}
                  {averageEntry ? (
                    <p className="font-mono text-xs text-muted-foreground">
                      Avg {averageEntry.score.toFixed(2)}
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
