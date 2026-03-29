# Architecture -- Management API

**Date:** 2026-03-29
**Version:** 3.0.6
**Type:** Backend API Service

---

## Executive Summary

The Management API is a FastAPI-based REST service that provides CRUD operations for all Guardian ABAC entities (apps, namespaces, roles, permissions, conditions, contexts, capabilities). It serves as the central configuration hub for the Guardian system and also hosts the OPA bundle server that generates Rego policy and data bundles consumed by OPA.

---

## Architecture Pattern

**Hexagonal (Ports & Adapters)** with strict model layer separation.

```text
HTTP Request
    │
    ▼
[Router] ─── thin wrapper, FastAPI Depends() for DI
    │
    ▼
[Business Logic] ─── orchestration: authc → authz → CRUD → response
    │
    ├──→ [API Port] ─── request/response model translation
    ├──→ [Persistence Port] ─── database CRUD
    ├──→ [AuthC Port] ─── authentication (JWT)
    ├──→ [AuthZ Port] ─── per-resource authorization
    └──→ [Bundle Server Port] ─── OPA bundle generation
```

### Three Model Layers

| Layer | Technology | Location | Purpose |
|-------|-----------|----------|---------|
| Domain | `@dataclass` | `models/*.py` | Business logic objects (frozen/mutable) |
| Router | Pydantic `BaseModel` | `models/routers/*.py` | HTTP serialization/validation |
| SQL | SQLAlchemy ORM | `models/sql_persistence.py` | Database persistence |

Adapters translate between layers. They are never the same classes.

---

## Ports (10 ports)

| Port | Type | Methods | Adapters |
|------|------|---------|----------|
| `SettingsPort` | Config | get_setting, get_str, get_int, get_bool | `EnvSettingsAdapter` |
| `AuthenticationPort` | Incoming | `__call__`, get_actor_identifier | AlwaysAuthorized, NeverAuthorized, OAuth2 |
| `ResourceAuthorizationPort` | Cross-cutting | authorize_operation | Always, Never, Guardian |
| `AppPersistencePort` | Outgoing | create, update, read_one, read_many | `SQLAppPersistenceAdapter` |
| `NamespacePersistencePort` | Outgoing | create, update, read_one, read_many | `SQLNamespacePersistenceAdapter` |
| `RolePersistencePort` | Outgoing | create, update, read_one, read_many | `SQLRolePersistenceAdapter` |
| `PermissionPersistencePort` | Outgoing | create, update, read_one, read_many | `SQLPermissionPersistenceAdapter` |
| `ConditionPersistencePort` | Outgoing | create, update, read_one, read_many | `SQLConditionPersistenceAdapter` |
| `ContextPersistencePort` | Outgoing | create, update, read_one, read_many | `SQLContextPersistenceAdapter` |
| `CapabilityPersistencePort` | Outgoing | create, update, delete, read_one, read_many | `SQLCapabilityPersistenceAdapter` |
| `BundleServerPort` | Outgoing | generate_bundles, schedule_bundle_build | `BundleServerAdapter` |

Plus 7 API ports (one per entity type, hardcoded, not via entry points).

### Adapter Selection

Adapters are loaded from Python entry points and selected at runtime via environment variables of the form `GUARDIAN__MANAGEMENT__ADAPTER__<PORT_NAME>`.

---

## Business Logic

`business_logic.py` (1,746 lines) contains all orchestration functions. Every function follows:

1. Convert API request to domain query (API port)
2. Authenticate caller (`authc_port.get_actor_identifier`)
3. Authorize operation (`authz_port.authorize_operation`)
4. Execute CRUD (persistence port)
5. Convert result to API response (API port)
6. Catch exceptions, transform via API port

**Special function: `register_app`** -- Creates app + default namespace + admin role + 2 capabilities + triggers bundle rebuild.

---

## Data Architecture

10 SQL tables with namespace-scoped uniqueness. See `data-models-management-api.md` for full schema.

Key design decisions:
- All relationships use `lazy="joined"` (eager loading)
- Capability update is implemented as delete + create (full replacement)
- SQLite FK enforcement via pragma event listener
- IntegrityError mapping: unique violations -> `ObjectExistsError`, FK violations -> `ParentNotFoundError`

---

## OPA Bundle Server

The management-api hosts an OPA bundle server that generates two bundles:
- **Data bundle** (`GuardianDataBundle.tar.gz`): Contains `roleCapabilityMapping` JSON
- **Policy bundle** (`GuardianPolicyBundle.tar.gz`): Contains all Rego policies + condition code

Bundles are rebuilt asynchronously via `asyncio.Queue(1)` when capabilities or conditions change. OPA polls every 10-15 seconds.

---

## API Surface

50 HTTP endpoints across 8 entity routers + bundle server. See `api-contracts-management-api.md` for full contracts.

All entities support GET (single + list with pagination) + POST (create) + PATCH (update). Capabilities additionally support PUT (full replacement) and DELETE.

---

## Testing Strategy

- Unit tests mock all ports via `pytest-mock`
- Integration tests use SQLite in-memory database
- E2E tests run against full Docker stack with UDM
- Shared auth test fixtures from `guardian_pytest`

---

_Generated using BMAD Method `document-project` workflow, Step 8_
