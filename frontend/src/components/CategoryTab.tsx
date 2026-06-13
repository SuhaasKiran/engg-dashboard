import { Separator } from "@/components/ui/separator"
import type { CategoryView } from "@/types"
import { CategoryIntro } from "./CategoryIntro"
import { Leaderboard } from "./Leaderboard"
import { SectionLabel } from "./SectionLabel"
import { SubMetricCard } from "./SubMetricCard"

interface CategoryTabProps {
  category: CategoryView
}

export function CategoryTab({ category }: CategoryTabProps) {
  return (
    <div className="flex flex-col gap-5">
      <CategoryIntro
        name={category.name}
        definition={category.definition}
        interpretation={category.interpretation}
      />

      <section className="flex flex-col gap-2">
        <SectionLabel>Leaderboard</SectionLabel>
        <Leaderboard entries={category.leaderboard} />
      </section>

      <Separator className="bg-border/60" />

      <section className="flex flex-col gap-3">
        <SectionLabel>Breakdown</SectionLabel>
        <div className="grid gap-3 lg:grid-cols-2">
          {category.sub_metrics.map((subMetric) => (
            <SubMetricCard key={subMetric.key} subMetric={subMetric} />
          ))}
        </div>
      </section>
    </div>
  )
}
