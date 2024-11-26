# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import inspect

import pytest
from guardian_lib.adapter_registry import initialize_adapters, port_dep
from guardian_lib.ports import SettingsPort
from port_loader import AsyncAdapterRegistry


class TestPort: ...


class TestPort2: ...


class TestAdapter: ...


@pytest.mark.asyncio
async def test_initialize_adapters(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_port = call_mock
    await initialize_adapters(registry, (TestPort, TestPort2))
    assert call_mock.call_args_list == [
        mocker.call(port_cls) for port_cls in [TestPort, TestPort2]
    ]


def test_port_dep_is_callable():
    """
    This test ensures that the return value from port_dep is a callable without
    any parameters to be used as a FastAPI dependency.
    """
    dep = port_dep(SettingsPort)
    assert inspect.isfunction(dep)
    signature = inspect.signature(dep)
    assert len(signature.parameters) == 0


@pytest.mark.asyncio
async def test_port_dep_port_only(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_port = call_mock
    mocker.patch("guardian_lib.adapter_registry.ADAPTER_REGISTRY", registry)
    await port_dep(SettingsPort)()
    assert await call_mock.called_once_with(SettingsPort)


@pytest.mark.asyncio
async def test_port_dep_with_adapter(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_adapter = call_mock
    mocker.patch("guardian_lib.adapter_registry.ADAPTER_REGISTRY", registry)
    await port_dep(TestPort, TestAdapter)()
    assert await call_mock.called_once_with(
        TestPort,
        TestAdapter,
    )
