from typing import Any

from guardian_authorization_api.udm_client import UnprocessableEntity


class MockUdmObject:
    def __init__(self, dn, properties):
        self.dn = dn
        self.properties = properties


class UDMModuleMock(dict):
    def get(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            raise UnprocessableEntity(0, "", None)


class UDMMock:
    def __init__(self, users: dict[str, Any] = None, groups: dict[str, Any] = None):
        if users is None:
            users = {}
        if groups is None:
            groups = {}
        self.modules = {
            "users/user": UDMModuleMock(users),
            "groups/group": UDMModuleMock(groups),
        }

    def get(self, module_name):
        # todo handle what happens if object is not found.
        return self.modules[module_name]
