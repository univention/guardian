"""Add Flags to models

Revision ID: 3.0.10
Revises: 3.0.4
Create Date: 2026-05-28 13:09:18.092084

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3.0.10"
down_revision: Union[str, None] = "3.0.4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BUILTIN_NS_FILTER = """
    namespace_id IN (
        SELECT n.id FROM namespace n
        JOIN app a ON a.id = n.app_id
        WHERE a.name = 'guardian' AND n.name = 'builtin'
    )
"""

MANAGEMENT_NS_FILTER = """
    namespace_id IN (
        SELECT n.id FROM namespace n
        JOIN app a ON a.id = n.app_id
        WHERE a.name = 'guardian' AND n.name = 'management-api'
    )
"""


def upgrade() -> None:
    op.add_column(
        "app", sa.Column("flags", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "capability",
        sa.Column("flags", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "condition",
        sa.Column("flags", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "context", sa.Column("flags", sa.Integer(), server_default="0", nullable=False)
    )
    op.add_column(
        "namespace",
        sa.Column("flags", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "permission",
        sa.Column("flags", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "role", sa.Column("flags", sa.Integer(), server_default="0", nullable=False)
    )

    op.execute("UPDATE app SET flags = 1 WHERE name = 'guardian'")
    op.execute(
        "UPDATE namespace SET flags = 1 WHERE app_id = "
        "(SELECT id FROM app WHERE name = 'guardian') "
        "AND name IN ('builtin', 'management-api', 'default')"
    )
    op.execute(f"UPDATE condition SET flags = 1 WHERE {BUILTIN_NS_FILTER}")
    op.execute(f"UPDATE permission SET flags = 1 WHERE {MANAGEMENT_NS_FILTER}")
    op.execute(f"UPDATE role SET flags = 1 WHERE {BUILTIN_NS_FILTER}")
    op.execute(f"UPDATE capability SET flags = 1 WHERE {MANAGEMENT_NS_FILTER}")


def downgrade() -> None:
    op.drop_column("role", "flags")
    op.drop_column("permission", "flags")
    op.drop_column("namespace", "flags")
    op.drop_column("context", "flags")
    op.drop_column("condition", "flags")
    op.drop_column("capability", "flags")
    op.drop_column("app", "flags")
