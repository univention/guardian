# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from guardian_lib.ports import BasePort

from .models.persistence import ObjectType, PersistenceObject
from .models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    GetPermissionsQuery,
    GetPermissionsResult,
    Policy,
)

GetPermissionsAPIResponseObject = TypeVar("GetPermissionsAPIResponseObject")
GetPermissionsAPIRequestObject = TypeVar("GetPermissionsAPIRequestObject")

CheckPermissionsAPIResponseObject = TypeVar("CheckPermissionsAPIResponseObject")
CheckPermissionsAPIRequestObject = TypeVar("CheckPermissionsAPIRequestObject")

CheckPermissionsWithLookupAPIRequestObject = TypeVar(
    "CheckPermissionsWithLookupAPIRequestObject"
)


class PersistencePort(BasePort, ABC):
    """
    This port enables access to objects in a persistent database.

    It is used to fetch actors and targets when the API is only provided with identifiers
    and not the full objects.
    """

    @abstractmethod
    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        """
        Fetches an object from the persistent database and returns it.

        :param identifier: The identifier for the object to retrieve
        :param object_type: The type of the object to retrieve
        :return: The object
        :raises ObjectNotFoundError: If the requested object could not be found
        :raises PersistenceError: For any errors other than object not found
        """
        raise NotImplementedError  # pragma: no cover


class PolicyPort(BasePort, ABC):
    """
    This port enables access to a policy evaluation agent such as OPA.
    """

    @abstractmethod
    async def check_permissions(
        self, query: CheckPermissionsQuery
    ) -> CheckPermissionsResult:
        """
        This method allows to check if an actor has the specified permissions,
        when acting on the specified targets.
        It also allows to query for general permissions, if acting on no particular target.

        :return: A result object detailing if the actor has the permissions regarding every target
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def get_permissions(self, query: GetPermissionsQuery) -> GetPermissionsResult:
        """
        This method allows to retrieve all permissions an actor has
        when acting on the specified targets.

        :return: A result object containing the permissions the actor has regarding every target
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def custom_policy(
        self, policy: Policy, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        This method allows to query a custom policy that was registered with the Guardian Management API.

        Since the expected data and the response of the custom policy are unknown, arbitrary data
        is passed and returned.

        :param policy: The policy to query
        :param data: The data that should be passed to the custom policy
        :return: The data returned by the custom policy
        """
        raise NotImplementedError  # pragma: no cover


class GetPermissionsAPIPort(
    BasePort,
    ABC,
    Generic[GetPermissionsAPIRequestObject, GetPermissionsAPIResponseObject],
):
    @abstractmethod
    async def to_policy_query(
        self, api_request: GetPermissionsAPIRequestObject
    ) -> GetPermissionsQuery:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def to_api_response(
        self, permissions_result: GetPermissionsResult
    ) -> GetPermissionsAPIResponseObject:
        raise NotImplementedError  # pragma: no cover


class CheckPermissionsAPIPort(
    BasePort,
    ABC,
    Generic[
        CheckPermissionsAPIRequestObject,
        CheckPermissionsAPIResponseObject,
        CheckPermissionsWithLookupAPIRequestObject,
    ],
):
    @abstractmethod
    async def transform_exception(self, exc: Exception) -> Exception:
        ...  # pragma: no cover

    @abstractmethod
    async def to_policy_query(
        self, api_request: CheckPermissionsAPIRequestObject
    ) -> CheckPermissionsQuery:
        ...  # pragma: no cover

    @abstractmethod
    async def to_api_response(
        self, actor_id, check_result: CheckPermissionsResult
    ) -> CheckPermissionsAPIResponseObject:
        ...  # pragma: no cover

    @abstractmethod
    async def to_policy_lookup_query(
        self, api_request: CheckPermissionsWithLookupAPIRequestObject, actor, targets
    ) -> CheckPermissionsQuery:
        ...  # pragma: no cover
