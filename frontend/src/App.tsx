import { useQuery } from "@tanstack/react-query"
import { AlertCircleIcon } from "lucide-react"

import { fetchMetrics } from "@/api"
import { Dashboard } from "@/components/Dashboard"
import { MetricsLoading } from "@/components/MetricsLoading"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

function App() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["metrics"],
    queryFn: fetchMetrics,
  })

  return (
    <div className="mx-auto flex h-svh max-w-6xl flex-col gap-3 overflow-hidden p-4">
      <header className="shrink-0">
        <h1 className="text-xl font-semibold tracking-tight">
          Engineering Impact Dashboard
        </h1>
        <p className="text-xs text-muted-foreground">
          PostHog contributor metrics · last 90 days · scores normalized (0.5 = average)
        </p>
      </header>

      <main className="min-h-0 flex-1 overflow-y-auto">
        {isLoading ? <MetricsLoading /> : null}

        {isError ? (
          <Alert variant="destructive">
            <AlertCircleIcon />
            <AlertTitle>Unable to load metrics</AlertTitle>
            <AlertDescription>
              {error instanceof Error
                ? error.message
                : "An unexpected error occurred. Check that the backend is running and data has been ingested."}
            </AlertDescription>
          </Alert>
        ) : null}

        {data ? <Dashboard data={data} /> : null}
      </main>
    </div>
  )
}

export default App
