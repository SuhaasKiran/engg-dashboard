import logging
from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ingest.github_client import GitHubClient, parse_github_datetime
from app.models import Issue, IssueComment, PrFile, PrReview, PrReviewComment, PullRequest

logger = logging.getLogger(__name__)

PRS_QUERY = """
query($owner: String!, $repo: String!, $cursor: String, $states: [PullRequestState!], $baseRefName: String!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: $states, baseRefName: $baseRefName, first: 50, after: $cursor,
                 orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        body
        state
        createdAt
        mergedAt
        additions
        deletions
        author { login }
        files(first: 100) {
          nodes { path }
        }
        reviews(first: 50) {
          nodes {
            author { login }
            state
            submittedAt
          }
        }
      }
    }
  }
}
"""

ISSUES_QUERY = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        __typename
        number
        title
        body
        state
        createdAt
        closedAt
        author { login }
        labels(first: 20) { nodes { name } }
        assignees(first: 10) { nodes { login } }
      }
    }
  }
}
"""


class GitHubFetcher:
    def __init__(self, session: AsyncSession, client: GitHubClient | None = None) -> None:
        self._session = session
        self._client = client or GitHubClient()
        self._owner = settings.github_owner
        self._repo = settings.github_repo
        self._default_branch = settings.default_branch
        self._window_start = settings.measurement_start
        # Extra buffer for PR durability follow-up overlap checks
        self._fetch_start = self._window_start - timedelta(days=14)

    async def run_full_ingest(self) -> None:
        logger.info(
            "Starting GitHub ingest for %s/%s (branch=%s)",
            self._owner,
            self._repo,
            self._default_branch,
        )
        await self.fetch_pull_requests(states=["MERGED"])
        await self.fetch_pull_requests(states=["OPEN", "CLOSED"])
        await self.fetch_issues()
        await self.fetch_issue_comments()
        await self.fetch_pr_review_comments()
        await self._session.commit()
        logger.info("GitHub ingest complete")

    async def fetch_pull_requests(self, states: list[str]) -> None:
        cursor: str | None = None
        total = 0

        while True:
            data = await self._client.graphql(
                PRS_QUERY,
                {
                    "owner": self._owner,
                    "repo": self._repo,
                    "cursor": cursor,
                    "states": states,
                    "baseRefName": self._default_branch,
                },
            )
            pr_connection = data["repository"]["pullRequests"]
            nodes = pr_connection["nodes"]

            for node in nodes:
                created_at = parse_github_datetime(node["createdAt"])
                merged_at = parse_github_datetime(node.get("mergedAt"))
                if created_at is None:
                    continue

                # Skip PRs outside fetch window
                relevant_date = merged_at or created_at
                if relevant_date < self._fetch_start:
                    continue

                author = (node.get("author") or {}).get("login")
                if not author:
                    continue

                pr_number = node["number"]
                pr = PullRequest(
                    pr_number=pr_number,
                    title=node["title"],
                    author_login=author,
                    state=node["state"],
                    merged_at=merged_at,
                    created_at=created_at,
                    additions=node.get("additions") or 0,
                    deletions=node.get("deletions") or 0,
                    body=node.get("body"),
                )
                await self._session.merge(pr)

                await self._session.execute(delete(PrFile).where(PrFile.pr_number == pr_number))
                for file_node in (node.get("files") or {}).get("nodes") or []:
                    self._session.add(
                        PrFile(pr_number=pr_number, filename=file_node["path"])
                    )

                await self._session.execute(delete(PrReview).where(PrReview.pr_number == pr_number))
                for review_node in (node.get("reviews") or {}).get("nodes") or []:
                    reviewer = (review_node.get("author") or {}).get("login")
                    submitted_at = parse_github_datetime(review_node.get("submittedAt"))
                    if not reviewer or not submitted_at:
                        continue
                    self._session.add(
                        PrReview(
                            pr_number=pr_number,
                            reviewer_login=reviewer,
                            state=review_node["state"],
                            submitted_at=submitted_at,
                        )
                    )

                total += 1

            page_info = pr_connection["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]

            # Stop early if oldest PR in batch is before fetch window
            if nodes:
                oldest = nodes[-1]
                oldest_date = parse_github_datetime(oldest.get("mergedAt") or oldest["createdAt"])
                if oldest_date and oldest_date < self._fetch_start:
                    break

        logger.info("Fetched %d pull requests (states=%s)", total, states)

    async def fetch_issues(self) -> None:
        cursor: str | None = None
        total = 0

        while True:
            data = await self._client.graphql(
                ISSUES_QUERY,
                {"owner": self._owner, "repo": self._repo, "cursor": cursor},
            )
            issue_connection = data["repository"]["issues"]
            nodes = issue_connection["nodes"]

            for node in nodes:
                if node.get("__typename") == "PullRequest":
                    continue

                created_at = parse_github_datetime(node["createdAt"])
                if created_at is None or created_at < self._window_start:
                    continue

                author = (node.get("author") or {}).get("login")
                if not author:
                    continue

                labels = [label["name"] for label in (node.get("labels") or {}).get("nodes") or []]
                assignees = [
                    a["login"] for a in (node.get("assignees") or {}).get("nodes") or [] if a.get("login")
                ]

                issue = Issue(
                    issue_number=node["number"],
                    title=node.get("title") or "",
                    author_login=author,
                    state=node["state"],
                    created_at=created_at,
                    closed_at=parse_github_datetime(node.get("closedAt")),
                    labels=labels,
                    assignees=assignees,
                    body=node.get("body"),
                )
                await self._session.merge(issue)
                total += 1

            page_info = issue_connection["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]

            if nodes:
                oldest_created = parse_github_datetime(nodes[-1]["createdAt"])
                if oldest_created and oldest_created < self._window_start:
                    break

        logger.info("Fetched %d issues", total)

    async def fetch_issue_comments(self) -> None:
        since_iso = self._window_start.isoformat()
        comments = await self._client.rest_get_paginated(
            f"/repos/{self._owner}/{self._repo}/issues/comments",
            {"since": since_iso, "per_page": 100},
        )

        issue_authors = await self._load_issue_authors()
        total = 0

        for comment in comments:
            created_at = parse_github_datetime(comment.get("created_at"))
            user = (comment.get("user") or {}).get("login")
            if not created_at or not user or created_at < self._window_start:
                continue

            issue_number = comment.get("issue_url", "").split("/")[-1]
            if not issue_number.isdigit():
                continue
            issue_num = int(issue_number)

            existing = await self._session.scalar(
                select(IssueComment).where(IssueComment.github_id == comment["id"])
            )
            if existing:
                continue

            self._session.add(
                IssueComment(
                    github_id=comment["id"],
                    issue_number=issue_num,
                    commenter_login=user,
                    issue_author_login=issue_authors.get(issue_num, "unknown"),
                    created_at=created_at,
                )
            )
            total += 1

        logger.info("Fetched %d issue comments", total)

    async def fetch_pr_review_comments(self) -> None:
        since_iso = self._window_start.isoformat()
        comments = await self._client.rest_get_paginated(
            f"/repos/{self._owner}/{self._repo}/pulls/comments",
            {"since": since_iso, "per_page": 100},
        )

        pr_authors = await self._load_pr_authors()
        total = 0

        for comment in comments:
            created_at = parse_github_datetime(comment.get("created_at"))
            user = (comment.get("user") or {}).get("login")
            if not created_at or not user or created_at < self._window_start:
                continue

            pr_url = comment.get("pull_request_url", "")
            pr_number_str = pr_url.split("/")[-1]
            if not pr_number_str.isdigit():
                continue
            pr_number = int(pr_number_str)

            existing = await self._session.scalar(
                select(PrReviewComment).where(PrReviewComment.github_id == comment["id"])
            )
            if existing:
                continue

            self._session.add(
                PrReviewComment(
                    github_id=comment["id"],
                    pr_number=pr_number,
                    commenter_login=user,
                    pr_author_login=pr_authors.get(pr_number, "unknown"),
                    created_at=created_at,
                )
            )
            total += 1

        logger.info("Fetched %d PR review comments", total)

    async def _load_issue_authors(self) -> dict[int, str]:
        result = await self._session.execute(select(Issue.issue_number, Issue.author_login))
        return {row[0]: row[1] for row in result.all()}

    async def _load_pr_authors(self) -> dict[int, str]:
        result = await self._session.execute(select(PullRequest.pr_number, PullRequest.author_login))
        return {row[0]: row[1] for row in result.all()}
