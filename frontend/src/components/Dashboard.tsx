import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { MetricsResponse } from "@/types"
import { CategoryTab } from "./CategoryTab"
import { OverallTab } from "./OverallTab"

interface DashboardProps {
  data: MetricsResponse
}

export function Dashboard({ data }: DashboardProps) {
  return (
    <Tabs defaultValue="overall" className="flex flex-col gap-3">
      <TabsList>
        <TabsTrigger value="overall">Overall</TabsTrigger>
        <TabsTrigger value="quantity">Quantity</TabsTrigger>
        <TabsTrigger value="quality">Quality</TabsTrigger>
        <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
      </TabsList>

      <TabsContent value="overall">
        <OverallTab overall={data.overall} />
      </TabsContent>
      <TabsContent value="quantity">
        <CategoryTab category={data.quantity} />
      </TabsContent>
      <TabsContent value="quality">
        <CategoryTab category={data.quality} />
      </TabsContent>
      <TabsContent value="collaboration">
        <CategoryTab category={data.collaboration} />
      </TabsContent>
    </Tabs>
  )
}
