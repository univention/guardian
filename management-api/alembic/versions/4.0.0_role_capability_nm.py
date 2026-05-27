"""role_capability_nm

Revision ID: 4.0.0
Revises: 3.0.4
Create Date: 2026-05-27 10:46:08.513872

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4.0.0"
down_revision: Union[str, None] = "3.0.4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
        "SELECT role_id, id FROM capability"
    )
    with op.batch_alter_table("capability") as batch_op:
        batch_op.drop_column("role_id")


def downgrade() -> None:
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
