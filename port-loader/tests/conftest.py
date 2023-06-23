# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from port_loader import AsyncAdapterRegistry


@pytest.fixture
def async_registry() -> AsyncAdapterRegistry:
    return AsyncAdapterRegistry()


@pytest.fixture
def mock_async_registry(mocker):
    return mocker.AsyncMock()


@pytest.fixture()
def register_and_set_adapter():
    def _register_and_set(registry: AsyncAdapterRegistry, port_cls, adapter_cls):
        registry.register_adapter(port_cls, adapter_cls=adapter_cls)
        registry.set_adapter(port_cls, adapter_cls)

    return _register_and_set
