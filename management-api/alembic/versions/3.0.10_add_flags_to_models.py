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


def upgrade() -> None:
    # ``batch_alter_table`` recreates ``capability`` via rename + new table +
    # INSERT SELECT + drop-of-old. Dropping the old table cascades through
    # ``ON DELETE CASCADE`` FKs and wipes ``capability_permission`` and
    # ``capability_condition``. Snapshot the existing relationships (including
    # the soon-to-be-removed ``role_id`` column) into temp tables first, then
    # restore them afterwards.
    op.execute(
        "CREATE TEMP TABLE _role_capability_seed AS "
        "SELECT role_id, id AS capability_id FROM capability"
    )
    op.execute(
        "CREATE TEMP TABLE _capability_permission_seed AS "
        "SELECT capability_id, permission_id FROM capability_permission"
    )
    op.execute(
        "CREATE TEMP TABLE _capability_condition_seed AS "
        "SELECT id, capability_id, condition_id, kwargs FROM capability_condition"
    )

    with op.batch_alter_table("capability") as batch_op:
        batch_op.drop_column("role_id")
        batch_op.add_column(
            sa.Column("flags", sa.Integer(), server_default="0", nullable=False)
        )

    op.execute(
        "INSERT INTO capability_permission (capability_id, permission_id) "
        "SELECT capability_id, permission_id FROM _capability_permission_seed"
    )
    op.execute(
        "INSERT INTO capability_condition (id, capability_id, condition_id, kwargs) "
        "SELECT id, capability_id, condition_id, kwargs FROM _capability_condition_seed"
    )
    op.execute("DROP TABLE _capability_permission_seed")
    op.execute("DROP TABLE _capability_condition_seed")

    op.create_table(
        "role_capability",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("capability_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["capability_id"], ["capability.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "capability_id"),
    )
    op.execute(
        "INSERT INTO role_capability (role_id, capability_id) "
        "SELECT role_id, capability_id FROM _role_capability_seed"
    )
    op.execute("DROP TABLE _role_capability_seed")

    op.add_column(
        "app", sa.Column("flags", sa.Integer(), server_default="0", nullable=False)
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
    op.execute(
        """
        UPDATE condition SET flags = 1 WHERE namespace_id IN (
            SELECT n.id FROM namespace n
            JOIN app a ON a.id = n.app_id
            WHERE a.name = 'guardian' AND n.name = 'builtin'
        )
        """
    )
    op.execute(
        """
        UPDATE permission SET flags = 1 WHERE namespace_id IN (
            SELECT n.id FROM namespace n
            JOIN app a ON a.id = n.app_id
            WHERE a.name = 'guardian' AND n.name = 'management-api'
        )
        """
    )
    op.execute(
        """
        UPDATE role SET flags = 1 WHERE namespace_id IN (
            SELECT n.id FROM namespace n
            JOIN app a ON a.id = n.app_id
            WHERE a.name = 'guardian' AND n.name = 'builtin'
        )
        """
    )
    op.execute(
        """
        UPDATE capability SET flags = 1 WHERE namespace_id IN (
            SELECT n.id FROM namespace n
            JOIN app a ON a.id = n.app_id
            WHERE a.name = 'guardian' AND n.name = 'management-api'
        )
        """
    )


def downgrade() -> None:
    op.drop_column("role", "flags")
    op.drop_column("permission", "flags")
    op.drop_column("namespace", "flags")
    op.drop_column("context", "flags")
    op.drop_column("condition", "flags")
    op.drop_column("capability", "flags")
    op.drop_column("app", "flags")

    with op.batch_alter_table("capability") as batch_op:
        batch_op.add_column(sa.Column("role_id", sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(
            "fk_capability_role_id", "role", ["role_id"], ["id"]
        )
    op.execute(
        "UPDATE capability SET role_id = ("
        "SELECT role_id FROM role_capability WHERE capability_id = capability.id LIMIT 1"
        ")"
    )
    op.drop_table("role_capability")
