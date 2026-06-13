from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int | None
    contributor: str
    score: float
    is_average: bool = False


class SubMetricView(BaseModel):
    key: str
    name: str
    definition: str
    interpretation: str
    leaderboard: list[LeaderboardEntry]


class CategoryView(BaseModel):
    key: str
    name: str
    definition: str
    interpretation: str
    score: float | None = None
    leaderboard: list[LeaderboardEntry]
    sub_metrics: list[SubMetricView]


class OverallView(BaseModel):
    name: str
    definition: str
    interpretation: str
    leaderboard: list[LeaderboardEntry]
    categories: list[CategoryView]


class MetricsResponse(BaseModel):
    overall: OverallView
    quantity: CategoryView
    quality: CategoryView
    collaboration: CategoryView
