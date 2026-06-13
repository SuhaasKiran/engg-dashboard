import asyncio
import logging
import sys

from app.database import async_session_factory, engine
from app.ingest.fetcher import GitHubFetcher
from app.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def run_ingest() -> None:
    await init_db()
    async with async_session_factory() as session:
        fetcher = GitHubFetcher(session)
        await fetcher.run_full_ingest()
    await engine.dispose()


def main() -> None:
    try:
        asyncio.run(run_ingest())
    except Exception:
        logger.exception("Ingest failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
