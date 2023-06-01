class SettingNotFoundError(ValueError):
    ...


class SettingTypeError(TypeError):
    ...


class ObjectNotFoundError(ValueError):
    ...


class PersistenceError(RuntimeError):
    ...


class AdapterLoadingError(RuntimeError):
    ...


class AdapterInitializationError(RuntimeError):
    ...


class AdapterConfigurationError(ValueError):
    ...
