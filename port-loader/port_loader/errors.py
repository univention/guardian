class DuplicateAdapterError(ValueError):
    ...


class DuplicatePortError(ValueError):
    ...


class PortTypeError(TypeError):
    ...


class AdapterNotFoundError(RuntimeError):
    ...


class PortNotFoundError(RuntimeError):
    ...


class AdapterNotSetError(RuntimeError):
    ...


class AdapterInstantiationError(RuntimeError):
    ...


class AdapterConfigurationError(RuntimeError):
    ...


class PortInjectionError(RuntimeError):
    ...
