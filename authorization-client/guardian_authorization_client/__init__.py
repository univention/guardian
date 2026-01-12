# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Guardian Authorization Client Library"""

from guardian_authorization_client.authorization import (
    DN,
    GuardianAuthorizationClient,
    LocalGuardianAuthorizationClient,
    TokenInvalidError,
    expand_namespace,
    expand_namespace_string,
    expand_role,
    expand_role_string,
    implode_permission,
)
from guardian_authorization_client.config import AuthorizationConfig
from guardian_authorization_client.management import (
    GuardianManagementClient,
    GuardianManagementClientLocal,
    expand_condition,
    expand_permission,
    expand_string,
    implode_string,
)

__all__ = [
    # Authorization clients
    "GuardianAuthorizationClient",
    "LocalGuardianAuthorizationClient",
    # Management clients
    "GuardianManagementClient",
    "GuardianManagementClientLocal",
    # Configuration
    "AuthorizationConfig",
    # Utilities
    "DN",
    "TokenInvalidError",
    "expand_condition",
    "expand_namespace",
    "expand_namespace_string",
    "expand_permission",
    "expand_role",
    "expand_role_string",
    "expand_string",
    "implode_permission",
    "implode_string",
]
