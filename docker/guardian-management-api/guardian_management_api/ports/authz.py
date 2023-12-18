from abc import ABC, abstractmethod

from guardian_lib.ports import BasePort

from guardian_management_api.models.authz import (
    Actor,
    OperationType,
    Resource,
)


class ResourceAuthorizationPort(BasePort, ABC):
    @abstractmethod
    async def authorize_operation(
        self, actor: Actor, operation_type: OperationType, resources: list[Resource]
    ) -> dict[str, bool]:
        """
        Method to check if an operation is permitted on a list of resources.

        :raises AuthorizationError: If there was an unhandled error during authorization
        """
