# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


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


class PolicyUpstreamError(Exception):
    ...
