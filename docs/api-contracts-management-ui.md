# API Contracts -- Management UI (Client-Side)

**Date:** 2026-03-29
**Architecture:** Hexagonal (Ports & Adapters) with TypeScript interfaces
**Data Adapter:** Configurable -- `InMemoryDataAdapter`, `ApiDataAdapter`

---

## DataPort Interface

The `DataPort` interface (`src/ports/data.ts`) defines all data operations the UI can perform. Concrete adapters implement this interface.

### Entity Operations

| Method | Returns | Description |
|--------|---------|-------------|
| `fetchApps()` | `Result<WrappedAppsList, string>` | List all apps |
| `fetchNamespaces(app?)` | `Result<WrappedNamespacesList, string>` | List namespaces, optionally filtered by app |
| `fetchNamespace(app, name)` | `Result<WrappedNamespace, FetchObjectError>` | Get single namespace |
| `createNamespace(namespace)` | `Result<WrappedNamespace, SaveError>` | Create namespace |
| `updateNamespace(namespace)` | `Result<WrappedNamespace, SaveError>` | Update namespace (PATCH) |
| `fetchRoles(app?, namespace?)` | `Result<WrappedRolesList, string>` | List roles |
| `fetchRole(app, ns, name)` | `Result<WrappedRole, FetchObjectError>` | Get single role |
| `createRole(role)` | `Result<WrappedRole, SaveError>` | Create role |
| `updateRole(role)` | `Result<WrappedRole, SaveError>` | Update role (PATCH) |
| `fetchContexts(app?, namespace?)` | `Result<WrappedContextsList, string>` | List contexts |
| `fetchContext(app, ns, name)` | `Result<WrappedContext, FetchObjectError>` | Get single context |
| `createContext(context)` | `Result<WrappedContext, SaveError>` | Create context |
| `updateContext(context)` | `Result<WrappedContext, SaveError>` | Update context (PATCH) |
| `fetchCapabilities(role, app?, ns?)` | `Result<WrappedCapabilitiesList, string>` | List capabilities for a role |
| `fetchCapability(app, ns, name)` | `Result<WrappedCapability, FetchObjectError>` | Get single capability |
| `createCapability(capability)` | `Result<WrappedCapability, SaveError>` | Create capability |
| `updateCapability(capability)` | `Result<WrappedCapability, SaveError>` | Update capability (PUT) |
| `removeCapability(app, ns, name)` | `Result<null, string>` | Delete capability |
| `fetchPermissions(app, namespace)` | `Result<WrappedPermissionsList, string>` | List permissions by namespace |
| `fetchConditions()` | `Result<WrappedConditionsList, string>` | List all conditions |

---

## ApiDataAdapter -- HTTP Endpoints Called

The `ApiDataAdapter` (`src/adapters/data.ts`) maps DataPort methods to Management API HTTP calls:

| DataPort Method | HTTP Method | API Path |
|-----------------|-------------|----------|
| `fetchApps()` | GET | `/apps` |
| `fetchNamespaces(app?)` | GET | `/namespaces` or `/namespaces/{app}` |
| `fetchNamespace(app, name)` | GET | `/namespaces/{app}/{name}` |
| `createNamespace(ns)` | POST | `/namespaces/{app}` |
| `updateNamespace(ns)` | PATCH | `/namespaces/{app}/{name}` |
| `fetchRoles(app?, ns?)` | GET | `/roles`, `/roles/{app}`, or `/roles/{app}/{ns}` |
| `fetchRole(app, ns, name)` | GET | `/roles/{app}/{ns}/{name}` |
| `createRole(role)` | POST | `/roles/{app}/{ns}` |
| `updateRole(role)` | PATCH | `/roles/{app}/{ns}/{name}` |
| `fetchContexts(app?, ns?)` | GET | `/contexts`, `/contexts/{app}`, or `/contexts/{app}/{ns}` |
| `fetchContext(app, ns, name)` | GET | `/contexts/{app}/{ns}/{name}` |
| `createContext(ctx)` | POST | `/contexts/{app}/{ns}` |
| `updateContext(ctx)` | PATCH | `/contexts/{app}/{ns}/{name}` |
| `fetchCapabilities(role)` | GET | `/roles/{app}/{ns}/{name}/capabilities` |
| `fetchCapability(app, ns, name)` | GET | `/capabilities/{app}/{ns}/{name}` |
| `createCapability(cap)` | POST | `/capabilities/{app}/{ns}` |
| `updateCapability(cap)` | PUT | `/capabilities/{app}/{ns}/{name}` |
| `removeCapability(app, ns, name)` | DELETE | `/capabilities/{app}/{ns}/{name}` |
| `fetchPermissions(app, ns)` | GET | `/permissions/{app}/{ns}` |
| `fetchConditions()` | GET | `/conditions` |

### Authentication Headers

All API requests include:

- `Authorization: Bearer <token>` (from `AuthenticationPort.getValidAuthorizationHeader()`)
- `Accept-Language: <locale>` (from browser)
- `Content-Type: application/json`

### Error Handling

| HTTP Status | Mapped To |
|-------------|-----------|
| 404 | `FetchObjectError { type: 'objectNotFound' }` |
| 422 | `SaveError { type: 'fieldErrors', errors: [{field, message}] }` |
| 400 (duplicate name) | `SaveError { type: 'fieldErrors', errors: [{field: 'name', message}] }` |
| Other non-OK | `SaveError { type: 'generic', message }` |
| DELETE 404 | Treated as success |

### Result Type

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
```

---

## Model Layer Mapping (API <-> Domain)

The `GenericDataAdapter` base class performs snake_case <-> camelCase conversion:

| API Field (snake_case) | Domain Field (camelCase) |
|----------------------|------------------------|
| `app_name` | `appName` |
| `namespace_name` | `namespaceName` |
| `display_name` | `displayName` |
| `resource_url` | `resourceUrl` |

### Entity ID Convention

Entities are identified by colon-separated strings in the UI:
- Namespace: `app:name`
- Role/Context/Capability: `app:namespace:name`

---

## CORS Proxy Support

The `ApiDataAdapter` supports an optional `useProxy` mode (configured via `managementUi.cors.useProxy`). When enabled, the adapter uses only the pathname portion of the API URI, routing through a same-origin proxy to avoid CORS issues.

---

_Generated using BMAD Method `document-project` workflow, Step 4_
