class DuplicateAdapterError(ValueError):
    """
    Another adapter of the same kind already exists for the port.

    This can happen when:

    1. An adapter of the same class is already registered.
    2. An adapter with the same alias is already registered.
    """

    ...


class DuplicatePortError(ValueError):
    """Another port with the same class is already registered."""

    ...


class PortSubclassError(TypeError):
    """Adapter is not a subclass of the specified port."""

    ...


class AdapterNotFoundError(RuntimeError):
    """
    Adapter was never registered with the port.

    This can happen when:

    1. The adapter is being found by alias, and the alias was not registered.
    2. The adapter is being found by class, and the class was not registered.
    """

    ...


class PortNotFoundError(RuntimeError):
    """Port class was never registered."""

    ...


class AdapterNotSetError(RuntimeError):
    """
    The port does not know which adapter to use.

    This can happen when:

    1. There are no adapters registered for the port.
    2. There are multiple adapters registered, and one isn't explicitly set.

    If there is exactly one adapter registered for the port, regardless of
    whether it is explicitly selected for the port, this error should not be
    thrown.
    """

    ...


class AdapterInstantiationError(RuntimeError):
    """
    An error occurred when the adapter class was instantiated.

    When using this error, please raise it from original exception.
    """

    ...


class AdapterConfigurationError(RuntimeError):
    """
    An error occurred when the adapter class was configured.

    When using this error, please raise it from original exception.
    """

    ...


class InjectionError(RuntimeError):
    """
    An error occurred when the adapter was injected into the code.

    This can happen when:

    1. The function using the injection is decorated.
    2. The decorated function is called.

    When using this error, please raise it from original exception.
    """

    ...
