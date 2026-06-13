import type { ApiError, MetricsResponse } from "./types"

const API_BASE = import.meta.env.VITE_API_URL ?? ""

export async function fetchMetrics(): Promise<MetricsResponse> {
  const response = await fetch(`${API_BASE}/api/metrics`)

  if (!response.ok) {
    let message = `Failed to load metrics (${response.status})`

    try {
      const errorBody = (await response.json()) as ApiError
      if (errorBody.detail) {
        message = errorBody.detail
      }
    } catch {
      // Keep default message when response body is not JSON.
    }

    throw new Error(message)
  }

  return response.json() as Promise<MetricsResponse>
}
