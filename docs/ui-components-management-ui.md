# UI Component Inventory -- Management UI

**Date:** 2026-03-29
**Framework:** Vue 3 (Composition API, `<script setup lang="ts">`)
**Component Library:** `@univention/univention-veb` 0.0.68
**Styling:** Stylus
**i18n:** i18next (English + German)

---

## View Components (3)

### ListView (`views/ListView.vue`, 644 lines)

**Props:** `{ objectType: ObjectType }` -- one of `'role' | 'context' | 'namespace' | 'capability'`
**Component name:** `'ListView'` (used in `KeepAlive include`)

**Purpose:** Generic list view for all entity types. Renders a searchable, filterable data grid with context actions.

**Features:**

- Tab navigation between Roles / Namespaces / Contexts (top-level) or Role / Capabilities (nested)
- Search form with cascading filters (app -> namespace)
- `UGrid` data table with column definitions per object type
- Context actions: Edit (all types), Delete (capabilities only, supports multi-select)
- Search limit warning modal
- Delete confirmation and error modals
- State preserved across tab switches via `KeepAlive`

**Data loading:** Calls `fetchListViewConfig()` on mount, then `fetchObjects()` with search form values.

---

### EditView (`views/EditView.vue`, 992 lines)

**Props:** `{ action: 'edit' | 'add'; objectType: ObjectType }`

**Purpose:** Generic edit/add form for all entity types. Multi-page form with validation.

**Features:**

- Multi-page form with sidebar page navigation
- Accordion fieldsets within pages
- Dynamic form fields via `<component :is="components[field.type]">`
- Per-page validation tracking with visual indicators
- Unsaved changes guard (`onBeforeRouteLeave`)
- Field-level error messages from server validation errors
- Sticky header with save/add/back buttons
- Nested `<RouterView>` for role's child routes (capabilities)

**Edit mode:** Fetches object via `fetchObject()`, maps fields with `access` levels (read/write/none).
**Add mode:** Fetches config via `fetchAddViewConfig()`, sets up cascading watchers for dynamic options.

---

### PageNotFound (`views/PageNotFound.vue`, 41 lines)

**Purpose:** 404 page with centered message and home button.

---

## Univention VEB Components Used

The UI relies heavily on the `@univention/univention-veb` component library:

| Component | Usage |
|-----------|-------|
| `UGrid` | Data tables in ListView |
| `UConfirmDialog` | Error modals, delete confirmation, unsaved changes |
| `UStandbyFullScreen` | Loading spinner during app initialization |
| `UInputText` | Text input fields |
| `UInputDate` | Date input fields |
| `UInputPassword` | Password input fields |
| `UInputCheckbox` | Checkbox fields |
| `USelect` | Single-select dropdowns |
| `UComboBox` | Searchable combo boxes (app/namespace filters) |
| `UMultiSelect` | Multi-select with columns |
| `UMultiInput` | Repeatable field groups (conditions, permissions in capabilities) |
| `UMultiObjectSelect` | Multi-object selection with search |
| `UExtendingInput` | Extensible input with dynamic sub-fields (conditions with parameters) |
| `UInputClassified` | Read-only classified field (for `access: 'none'`) |

---

## Field Type System

Forms are driven by a discriminated union of field types:

| Field Type | Component | Description |
|-----------|-----------|-------------|
| `'UExtendingInput'` | `UExtendingInput` | Root element + dynamic extensions per selection |
| `'UInputText'` | `UInputText` | Text input with optional validators |
| `'UInputDate'` | `UInputDate` | Date picker |
| `'UInputPassword'` | `UInputPassword` | Password field |
| `'UInputCheckbox'` | `UInputCheckbox` | Boolean toggle |
| `'USelect'` | `USelect` | Static options dropdown |
| `'UComboBox'` | `UComboBox` | Searchable dropdown with dynamic options |
| `'UMultiSelect'` | `UMultiSelect` | Multi-column multi-select |
| `'UMultiInput'` | `UMultiInput` | Repeatable sub-element groups |
| `'UMultiObjectSelect'` | `UMultiObjectSelect` | Object search and selection |
| `'UInputClassified'` | `UInputClassified` | Restricted-access placeholder |

---

## View Configuration Objects

Configuration objects define the structure of list views and add/edit forms per entity type.

### List View Configs (`helpers/configs/listViewConfig.ts`)

| ObjectType | Search Fields | Columns | Global Actions |
|-----------|--------------|---------|---------------|
| Role | App (UComboBox), Namespace (UComboBox) | name, displayName, appName, namespaceName | Add |
| Namespace | App (UComboBox) | name, displayName, appName | Add |
| Context | App (UComboBox), Namespace (UComboBox) | name, displayName, appName, namespaceName | Add |
| Capability | (inherits from parent role view) | name, displayName, appName, namespaceName | Add |

### Add View Configs

| ObjectType | Config File | Fields |
|-----------|------------|--------|
| Role | `addRoleViewConfig.ts` | appName (UComboBox), namespaceName (UComboBox), name (UInputText + validateName), displayName (UInputText) |
| Namespace | `addNamespaceViewConfig.ts` | appName (UComboBox), name (UInputText + validateName), displayName (UInputText) |
| Context | `addContextViewConfig.ts` | appName (UComboBox), namespaceName (UComboBox), name (UInputText + validateName), displayName (UInputText) |
| Capability | `addCapabilityViewConfig.ts` | appName, namespaceName, displayName, name (optional, auto-generated), conditions (UMultiInput + UExtendingInput), relation (UComboBox AND/OR), permissions (UMultiInput + UComboBox) |

### Detail (Edit) View Configs

| ObjectType | Config File | Read-Only Fields | Writable Fields |
|-----------|------------|-----------------|-----------------|
| Role | `roleDetailResponseModel.ts` | appName, namespaceName, name | displayName |
| Namespace | `namespaceDetailResponseModel.ts` | appName, name | displayName |
| Context | `contextDetailResponseModel.ts` | appName, namespaceName, name | displayName |
| Capability | `capabilityDetailResponseModel.ts` | appName, namespaceName, name | displayName, conditions, relation, permissions |

---

## Router Structure

### Production Routes (14)

| Path | Route Name | View | Props |
|------|-----------|------|-------|
| `/` | `landing` | Redirect -> `listRoles` | -- |
| `/roles` | `listRoles` | `ListView` | `objectType: 'role'` |
| `/roles/add/:page?` | `addRole` | `EditView` | `action: 'add', objectType: 'role'` |
| `/roles/edit/:id/:page?` | `editRole` | `EditView` | `action: 'edit', objectType: 'role'` |
| `/roles/edit/:id/:page?/capabilties` | `listCapabilities` | `ListView` | `objectType: 'capability'` |
| `/roles/edit/:id/:page?/capabilties/add/:page?` | `addCapability` | `EditView` | `action: 'add', objectType: 'capability'` |
| `/roles/edit/:id/:page?/capabilties/edit/:id2/:page?` | `editCapability` | `EditView` | `action: 'edit', objectType: 'capability'` |
| `/namespaces` | `listNamespaces` | `ListView` | `objectType: 'namespace'` |
| `/namespaces/add/:page?` | `addNamespace` | `EditView` | `action: 'add', objectType: 'namespace'` |
| `/namespaces/edit/:id/:page?` | `editNamespace` | `EditView` | `action: 'edit', objectType: 'namespace'` |
| `/contexts` | `listContexts` | `ListView` | `objectType: 'context'` |
| `/contexts/add/:page?` | `addContext` | `EditView` | `action: 'add', objectType: 'context'` |
| `/contexts/edit/:id/:page?` | `editContext` | `EditView` | `action: 'edit', objectType: 'context'` |
| `/:pathMatch(.*)*` | -- | `PageNotFound` | -- |

**Note:** Capability routes are **nested children** of `editRole`. There is a known typo in the path: `capabilties` (missing 'i').

### Test Routes (5, conditional on `VITE__MANAGEMENT_UI__TESTING__ENABLE_TEST_ROUTES === '1'`)

| Path | Component | Purpose |
|------|-----------|---------|
| `/tests` | `TestView` | Hub page with links |
| `/tests/settings-adapter` | `SettingsAdapter.vue` | Manual settings adapter test |
| `/tests/authentication-adapter` | `AuthenticationAdapter.vue` | Manual auth adapter test |
| `/tests/data-adapter` | `DataAdapter.vue` | Comprehensive CRUD test (1800+ lines) |
| `/tests/language-selector` | `LanguageSelector.vue` | Language switching test |

---

## Internationalization

| Language | Locale File | Keys |
|----------|------------|------|
| English | `i18n/locales/en.json` | 181 translation keys |
| German | `i18n/locales/de.json` | 181 translation keys |

**Language detection:** Reads `UMCLang` cookie -> `navigator.language` -> fallback `'en-US'`.

**Key namespaces:** `App.error`, `ConfirmBackModal`, `DeleteModal`, `EditView`, `ListView`, `NotFoundView`, `SearchLimitReachedModal`, `configs.addView`, `configs.listView`, `dataAccess`, `dataAdapter`, `validators`.

---

## Validators

| Function | Pattern | Description |
|----------|---------|-------------|
| `validateName` | `/^[a-z][a-z0-9\-_]*$/` | Entity name validation (matches backend regex) |

---

## Mock Data Layer

Located in `helpers/mocks/api/`. Used by `InMemoryDataAdapter`.

| Generator | Volume |
|-----------|--------|
| `makeMockApps()` | 100 apps |
| `makeMockNamespaces()` | 300 namespaces (3 per app) |
| `makeMockRoles()` | 1,500 roles (5 per namespace) |
| `makeMockContexts()` | 1,500 contexts |
| `makeMockPermissions()` | 1,500 permissions |
| `makeMockConditions()` | 1,500 conditions (with N-1 parameters each) |
| `makeMockCapabilities()` | 4,500 capabilities (3 per role) |

All in-memory operations include a 1-second simulated delay.

---

## Total

3 view components, 14 production routes, 56 source files

---
