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
    <div className="relative flex h-svh overflow-hidden bg-background">
      <div
        aria-hidden
        className="signal-rail absolute inset-y-0 left-0 w-px opacity-60"
      />

      <div className="mx-auto flex min-w-0 flex-1 flex-col gap-5 overflow-hidden px-6 py-5 pl-7">
        <header className="shrink-0">
          <p className="font-mono text-[10px] tracking-[0.16em] text-accent uppercase">
            PostHog · 120 days
          </p>
          <h1 className="font-heading mt-1 text-2xl leading-tight font-medium tracking-tight">
            Engineering Impact
          </h1>
          <p className="mt-1 max-w-lg text-xs leading-relaxed text-muted-foreground">
            Normalized contributor scores.
          </p>
        </header>

        <main className="min-h-0 flex-1 overflow-y-auto">
          {isLoading ? <MetricsLoading /> : null}

          {isError ? (
            <Alert variant="destructive" className="max-w-lg">
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
    </div>
  )
}

export default App
