from faker import Faker

fake = Faker()


def get_authz_permission_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_context_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_roles_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_object_dict(id=None, n_roles=3, n_attributes=3) -> dict:
    return {
        "id": id if id else fake.unique.pystr(),
        "roles": [get_authz_roles_dict() for _ in range(n_roles)],
        "attributes": fake.pydict(n_attributes, value_types=[int, str]),
    }


def get_target_dict(id=None) -> dict:
    if id is None:
        return {
            "old_target": get_authz_object_dict(),
            "new_target": get_authz_object_dict(),
        }
    else:
        return {
            "old_target": get_authz_object_dict(id=id),
            "new_target": get_authz_object_dict(id=id),
        }


def get_namespace_dict() -> dict:
    return {"app_name": fake.pystr(), "name": fake.pystr()}


def get_authz_permissions_check_request_dict(
    n_actor_roles=3,
    n_namespaces=3,
    n_targets=3,
    n_context=3,
    n_extra_request_data=3,
    n_general_permissions=3,
    n_permissions=3,
) -> dict:
    return {
        "namespaces": [get_namespace_dict() for _ in range(n_namespaces)],
        "actor": get_authz_object_dict(n_roles=n_actor_roles),
        "targets": [get_target_dict() for _ in range(n_targets)],
        "contexts": [get_authz_context_dict() for _ in range(n_context)],
        "permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_permissions)
        ],
        "general_permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_general_permissions)
        ],
        "extra_request_data": fake.pydict(n_extra_request_data, value_types=[str, int]),
    }
