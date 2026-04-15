# Architecture -- Authorization API

**Date:** 2026-03-29
**Version:** 3.0.6
**Type:** Backend API Service

---

## Executive Summary

The Authorization API is a FastAPI-based service that evaluates authorization requests against OPA. It answers two questions: "What permissions does this actor have?" (get_permissions) and "Does this actor have these specific permissions?" (check_permissions). It supports both "direct" mode (caller supplies full objects) and "with-lookup" mode (Guardian resolves actors/targets from UDM).

---

## Architecture Pattern

**Hexagonal (Ports & Adapters)** with four model layers.

```text
HTTP Request
    │
    ▼
[Router] ─── 5 endpoints, thin wrapper
    │
    ▼
[Business Logic] ─── 4 orchestration functions (125 lines)
    │
    ├──→ [API Port] ─── route ↔ domain model translation
    ├──→ [Policy Port] ─── OPA communication
    └──→ [Persistence Port] ─── UDM data lookup
```

### Four Model Layers

| Layer | Technology | Location | Purpose |
|-------|-----------|----------|---------|
| Route | Pydantic `BaseModel` | `models/routes.py` | HTTP serialization |
| Domain | Frozen `@dataclass` | `models/policies.py` | Business logic (immutable) |
| Persistence | `@dataclass` | `models/persistence.py` | UDM object representation |
| OPA | Frozen `@dataclass` | `models/opa.py` | OPA wire format (camelCase) |

---

## Ports (6 ports)

| Port | Type | Methods | Adapter |
|------|------|---------|---------|
| `SettingsPort` | Config | get_setting | `EnvSettingsAdapter` |
| `AuthenticationPort` | Incoming | `__call__`, get_actor_identifier | AlwaysAuthorized, NeverAuthorized, OAuth2 |
| `PersistencePort` | Outgoing | get_object, lookup_actor_and_old_targets | `UDMPersistenceAdapter` |
| `PolicyPort` | Outgoing | get_permissions, check_permissions, custom_policy | `OPAAdapter` |
| `GetPermissionsAPIPort` | Translation | to_policy_query, to_api_response, to_policy_lookup_query | `FastAPIGetPermissionsAPIAdapter` |
| `CheckPermissionsAPIPort` | Translation | to_policy_query, to_api_response, to_policy_lookup_query | `FastAPICheckPermissionsAPIAdapter` |

---

## Business Logic

4 functions, each following: API port → (persistence port) → policy port → API port → response.

| Function | Lookup? | Policy call |
|----------|---------|-------------|
| `get_permissions` | No | `policy_port.get_permissions` |
| `get_permissions_with_lookup` | Yes (UDM) | `policy_port.get_permissions` |
| `check_permissions` | No | `policy_port.check_permissions` |
| `check_permissions_with_lookup` | Yes (UDM) | `policy_port.check_permissions` |

---

## External Integration

### OPA Communication

- Two policy paths: `/v1/data/univention/base/get_permissions` and `/v1/data/univention/base/check_permissions`
- General permissions use empty target sentinel (`id=""`)
- Check-permissions may make up to 2 OPA calls (targeted + general)

### UDM Communication

- Vendored synchronous HTTP client (`udm_client.py`, 801 lines)
- HAL+JSON hypermedia format
- Objects fetched by DN, role properties merged (`guardianRoles` + `guardianInheritedRoles`)
- Object type inferred from DN prefix (`uid=` -> USER, `cn=` -> GROUP)
- 5 retries with `Retry-After` on 503

### Correlation ID

- Per-request `X-Request-ID` header (or auto-generated UUID4)
- Stored in `ContextVar`, added to all log entries and response headers

---

## API Surface

5 endpoints (4 implemented + 1 stub). See `api-contracts-authorization-api.md`.

---

## Testing Strategy

- Unit tests mock OPA (`opa_async_mock`) and UDM (`UDMMock`)
- Integration tests require OPA with test data loaded (marked `in_container_test`)
- Full integration tests require UDM REST API access
- Shared auth test fixtures from `guardian_pytest`
- 48 unit tests + 21 integration tests

---

_Generated using BMAD Method `document-project` workflow, Step 8_
