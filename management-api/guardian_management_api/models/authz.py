from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class OperationType(StrEnum):
    READ_RESOURCE = "read_resource"
    CREATE_RESOURCE = "create_resource"
    UPDATE_RESOURCE = "update_resource"
    DELETE_RESOURCE = "delete_resource"


class ResourceType(StrEnum):
    APP = "app"
    NAMESPACE = "namespace"
    ROLE = "role"
    CONTEXT = "context"
    PERMISSION = "permission"
    CONDITION = "condition"
    CAPABILITY = "capability"


@dataclass
class Actor:
    id: str


@dataclass
class Resource:
    resource_type: ResourceType
    name: str
    app_name: Optional[str] = None
    namespace_name: Optional[str] = None

    @property
    def id(self):
        if self.resource_type == ResourceType.APP:
            return self.name
        elif self.resource_type == ResourceType.NAMESPACE:
            return f"{self.app_name}:{self.name}"
        else:
            return f"{self.app_name}:{self.namespace_name}:{self.name}"
