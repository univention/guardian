# Integration Architecture -- Guardian

**Date:** 2026-03-29

---

```text
                    ┌─────────────┐
                    │   Keycloak  │ (Identity Provider)
                    │  OIDC/OAuth2│
                    └──────┬──────┘
                           │ JWT tokens
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────────┐
│  Management UI  │ │ Management API│ │ Authorization API  │
│  (Vue 3 SPA)    │ │ (FastAPI)     │ │ (FastAPI)          │
│                 │ │               │ │                    │
│ keycloak-js     │ │ PyJWT (RS256) │ │ PyJWT (RS256)      │
│ PKCE flow       │ │ well-known    │ │ well-known         │
└────────┬────────┘ └──┬─────┬─────┘ └──┬──────┬──────────┘
         │             │     │           │      │
         │ HTTP/JSON   │     │           │      │
         ▼             │     │           │      │
┌─────────────────┐    │     │           │      │
│ Management API  │◄───┘     │           │      │
│ REST endpoints  │          │           │      │
└─────────────────┘          │           │      │
                             │ Bundles   │ OPA  │ UDM REST
                             ▼ (polling) ▼      ▼
                       ┌──────────┐  ┌──────────────┐
                       │   OPA    │  │  UDM REST API│
                       │ (Rego)   │  │  (UCS LDAP)  │
                       └──────────┘  └──────────────┘
```

---

## Integration Points

### 1. Management UI -> Management API

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP/JSON (REST) |
| **Direction** | UI -> API (client-initiated) |
| **Auth** | Bearer token from Keycloak (PKCE flow) |
| **Adapter** | `ApiDataAdapter` in management-ui |
| **Base path** | `/guardian/management` (via Traefik) |
| **Operations** | Full CRUD on apps, namespaces, roles, permissions, conditions, contexts, capabilities |
| **Error mapping** | 404 -> objectNotFound, 422 -> fieldErrors, 400 (duplicate) -> fieldErrors |
| **CORS** | Optional proxy mode or explicit allowed origins |

### 2. Management API -> OPA (Bundle Serving)

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP (OPA bundle polling) |
| **Direction** | OPA -> Management API (OPA-initiated polling) |
| **Auth** | None (internal network) |
| **Adapter** | `BundleServerAdapter` in management-api |
| **Endpoints** | `GET /bundles/GuardianDataBundle.tar.gz`, `GET /bundles/GuardianPolicyBundle.tar.gz` |
| **Data format** | tar.gz bundles containing JSON data and Rego policy files |
| **Trigger** | Bundles rebuilt asynchronously when capabilities/conditions change (asyncio queues) |
| **Polling interval** | 10-15 seconds (configurable) |

**Data bundle contents:** `roleCapabilityMapping` -- maps roles to their capabilities with permissions, conditions, and relations.

**Policy bundle contents:** Rego source code -- `base.rego` (evaluation logic), `utils.rego` (helpers), and all condition `.rego` files.

### 3. Authorization API -> OPA (Policy Evaluation)

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP/JSON |
| **Direction** | Authorization API -> OPA (request-response) |
| **Auth** | None (internal network) |
| **Adapter** | `OPAAdapter` in authorization-api |
| **Endpoints** | `POST /v1/data/univention/base/get_permissions`, `POST /v1/data/univention/base/check_permissions` |
| **Library** | `opa-client` (private Univention registry) |
| **Pattern** | Up to 2 calls per check-permissions request (targeted + general) |

**OPA input format:**

```json
{
  "actor": {"id": "...", "roles": ["app:ns:role&app:ns:ctx"], "attributes": {}},
  "targets": [{"old": {...}, "new": {...}}],
  "namespaces": {"app": ["ns1", "ns2"]},
  "contexts": ["app:ns:ctx"],
  "extra_args": {},
  "permissions": [{"appName": "...", "namespace": "...", "permission": "..."}]
}
```

### 4. Authorization API -> UDM REST API (Data Lookup)

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP/JSON (HAL+JSON hypermedia) |
| **Direction** | Authorization API -> UDM (request-response) |
| **Auth** | HTTP Basic Auth (username/password) |
| **Adapter** | `UDMPersistenceAdapter` + vendored `udm_client.py` |
| **Operations** | Object lookup by DN (`users/user`, `groups/group` modules) |
| **Role properties** | Merges `guardianRoles` + `guardianInheritedRoles` |
| **Retry** | 5 retries with `Retry-After` on 503 |
| **Object type detection** | From DN prefix: `uid=` -> USER, `cn=` -> GROUP |

### 5. All Services -> Keycloak (Authentication)

| Aspect | Detail |
|--------|--------|
| **Protocol** | OIDC / OAuth2 |
| **Management UI** | PKCE authorization code flow via `keycloak-js` |
| **Backend services** | JWT validation via `PyJWT` (RS256, JWKS fetched from well-known) |
| **JWT claims** | Required: `exp`, `iss`, `aud`, `sub`, `iat`, `jti`. Actor ID from `dn` claim. |
| **Audience** | `"guardian"` (hardcoded in backend validation) |
| **Client IDs** | `guardian-ui` (management-ui), `guardian-scripts` (authorization-client) |

### 6. Management API Self-Authorization (Optional)

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP/JSON (to itself via Authorization API) |
| **Direction** | Management API -> Authorization API |
| **Adapter** | `GuardianAuthorizationAdapter` (uses M2M OAuth2 token) |
| **Purpose** | Per-resource ABAC authorization for management operations |
| **Configurable** | `RESOURCE_AUTHORIZATION_PORT=always` (dev) / `guardian` (prod) |
| **Operation** | Calls `/permissions/check/with-lookup` for each resource |

### 7. Authorization Client -> Guardian APIs (External Integration)

| Aspect | Detail |
|--------|--------|
| **Protocol** | HTTP/JSON |
| **Direction** | External app -> Guardian APIs |
| **Auth** | Password grant (via Keycloak token endpoint) |
| **Remote client** | `GuardianAuthorizationClient` -> Authorization API, `GuardianManagementClient` -> Management API |
| **Local client** | `LocalGuardianAuthorizationClient` -- evaluates from local JSON files (no network) |
| **Token caching** | LRU-cached, auto-refresh on 401 |
| **Retry** | 5 retries with 2s delay on HTTP errors |

---

## Shared Dependencies (guardian-lib)

Both backend services depend on `guardian-lib` for:

| Component | Usage |
|-----------|-------|
| `SettingsPort` / `EnvSettingsAdapter` | Environment variable configuration |
| `AuthenticationPort` / `FastAPIOAuth2` | JWT authentication with OIDC |
| `ADAPTER_REGISTRY` | Global adapter registry singleton |
| `port_dep()` | FastAPI dependency injection factory |
| `initialize_adapters()` | Eager adapter initialization at startup |
| `configure_logger()` | Loguru structured logging configuration |
| `guardian_pytest` fixtures | Shared test JWT tokens and mock JWKS |

---

## Data Flow: End-to-End Permission Check

```text
1. External App calls authorization-client.check_permissions(actor, targets, permissions)
2. authorization-client authenticates with Keycloak (password grant) -> access token
3. authorization-client POSTs to Authorization API /permissions/check/with-lookup
4. Authorization API authenticates request (JWT validation via Keycloak JWKS)
5. Authorization API looks up actor from UDM REST API (guardianRoles + guardianInheritedRoles)
6. Authorization API looks up targets from UDM REST API
7. Authorization API builds OPA query (domain -> OPA wire format)
8. Authorization API sends query to OPA /v1/data/univention/base/check_permissions
9. OPA evaluates Rego policies:
   a. For each actor role, find matching capabilities in roleCapabilityMapping
   b. Evaluate conditions (AND/OR) for each capability
   c. Collect granted permissions, check if requested permissions are a subset
10. OPA returns per-target boolean results
11. Authorization API maps OPA response to domain result
12. Authorization API returns HTTP response to authorization-client
13. authorization-client returns structured result to external app
```

---

## Data Flow: Management UI Entity Update

```text
1. User edits a capability in the Management UI
2. EditView validates form, calls updateObject() via dataAccess.ts
3. ApiDataAdapter sends PUT /capabilities/{app}/{ns}/{name} with auth header
4. Traefik routes to Management API
5. Management API authenticates request (JWT)
6. Management API authorizes operation (ResourceAuthorizationPort)
7. Business logic calls CapabilityPersistencePort.update() (delete + create)
8. SQLCapabilityPersistenceAdapter executes SQL transaction
9. Business logic calls BundleServerPort.schedule_bundle_build(BundleType.data)
10. Bundle build is enqueued (asyncio queue)
11. Background task rebuilds roleCapabilityMapping bundle as tar.gz
12. OPA polls and picks up new data bundle (within 10-15 seconds)
13. Subsequent permission checks use updated capability mapping
```

---
