from enum import StrEnum
from typing import Optional

from fastapi import APIRouter
from pydantic import Field

from guardian_management_api.models.routers.base import (
    GuardianBaseModel,
    NamespacedObjectMixin,
)

router = APIRouter(tags=["capability"])


class MappingRole(GuardianBaseModel):
    app_name: str = "app"
    namespace_name: str = "namespace"
    name: str = "role"


class MappingPermission(GuardianBaseModel):
    app_name: str = "app"
    namespace_name: str = "namespace"
    name: str = "role"


class MappingCondition(GuardianBaseModel, NamespacedObjectMixin):
    app_name: str = "app"
    namespace_name: str = "namespace"
    name: str = "condition"
    parameters: dict[str, str | bool | int | float] = Field(
        {"a": 1, "b": True},
        description="The preset parameter values for the condition.",
    )


class RelationChoices(StrEnum):
    AND = "AND"
    OR = "OR"


class Capability(GuardianBaseModel):
    app_name: str = "app"
    namespace_name: str = "namespace"
    name: str = "387956"
    role: MappingRole = MappingRole()
    conditions: list[MappingCondition] = [MappingCondition()]
    relation: RelationChoices = RelationChoices.AND
    permissions: list[MappingPermission] = [MappingPermission()]


class CreateCapability(GuardianBaseModel):
    name: Optional[str] = None  # GENERATED str(UUID)
    role: MappingRole = MappingRole()
    conditions: list[MappingCondition] = [MappingCondition()]
    relation: RelationChoices = RelationChoices.AND
    permissions: list[MappingPermission] = [MappingPermission()]


class PutCapability(GuardianBaseModel):
    role: MappingRole = MappingRole()
    conditions: list[MappingCondition] = [MappingCondition()]
    relation: RelationChoices = RelationChoices.AND
    permissions: list[MappingPermission] = [MappingPermission()]


class ManyCapabilities(GuardianBaseModel):
    capabilities: list[Capability] = [Capability(), Capability()]


@router.get("/capabilities/{app_name}/{namespace_name}/{:name}")
def get_capability(app_name: str, namespace_name: str, name: str):
    return Capability()


@router.get("/capabilities/{app_name}/{namespace_name}")
def get_capability(app_name: str, namespace_name: str):
    return ManyCapabilities()


@router.get("/capabilities/role/{app_name}/{namespace_name}/{:role_name}")
def get_capability(app_name: str, namespace_name: str, role_name: str):
    return ManyCapabilities()


@router.get("/capabilities")
def all_capabilities():
    return ManyCapabilities()


@router.post("/capabilities/{app_name}/{namespace_name}")
def create_capability(new_cap: CreateCapability):
    return Capability()


@router.put("/capabilities/{app_name}/{namespace_name}/{name}")
def create_capability(new_cap: PutCapability):
    return Capability()


@router.delete("/capabilities/{app_name}/{namespace_name}/{:uuid}")
def create_capability():
    return Capability()
