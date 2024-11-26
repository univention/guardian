"""Initial Schema

Revision ID: 1.0.0
Revises:
Create Date: 2023-09-22 08:02:51.412858

"""

import base64
import json
import os.path
from pathlib import Path
from typing import Sequence, Tuple, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import insert, orm

# revision identifiers, used by Alembic.
revision: str = "1.0.0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_guardian_app(session, app_table, ns_table) -> Tuple[int, int]:
    app_data = {"name": "guardian", "display_name": "The Guardian Application"}
    app_id = session.execute(insert(app_table).values(app_data)).inserted_primary_key[0]
    ns_default = {
        "app_id": app_id,
        "name": "default",
        "display_name": "Default Namespace of the Guardian Application",
    }
    ns_protected = {
        "app_id": app_id,
        "name": "builtin",
        "display_name": "Builtin Namespace of the Guardian Application",
    }
    session.execute(insert(ns_table).values(ns_default))
    ns_id = session.execute(insert(ns_table).values(ns_protected)).inserted_primary_key[
        0
    ]
    return app_id, ns_id


def create_app_admin(
    session,
    role_table,
    cap_table,
    cap_perm_table,
    cap_cond_table,
    builtin_ns_id,
    management_ns_id,
    conditions,
    permissions,
):
    role_data = {
        "namespace_id": builtin_ns_id,
        "name": "app-admin",
        "display_name": "The app admin for the Guardian Application",
    }
    role_id = session.execute(
        insert(role_table).values(role_data)
    ).inserted_primary_key[0]
    cap_id = session.execute(
        insert(cap_table).values(
            {
                "namespace_id": management_ns_id,
                "name": "guardian-admin-cap",
                "display_name": "App admin capability",
                "role_id": role_id,
                "relation": "AND",
            }
        )
    ).inserted_primary_key[0]
    readonly_cap_id = session.execute(
        insert(cap_table).values(
            {
                "namespace_id": management_ns_id,
                "name": "guardian-admin-cap-read-role-cond",
                "display_name": "App admin capability for read access to all roles and conditions",
                "role_id": role_id,
                "relation": "OR",
            }
        )
    ).inserted_primary_key[0]
    for perm_id in permissions.values():
        session.execute(
            insert(cap_perm_table).values(
                {"capability_id": cap_id, "permission_id": perm_id}
            )
        )
    session.execute(
        insert(cap_perm_table).values(
            {
                "capability_id": readonly_cap_id,
                "permission_id": permissions["read_resource"],
            }
        )
    )
    session.execute(
        insert(cap_cond_table).values(
            {
                "capability_id": cap_id,
                "condition_id": conditions["target_field_equals_value"],
                "kwargs": [
                    {"name": "field", "value": "app_name"},
                    {"name": "value", "value": "guardian"},
                ],
            }
        )
    )
    session.execute(
        insert(cap_cond_table).values(
            {
                "capability_id": cap_id,
                "condition_id": conditions["target_field_not_equals_value"],
                "kwargs": [
                    {"name": "field", "value": "namespace_name"},
                    {"name": "value", "value": "builtin"},
                ],
            }
        )
    )
    for field, value in [
        ("resource_type", "condition"),
        ("resource_type", "role"),
        ("app_name", "guardian"),
    ]:
        session.execute(
            insert(cap_cond_table).values(
                {
                    "capability_id": readonly_cap_id,
                    "condition_id": conditions["target_field_equals_value"],
                    "kwargs": [
                        {"name": "field", "value": field},
                        {"name": "value", "value": value},
                    ],
                }
            )
        )


def create_management_permissions(session, permission_table, ns_id):
    permissions = {}
    for perm_data in [
        {
            "namespace_id": ns_id,
            "name": "create_resource",
            "display_name": "Create Resource",
        },
        {
            "namespace_id": ns_id,
            "name": "read_resource",
            "display_name": "Read Resource",
        },
        {
            "namespace_id": ns_id,
            "name": "update_resource",
            "display_name": "Update Resource",
        },
        {
            "namespace_id": ns_id,
            "name": "delete_resource",
            "display_name": "Delete Resource",
        },
    ]:
        permissions[perm_data["name"]] = session.execute(
            insert(permission_table).values(perm_data)
        ).inserted_primary_key[0]
    return permissions


def create_super_admin(
    session,
    role_table,
    cap_table,
    cap_perm_table,
    cap_cond_table,
    builtin_ns,
    management_ns,
    permissions,
    conditions,
):
    super_admin = {
        "namespace_id": builtin_ns,
        "name": "super-admin",
        "display_name": "The super admin for the Guardian Application",
    }
    super_admin_id = session.execute(
        insert(role_table).values(super_admin)
    ).inserted_primary_key[0]
    super_cap_data = {
        "namespace_id": management_ns,
        "name": "super_admin_cap",
        "display_name": "The super admin capability",
        "role_id": super_admin_id,
        "relation": "OR",
    }
    cap_id = session.execute(
        insert(cap_table).values(super_cap_data)
    ).inserted_primary_key[0]
    for perm_id in permissions.values():
        session.execute(
            insert(cap_perm_table).values(
                {"capability_id": cap_id, "permission_id": perm_id}
            )
        )
    for field, value in [("namespace_name", "builtin"), ("app_name", "guardian")]:
        session.execute(
            insert(cap_cond_table).values(
                {
                    "capability_id": cap_id,
                    "condition_id": conditions["target_field_not_equals_value"],
                    "kwargs": [
                        {"name": "field", "value": field},
                        {"name": "value", "value": value},
                    ],
                }
            )
        )
    read_all_cap_data = {
        "namespace_id": management_ns,
        "name": "super_admin_cap_read_all",
        "display_name": "The super admin capability to read everything",
        "role_id": super_admin_id,
        "relation": "AND",
    }
    read_all_cap_id = session.execute(
        insert(cap_table).values(read_all_cap_data)
    ).inserted_primary_key[0]
    session.execute(
        insert(cap_perm_table).values(
            {
                "capability_id": read_all_cap_id,
                "permission_id": permissions["read_resource"],
            }
        )
    )


def create_builtin_conditions(session, cond_table, ns_id, cond_param_table):
    conditions = {}
    condition_path = (
        Path(os.path.dirname(os.path.realpath(__file__)))
        / "../1.0.0_builtin_conditions"
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
        cond_id = session.execute(insert(cond_table).values(cond)).inserted_primary_key[
            0
        ]
        conditions[cond_name] = cond_id
        for cond_param in data["parameters"]:
            session.execute(
                insert(cond_param_table).values({**cond_param, "condition_id": cond_id})
            )
    return conditions


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    app_table = op.create_table(
        "app",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    ns_table = op.create_table(
        "namespace",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ["app_id"],
            ["app.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("app_id", "name"),
    )
    cond_table = op.create_table(
        "condition",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("namespace_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column("documentation", sa.Text(), nullable=True),
        sa.Column("code", sa.LargeBinary(), nullable=False),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("namespace_id", "name"),
    )
    op.create_table(
        "context",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("namespace_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("namespace_id", "name"),
    )
    permission_table = op.create_table(
        "permission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("namespace_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("namespace_id", "name"),
    )
    role_table = op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("namespace_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("namespace_id", "name"),
    )
    cap_table = op.create_table(
        "capability",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("namespace_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("display_name", sa.String(length=256), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "relation",
            sa.Enum("AND", "OR", name="capabilityconditionrelation", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("namespace_id", "name"),
    )
    cond_param_table = op.create_table(
        "condition_parameter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("condition_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "value_type",
            sa.Enum(
                "ANY",
                "STRING",
                "FLOAT",
                "INT",
                "BOOLEAN",
                "ROLE",
                "CONTEXT",
                name="conditionparametertype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["condition_id"],
            ["condition.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    cap_cond_table = op.create_table(
        "capability_condition",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("capability_id", sa.Integer(), nullable=False),
        sa.Column("condition_id", sa.Integer(), nullable=False),
        sa.Column("kwargs", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["capability_id"], ["capability.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["condition_id"], ["condition.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    cap_perm_table = op.create_table(
        "capability_permission",
        sa.Column("capability_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["capability_id"], ["capability.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permission.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("capability_id", "permission_id"),
    )
    # ### end Alembic commands ###

    # Setup Guardian default objects
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    app_id, builtin_ns_id = create_guardian_app(session, app_table, ns_table)
    management_ns_id = session.execute(
        insert(ns_table).values(
            {
                "app_id": app_id,
                "name": "management-api",
                "display_name": "Management API Namespace of the Guardian Application",
            }
        )
    ).inserted_primary_key[0]
    conditions = create_builtin_conditions(
        session, cond_table, builtin_ns_id, cond_param_table
    )
    permissions = create_management_permissions(
        session, permission_table, management_ns_id
    )
    create_app_admin(
        session,
        role_table,
        cap_table,
        cap_perm_table,
        cap_cond_table,
        builtin_ns_id,
        management_ns_id,
        conditions,
        permissions,
    )
    create_super_admin(
        session,
        role_table,
        cap_table,
        cap_perm_table,
        cap_cond_table,
        builtin_ns_id,
        management_ns_id,
        permissions,
        conditions,
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("capability_permission")
    op.drop_table("capability_condition")
    op.drop_table("condition_parameter")
    op.drop_table("capability")
    op.drop_table("role")
    op.drop_table("permission")
    op.drop_table("context")
    op.drop_table("condition")
    op.drop_table("namespace")
    op.drop_table("app")
    # ### end Alembic commands ###
