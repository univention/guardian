from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Type

import loguru
from port_loader import AsyncAdapterSettingsProvider

from .errors import SettingFormatError, SettingTypeError
from .models.persistence import ObjectType, PersistenceObject
from .models.policies import (
    CheckPermissionsResult,
    Context,
    GetPermissionsResult,
    Namespace,
    Permission,
    Policy,
    PolicyObject,
    Target,
)
from .models.settings import SettingType


class BasePort(ABC):
    """
    Base class for all ports.
    """

    @property
    def logger(self) -> "loguru.Logger":
        return loguru.logger.bind()


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
        raise NotImplementedError


class SettingsPort(BasePort, AsyncAdapterSettingsProvider, ABC):
    """
    This port enables access to settings defined for the application.

    All adapters and application settings will be retrieved through this port. The only exception
    are the configuration of which adapters to initialize and potential settings the SettingsPort
    adapter itself might need.

    Any setting name is an alphanumeric sequence of characters, where '.', '_' and '-' are
    also allowed. The '.' character has special meaning and might be used by adapters to model
    object hierarchies or similar.

    Setting names are always case-insensitive. The implementing adapters might impose additional
    requirements on the adapter specific details, e.g. ENV variables must consist of capital letters.

    Notes for implementing adapters:
        - The code to fetch the settings should ideally be lazy loaded, if access to resources
          is required
        - The code to fetch settings should ideally be cached
    """

    @staticmethod
    def check_setting_name_format(setting_name: str):
        """
        Checks if setting_name is a valid setting name.

        Only [a-zA-Z0-9.-_] is allowed.

        :param setting_name: The setting name to check
        :raises SettingFormatError: If the setting name does not follow the defined format
        """
        check_str = setting_name.replace("-", "").replace("_", "").replace(".", "")
        if not check_str.isalnum():
            raise SettingFormatError(
                f"The requested setting '{setting_name}' does not follow the setting name format "
                f"and thus cannot be processed."
            )

    async def get_setting(
        self,
        setting_name: str,
        setting_type: Type[SettingType],
        default: Optional[SettingType] = None,
    ) -> SettingType:
        """
        This function returns a settings value.

        For the standard types str, int, float and bool please use the provided
        wrapper functions, as they might implement some special handling, that differs
        from the builtin methods for casting to those types.

        :param setting_name: The name of the setting to return
        :param setting_type: The type the setting should have.
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
                                  or the specified type is not supported
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        self.check_setting_name_format(setting_name)
        if setting_type is str:
            return await self.get_str(setting_name, default)  # type: ignore[return-value,arg-type]
        elif setting_type is bool:
            return await self.get_bool(setting_name, default)  # type: ignore[return-value,arg-type]
        elif setting_type is int:
            return await self.get_int(setting_name, default)  # type: ignore[return-value,arg-type]
        else:
            raise SettingTypeError(
                f"The requested setting type '{setting_type.__name__}' is not supported."
            )

    @abstractmethod
    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        """
        Returns the requested setting as an integer.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to an integer
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError

    @abstractmethod
    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        """
        Returns the requested setting as a string.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to a string
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError

    @abstractmethod
    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        """
        Returns the requested setting as a boolean.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to a boolean
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError


class PolicyPort(BasePort, ABC):
    """
    This port enables access to a policy evaluation agent such as OPA.
    """

    @abstractmethod
    async def check_permissions(
        self,
        actor: PolicyObject,
        targets: Optional[Iterable[Target]] = None,
        target_permissions: Optional[set[Permission]] = None,
        general_permissions: Optional[set[Permission]] = None,
        context: Optional[set[Context]] = None,
        extra_args: Optional[dict[str, Any]] = None,
    ) -> CheckPermissionsResult:
        """
        This method allows to check if an actor has the specified permissions,
        when acting on the specified targets.
        It also allows to query for general permissions, if acting on no particular target.

        :param actor: The actor to check the permissions for
        :param targets: The targets that are acted on
        :param target_permissions: The permissions to check regarding the targets
        :param general_permissions: The permissions to check with no regards to a particular target
        :param context: Additional contexts to pass to the policy evaluation agent
        :param extra_args: Additional arguments to pass to the policy evaluation agent
        :return: A result object detailing if the actor has the permissions regarding every target
        """
        raise NotImplementedError

    @abstractmethod
    async def get_permissions(
        self,
        actor: PolicyObject,
        targets: Optional[Iterable[Target]] = None,
        namespaces: Optional[Iterable[Namespace]] = None,
        contexts: Optional[Iterable[Context]] = None,
        extra_args: Optional[dict[str, Any]] = None,
        include_general_permissions: bool = False,
    ) -> GetPermissionsResult:
        """
        This method allows to retrieve all permissions an actor has
        when acting on the specified targets.

        :param actor: The actor to retrieve the permissions for
        :param targets: The targets that are acted on
        :param namespaces: A list of namespaces used to restrict the permissions contained in the result
        :param contexts: Additional contexts to pass to the policy evaluation agent
        :param extra_args: Additional arguments to pass to the policy evaluation agent
        :param include_general_permissions: If True the result will contain a list of permissions
                                            the actor has if acting on no particular target
        :return: A result object containing the permissions the actor has regarding every target
        """
        raise NotImplementedError

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
        raise NotImplementedError
