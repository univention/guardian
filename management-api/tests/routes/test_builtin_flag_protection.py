# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""End-to-end protection that rows with is_builtin=True cannot be deleted."""

import pytest
from guardian_management_api.adapters.capability import SQLCapabilityPersistenceAdapter
from guardian_management_api.main import app
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBCapability,
    DBCondition,
    DBContext,
    DBNamespace,
    DBPermission,
    DBRole,
    role_capability_table,
)
from sqlalchemy import select, update
from sqlalchemy.sql.functions import count


async def _set_builtin(sqlalchemy_mixin, model, row_id, value=True):
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            await session.execute(
                update(model).where(model.id == row_id).values(is_builtin=value)
            )


@pytest.mark.e2e
class TestBuiltinFlagProtectionRoutes:
    """For every DELETE endpoint, a row with is_builtin=True responds 409 conflict."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_app_blocked_when_builtin(
        self, client, create_apps, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_app = (await create_apps(session, 1))[0]
        await _set_builtin(sqlalchemy_mixin, DBApp, db_app.id)

        result = client.delete(app.url_path_for("delete_app", name=db_app.name))

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBApp.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_namespace_blocked_when_builtin(
        self, client, create_namespaces, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        await _set_builtin(sqlalchemy_mixin, DBNamespace, db_namespace.id)

        result = client.delete(
            app.url_path_for(
                "delete_namespace",
                app_name=db_namespace.app.name,
                name=db_namespace.name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBNamespace.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_role_blocked_when_builtin(
        self, client, create_roles, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_role = (await create_roles(session, 1))[0]
            app_name = db_role.namespace.app.name
            namespace_name = db_role.namespace.name
            name = db_role.name
        await _set_builtin(sqlalchemy_mixin, DBRole, db_role.id)

        result = client.delete(
            client.app.url_path_for(
                "delete_role",
                app_name=app_name,
                namespace_name=namespace_name,
                name=name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBRole.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_permission_blocked_when_builtin(
        self, client, create_permissions, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_perm = (await create_permissions(session, 1))[0]
            app_name = db_perm.namespace.app.name
            namespace_name = db_perm.namespace.name
            name = db_perm.name
        await _set_builtin(sqlalchemy_mixin, DBPermission, db_perm.id)

        result = client.delete(
            client.app.url_path_for(
                "delete_permission",
                app_name=app_name,
                namespace_name=namespace_name,
                name=name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBPermission.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_condition_blocked_when_builtin(
        self, client, create_conditions, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cond = (await create_conditions(session, 1))[0]
            app_name = db_cond.namespace.app.name
            namespace_name = db_cond.namespace.name
            name = db_cond.name
        await _set_builtin(sqlalchemy_mixin, DBCondition, db_cond.id)

        result = client.delete(
            client.app.url_path_for(
                "delete_condition",
                app_name=app_name,
                namespace_name=namespace_name,
                name=name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBCondition.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_context_blocked_when_builtin(
        self, client, create_contexts, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_ctx = (await create_contexts(session, 1))[0]
            app_name = db_ctx.namespace.app.name
            namespace_name = db_ctx.namespace.name
            name = db_ctx.name
        await _set_builtin(sqlalchemy_mixin, DBContext, db_ctx.id)

        result = client.delete(
            client.app.url_path_for(
                "delete_context",
                app_name=app_name,
                namespace_name=namespace_name,
                name=name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBContext.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_capability_blocked_when_builtin(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        await _set_builtin(sqlalchemy_mixin, DBCapability, db_cap.id)

        result = client.delete(
            client.app.url_path_for(
                "delete_capability",
                app_name=cap.app_name,
                namespace_name=cap.namespace_name,
                name=cap.name,
            )
        )

        assert result.status_code == 409, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBCapability.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_proceeds_when_not_builtin(
        self, client, create_conditions, sqlalchemy_mixin
    ):
        # Positive control: a row left with is_builtin=False deletes normally.
        async with sqlalchemy_mixin.session() as session:
            db_cond = (await create_conditions(session, 1))[0]
            app_name = db_cond.namespace.app.name
            namespace_name = db_cond.namespace.name
            name = db_cond.name

        result = client.delete(
            client.app.url_path_for(
                "delete_condition",
                app_name=app_name,
                namespace_name=namespace_name,
                name=name,
            )
        )

        assert result.status_code == 204, result.text
        async with sqlalchemy_mixin.session() as session:
            assert (
                await session.scalar(
                    select(count(DBCondition.id)).where(DBCondition.name == name)
                )
            ) == 0


@pytest.mark.e2e
class TestBuiltinFlagPreservedThroughEdits:
    """Editing a built-in object must not silently clear its is_builtin flag."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_capability_edit_preserves_builtin_flag(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        # capability.update is a delete+create under the hood, which is why it has
        # a flag-preservation path. Regression guard for that.
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
            cap_id = db_cap.id
        cap = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        await _set_builtin(sqlalchemy_mixin, DBCapability, db_cap.id)

        edit_payload = {
            "name": cap.name,
            "display_name": "EDITED",
            "relation": cap.relation,
            "conditions": [],
            "permissions": [],
        }
        result = client.put(
            client.app.url_path_for(
                "update_capability",
                app_name=cap.app_name,
                namespace_name=cap.namespace_name,
                name=cap.name,
            ),
            json=edit_payload,
        )
        assert result.status_code == 200, result.json()

        # Detach the role link so the final 409 is attributable to is_builtin
        # rather than to the role dependency check.
        async with sqlalchemy_mixin.session() as session:
            async with session.begin():
                await session.execute(
                    role_capability_table.delete().where(
                        role_capability_table.c.capability_id == cap_id
                    )
                )

        # After edit, delete must still be blocked: the flag must have survived.
        delete_result = client.delete(
            client.app.url_path_for(
                "delete_capability",
                app_name=cap.app_name,
                namespace_name=cap.namespace_name,
                name=cap.name,
            )
        )
        assert delete_result.status_code == 409, delete_result.json()
