from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CategoryView, LeaderboardEntry, MetricsResponse, OverallView, SubMetricView
from app.database import get_session
from app.metrics.calculator import MetricsCalculator
from app.metrics.definitions import CATEGORY_DEFINITIONS, METRIC_DEFINITIONS
from app.metrics.scorer import MetricsScorer

router = APIRouter()


def _build_leaderboard(
    scorer: MetricsScorer, score_fn, raw_fn=None
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
async def get_metrics(session: AsyncSession = Depends(get_session)) -> MetricsResponse:
    calculator = MetricsCalculator(session)
    raw_metrics = await calculator.compute_raw_metrics()

    if not raw_metrics:
        raise HTTPException(
            status_code=503,
            detail="No ingested data found. Run `python -m app.ingest.cli` first.",
        )

    scorer = MetricsScorer(raw_metrics)

    quantity = _build_category_view(scorer, "quantity")
    quality = _build_category_view(scorer, "quality")
    collaboration = _build_category_view(scorer, "collaboration")

    overall_meta = CATEGORY_DEFINITIONS["overall"]
    overall = OverallView(
        name=overall_meta["name"],
        definition=overall_meta["definition"],
        interpretation=overall_meta["interpretation"],
        leaderboard=_build_leaderboard(scorer, scorer.get_overall_score),
        categories=[quantity, quality, collaboration],
    )

    return MetricsResponse(
        overall=overall,
        quantity=quantity,
        quality=quality,
        collaboration=collaboration,
    )
