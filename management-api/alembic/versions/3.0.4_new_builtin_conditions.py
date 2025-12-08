"""new_builtin_conditions

Revision ID: 3.0.4
Revises: 1.0.0
Create Date: 2025-12-04 10:25:43.518339

"""

import base64
import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3.0.4"
down_revision: Union[str, None] = "2.0.0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_builtin_conditions(session, cond_table, ns_id, cond_param_table):
    condition_path = (
        Path(__file__).resolve().parent / f"../{revision}_builtin_conditions"
    )
    for data_file in condition_path.glob("*.json"):
        cond_name = data_file.stem
        with open(data_file, "r") as f:
            data = json.load(f)
        with open(condition_path / f"{cond_name}.rego", "rb") as f:
            code = f.read()
        cond = {
            **data,
            "code": base64.b64encode(code),
            "name": cond_name,
            "namespace_id": ns_id,
        }
        del cond["parameters"]
        cond_id = session.execute(
            sa.insert(cond_table).values(cond)
        ).inserted_primary_key[0]
        for cond_param in data["parameters"]:
            session.execute(
                sa.insert(cond_param_table).values(
                    {**cond_param, "condition_id": cond_id}
                )
            )


def drop_builtin_conditions(session, cond_table, cond_param_table):
    condition_path = (
        Path(__file__).resolve().parent / f"../{revision}_builtin_conditions"
    )

    cond_table_primary_key_column_name = cond_table.primary_key.columns.values()[0].name

    for data_file in condition_path.glob("*.json"):
        cond_name = data_file.stem
        result = session.execute(
            sa.select(sa.text(cond_table_primary_key_column_name)).where(
                cond_table.c.name == cond_name
            )
        )

        row = result.fetchone()
        if not row:
            raise Exception(f"Failed to get 'id' for condition {cond_name}")

        cond_id = row[0]
        session.execute(
            sa.delete(cond_param_table).where(
                cond_param_table.c.condition_id == cond_id
            )
        )
        session.execute(sa.delete(cond_table).where(cond_table.c.id == cond_id))


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    ns_table = sa.Table("namespace", sa.MetaData(), autoload_with=bind)
    ns_table_primary_key_column_name = ns_table.primary_key.columns.values()[0].name

    result = session.execute(
        sa.select(sa.text(ns_table_primary_key_column_name)).where(
            ns_table.c.name == "builtin"
        )
    )

    row = result.fetchone()
    if not row:
        raise Exception("Failed to get 'builtin' namespace")

    builtin_ns_id = row[0]
    cond_table = sa.Table("condition", sa.MetaData(), autoload_with=bind)
    cond_param_table = sa.Table(
        "condition_parameter", sa.MetaData(), autoload_with=bind
    )

    create_builtin_conditions(session, cond_table, builtin_ns_id, cond_param_table)


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    cond_table = sa.Table("condition", sa.MetaData(), autoload_with=bind)
    cond_param_table = sa.Table(
        "condition_parameter", sa.MetaData(), autoload_with=bind
    )

    drop_builtin_conditions(session, cond_table, cond_param_table)
