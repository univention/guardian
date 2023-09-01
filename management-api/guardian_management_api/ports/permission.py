# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC

from ..models.permission import Permission, PermissionGetQuery, PermissionsGetQuery
from .base import BasePersistencePort


class PermissionPersistencePort(
    BasePersistencePort[Permission, PermissionGetQuery, PermissionsGetQuery], ABC
):
    ...
