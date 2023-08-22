# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Iterable, Optional, Type

import lazy_object_proxy
from port_loader import AsyncAdapterRegistry

ADAPTER_REGISTRY = lazy_object_proxy.Proxy(AsyncAdapterRegistry)


def port_dep(port_cls: Type, adapter_cls: Optional[Type] = None):
    async def _wrapper():
        return await ADAPTER_REGISTRY(port_cls, adapter_cls)

    return _wrapper


async def initialize_adapters(
    adapter_registry: AsyncAdapterRegistry, port_classes: Iterable[Type]
):
    for port_cls in port_classes:
        await adapter_registry(port_cls)
