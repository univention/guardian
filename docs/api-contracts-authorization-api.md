# API Contracts -- Authorization API

**Date:** 2026-03-29
**Base Path:** `/guardian/authorization` (configurable via `GUARDIAN__AUTHZ__API_PREFIX`)
**Authentication:** All endpoints require OAuth2 bearer token (configurable via adapter)
**Response Format:** JSON (ORJSONResponse)
**Correlation ID:** All requests receive an `X-Request-ID` response header (from request header or auto-generated UUID4)

---

## Get Permissions (Direct)

**POST** `/permissions`

Caller supplies full actor and target objects. No data store lookup.

**Request body:**

```json
{
  "actor": {
    "id": "uid=teacher1,dc=example,dc=com",
    "roles": [
      {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher",
       "context": {"app_name": "ucsschool", "namespace_name": "users", "name": "school1"}}
    ],
    "attributes": {"firstName": "John"}
  },
  "targets": [
    {
      "old_target": {"id": "uid=student1,dc=example,dc=com", "roles": [...], "attributes": {...}},
      "new_target": null
    }
  ],
  "namespaces": [{"app_name": "ucsschool", "name": "users"}],
  "contexts": [{"app_name": "ucsschool", "namespace_name": "users", "name": "school1"}],
  "include_general_permissions": false,
  "extra_request_data": {}
}
```

**Response (200):**

```json
{
  "actor_id": "uid=teacher1,dc=example,dc=com",
  "general_permissions": [],
  "target_permissions": [
    {
      "target_id": "uid=student1,dc=example,dc=com",
      "permissions": [
        {"app_name": "ucsschool", "namespace_name": "users", "name": "read_first_name"}
      ]
    }
  ]
}
```

---

## Get Permissions (With Lookup)

**POST** `/permissions/with-lookup`

Guardian resolves actor and old targets from the UDM data store. New targets can still be supplied directly.

**Request body:**

```json
{
  "actor": {"id": "uid=teacher1,dc=example,dc=com"},
  "targets": [
    {"old_target": {"id": "uid=student1,dc=example,dc=com"}, "new_target": null}
  ],
  "namespaces": null,
  "contexts": null,
  "include_general_permissions": true,
  "extra_request_data": {}
}
```

Targets support **hybrid mode**: some targets can have `old_target` as a full `AuthzObject` (no lookup) while others have `old_target` as an `AuthzObjectLookup` (ID only, looked up from UDM).

**Response (200):** Same structure as direct endpoint.

---

## Check Permissions (Direct)

**POST** `/permissions/check`

Checks whether the actor has specific permissions for the given targets.

**Request body:**

```json
{
  "actor": {"id": "...", "roles": [...], "attributes": {...}},
  "targets": [{"old_target": {...}, "new_target": null}],
  "namespaces": null,
  "contexts": null,
  "extra_request_data": {},
  "targeted_permissions_to_check": [
    {"app_name": "ucsschool", "namespace_name": "users", "name": "read_first_name"}
  ],
  "general_permissions_to_check": []
}
```

**Response (200):**

```json
{
  "actor_id": "uid=teacher1,dc=example,dc=com",
  "permissions_check_results": [
    {"target_id": "uid=student1,dc=example,dc=com", "actor_has_permissions": true}
  ],
  "actor_has_all_general_permissions": true,
  "actor_has_all_targeted_permissions": true
}
```

**Note:** `actor_has_all_targeted_permissions` is computed as `all(result.actor_has_permissions for result in permissions_check_results)`. Defaults to `false` if no target permissions exist.

---

## Check Permissions (With Lookup)

**POST** `/permissions/check/with-lookup`

Same as check-permissions but actor and old targets are resolved from UDM.

**Request body:** Same structure as get-permissions-with-lookup but with additional `targeted_permissions_to_check` and `general_permissions_to_check` fields.

**Response (200):** Same as check-permissions direct.

---

## Custom Policy Endpoint (NOT IMPLEMENTED)

**POST** `/permissions/custom/{app_name}/{namespace_name}/{endpoint_name}`

Placeholder for custom policy queries. Currently raises `NotImplementedError`.

---

## OPA Communication Details

The authorization-api communicates with OPA via two policy paths:

| Operation | OPA Path | OPA Makes |
|-----------|----------|-----------|
| Get permissions | `/v1/data/univention/base/get_permissions` | 1 call |
| Check permissions | `/v1/data/univention/base/check_permissions` | Up to 2 calls (targeted + general) |

**General permissions pattern:** An empty target sentinel (empty ID, attributes, roles) is appended to the targets list. OPA results for `target_id == ""` are interpreted as general permissions.

---

## Error Responses

| HTTP Status | Domain Exception | Detail |
|-------------|-----------------|--------|
| 404 | `ObjectNotFoundError` | Actor or target not found in UDM |
| 422 | `ValidationError` | Request validation failure |
| 500 | `PolicyUpstreamError` | OPA returned error or malformed data |
| 500 | `PersistenceError` | UDM connection/auth failure |
| 500 | Any other | "Internal server error." |

## Input Validation

- `AuthzObjectIdentifier`: string, min_length=3
- `AppName`: string, pattern=`^[a-z][a-z0-9\-]*$`, min_length=3
- `NamespaceName`: string, pattern=`^[a-z][a-z0-9\-]*$`, min_length=3
- `ContextName`: string, min_length=3
- `PermissionName`: string, min_length=3

---

## Total

5 endpoints (4 implemented + 1 stub)

---
