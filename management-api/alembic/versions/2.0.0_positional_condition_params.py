"""positional_condition_params

Revision ID: 2.0.0
Revises: 1.0.0
Create Date: 2024-01-10 10:12:16.518339

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2.0.0"
down_revision: Union[str, None] = "1.0.0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE condition_parameter ADD COLUMN position INTEGER NOT NULL DEFAULT 0;"
    )
    op.execute("UPDATE condition_parameter SET position=1 where name='value';")
    op.execute("UPDATE condition_parameter SET position=1 where name='actor_field';")


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("condition_parameter", "position")
    # ### end Alembic commands ###
