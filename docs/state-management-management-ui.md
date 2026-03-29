# State Management -- Management UI

**Date:** 2026-03-29
**Framework:** Pinia (Vue 3 official state management)
**Pattern:** Stores as adapter wiring layer + application error queue

---

## Store Architecture

The management-ui uses three Pinia stores, each serving a distinct purpose in the hexagonal architecture:

```text
Settings Store (init) -> Adapter Store (wiring) -> Components (consumption)
                                                  -> Error Store (errors)
```

---

## 1. Settings Store (`stores/settings.ts`)

**Store ID:** `'settings'`
**Purpose:** Loads and provides configuration for adapter selection and initialization.

### State

| Field | Type | Description |
|-------|------|-------------|
| `config` | `Ref<SettingsConfig>` | Reactive configuration object |

### Configuration Shape (`SettingsConfig`)

```typescript
interface SettingsConfig {
  settingsPort: {
    adapter: string;           // 'env' or 'url'
    urlConfig: { configUrl: string; useProxy: boolean };
  };
  authenticationPort: {
    adapter: string;           // 'in_memory' or 'keycloak'
    inMemoryConfig: { isAuthenticated: boolean; username: string };
    keycloakConfig: { ssoUri: string; realm: string; clientId: string };
  };
  dataPort: {
    adapter: string;           // 'in_memory', 'test', or 'api'
    apiConfig: { uri: string; useProxy: boolean };
  };
}
```

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `init` | `(adapterName?: string, forceReinitialize?: boolean) -> Promise<void>` | Creates a settings adapter based on `VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT` env var, calls `init()` on it, then reads all config values. Skips if already initialized (unless forced). |

### Settings Adapter Selection

| Env Var / Config Value | Adapter | Behavior |
|----------------------|---------|----------|
| `'env'` | `EnvSettingsAdapter` | Reads from `import.meta.env` (Vite env vars) |
| `'url'` | `UrlSettingsAdapter` | Fetches from `{BASE_URL}/config.json` (or custom URL) |

---

## 2. Adapter Store (`stores/adapter.ts`)

**Store ID:** `'adapter'`
**Purpose:** Creates and holds concrete adapter instances based on settings configuration.

This is a **factory store** -- it is created via `useAdapterStore(config)` which immediately invokes `defineStore()`. The `SettingsConfig` parameter drives adapter selection via switch/case.

### State

| Field | Type | Description |
|-------|------|-------------|
| `authenticationAdapter` | `AuthenticationPort` | Active authentication adapter |
| `dataAdapter` | `DataPort` | Active data adapter |

### Authentication Adapter Selection

| Config Value | Adapter | Behavior |
|-------------|---------|----------|
| `'in_memory'` | `InMemoryAuthenticationAdapter` | Always authenticated with configured username |
| `'keycloak'` | `KeycloakAuthenticationAdapter` | Full OIDC with PKCE, login-required, token refresh |
| Other | -- | Throws `InvalidAdapterError` |

### Data Adapter Selection

| Config Value | Adapter | Behavior |
|-------------|---------|----------|
| `'in_memory'` | `InMemoryDataAdapter` | Generated mock data (100 apps, 300 namespaces, 1500 roles, etc.) with 1s delay |
| `'test'` | `InMemoryDataAdapter` | Hardcoded small test dataset (2 apps, 4 namespaces, 8 roles) |
| `'api'` | `ApiDataAdapter` | Real HTTP calls to Management API |
| Other | -- | Throws `InvalidAdapterError` |

---

## 3. Error Store (`stores/error.ts`)

**Store ID:** `'error'`
**Purpose:** Application-wide error queue with deduplication and modal lifecycle.

### State

| Field | Type | Description |
|-------|------|-------------|
| `activeError` | `Ref<ApplicationError \| null>` | Currently displayed error |
| `errorQueue` | `ApplicationError[]` (private) | Pending errors |

### Interface

```typescript
interface ApplicationError {
  message: string;
  title?: string;
  unRecoverable?: boolean;
}
```

### Actions

| Action | Signature | Description |
|--------|-----------|-------------|
| `push` | `(error: ApplicationError) -> void` | Adds error to queue if not duplicate; updates `activeError` |
| `advance` | `() -> void` | Shifts queue, shows next error (called when user dismisses current error) |

### Deduplication

Errors are compared by `message`, `title`, and `unRecoverable` fields. Duplicate errors are silently discarded.

### Error Classification

| `unRecoverable` | Behavior |
|-----------------|----------|
| `true` | Replaces entire app UI with static error card (no RouterView) |
| `false` / undefined | Shows dismissible `UConfirmDialog` modal overlay |

---

## Initialization Sequence

The app bootstrap in `App.vue` follows this sequence:

1. `settingsStore.init()` -- Load all configuration
2. `useAdapterStore(settingsStore.config)` -- Create adapters from config
3. `router.isReady()` -- Wait for initial route resolution
4. `adapterStore.authenticationAdapter.authenticate()` -- Perform login

Failures at steps 1 or 4 push unrecoverable errors to the error store.

---

## Environment Variables

All settings are read via the `EnvSettingsAdapter`, which converts dot-notation setting names to Vite env var format:

| Setting Name | Env Var | Purpose |
|-------------|---------|---------|
| `managementUi.adapter.settingsPort` | `VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT` | Settings adapter (`env` or `url`) |
| `managementUi.adapter.authenticationPort` | `VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT` | Auth adapter |
| `managementUi.adapter.dataPort` | `VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT` | Data adapter |
| `keycloakAuthenticationAdapter.ssoUri` | `VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__SSO_URI` | Keycloak server URL |
| `keycloakAuthenticationAdapter.realm` | `VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__REALM` | Keycloak realm |
| `keycloakAuthenticationAdapter.clientId` | `VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__CLIENT_ID` | Keycloak client ID |
| `apiDataAdapter.uri` | `VITE__API_DATA_ADAPTER__URI` | Management API base URL |
| `managementUi.cors.useProxy` | `VITE__MANAGEMENT_UI__CORS__USE_PROXY` | Enable CORS proxy |

---

_Generated using BMAD Method `document-project` workflow, Step 4_
