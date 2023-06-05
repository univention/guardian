class SettingNotFoundError(ValueError):
    ...


class SettingTypeError(TypeError):
    ...


class SettingFormatError(RuntimeError):
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
