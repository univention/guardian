# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""End-to-end protection that rows with Flag.IS_BUILTIN cannot be deleted."""

import pytest
from guardian_management_api.adapters.capability import SQLCapabilityPersistenceAdapter
from guardian_management_api.main import app
from guardian_management_api.models.flags import Flag
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBCapability,
    DBCondition,
    DBContext,
    DBNamespace,
    DBPermission,
    DBRole,
)
from sqlalchemy import select, update
from sqlalchemy.sql.functions import count

OTHER_BIT_ONLY = 1 << 1  # a hypothetical second flag bit, IS_BUILTIN unset


async def _set_flags(sqlalchemy_mixin, model, row_id, flags_value):
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            await session.execute(
                update(model).where(model.id == row_id).values(flags=flags_value)
            )


@pytest.mark.e2e
class TestBuiltinFlagProtectionRoutes:
    """For every DELETE endpoint, a row flagged IS_BUILTIN responds 409 conflict."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_app_blocked_when_builtin(
        self, client, create_apps, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_app = (await create_apps(session, 1))[0]
        await _set_flags(sqlalchemy_mixin, DBApp, db_app.id, Flag.IS_BUILTIN)

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
        await _set_flags(
            sqlalchemy_mixin, DBNamespace, db_namespace.id, Flag.IS_BUILTIN
        )

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
        await _set_flags(sqlalchemy_mixin, DBRole, db_role.id, Flag.IS_BUILTIN)

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
        await _set_flags(sqlalchemy_mixin, DBPermission, db_perm.id, Flag.IS_BUILTIN)

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
        await _set_flags(sqlalchemy_mixin, DBCondition, db_cond.id, Flag.IS_BUILTIN)

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
        await _set_flags(sqlalchemy_mixin, DBContext, db_ctx.id, Flag.IS_BUILTIN)

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
        await _set_flags(sqlalchemy_mixin, DBCapability, db_cap.id, Flag.IS_BUILTIN)

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


@pytest.mark.e2e
class TestBuiltinFlagProtectionBitSemantics:
    """Verify the check is a true bitmask AND, not an equality with 1 or != 0."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_other_bit_alone_does_not_block_delete(
        self, client, create_conditions, sqlalchemy_mixin
    ):
        # A flag with only a non-IS_BUILTIN bit set must NOT block deletion.
        async with sqlalchemy_mixin.session() as session:
            db_cond = (await create_conditions(session, 1))[0]
            app_name = db_cond.namespace.app.name
            namespace_name = db_cond.namespace.name
            name = db_cond.name
        await _set_flags(sqlalchemy_mixin, DBCondition, db_cond.id, OTHER_BIT_ONLY)

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

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_composite_flag_with_builtin_bit_blocks_delete(
        self, client, create_conditions, sqlalchemy_mixin
    ):
        # IS_BUILTIN bit alongside other future bits must still block deletion.
        async with sqlalchemy_mixin.session() as session:
            db_cond = (await create_conditions(session, 1))[0]
            app_name = db_cond.namespace.app.name
            namespace_name = db_cond.namespace.name
            name = db_cond.name
        composite = int(Flag.IS_BUILTIN) | OTHER_BIT_ONLY
        await _set_flags(sqlalchemy_mixin, DBCondition, db_cond.id, composite)

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
            assert (
                await session.scalar(
                    select(count(DBCondition.id)).where(DBCondition.name == name)
                )
            ) == 1


@pytest.mark.e2e
class TestBuiltinFlagPreservedThroughEdits:
    """Editing a built-in object must not silently clear its IS_BUILTIN flag."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_capability_edit_preserves_builtin_flag(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        # capability.update is a delete+create under the hood, which is why it has
        # a flag-preservation path. Regression guard for that.
        from guardian_management_api.adapters.capability import (
            SQLCapabilityPersistenceAdapter,
        )

        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        await _set_flags(sqlalchemy_mixin, DBCapability, db_cap.id, Flag.IS_BUILTIN)

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

        # After edit, delete must still be blocked: flag must have survived.
        delete_result = client.delete(
            client.app.url_path_for(
                "delete_capability",
                app_name=cap.app_name,
                namespace_name=cap.namespace_name,
                name=cap.name,
            )
        )
        assert delete_result.status_code == 409, delete_result.json()
