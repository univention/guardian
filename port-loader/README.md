# Port Loader

This library provides you with a AdapterRegistry with which you can implement a configurable
Ports And Adapters pattern in your application

## Usage

```python
from typing import Type
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider, Settings

registry = AsyncAdapterRegistry()

@registry.register_adapter(AsyncAdapterSettingsProvider, set_adapter=True)
class MyAsyncAdapterSettingsProvider(AsyncAdapterSettingsProvider):
        async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
            raise NotImplementedError

@registry.register_port
class MyPort:
    ...

@registry.register_adapter(MyPort, set_adapter=True)
class MyAdapter(MyPort):
    ...

my_port_instance = await registry(MyPort)
```
