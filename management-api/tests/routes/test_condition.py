# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from urllib.parse import urljoin

import pytest
from guardian_management_api.adapters.condition import SQLConditionPersistenceAdapter
from guardian_management_api.constants import BASE_URL, COMPLETE_URL
from guardian_management_api.models.condition import Condition, ConditionParameterType
from guardian_management_api.models.routers.condition import (
    ConditionParameter,
    ConditionParameterName,
)
from guardian_management_api.models.sql_persistence import DBCondition


@pytest.mark.e2e
class TestConditionEndpoints:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_condition(self, client, create_conditions, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_condition = (await create_conditions(session, 1))[0]
        condition = SQLConditionPersistenceAdapter._db_condition_to_condition(
            db_condition
        )
        resource = client.app.url_path_for(
            "get_condition",
            app_name=condition.app_name,
            namespace_name=condition.namespace_name,
            name=condition.name,
        )
        response = client.get(resource)
        assert response.status_code == 200
        assert response.json() == {
            "condition": {
                "app_name": condition.app_name,
                "namespace_name": condition.namespace_name,
                "name": condition.name,
                "display_name": condition.display_name,
                "documentation": condition.documentation,
                "parameters": [
                    {"name": cond_param.name, "value_type": cond_param.value_type.name}
                    for cond_param in condition.parameters
                ],
                "resource_url": urljoin(BASE_URL, resource),
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_condition_404(self, client):
        resource = client.app.url_path_for(
            "get_condition",
            app_name="app",
            namespace_name="namespace",
            name="condition",
        )
        response = client.get(resource)
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_conditions(self, client, create_conditions, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_conditions = await create_conditions(session, 5)
        response = client.get(client.app.url_path_for("get_all_conditions"))
        assert response.status_code == 200
        conditions = response.json()["conditions"]
        pagination = response.json()["pagination"]
        assert pagination == {"offset": 0, "limit": 5, "total_count": 5}
        for index, condition in enumerate(conditions):
            orig_condition = SQLConditionPersistenceAdapter._db_condition_to_condition(
                db_conditions[index]
            )
            resource = client.app.url_path_for(
                "get_condition",
                app_name=orig_condition.app_name,
                namespace_name=orig_condition.namespace_name,
                name=orig_condition.name,
            )
            assert condition == {
                "app_name": orig_condition.app_name,
                "namespace_name": orig_condition.namespace_name,
                "name": orig_condition.name,
                "display_name": orig_condition.display_name,
                "documentation": orig_condition.documentation,
                "parameters": [
                    {"name": cond_param.name, "value_type": cond_param.value_type.name}
                    for cond_param in orig_condition.parameters
                ],
                "resource_url": urljoin(BASE_URL, resource),
            }

    @pytest.mark.parametrize(
        "offset,limit", [(0, None), (1, None), (0, None), (0, 3), (0, 20)]
    )
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_conditions_pagination(
        self, client, create_conditions, sqlalchemy_mixin, offset, limit
    ):
        async with sqlalchemy_mixin.session() as session:
            db_conditions = await create_conditions(session, 10)
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        response = client.get(
            client.app.url_path_for("get_all_conditions"), params=params
        )
        assert response.status_code == 200, response.json()
        conditions = response.json()["conditions"]
        pagination = response.json()["pagination"]
        assert pagination == {
            "offset": offset,
            "limit": 10 if limit is None else limit,
            "total_count": 10,
        }
        for index, condition in enumerate(conditions):
            orig_condition = SQLConditionPersistenceAdapter._db_condition_to_condition(
                db_conditions[offset + index]
            )
            resource = client.app.url_path_for(
                "get_condition",
                app_name=orig_condition.app_name,
                namespace_name=orig_condition.namespace_name,
                name=orig_condition.name,
            )
            assert condition == {
                "app_name": orig_condition.app_name,
                "namespace_name": orig_condition.namespace_name,
                "name": orig_condition.name,
                "display_name": orig_condition.display_name,
                "documentation": orig_condition.documentation,
                "parameters": [
                    {"name": param.name, "value_type": param.value_type.name}
                    for param in orig_condition.parameters
                ],
                "resource_url": urljoin(BASE_URL, resource),
            }

    @pytest.mark.asyncio
    async def test_get_conditions_error(self, client):
        response = client.get(client.app.url_path_for("get_all_conditions"))
        assert response.status_code == 500

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_condition(self, client, sqlalchemy_mixin, create_namespaces):
        async with sqlalchemy_mixin.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        condition_to_create = Condition(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="condition",
            display_name="Condition",
            documentation="doc",
            code=b"Q09ERQ==",
            parameters=[
                ConditionParameter(
                    name=ConditionParameterName("a"),
                    value_type=ConditionParameterType.ANY,
                )
            ],
        )
        result = client.post(
            client.app.url_path_for(
                "create_condition",
                app_name=condition_to_create.app_name,
                namespace_name=condition_to_create.namespace_name,
            ),
            json={
                "name": condition_to_create.name,
                "display_name": condition_to_create.display_name,
                "documentation": condition_to_create.documentation,
                "parameters": [{"name": "a", "value_type": "ANY"}],
                "code": condition_to_create.code.decode(),
            },
        )
        assert result.status_code == 201, result.json()
        expected_result = asdict(condition_to_create)
        del expected_result["code"]
        expected_result["resource_url"] = (
            f"{COMPLETE_URL}/conditions/{condition_to_create.app_name}/"
            f"{condition_to_create.namespace_name}/{condition_to_create.name}"
        )
        assert result.json()["condition"] == expected_result
        db_condition = await sqlalchemy_mixin._get_single_object(
            DBCondition,
            name=condition_to_create.name,
            app_name=condition_to_create.app_name,
            namespace_name=namespace.name,
        )
        for attribute in ("name", "display_name", "documentation", "code"):
            assert getattr(db_condition, attribute) == getattr(
                condition_to_create, attribute
            )
        assert len(db_condition.parameters) == 1
        assert db_condition.parameters[0].name == "a"
        assert db_condition.parameters[0].value_type == ConditionParameterType.ANY

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_condition_unknown_parents(self, client):
        condition_to_create = Condition(
            app_name="some_app",
            namespace_name="some_namespace",
            name="condition",
            display_name="Condition",
            documentation="doc",
            code=b"Q09ERQ==",
            parameters=["A", "B", "Z"],
        )
        result = client.post(
            client.app.url_path_for(
                "create_condition",
                app_name=condition_to_create.app_name,
                namespace_name=condition_to_create.namespace_name,
            ),
            json={
                "name": condition_to_create.name,
                "display_name": condition_to_create.display_name,
                "documentation": condition_to_create.documentation,
                "parameter_names": condition_to_create.parameters,
                "code": condition_to_create.code.decode(),
            },
        )
        assert result.status_code == 404, result.json()
        assert result.json() == {
            "detail": {"message": "The app of the object to be created does not exist."}
        }, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_condition_already_exists(
        self, client, sqlalchemy_mixin, create_conditions
    ):
        async with sqlalchemy_mixin.session() as session:
            db_condition = (await create_conditions(session, 1))[0]
        condition_to_create = Condition(
            app_name=db_condition.namespace.app.name,
            namespace_name=db_condition.namespace.name,
            name=db_condition.name,
            display_name="Condition",
            documentation="doc",
            code=b"Q09ERQ==",
            parameters=["A", "B", "Z"],
        )
        result = client.post(
            client.app.url_path_for(
                "create_condition",
                app_name=condition_to_create.app_name,
                namespace_name=condition_to_create.namespace_name,
            ),
            json={
                "name": condition_to_create.name,
                "display_name": condition_to_create.display_name,
                "documentation": condition_to_create.documentation,
                "parameter_names": condition_to_create.parameters,
                "code": condition_to_create.code.decode(),
            },
        )
        assert result.status_code == 400, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_edit_condition(self, client, sqlalchemy_mixin, create_conditions):
        async with sqlalchemy_mixin.session() as session:
            db_condition = (await create_conditions(session, 1))[0]
        new_values = {"documentation": "NEW DOC", "display_name": "NEW DISPLAY NAME"}
        result = client.patch(
            client.app.url_path_for(
                "edit_condition",
                app_name=db_condition.namespace.app.name,
                namespace_name=db_condition.namespace.name,
                name=db_condition.name,
            ),
            json=new_values,
        )
        assert result.status_code == 200, result.json()
        result_data = result.json()
        for key, value in new_values.items():
            assert result_data["condition"][key] == value, result_data

    @pytest.mark.asyncio
    async def test_edit_condition_error(self, client):
        new_values = {"documentation": "NEW DOC", "display_name": "NEW DISPLAY NAME"}
        result = client.patch(
            client.app.url_path_for(
                "edit_condition",
                app_name="app",
                namespace_name="namespace",
                name="condition",
            ),
            json=new_values,
        )
        assert result.status_code == 500, result.json()
