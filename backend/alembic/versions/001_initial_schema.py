"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pull_requests",
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("author_login", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False),
        sa.Column("deletions", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("pr_number"),
    )
    op.create_index("ix_pull_requests_author_login", "pull_requests", ["author_login"])

    op.create_table(
        "issues",
        sa.Column("issue_number", sa.Integer(), nullable=False),
        sa.Column("author_login", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("labels", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("issue_number"),
    )
    op.create_index("ix_issues_author_login", "issues", ["author_login"])

    op.create_table(
        "pr_files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=1024), nullable=False),
        sa.ForeignKeyConstraint(["pr_number"], ["pull_requests.pr_number"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pr_files_pr_number", "pr_files", ["pr_number"])

    op.create_table(
        "pr_reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("reviewer_login", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pr_number"], ["pull_requests.pr_number"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pr_reviews_pr_number", "pr_reviews", ["pr_number"])
    op.create_index("ix_pr_reviews_reviewer_login", "pr_reviews", ["reviewer_login"])

    op.create_table(
        "pr_review_comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("github_id", sa.Integer(), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=False),
        sa.Column("commenter_login", sa.String(length=255), nullable=False),
        sa.Column("pr_author_login", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id"),
    )
    op.create_index("ix_pr_review_comments_pr_number", "pr_review_comments", ["pr_number"])
    op.create_index("ix_pr_review_comments_commenter_login", "pr_review_comments", ["commenter_login"])
    op.create_index("ix_pr_review_comments_pr_author_login", "pr_review_comments", ["pr_author_login"])

    op.create_table(
        "issue_comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("github_id", sa.Integer(), nullable=False),
        sa.Column("issue_number", sa.Integer(), nullable=False),
        sa.Column("commenter_login", sa.String(length=255), nullable=False),
        sa.Column("issue_author_login", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id"),
    )
    op.create_index("ix_issue_comments_issue_number", "issue_comments", ["issue_number"])
    op.create_index("ix_issue_comments_commenter_login", "issue_comments", ["commenter_login"])


def downgrade() -> None:
    op.drop_table("issue_comments")
    op.drop_table("pr_review_comments")
    op.drop_table("pr_reviews")
    op.drop_table("pr_files")
    op.drop_table("issues")
    op.drop_table("pull_requests")
