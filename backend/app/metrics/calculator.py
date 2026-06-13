import re
import statistics
from collections import defaultdict
from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Issue, IssueComment, PrFile, PrReview, PrReviewComment, PullRequest

REVERT_PATTERN = re.compile(r"Revert.*\(#(\d+)\)", re.IGNORECASE)
PR_REF_PATTERN = re.compile(r"#(\d+)")
CLOSES_PATTERN = re.compile(r"(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)", re.IGNORECASE)

DURABILITY_DAYS = 14

# Contributors without review responsiveness samples are excluded from normalization.
MISSING_METRIC: float | None = None


class MetricsCalculator:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._window_start = settings.measurement_start

    async def compute_raw_metrics(self) -> dict[str, dict[str, float | None]]:
        prs = await self._load_prs()
        issues = await self._load_issues()
        pr_files = await self._load_pr_files()
        pr_reviews = await self._load_pr_reviews()
        pr_comments = await self._load_pr_review_comments()
        issue_comments = await self._load_issue_comments()

        contributors = self._collect_contributors(prs, issues, pr_reviews, pr_comments, issue_comments)
        reverted_prs = self._find_reverted_prs(prs)

        raw: dict[str, dict[str, float | None]] = {login: {} for login in contributors}

        for login in contributors:
            raw[login]["merged_pr_lines_changed"] = self._merged_pr_lines_changed(login, prs)
            raw[login]["issues_opened"] = self._issues_opened(login, issues)
            raw[login]["prs_created"] = self._prs_created(login, prs)
            raw[login]["reverted_merged_pr_rate"] = self._reverted_merged_pr_rate(
                login, prs, reverted_prs
            )
            raw[login]["pr_durability_rate"] = self._pr_durability_rate(login, prs, pr_files)
            raw[login]["post_merge_bug_issue_rate"] = self._post_merge_bug_issue_rate(
                login, prs, issues
            )
            raw[login]["pr_acceptance_rate"] = self._pr_acceptance_rate(login, prs, pr_reviews)
            raw[login]["code_reviews"] = self._code_reviews(login, prs, pr_reviews)
            raw[login]["issues_closed"] = self._issues_closed(login, prs, issues)
            raw[login]["peer_comment_volume"] = self._peer_comment_volume(
                login, pr_comments, issue_comments
            )
            raw[login]["review_responsiveness"] = self._review_responsiveness(
                login, prs, pr_reviews, pr_comments
            )

        return raw

    async def _load_prs(self) -> list[PullRequest]:
        result = await self._session.execute(select(PullRequest))
        return list(result.scalars().all())

    async def _load_issues(self) -> list[Issue]:
        result = await self._session.execute(select(Issue))
        return list(result.scalars().all())

    async def _load_pr_files(self) -> dict[int, set[str]]:
        result = await self._session.execute(select(PrFile))
        files: dict[int, set[str]] = defaultdict(set)
        for row in result.scalars().all():
            files[row.pr_number].add(row.filename)
        return files

    async def _load_pr_reviews(self) -> list[PrReview]:
        result = await self._session.execute(select(PrReview))
        return list(result.scalars().all())

    async def _load_pr_review_comments(self) -> list[PrReviewComment]:
        result = await self._session.execute(select(PrReviewComment))
        return list(result.scalars().all())

    async def _load_issue_comments(self) -> list[IssueComment]:
        result = await self._session.execute(select(IssueComment))
        return list(result.scalars().all())

    def _in_window(self, dt: Any) -> bool:
        return dt is not None and dt >= self._window_start

    def _merged_prs_in_window(self, login: str, prs: list[PullRequest]) -> list[PullRequest]:
        return [
            pr
            for pr in prs
            if pr.author_login == login
            and pr.merged_at is not None
            and self._in_window(pr.merged_at)
        ]

    def _collect_contributors(
        self,
        prs: list[PullRequest],
        issues: list[Issue],
        reviews: list[PrReview],
        pr_comments: list[PrReviewComment],
        issue_comments: list[IssueComment],
    ) -> set[str]:
        logins: set[str] = set()
        for pr in prs:
            if self._in_window(pr.created_at) or (pr.merged_at and self._in_window(pr.merged_at)):
                logins.add(pr.author_login)
        for issue in issues:
            if self._in_window(issue.created_at):
                logins.add(issue.author_login)
        for review in reviews:
            if self._in_window(review.submitted_at):
                logins.add(review.reviewer_login)
        for comment in pr_comments:
            if self._in_window(comment.created_at):
                logins.add(comment.commenter_login)
        for comment in issue_comments:
            if self._in_window(comment.created_at):
                logins.add(comment.commenter_login)
        logins.discard("unknown")
        return logins

    def _find_reverted_prs(self, prs: list[PullRequest]) -> set[int]:
        reverted: set[int] = set()
        for pr in prs:
            if pr.merged_at is None:
                continue
            match = REVERT_PATTERN.search(pr.title)
            if match:
                reverted.add(int(match.group(1)))
        return reverted

    def _merged_pr_lines_changed(self, login: str, prs: list[PullRequest]) -> float:
        return float(
            sum(pr.additions + pr.deletions for pr in self._merged_prs_in_window(login, prs))
        )

    def _issues_opened(self, login: str, issues: list[Issue]) -> float:
        return float(
            sum(1 for issue in issues if issue.author_login == login and self._in_window(issue.created_at))
        )

    def _prs_created(self, login: str, prs: list[PullRequest]) -> float:
        return float(
            sum(1 for pr in prs if pr.author_login == login and self._in_window(pr.created_at))
        )

    def _reverted_merged_pr_rate(
        self, login: str, prs: list[PullRequest], reverted_prs: set[int]
    ) -> float:
        merged = self._merged_prs_in_window(login, prs)
        if not merged:
            return 0.0
        reverted_count = sum(1 for pr in merged if pr.pr_number in reverted_prs)
        return reverted_count / len(merged)

    def _pr_durability_rate(
        self, login: str, prs: list[PullRequest], pr_files: dict[int, set[str]]
    ) -> float:
        merged = self._merged_prs_in_window(login, prs)
        if not merged:
            return 0.0

        all_merged = [pr for pr in prs if pr.merged_at is not None]
        durable = 0
        for pr in merged:
            files = pr_files.get(pr.pr_number, set())
            if not files:
                durable += 1
                continue
            follow_up_end = pr.merged_at + timedelta(days=DURABILITY_DAYS)
            has_overlap = False
            for other in all_merged:
                if other.pr_number == pr.pr_number or other.merged_at is None:
                    continue
                if other.merged_at <= pr.merged_at or other.merged_at > follow_up_end:
                    continue
                if files & pr_files.get(other.pr_number, set()):
                    has_overlap = True
                    break
            if not has_overlap:
                durable += 1
        return durable / len(merged)

    def _post_merge_bug_issue_rate(
        self, login: str, prs: list[PullRequest], issues: list[Issue]
    ) -> float:
        merged = self._merged_prs_in_window(login, prs)
        if not merged:
            return 0.0

        merged_numbers = {pr.pr_number for pr in merged}
        merged_by_number = {pr.pr_number: pr for pr in merged}
        bug_count = 0

        for issue in issues:
            if not self._is_bug_issue(issue):
                continue
            referenced_prs = self._extract_pr_refs(issue.body or "")
            for pr_num in referenced_prs:
                if pr_num not in merged_numbers:
                    continue
                pr = merged_by_number[pr_num]
                if issue.created_at > pr.merged_at:
                    bug_count += 1

        return bug_count / len(merged)

    def _pr_acceptance_rate(
        self, login: str, prs: list[PullRequest], reviews: list[PrReview]
    ) -> float:
        merged = self._merged_prs_in_window(login, prs)
        if not merged:
            return 0.0

        accepted = 0
        for pr in merged:
            pr_reviews = [r for r in reviews if r.pr_number == pr.pr_number]
            has_changes_requested = any(
                r.state == "CHANGES_REQUESTED"
                and r.submitted_at <= pr.merged_at
                for r in pr_reviews
            )
            if not has_changes_requested:
                accepted += 1
        return accepted / len(merged)

    def _code_reviews(
        self, login: str, prs: list[PullRequest], reviews: list[PrReview]
    ) -> float:
        pr_authors = {pr.pr_number: pr.author_login for pr in prs}
        count = 0
        for review in reviews:
            if not self._in_window(review.submitted_at):
                continue
            author = pr_authors.get(review.pr_number)
            if author and review.reviewer_login == login and author != login:
                count += 1
        return float(count)

    def _issues_closed(
        self, login: str, prs: list[PullRequest], issues: list[Issue]
    ) -> float:
        closed_issue_numbers: set[int] = set()

        for issue in issues:
            if issue.closed_at is None or not self._in_window(issue.closed_at):
                continue

            # Closed via a merged PR authored by the contributor (Closes/Fixes in PR body)
            for pr in prs:
                if pr.author_login != login or pr.merged_at is None:
                    continue
                if issue.issue_number in self._extract_closing_issue_refs(pr.body or ""):
                    closed_issue_numbers.add(issue.issue_number)
                    break

            # Directly assigned and closed while assigned to contributor
            if issue.issue_number not in closed_issue_numbers and login in issue.assignees:
                closed_issue_numbers.add(issue.issue_number)

        return float(len(closed_issue_numbers))

    def _peer_comment_volume(
        self,
        login: str,
        pr_comments: list[PrReviewComment],
        issue_comments: list[IssueComment],
    ) -> float:
        pr_count = sum(
            1
            for c in pr_comments
            if c.commenter_login == login
            and c.pr_author_login != login
            and self._in_window(c.created_at)
        )
        issue_count = sum(
            1
            for c in issue_comments
            if c.commenter_login == login
            and c.issue_author_login != login
            and self._in_window(c.created_at)
        )
        return float(pr_count + issue_count)

    def _review_responsiveness(
        self,
        login: str,
        prs: list[PullRequest],
        reviews: list[PrReview],
        pr_comments: list[PrReviewComment],
    ) -> float | None:
        authored_prs = [
            pr for pr in prs if pr.author_login == login and self._in_window(pr.created_at)
        ]
        response_hours: list[float] = []

        for pr in authored_prs:
            feedback_times: list[Any] = []
            for review in reviews:
                if review.pr_number != pr.pr_number or review.reviewer_login == login:
                    continue
                if review.state in ("CHANGES_REQUESTED", "COMMENTED"):
                    if self._in_window(review.submitted_at):
                        feedback_times.append(review.submitted_at)
            for comment in pr_comments:
                if (
                    comment.pr_number == pr.pr_number
                    and comment.commenter_login != login
                    and self._in_window(comment.created_at)
                ):
                    feedback_times.append(comment.created_at)

            if not feedback_times:
                continue
            first_feedback = min(feedback_times)

            author_replies = [
                c.created_at
                for c in pr_comments
                if c.pr_number == pr.pr_number
                and c.commenter_login == login
                and c.created_at > first_feedback
                and self._in_window(c.created_at)
            ]
            if not author_replies:
                continue
            delta_hours = (min(author_replies) - first_feedback).total_seconds() / 3600
            response_hours.append(delta_hours)

        if not response_hours:
            return MISSING_METRIC
        return float(statistics.median(response_hours))

    def _is_bug_issue(self, issue: Issue) -> bool:
        labels_lower = {label.lower() for label in issue.labels}
        if "bug" in labels_lower:
            return True
        title_lower = (issue.title or "").lower()
        return title_lower.startswith("bug") or title_lower.startswith("[bug]")

    def _extract_pr_refs(self, text: str) -> set[int]:
        return {int(match) for match in PR_REF_PATTERN.findall(text)}

    def _extract_closing_issue_refs(self, text: str) -> set[int]:
        return {int(match) for match in CLOSES_PATTERN.findall(text)}
