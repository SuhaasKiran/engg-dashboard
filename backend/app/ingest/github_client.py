import asyncio
import logging
import re
from datetime import datetime
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"
# GitHub REST page-based pagination is limited to 100 pages per query window.
MAX_REST_PAGE = 100


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
        seen_ids: set[int | str] = set()
        page_params = dict(params or {})
        page_params.setdefault("per_page", 100)
        supports_since = "since" in page_params

        while True:
            page = 1
            count_at_window_start = len(results)
            needs_continuation = False

            while page <= MAX_REST_PAGE:
                page_params["page"] = page
                response = await self._rest_get_response(f"{REST_URL}{path}", page_params)

                if response.status_code in (403, 429):
                    logger.warning("Rate limited on paginated REST. Waiting 30s...")
                    await asyncio.sleep(30)
                    continue

                if response.status_code == 422:
                    logger.warning(
                        "GitHub pagination limit reached for %s at page %d", path, page
                    )
                    needs_continuation = True
                    break

                response.raise_for_status()
                batch = response.json()
                if not batch:
                    return results

                for item in batch:
                    item_id = item.get("id")
                    if item_id is not None and item_id in seen_ids:
                        continue
                    if item_id is not None:
                        seen_ids.add(item_id)
                    results.append(item)

                if len(batch) < page_params["per_page"]:
                    return results
                if not self._has_next_page(response):
                    return results

                page += 1
            else:
                # Exhausted MAX_REST_PAGE with a full last page and a next link
                needs_continuation = True

            if not needs_continuation:
                return results

            if not supports_since or len(results) == count_at_window_start:
                logger.warning(
                    "Stopped pagination for %s at GitHub page limit (%d pages)", path, MAX_REST_PAGE
                )
                break

            last_updated = self._item_timestamp(results[-1])
            if not last_updated:
                logger.warning("Cannot continue pagination for %s: no timestamp on last item", path)
                break

            page_params["since"] = last_updated
            logger.info(
                "Continuing pagination for %s (%d items so far, since=%s)",
                path,
                len(results),
                last_updated,
            )

        return results

    async def _rest_get_response(
        self, url: str, params: dict[str, Any]
    ) -> httpx.Response:
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

            return response

        raise RuntimeError(f"GitHub REST request failed after retries: {url}")

    @staticmethod
    def _has_next_page(response: httpx.Response) -> bool:
        link = response.headers.get("Link") or response.headers.get("link") or ""
        return bool(re.search(r'rel="next"', link))

    @staticmethod
    def _item_timestamp(item: dict[str, Any]) -> str | None:
        for key in ("updated_at", "created_at"):
            value = item.get(key)
            if value:
                return value
        return None

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
