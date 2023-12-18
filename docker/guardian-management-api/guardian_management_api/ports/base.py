# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
Shared classes for the ports/models implementations
"""

from abc import ABC, abstractmethod
from typing import Generic

from guardian_lib.ports import BasePort

from ..models.base import (
    PersistenceGetManyQuery,
    PersistenceGetManyResult,
    PersistenceGetQuery,
    PersistenceObject,
)


class BasePersistencePort(
    BasePort,
    ABC,
    Generic[PersistenceObject, PersistenceGetQuery, PersistenceGetManyQuery],
):  # pragma: no cover
    @abstractmethod
    async def create(self, obj: PersistenceObject) -> PersistenceObject:
        """
        Creates the specified object in the persistent storage.

        :raises ObjectExistsError: If an object with that identity already exists.
        :raises ParentNotFoundError: If the parent object of the object to create could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, obj: PersistenceObject) -> PersistenceObject:
        """
        Updates the specified object in the persistent storage.

        :raises ObjectNotFoundError: If the object could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError

    @abstractmethod
    async def read_one(self, query: PersistenceGetQuery) -> PersistenceObject:
        """
        Reads the specified object from the persistent storage.

        :raises ObjectNotFoundError: If the object could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError

    @abstractmethod
    async def read_many(
        self, query: PersistenceGetManyQuery
    ) -> PersistenceGetManyResult[PersistenceObject]:
        """
        Returns all specified objects from the persistent storage.

        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError
