import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"


class GitHubClient:
    def __init__(self) -> None:
        self._headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
        }
        self._rate_limit_remaining: int | None = None

    async def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(5):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(GRAPHQL_URL, headers=self._headers, json=payload)

            self._update_rate_limit(response.headers)

            if response.status_code in (403, 429):
                wait = 2**attempt * 5
                logger.warning(
                    "Rate limited (remaining=%s). Retrying in %ss...",
                    self._rate_limit_remaining,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise RuntimeError(f"GraphQL errors: {data['errors']}")

            return data["data"]

        raise RuntimeError("GitHub GraphQL request failed after retries")

    async def rest_get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{REST_URL}{path}"

        for attempt in range(5):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=self._headers, params=params)

            self._update_rate_limit(response.headers)

            if response.status_code in (403, 429):
                wait = 2**attempt * 5
                logger.warning(
                    "Rate limited on REST (remaining=%s). Retrying in %ss...",
                    self._rate_limit_remaining,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError(f"GitHub REST request failed after retries: {path}")

    async def rest_get_paginated(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[Any]:
        results: list[Any] = []
        page_params = dict(params or {})
        page_params.setdefault("per_page", 100)
        page = 1

        while True:
            page_params["page"] = page
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{REST_URL}{path}", headers=self._headers, params=page_params
                )

            self._update_rate_limit(response.headers)

            if response.status_code in (403, 429):
                logger.warning("Rate limited on paginated REST. Waiting 30s...")
                await asyncio.sleep(30)
                continue

            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            results.extend(batch)
            if len(batch) < page_params["per_page"]:
                break
            page += 1

        return results

    def _update_rate_limit(self, headers: httpx.Headers) -> None:
        remaining = headers.get("X-RateLimit-Remaining") or headers.get("x-ratelimit-remaining")
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)
            if self._rate_limit_remaining < 100:
                logger.warning("Low rate limit remaining: %s", self._rate_limit_remaining)


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
