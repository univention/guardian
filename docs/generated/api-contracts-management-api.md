# API Contracts -- Management API

**Date:** 2026-03-29
**Base Path:** `/guardian/management` (configurable via `GUARDIAN__MANAGEMENT__API_PREFIX`)
**Authentication:** All endpoints require OAuth2 bearer token (configurable via adapter)
**Authorization:** Per-resource ABAC via `ResourceAuthorizationPort` (configurable: `always`, `never`, `guardian`)
**Response Format:** JSON (ORJSONResponse)

---

## App Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/apps/{name}` | Path: `name` | `AppSingleResponse` | 200 | Get single app by name |
| GET | `/apps` | Query: `offset`, `limit` | `AppMultipleResponse` | 200 | List all apps (paginated, authz-filtered) |
| POST | `/apps` | Body: `name`, `display_name` | `AppSingleResponse` | 201 | Create app |
| POST | `/apps/register` | Body: `name`, `display_name` | `AppRegisterResponse` | 201 | Register app (creates app + default namespace + admin role + 2 capabilities) |
| PATCH | `/apps/{name}` | Path: `name`, Body: `display_name` | `AppSingleResponse` | 200 | Update app display name |

**Register app** creates: the app, a "default" namespace, an "app-admin" role, a CRUD capability with `target_field_equals_value` condition, and a read capability for roles/conditions.

---

## Namespace Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/namespaces/{app_name}/{name}` | Path: `app_name`, `name` | `NamespaceSingleResponse` | 200 | Get single namespace |
| GET | `/namespaces` | Query: `offset`, `limit` | `NamespaceMultipleResponse` | 200 | List all namespaces |
| GET | `/namespaces/{app_name}` | Path: `app_name`, Query: `offset`, `limit` | `NamespaceMultipleResponse` | 200 | List namespaces by app |
| POST | `/namespaces/{app_name}` | Path: `app_name`, Body: `name`, `display_name` | `NamespaceSingleResponse` | 201 | Create namespace |
| PATCH | `/namespaces/{app_name}/{name}` | Path: `app_name`, `name`, Body: `display_name` | `NamespaceSingleResponse` | 201 | Update namespace |

---

## Role Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/roles/{app_name}/{namespace_name}/{name}` | Path: 3-part identifier | `RoleSingleResponse` | 200 | Get single role |
| GET | `/roles` | Query: `offset`, `limit` | `RoleMultipleResponse` | 200 | List all roles |
| GET | `/roles/{app_name}` | Path: `app_name`, Query: pagination | `RoleMultipleResponse` | 200 | List roles by app |
| GET | `/roles/{app_name}/{namespace_name}` | Path: 2-part, Query: pagination | `RoleMultipleResponse` | 200 | List roles by namespace |
| POST | `/roles/{app_name}/{namespace_name}` | Path: 2-part, Body: `name`, `display_name` | `RoleSingleResponse` | 201 | Create role |
| PATCH | `/roles/{app_name}/{namespace_name}/{name}` | Path: 3-part, Body: `display_name` | `RoleSingleResponse` | 200 | Update role |

---

## Permission Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/permissions/{app_name}/{namespace_name}/{name}` | Path: 3-part | `PermissionSingleResponse` | 200 | Get single permission |
| GET | `/permissions` | Query: pagination | `PermissionMultipleResponse` | 200 | List all permissions |
| GET | `/permissions/{app_name}` | Path: `app_name`, Query: pagination | `PermissionMultipleResponse` | 200 | List by app |
| GET | `/permissions/{app_name}/{namespace_name}` | Path: 2-part, Query: pagination | `PermissionMultipleResponse` | 200 | List by namespace |
| POST | `/permissions/{app_name}/{namespace_name}` | Path: 2-part, Body: `name`, `display_name` | `PermissionSingleResponse` | 201 | Create permission |
| PATCH | `/permissions/{app_name}/{namespace_name}/{name}` | Path: 3-part, Body: `display_name` | `PermissionSingleResponse` | 200 | Update permission |

---

## Condition Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/conditions/{app_name}/{namespace_name}/{name}` | Path: 3-part | `ConditionSingleResponse` | 200 | Get single condition |
| GET | `/conditions` | Query: pagination | `ConditionMultipleResponse` | 200 | List all conditions |
| GET | `/conditions/{app_name}` | Path: `app_name`, Query: pagination | `ConditionMultipleResponse` | 200 | List by app |
| GET | `/conditions/{app_name}/{namespace_name}` | Path: 2-part, Query: pagination | `ConditionMultipleResponse` | 200 | List by namespace |
| POST | `/conditions/{app_name}/{namespace_name}` | Path: 2-part, Body: `name`, `display_name`, `documentation`, `code` (base64), `parameters[]` | `ConditionSingleResponse` | 201 | Create condition |
| PATCH | `/conditions/{app_name}/{namespace_name}/{name}` | Path: 3-part, Body: `display_name`, `documentation`, `code`, `parameters[]` | `ConditionSingleResponse` | 200 | Update condition |

**Side effect:** Create and update trigger `schedule_bundle_build(BundleType.policies)`.

---

## Context Endpoints

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/contexts/{app_name}/{namespace_name}/{name}` | Path: 3-part | `ContextSingleResponse` | 200 | Get single context |
| GET | `/contexts` | Query: pagination | `ContextMultipleResponse` | 200 | List all contexts |
| GET | `/contexts/{app_name}` | Path: `app_name`, Query: pagination | `ContextMultipleResponse` | 200 | List by app |
| GET | `/contexts/{app_name}/{namespace_name}` | Path: 2-part, Query: pagination | `ContextMultipleResponse` | 200 | List by namespace |
| POST | `/contexts/{app_name}/{namespace_name}` | Path: 2-part, Body: `name`, `display_name` | `ContextSingleResponse` | 201 | Create context |
| PATCH | `/contexts/{app_name}/{namespace_name}/{name}` | Path: 3-part, Body: `display_name` | `ContextSingleResponse` | 200 | Update context |

---

## Capability Endpoints

Capabilities are the **only entity** that uses PUT (full replacement) for updates and the **only entity** with a DELETE endpoint.

| Method | Path | Request | Response | Status | Description |
|--------|------|---------|----------|--------|-------------|
| GET | `/capabilities/{app_name}/{namespace_name}/{name}` | Path: 3-part | `CapabilitySingleResponse` | 200 | Get single capability |
| GET | `/capabilities/{app_name}/{namespace_name}` | Path: 2-part, Query: pagination | `CapabilityMultipleResponse` | 200 | List by namespace |
| GET | `/capabilities` | Query: pagination | `CapabilityMultipleResponse` | 200 | List all |
| GET | `/roles/{app_name}/{namespace_name}/{name}/capabilities` | Path: 3-part (role), Query: pagination | `CapabilityMultipleResponse` | 200 | List capabilities by role |
| POST | `/capabilities/{app_name}/{namespace_name}` | Path: 2-part, Body: `name` (optional, auto-generated), `display_name`, `role`, `conditions[]`, `relation`, `permissions[]` | `CapabilitySingleResponse` | 201 | Create capability |
| PUT | `/capabilities/{app_name}/{namespace_name}/{name}` | Path: 3-part, Body: `role`, `conditions[]`, `relation`, `permissions[]` | `CapabilitySingleResponse` | 200 | Replace capability (full replacement) |
| DELETE | `/capabilities/{app_name}/{namespace_name}/{name}` | Path: 3-part | -- | 204 | Delete capability |

**Side effect:** Create, update, and delete trigger `schedule_bundle_build(BundleType.data)`.

**Validation:** All permissions in a capability must be in the same namespace as the capability itself (`check_permissions_in_namespace` model validator).

**Capability body structure:**

```json
{
  "name": "optional-auto-generated",
  "display_name": "My Capability",
  "role": {"app_name": "myapp", "namespace_name": "myns", "name": "myrole"},
  "conditions": [
    {
      "app_name": "guardian", "namespace_name": "builtin", "name": "target_is_self",
      "parameters": [{"name": "field", "value": "uid", "value_type": "STRING"}]
    }
  ],
  "relation": "AND",
  "permissions": [
    {"app_name": "myapp", "namespace_name": "myns", "name": "read_first_name"}
  ]
}
```

---

## Custom Endpoint (Stub)

**Status:** NOT IMPLEMENTED -- returns hardcoded dummy data, no business logic, no persistence, no auth.

| Method | Path |
|--------|------|
| GET | `/custom_endpoints/{app_name}/{namespace_name}/{name}` |
| GET | `/custom_endpoints` |
| GET | `/custom_endpoints/{app_name}` |
| GET | `/custom_endpoints/{app_name}/{namespace_name}` |
| POST | `/custom_endpoints/{app_name}/{namespace_name}` |
| PATCH | `/custom_endpoints/{app_name}/{namespace_name}/{name}` |

---

## Bundle Server Endpoints

| Method | Path | Response | Description |
|--------|------|----------|-------------|
| GET | `/bundles/GuardianDataBundle.tar.gz` | Binary tar.gz | OPA data bundle (role-capability mappings) |
| GET | `/bundles/GuardianPolicyBundle.tar.gz` | Binary tar.gz | OPA policy bundle (Rego code + conditions) |

Bundles are rebuilt asynchronously when capabilities/conditions are created/updated/deleted.

---

## Error Responses

| HTTP Status | Domain Exception | Detail |
|-------------|-----------------|--------|
| 400 | `ObjectExistsError` | "An object with the given identifiers already exists." |
| 403 | `UnauthorizedError` | "Not allowed." |
| 404 | `ObjectNotFoundError` / `ParentNotFoundError` | Descriptive message |
| 422 | `ValidationError` | Pydantic validation details |
| 500 | Any other | "Internal Server Error" |

## Pagination

All list endpoints support:

- `offset` (query param, default: 0)
- `limit` (query param, optional)

Responses include `pagination` object: `{"offset": 0, "limit": 50, "total_count": 123}`.

---

## Name Validation

All entity names must match: `^[a-z][a-z0-9\-_]*$` (lowercase, starts with letter, min 1, max 256 chars).

---

## Total

44 implemented endpoints + 6 stub endpoints = 50 routes

---
