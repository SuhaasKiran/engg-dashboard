import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.schemas import CategoryView, LeaderboardEntry, MetricsResponse, OverallView, SubMetricView
from app.metrics.definitions import CATEGORY_DEFINITIONS, METRIC_DEFINITIONS, METRICS_BY_KEY
from app.metrics.scorer import MetricsScorer, to_display_score

router = APIRouter()

METRICS_FILE = Path(__file__).parent.parent.parent / "data" / "metrics.json"


def _build_normalized_leaderboard(
    scorer: MetricsScorer, score_fn
) -> list[LeaderboardEntry]:
    """Leaderboard using normalized scores on 0-100 scale."""
    top = scorer.get_top_contributors(score_fn, limit=5)
    entries = [
        LeaderboardEntry(rank=i + 1, contributor=login, score=to_display_score(score))
        for i, (login, score) in enumerate(top)
    ]
    entries.append(
        LeaderboardEntry(
            rank=None,
            contributor="Average",
            score=scorer.get_average_display_score(score_fn),
            is_average=True,
        )
    )
    return entries


def _build_raw_leaderboard(scorer: MetricsScorer, metric_key: str) -> list[LeaderboardEntry]:
    """Leaderboard using actual raw metric values."""
    metric_def = METRICS_BY_KEY[metric_key]
    top = scorer.get_top_contributors_raw(
        metric_key, higher_is_better=metric_def.higher_is_better, limit=5
    )
    entries = [
        LeaderboardEntry(rank=i + 1, contributor=login, score=round(score, 4))
        for i, (login, score) in enumerate(top)
    ]
    entries.append(
        LeaderboardEntry(
            rank=None,
            contributor="Average",
            score=round(scorer.get_average_raw_metric(metric_key), 4),
            is_average=True,
        )
    )
    return entries


def _build_sub_metrics(scorer: MetricsScorer, category: str) -> list[SubMetricView]:
    sub_metrics: list[SubMetricView] = []
    for metric_def in METRIC_DEFINITIONS:
        if metric_def.category != category:
            continue
        sub_metrics.append(
            SubMetricView(
                key=metric_def.key,
                name=metric_def.name,
                definition=metric_def.definition,
                interpretation=metric_def.interpretation,
                leaderboard=_build_raw_leaderboard(scorer, metric_def.key),
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
        leaderboard=_build_normalized_leaderboard(scorer, category_score),
        sub_metrics=_build_sub_metrics(scorer, category),
    )


def _build_overall_category_breakdown(scorer: MetricsScorer, category: str) -> CategoryView:
    """Category summary for the Overall tab: normalized 0-100 only, no sub-metrics."""
    meta = CATEGORY_DEFINITIONS[category]

    def category_score(login: str) -> float:
        return scorer.get_category_score(category, login)

    return CategoryView(
        key=category,
        name=meta["name"],
        definition=meta["definition"],
        interpretation=meta["interpretation"],
        leaderboard=_build_normalized_leaderboard(scorer, category_score),
        sub_metrics=[],
    )


def build_metrics_response(scorer: MetricsScorer) -> MetricsResponse:
    quantity = _build_category_view(scorer, "quantity")
    quality = _build_category_view(scorer, "quality")
    collaboration = _build_category_view(scorer, "collaboration")

    overall_meta = CATEGORY_DEFINITIONS["overall"]
    overall = OverallView(
        name=overall_meta["name"],
        definition=overall_meta["definition"],
        interpretation=overall_meta["interpretation"],
        leaderboard=_build_normalized_leaderboard(scorer, scorer.get_overall_score),
        categories=[
            _build_overall_category_breakdown(scorer, "quantity"),
            _build_overall_category_breakdown(scorer, "quality"),
            _build_overall_category_breakdown(scorer, "collaboration"),
        ],
    )

    return MetricsResponse(
        overall=overall,
        quantity=quantity,
        quality=quality,
        collaboration=collaboration,
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
