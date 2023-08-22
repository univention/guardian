# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


class SettingTypeError(TypeError):
    """If a value was found, but cannot be converted to the expected type."""

    ...


class SettingFormatError(RuntimeError):
    """If the requested setting name is malformed."""

    ...


class SettingNotFoundError(ValueError):
    """If no value for the specified setting can be found.

    And no default is specified.
    """

    ...
