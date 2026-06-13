"""Add issue title and assignees

Revision ID: 002
Revises: 001
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "issues",
        sa.Column("title", sa.String(length=512), nullable=False, server_default=""),
    )
    op.add_column(
        "issues",
        sa.Column("assignees", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
    )
    op.alter_column("issues", "title", server_default=None)


def downgrade() -> None:
    op.drop_column("issues", "assignees")
    op.drop_column("issues", "title")
