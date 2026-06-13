"""Compute metrics from the ingested database and write results to data/metrics.json.

Run after ingest:
    python -m app.metrics.cli
"""

import asyncio
import logging
import sys
from pathlib import Path

from app.api.routes import build_metrics_response
from app.database import async_session_factory, engine
from app.metrics.calculator import MetricsCalculator
from app.metrics.scorer import MetricsScorer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "metrics.json"


async def compute_and_save() -> None:
    async with async_session_factory() as session:
        calculator = MetricsCalculator(session)
        logger.info("Computing raw metrics from database...")
        raw_metrics = await calculator.compute_raw_metrics()

    await engine.dispose()

    if not raw_metrics:
        logger.error("No ingested data found. Run `python -m app.ingest.cli` first.")
        sys.exit(1)

    logger.info("Scoring %d contributors...", len(raw_metrics))
    scorer = MetricsScorer(raw_metrics)
    response = build_metrics_response(scorer)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(response.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Metrics written to %s", OUTPUT_PATH)


def main() -> None:
    try:
        asyncio.run(compute_and_save())
    except Exception:
        logger.exception("Compute failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
