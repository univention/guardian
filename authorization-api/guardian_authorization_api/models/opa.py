from dataclasses import dataclass
from typing import Any, Optional

from ..models.policies import PolicyObject


@dataclass(frozen=True)
class OPAPermission:
    appName: str
    namespace: str
    permission: str


@dataclass(frozen=True)
class OPAPolicyObject:
    id: str
    roles: list[str]
    attributes: dict[str, Any]

    @classmethod
    def from_policy_object(cls, obj: PolicyObject) -> "OPAPolicyObject":
        return OPAPolicyObject(
            roles=[
                f"{role.app_name}:{role.namespace_name}:{role.name}"
                for role in obj.roles
            ],
            id=obj.id,
            attributes=obj.attributes,
        )


@dataclass(frozen=True)
class OPATarget:
    old_target: Optional[OPAPolicyObject]
    new_target: Optional[OPAPolicyObject]
