from typing import Any

from guardian_authorization_api.udm_client import UnprocessableEntity


class MockUdmObject:
    def __init__(self, dn, properties):
        self.dn = dn
        self.properties = properties


class MockUDMModule(dict):
    def get(self, key, properties=None):
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
            "users/user": MockUDMModule(users),
            "groups/group": MockUDMModule(groups),
        }

    def get(self, module_name):
        return self.modules[module_name]
