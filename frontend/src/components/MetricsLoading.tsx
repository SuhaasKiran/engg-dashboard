import { Skeleton } from "@/components/ui/skeleton"

export function MetricsLoading() {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-3 w-full max-w-md" />
      </div>
      <Skeleton className="h-9 w-full max-w-sm" />
      <Skeleton className="h-36 w-full rounded-md" />
      <div className="grid gap-3 lg:grid-cols-2">
        <Skeleton className="h-40 w-full rounded-md" />
        <Skeleton className="h-40 w-full rounded-md" />
      </div>
    </div>
  )
}
