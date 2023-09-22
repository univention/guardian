# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
import re
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, PersistenceError
from ..models.persistence import (
    ObjectType,
    PersistenceObject,
    StaticDataAdapterSettings,
    UDMPersistenceAdapterSettings,
)
from ..models.policies import PolicyObject
from ..models.policies import Role as PoliciesRole
from ..ports import PersistencePort
from ..udm_client import (  # type: ignore[attr-defined]
    UDM,
    NotFound,
    Object,
    Unauthorized,
    UnprocessableEntity,
)
from ..udm_client import (  # type: ignore[attr-defined]
    ConnectionError as UDMConnectionError,
)

re_split_roles_and_contexts = re.compile(
    r"^(([a-z0-9-_]+):([a-z0-9-_]+):([a-z0-9-_]+))(&([a-z0-9-_]+):([a-z0-9-_]+):([a-z0-9-_]+))?$"
)


class UDMPersistenceAdapter(PersistencePort, AsyncConfiguredAdapterMixin):
    """
    This adapter for the data storage queries a UDM REST API for the required objects.

    It expects the identifier of objects to be their DN in UDM.
    """

    class Config:
        is_cached = True
        alias = "udm_data"

    TYPE_MODULE_MAPPING = {
        ObjectType.GROUP: "groups/group",
        ObjectType.USER: "users/user",
    }

    def __init__(self):
        self._settings = None
        self._udm_client = None

    @property
    def udm_client(self):
        if self._udm_client is None:
            self._udm_client = UDM(
                self._settings.url, self._settings.username, self._settings.password
            )
        return self._udm_client

    async def configure(self, settings: UDMPersistenceAdapterSettings):
        self._settings = settings

    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        module_name = self.TYPE_MODULE_MAPPING.get(object_type, "")
        local_logger = self.logger.bind(
            module_name=module_name, identifier=identifier, object_type=object_type
        )
        local_logger.debug("Fetching object from UDM.")
        if not module_name:
            raise PersistenceError(
                f"The object type '{object_type.name}' is not supported by {self.__class__.__name__}."
            )
        try:
            module = self.udm_client.get(module_name)
        except (NotFound, UDMConnectionError) as exc:
            raise PersistenceError(
                f"The UDM at '{self._settings.url}' could not be reached."
            ) from exc
        except Unauthorized as exc:
            raise PersistenceError(
                f"Could not authorize against UDM at '{self._settings.url}'."
            ) from exc
        except Exception as exc:
            raise PersistenceError(
                "An unexpected error occurred while fetching data from UDM."
            ) from exc
        try:
            raw_object: Object = module.get(identifier)
        except (UnprocessableEntity, NotFound) as exc:
            raise ObjectNotFoundError(
                f"Could not find object of type '{object_type.name}' with identifier '{identifier}'."
            ) from exc
        result = PersistenceObject(
            id=raw_object.dn,
            object_type=object_type,
            attributes=raw_object.properties,
            roles=raw_object.properties.get("guardianRole", []),
        )
        local_logger.debug("Object retrieved from UDM.")
        return result

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[UDMPersistenceAdapterSettings]:  # pragma: no cover
        return UDMPersistenceAdapterSettings

    @staticmethod
    def _to_policy_role(role: str):
        if res := re.search(re_split_roles_and_contexts, role):
            groups = res.groups()
            role_app = groups[1]
            role_namespace = groups[2]
            role_name = groups[3]
            # fixme: add context support
            # if len(groups) == 8:
            #     context = PoliciesContext(
            #         name=groups[7], app_name=groups[5], namespace_name=groups[6]
            #     )
            return PoliciesRole(
                app_name=role_app,
                namespace_name=role_namespace,
                name=role_name,
            )
        raise PersistenceError(f"Role {role} is malformed.")

    @staticmethod
    def _to_policy_object(po: PersistenceObject) -> PolicyObject:
        # todo in opa adapter include context in role
        roles = []
        for role in po.roles:
            roles.append(UDMPersistenceAdapter._to_policy_role(role))
        if "guardianRole" in po.attributes:
            po.attributes.pop("guardianRole")
        return PolicyObject(id=po.id, roles=roles, attributes=po.attributes)

    async def lookup_actor_and_old_targets(
        self, actor_id: str, old_target_ids: list[str | None]
    ) -> tuple[PolicyObject, list[PolicyObject | None]]:
        actor = UDMPersistenceAdapter._to_policy_object(
            await self.get_object(identifier=actor_id, object_type=ObjectType.USER)
        )
        old_targets = []
        for old_target_id in old_target_ids:
            # In the context of the UDMPersistenceAdapter the IDs are equal to distinguished names
            obj = None
            if old_target_id:
                if old_target_id.startswith("cn"):
                    # Three remarks:
                    # 1. This can match other, but not yet supported targets like shares and computers.
                    #    In that case, we will get an error when looking up the object.
                    # 2. It is possible that a group DN does not contain 'cn=groups'
                    #    as UCS supports changing the default groups container, so we cannot determine
                    #    the group object type via `'cn=groups' in  old_target_id`
                    # 3. We might want to use the method `obj_by_dn` from the udm client instead of
                    #    instantiating the different object modules
                    object_type = ObjectType.GROUP
                elif old_target_id.startswith("uid"):
                    object_type = ObjectType.USER
                else:
                    raise PersistenceError(
                        f"Cannot determine object type from DN: {old_target_id}"
                    )
                obj = UDMPersistenceAdapter._to_policy_object(
                    await self.get_object(
                        identifier=old_target_id, object_type=object_type
                    )
                )
            old_targets.append(obj)

        return actor, old_targets


class StaticDataAdapter(PersistencePort, AsyncConfiguredAdapterMixin):
    """
    This adapter for the PersistencePort implements a data store that is held in memory and
    seeded by a json file that is loaded from the path configured by 'static_data_adapter.data_file'.

    This adapter is not meant for production but rather for testing purposes.
    """

    async def lookup_actor_and_old_targets(
        self, actor_id: str, old_target_ids: list[str | None]
    ) -> tuple[PolicyObject, list[PolicyObject | None]]:  # pragma: no cover
        # fix me with https://git.knut.univention.de/univention/components/authorization-engine/guardian/-/issues/139
        return (
            PolicyObject(
                id="non-existent",
                roles=[
                    PoliciesRole(
                        app_name="app", namespace_name="namespace", name="role"
                    )
                ],
                attributes={},
            ),
            [],
        )

    class Config:
        is_cached = True
        alias = "static_data"

    @classmethod
    def get_settings_cls(cls) -> Type[StaticDataAdapterSettings]:
        return StaticDataAdapterSettings

    async def configure(self, settings: StaticDataAdapterSettings):
        self._load_static_data(settings.data_file_path)

    def __init__(self):
        self._users = dict()
        self._groups = dict()

    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        if object_type == ObjectType.USER:
            raw_object = self._users.get(identifier, None)
        elif object_type == ObjectType.GROUP:
            raw_object = self._groups.get(identifier, None)
        else:
            raise PersistenceError(
                f"The object type {object_type.name} is not supported by {self.__class__.__name__}."
            )
        if raw_object is None:
            raise ObjectNotFoundError(
                f"The {object_type.name} with the identifier '{identifier}' could not be found."
            )
        attributes = raw_object.get("attributes", {})
        if type(attributes) != dict:
            raise PersistenceError(
                f"The data of the object with type '{object_type.name}' and identifier "
                f"'{identifier}' is malformed and could not be loaded."
            )
        return PersistenceObject(
            object_type=object_type,
            id=identifier,
            attributes=attributes,
            roles=attributes.get("roles", []),
        )

    def _load_static_data(self, data_file_path: str):
        """
        No good error handling here, since this is a dev-adapter and all exceptions
        are caught outside, when configuring.

        If we ever evolve this Adapter to production quality this has to change of course.
        """
        with open(data_file_path, "r") as fp:
            data = json.load(fp)
        self._users = data.get("users", {})
        self._groups = data.get("groups", {})
        if type(self._users) != dict or type(self._groups) != dict:
            raise RuntimeError("The json file did not contain the correct data.")
