# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from port_loader import EnvSettingsProvider

from ..ports import SettingsPort


class EnvSettingsAdapter(EnvSettingsProvider, SettingsPort):
    """
    This adapter loads all settings exclusively from environment variables.


    This adapter is a singleton and will be instantiated only once.
    This adapter interprets the '.' symbol in setting name as a double underscore, when
    converting to an environment variable and assumes capital letters only.

    """
