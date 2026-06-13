export interface LeaderboardEntry {
  rank: number | null
  contributor: string
  score: number
  is_average: boolean
}

export interface SubMetricView {
  key: string
  name: string
  definition: string
  interpretation: string
  leaderboard: LeaderboardEntry[]
}

export interface CategoryView {
  key: string
  name: string
  definition: string
  interpretation: string
  score: number | null
  leaderboard: LeaderboardEntry[]
  sub_metrics: SubMetricView[]
}

export interface OverallView {
  name: string
  definition: string
  interpretation: string
  leaderboard: LeaderboardEntry[]
  categories: CategoryView[]
}

export interface MetricsResponse {
  overall: OverallView
  quantity: CategoryView
  quality: CategoryView
  collaboration: CategoryView
}

export interface ApiError {
  detail: string
}
