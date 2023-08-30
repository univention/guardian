from abc import ABC

from ..models.permission import Permission, PermissionGetQuery, PermissionsGetQuery
from .base import BasePersistencePort


class PermissionPersistencePort(
    BasePersistencePort[Permission, PermissionGetQuery, PermissionsGetQuery], ABC
):
    ...
