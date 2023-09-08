# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC
from typing import Union

from guardian_management_api.models.capability import (
    CapabilitiesByRoleQuery,
    CapabilitiesGetQuery,
    Capability,
    CapabilityGetQuery,
)
from guardian_management_api.ports.base import BasePersistencePort


class CapabilityPersistencePort(
    BasePersistencePort[
        Capability,
        CapabilityGetQuery,
        Union[CapabilitiesGetQuery, CapabilitiesByRoleQuery],
    ],
    ABC,
):
    async def delete(self, query: CapabilityGetQuery) -> None:
        """
        Deletes the specified object from the persistent storage.

        :raises ObjectNotFoundError: If the object could not be found.
        :raises PersistenceError: For any other error during interaction with the persistence.
        """
        raise NotImplementedError  # pragma: no cover
