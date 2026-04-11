# Data Models -- Authorization API

**Date:** 2026-03-29
**Persistence:** UDM REST API (Univention Directory Manager) -- no local database
**Policy Engine:** OPA (Open Policy Agent) via `opa-client` library

---

## Overview

The authorization-api does not maintain its own database. It operates with four model layers that translate data between the HTTP boundary, domain logic, the UDM data store, and OPA:

1. **Route models** (`models/routes.py`) -- Pydantic BaseModel classes for HTTP serialization
2. **Domain models** (`models/policies.py`) -- Frozen dataclasses for business logic
3. **Persistence models** (`models/persistence.py`) -- Dataclasses for UDM object representation
4. **OPA models** (`models/opa.py`) -- Frozen dataclasses with camelCase fields for OPA wire format

---

## Route Models (HTTP Layer)

### Core Types

| Type | Constraint | Description |
|------|-----------|-------------|
| `AuthzObjectIdentifier` | str, min_length=3 | Entity identifier (typically a DN) |
| `AppName` | str, pattern=`^[a-z][a-z0-9\-]*$`, min_length=3 | Application name |
| `NamespaceName` | str, pattern=`^[a-z][a-z0-9\-]*$`, min_length=3 | Namespace name |
| `ContextName` | str, min_length=3 | Context name |
| `PermissionName` | str, min_length=3 | Permission name |

### Request/Response Object Hierarchy

| Model | Fields | Usage |
|-------|--------|-------|
| `AuthzObject` | `id`, `roles[]`, `attributes{}` | Full actor/target with all data |
| `AuthzObjectLookup` | `id` | Reference to look up from UDM |
| `Actor(AuthzObject)` | (inherits) | Actor in direct requests |
| `ActorLookup(AuthzObjectLookup)` | (inherits) | Actor in lookup requests |
| `Role` | `app_name`, `namespace_name`, `name`, `context?` | Role with optional context |
| `Context` | `app_name`, `namespace_name`, `name` | Scoping context |
| `Permission` | `app_name`, `namespace_name`, `name` | Permission identifier |
| `NamespaceMinimal` | `app_name`, `name` | Namespace filter |
| `Target` | `old_target: AuthzObject?`, `new_target: AuthzObject?` | Direct target |
| `TargetLookup` | `old_target: AuthzObjectLookup?`, `new_target: AuthzObject?` | Target with old state looked up |

---

## Domain Models (Policy Layer)

All frozen dataclasses. Used by business logic and port interfaces.

| Model | Fields | Description |
|-------|--------|-------------|
| `NamespacedValue` | `app_name`, `namespace_name`, `name` | Base for namespaced entities; `__str__` returns `app:ns:name` |
| `Permission(NamespacedValue)` | (inherits) | Permission identifier |
| `Context(NamespacedValue)` | (inherits) | Context identifier |
| `Role(NamespacedValue)` | + `context: Context?` | Role; `__str__` returns `app:ns:name` or `app:ns:name&ctx_app:ctx_ns:ctx_name` |
| `Policy(NamespacedValue)` | (inherits) | Custom policy reference |
| `Namespace` | `app_name`, `name` | Namespace for filtering |
| `PolicyObject` | `id`, `roles: list[Role]`, `attributes: dict` | Actor or target for policy evaluation |
| `Target` | `old_target: PolicyObject?`, `new_target: PolicyObject?` | Wraps old/new target states |

### Query Objects

| Model | Fields |
|-------|--------|
| `GetPermissionsQuery` | `actor`, `targets?`, `namespaces?`, `contexts?`, `extra_args?`, `include_general_permissions` |
| `CheckPermissionsQuery` | `actor`, `targets?`, `namespaces?`, `target_permissions?`, `general_permissions?`, `contexts?`, `extra_args?` |

### Result Objects

| Model | Fields |
|-------|--------|
| `TargetPermissions` | `target_id`, `permissions: list[Permission]` |
| `GetPermissionsResult` | `actor`, `target_permissions[]`, `general_permissions?` |
| `CheckResult` | `target_id`, `actor_has_permissions: bool` |
| `CheckPermissionsResult` | `target_permissions: list[CheckResult]`, `actor_has_general_permissions?` |

---

## Persistence Models (UDM Layer)

| Model | Fields | Description |
|-------|--------|-------------|
| `ObjectType` (Enum) | `USER=0`, `GROUP=1`, `UNKNOWN=2` | UDM object type classification |
| `PersistenceObject` | `id`, `object_type`, `attributes: dict`, `roles: list[str]` | Raw object from UDM |

### UDM Object Type Mapping

| ObjectType | UDM Module | DN Prefix Detection |
|------------|-----------|-------------------|
| `USER` | `users/user` | DN starts with `uid=` |
| `GROUP` | `groups/group` | DN starts with `cn=` |
| `UNKNOWN` | (not supported) | Raises `PersistenceError` |

### Role Handling

UDM objects have two role properties:
- `guardianRoles`: Directly assigned roles
- `guardianInheritedRoles`: Roles inherited from group membership

The adapter **merges both** (set union, deduplicated) into the `PersistenceObject.roles` list and removes both properties from `attributes`.

Role strings are parsed via regex:

```text
^(app:namespace:name)(&context_app:context_namespace:context_name)?$
```

---

## OPA Models (Wire Format)

Field names use **camelCase** to match OPA's expected input format.

| Model | Fields | Description |
|-------|--------|-------------|
| `OPAPermission` | `appName`, `namespace`, `permission` | Permission in OPA format |
| `OPAPolicyObject` | `id`, `roles: list[str]`, `attributes: dict` | Actor/target for OPA; roles serialized as strings |
| `OPATarget` | `old_target: OPAPolicyObject?`, `new_target: OPAPolicyObject?` | Target pair |

`OPAPolicyObject.from_policy_object(obj)` converts domain `PolicyObject` to OPA format by stringifying roles via `Role.__str__()`.

### Empty Target Sentinel

```python
EMPTY_TARGET = OPATarget(
    old_target=OPAPolicyObject(id="", attributes={}, roles=[]),
    new_target=OPAPolicyObject(id="", attributes={}, roles=[]),
)
```

Used for general permission queries. OPA results with `target_id == ""` are interpreted as general (non-target-specific) permissions.

---

## Data Flow

### Direct Request

```text
HTTP Request (Pydantic route model)
  -> API Adapter: route model -> domain query
    -> OPA Adapter: domain query -> OPA input (camelCase)
      -> OPA evaluates Rego policies
    <- OPA Adapter: OPA response -> domain result
  <- API Adapter: domain result -> Pydantic response
```

### Lookup Request

```text
HTTP Request (Pydantic route model)
  -> API Adapter: extract actor_id + target_ids
    -> UDM Adapter: fetch PersistenceObjects from UDM REST API
    -> UDM Adapter: parse roles, convert to PolicyObjects
  -> API Adapter: build domain query with looked-up data
    -> OPA Adapter: domain query -> OPA evaluation
  <- API Adapter: domain result -> Pydantic response
```

---

_Generated using BMAD Method `document-project` workflow, Step 4_
