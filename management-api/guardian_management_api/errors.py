# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


class SettingNotFoundError(ValueError):
    """If no value for the specified setting can be found.

    And no default is specified.
    """

    ...


class SettingTypeError(TypeError):
    """If a value was found, but cannot be converted to the expected type."""

    ...


class SettingFormatError(RuntimeError):
    """If the requested setting name is malformed."""

    ...


class ObjectNotFoundError(ValueError):
    """If the requested object could not be found."""

    ...


class PersistenceError(RuntimeError):
    """For any errors other than object not found."""

    ...


class AdapterLoadingError(RuntimeError):
    """For errors that occure during loading of an adapter."""

    ...


class AdapterInitializationError(RuntimeError):
    """For errors that occure during initialization of an adapter."""

    ...


class AdapterConfigurationError(ValueError):
    """For errors that occure during configuration of an adapter."""

    ...
