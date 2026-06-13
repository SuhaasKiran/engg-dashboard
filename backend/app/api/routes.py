import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.schemas import CategoryView, LeaderboardEntry, MetricsResponse, OverallView, SubMetricView
from app.metrics.definitions import CATEGORY_DEFINITIONS, METRIC_DEFINITIONS
from app.metrics.scorer import MetricsScorer

router = APIRouter()

METRICS_FILE = Path(__file__).parent.parent.parent / "data" / "metrics.json"


def _build_leaderboard(
    scorer: MetricsScorer, score_fn
) -> list[LeaderboardEntry]:
    top = scorer.get_top_contributors(score_fn, limit=5)
    entries = [
        LeaderboardEntry(rank=i + 1, contributor=login, score=round(score, 4))
        for i, (login, score) in enumerate(top)
    ]
    avg_score = scorer.get_average_score(score_fn)
    entries.append(
        LeaderboardEntry(
            rank=None,
            contributor="Average",
            score=round(avg_score, 4),
            is_average=True,
        )
    )
    return entries


def _build_sub_metrics(scorer: MetricsScorer, category: str) -> list[SubMetricView]:
    sub_metrics: list[SubMetricView] = []
    for metric_def in METRIC_DEFINITIONS:
        if metric_def.category != category:
            continue

        def metric_score(login: str, key: str = metric_def.key) -> float:
            return scorer.get_normalized_metric(key, login)

        sub_metrics.append(
            SubMetricView(
                key=metric_def.key,
                name=metric_def.name,
                definition=metric_def.definition,
                interpretation=metric_def.interpretation,
                leaderboard=_build_leaderboard(scorer, metric_score),
            )
        )
    return sub_metrics


def _build_category_view(scorer: MetricsScorer, category: str) -> CategoryView:
    meta = CATEGORY_DEFINITIONS[category]

    def category_score(login: str) -> float:
        return scorer.get_category_score(category, login)

    return CategoryView(
        key=category,
        name=meta["name"],
        definition=meta["definition"],
        interpretation=meta["interpretation"],
        leaderboard=_build_leaderboard(scorer, category_score),
        sub_metrics=_build_sub_metrics(scorer, category),
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> JSONResponse:
    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Metrics file not found. "
                "Run `python -m app.ingest.cli` then `python -m app.metrics.cli` first."
            ),
        )
    return JSONResponse(content=json.loads(METRICS_FILE.read_text(encoding="utf-8")))
