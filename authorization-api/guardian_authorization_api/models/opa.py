# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from typing import Any, Optional, Self

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
    def from_policy_object(cls, obj: PolicyObject) -> Self:
        return cls(
            roles=[f"{role}" for role in obj.roles],
            id=obj.id,
            attributes=obj.attributes,
        )


@dataclass(frozen=True)
class OPATarget:
    old_target: Optional[OPAPolicyObject]
    new_target: Optional[OPAPolicyObject]
