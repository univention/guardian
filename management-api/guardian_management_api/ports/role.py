# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Proposed layout for role ports/models
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models.role import Role, RoleAPIResponse, RoleQuery, RolesListAPIResponse
from .base import (
    BasePort,
)

###############################################################################
#                                                                             #
#  Incoming ports                                                             #
#                                                                             #
###############################################################################


class RoleAPIPort(BasePort, ABC):
    @abstractmethod
    def create(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
        display_name: Optional[str] = None,
    ) -> RoleAPIResponse:
        pass

    @abstractmethod
    def read_one(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
    ) -> RoleAPIResponse:
        pass

    @abstractmethod
    def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        pagination_offset: Optional[int] = None,
        pagination_limit: Optional[int] = None,
    ) -> RolesListAPIResponse:
        pass

    @abstractmethod
    def update(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
        display_name: str,
    ) -> RoleAPIResponse:
        pass


###############################################################################
#                                                                             #
#  Outgoing ports                                                             #
#                                                                             #
###############################################################################


class RolePersistencePort(BasePort, ABC):
    @abstractmethod
    async def create(
        self,
        role: Role,
    ) -> Role:
        pass

    @abstractmethod
    async def read_one(
        self,
        app_name: str,
        namespace_name: str,
        role_name: str,
    ) -> Role:
        pass

    @abstractmethod
    async def read_many(
        self,
        app_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> RoleQuery:
        pass

    @abstractmethod
    async def update(
        self,
        role: Role,
    ) -> Role:
        pass
