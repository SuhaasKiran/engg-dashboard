import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { CategoryView } from "@/types"
import { Leaderboard } from "./Leaderboard"
import { SubMetricCard } from "./SubMetricCard"

interface CategoryTabProps {
  category: CategoryView
}

export function CategoryTab({ category }: CategoryTabProps) {
  return (
    <div className="flex flex-col gap-3">
      <Card size="sm">
        <CardHeader>
          <CardTitle>{category.name}</CardTitle>
          <CardDescription>{category.definition}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">{category.interpretation}</p>
        </CardContent>
      </Card>

      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Leaderboard</h3>
        <Leaderboard entries={category.leaderboard} />
      </section>

      <Separator />

      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Breakdown</h3>
        <div className="grid gap-2 lg:grid-cols-2">
          {category.sub_metrics.map((subMetric) => (
            <SubMetricCard key={subMetric.key} subMetric={subMetric} />
          ))}
        </div>
      </section>
    </div>
  )
}
