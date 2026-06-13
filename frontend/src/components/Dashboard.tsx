import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { MetricsResponse } from "@/types"
import { CategoryTab } from "./CategoryTab"
import { OverallTab } from "./OverallTab"

interface DashboardProps {
  data: MetricsResponse
}

export function Dashboard({ data }: DashboardProps) {
  return (
    <Tabs defaultValue="overall" className="flex flex-col gap-4">
      <TabsList variant="line" className="w-full justify-start">
        <TabsTrigger value="overall">Overall</TabsTrigger>
        <TabsTrigger value="quantity">Quantity</TabsTrigger>
        <TabsTrigger value="quality">Quality</TabsTrigger>
        <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
      </TabsList>

      <TabsContent value="overall" className="mt-0">
        <OverallTab overall={data.overall} />
      </TabsContent>
      <TabsContent value="quantity" className="mt-0">
        <CategoryTab category={data.quantity} />
      </TabsContent>
      <TabsContent value="quality" className="mt-0">
        <CategoryTab category={data.quality} />
      </TabsContent>
      <TabsContent value="collaboration" className="mt-0">
        <CategoryTab category={data.collaboration} />
      </TabsContent>
    </Tabs>
  )
}
