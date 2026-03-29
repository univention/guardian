# Architecture -- Management UI

**Date:** 2026-03-29
**Type:** Web Frontend (Single Page Application)

---

## Executive Summary

The Management UI is a Vue 3 single-page application that provides a graphical interface for managing Guardian ABAC entities. It follows the same hexagonal architecture as the backend services, with TypeScript port interfaces, Pinia-based adapter wiring, and three concrete adapter sets (in-memory mock, test data, real API).

---

## Architecture Pattern

**Hexagonal (Ports & Adapters)** with Pinia state management.

```text
Vue Components (views)
    │
    ▼
[dataAccess.ts] ─── bridge layer (651 lines)
    │
    ▼
[DataPort interface] ─── abstract contract (20 methods)
    │
    ├──→ InMemoryDataAdapter (mock, 1s delay)
    ├──→ ApiDataAdapter (real HTTP to Management API)
    │
[AuthenticationPort interface]
    ├──→ InMemoryAuthenticationAdapter
    └──→ KeycloakAuthenticationAdapter (PKCE)
```

### Adapter Selection

Unlike the backend (entry points + env vars), the frontend uses **switch/case in the Pinia adapter store** on configuration strings loaded from settings.

---

## Component Architecture

### Views (3 generic components)

| Component | Lines | Purpose |
|-----------|-------|---------|
| `ListView` | 644 | Generic searchable data grid for all entity types |
| `EditView` | 992 | Generic multi-page edit/add form with validation |
| `PageNotFound` | 41 | 404 page |

Both `ListView` and `EditView` are parameterized by `objectType` (role/namespace/context/capability) and `action` (add/edit), making them fully generic.

### Stores (3)

| Store | Purpose |
|-------|---------|
| `settings` | Loads config from env vars or remote JSON |
| `adapter` | Factory: creates auth + data adapters from config |
| `error` | Application-wide error queue with dedup |

### Data Flow

```text
View -> dataAccess.ts -> DataPort -> Adapter -> Management API
                                               -> (or in-memory mock)
```

`dataAccess.ts` (651 lines) is the bridge between views and adapters, handling:

- Adapter store initialization
- Entity-to-form-model conversion
- Form-model-to-entity conversion
- Colon-separated ID parsing (`app:ns:name`)
- Error result wrapping

---

## UI Component Library

The UI is built on `@univention/univention-veb` (v0.0.68), using components like `UGrid`, `UConfirmDialog`, `UComboBox`, `UMultiInput`, `UExtendingInput`, etc.

Forms are driven by a discriminated union field type system (11 field types) with configuration objects that define per-entity-type form structure.

---

## Routing

14 production routes with capabilities nested under role edit. Landing page redirects to role list. All routes use `KeepAlive` for `ListView` state preservation.

Known typo in routes: `capabilties` (missing 'i').

---

## Internationalization

i18next with English and German (181 keys each). Language detected from `UMCLang` cookie -> browser locale -> `en-US` fallback.

---

## Testing Strategy

- **Unit tests**: Vitest with `@vue/test-utils` and `jsdom`
- **E2E tests**: Playwright (Chromium, Firefox, WebKit)
- **Manual test views**: 5 test components at `/tests/*` (conditional on env var)
- **Mock data**: 8 generator files producing ~10,000 mock entities

---

## Key Dependencies

Vue 3 (Composition API), Pinia, vue-router, Vite, keycloak-js (26.0.5), i18next, @univention/univention-veb, TypeScript ~5.9.3

---
