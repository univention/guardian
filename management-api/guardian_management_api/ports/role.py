# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from abc import ABC

from ..models.role import Role, RoleGetQuery, RolesGetQuery
from .base import BasePersistencePort

###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RolePersistencePort(BasePersistencePort[Role, RoleGetQuery, RolesGetQuery], ABC):
    ...
