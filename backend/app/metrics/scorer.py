from statistics import mean

from app.metrics.definitions import CATEGORY_DEFINITIONS, METRIC_DEFINITIONS, METRICS_BY_KEY

NEUTRAL_SCORE = 0.5
SCORE_SCALE = 100


def to_display_score(normalized: float) -> float:
    """Convert normalized 0-1 score to 0-100 display scale."""
    return round(normalized * SCORE_SCALE, 2)


def normalize_metric(
    values: dict[str, float | None],
    higher_is_better: bool,
) -> dict[str, float]:
    """Normalize so mean score is 0.5 across contributors with measured values.

    Contributors with None values receive a neutral score of 0.5 and are excluded
    from the mean used to normalize others.
    """
    if not values:
        return {}

    measured = {login: val for login, val in values.items() if val is not None}
    missing = [login for login, val in values.items() if val is None]

    if not measured:
        return {login: NEUTRAL_SCORE for login in values}

    if higher_is_better:
        transformed = measured
    else:
        transformed = {login: 1.0 / (1.0 + val) for login, val in measured.items()}

    avg = mean(transformed.values())
    if avg == 0:
        normalized = {login: NEUTRAL_SCORE for login in measured}
    else:
        normalized = {
            login: min(1.0, max(0.0, val / (2 * avg))) for login, val in transformed.items()
        }

    for login in missing:
        normalized[login] = NEUTRAL_SCORE

    return normalized


class MetricsScorer:
    def __init__(self, raw_metrics: dict[str, dict[str, float | None]]) -> None:
        self._raw = raw_metrics
        self._contributors = sorted(raw_metrics.keys())
        self._normalized_by_metric: dict[str, dict[str, float]] = {}
        self._build_normalized()

    def _build_normalized(self) -> None:
        for metric_def in METRIC_DEFINITIONS:
            values = {
                login: metrics.get(metric_def.key)
                for login, metrics in self._raw.items()
            }
            self._normalized_by_metric[metric_def.key] = normalize_metric(
                values, metric_def.higher_is_better
            )

    def get_normalized_metric(self, metric_key: str, login: str) -> float:
        return self._normalized_by_metric.get(metric_key, {}).get(login, NEUTRAL_SCORE)

    def get_raw_metric(self, metric_key: str, login: str) -> float | None:
        value = self._raw.get(login, {}).get(metric_key)
        if value is None:
            return None
        return float(value)

    def get_average_raw_metric(self, metric_key: str) -> float:
        values = [
            v
            for login in self._contributors
            if (v := self.get_raw_metric(metric_key, login)) is not None
        ]
        if not values:
            return 0.0
        return mean(values)

    def get_top_contributors_raw(
        self, metric_key: str, higher_is_better: bool, limit: int = 5
    ) -> list[tuple[str, float]]:
        ranked = [
            (login, self.get_raw_metric(metric_key, login))
            for login in self._contributors
            if self.get_raw_metric(metric_key, login) is not None
        ]
        ranked.sort(key=lambda item: item[1], reverse=higher_is_better)
        return [(login, val) for login, val in ranked[:limit] if val is not None]

    def get_category_score(self, category: str, login: str) -> float:
        keys = [m.key for m in METRIC_DEFINITIONS if m.category == category]
        if not keys:
            return 0.0
        scores = [self.get_normalized_metric(key, login) for key in keys]
        return mean(scores)

    def get_overall_score(self, login: str) -> float:
        categories = ["quantity", "quality", "collaboration"]
        scores = [self.get_category_score(cat, login) for cat in categories]
        return mean(scores) if scores else 0.0

    def get_average_score(self, score_fn) -> float:
        if not self._contributors:
            return NEUTRAL_SCORE
        return mean(score_fn(login) for login in self._contributors)

    def get_average_display_score(self, score_fn) -> float:
        return to_display_score(self.get_average_score(score_fn))

    def get_top_contributors(
        self, score_fn, limit: int = 5
    ) -> list[tuple[str, float]]:
        ranked = sorted(
            ((login, score_fn(login)) for login in self._contributors),
            key=lambda item: item[1],
            reverse=True,
        )
        return ranked[:limit]

    @property
    def contributors(self) -> list[str]:
        return self._contributors

    @property
    def normalized_by_metric(self) -> dict[str, dict[str, float]]:
        return self._normalized_by_metric

    @property
    def raw_metrics(self) -> dict[str, dict[str, float | None]]:
        return self._raw

    @staticmethod
    def category_meta(category: str) -> dict[str, str]:
        return CATEGORY_DEFINITIONS[category]

    @staticmethod
    def metric_meta(metric_key: str):
        return METRICS_BY_KEY[metric_key]
