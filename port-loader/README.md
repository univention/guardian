<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Port Loader

This library provides you with a AdapterRegistry with which you can implement a configurable
Ports And Adapters pattern in your application

## Usage

```python
from typing import Type
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider, Settings, inject_port

registry = AsyncAdapterRegistry()

@registry.register_adapter(AsyncAdapterSettingsProvider, set_adapter=True)
class MyAsyncAdapterSettingsProvider(AsyncAdapterSettingsProvider):
        async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
            raise NotImplementedError

@registry.register_port
class MyPort:
    def some_function(self, a: int):
        pass

@registry.register_port
class OtherPort:
    ...

@registry.register_adapter(MyPort, set_adapter=True)
class MyAdapter(MyPort):
    def some_function(self, a: int, other_port: OtherPort = inject_port(OtherPort)):
        ...

my_port_instance = await registry(MyPort)
```

## About injection

The port injection via the `inject_port` default parameter works on instance methods only.
staticmethods, classmethods, properties, etc. are excluded for technical reasons.
