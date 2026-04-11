# Data Models -- Management API

**Date:** 2026-03-29
**ORM:** SQLAlchemy 2 (async, with aiosqlite for dev / asyncpg for production)
**Migration Tool:** Alembic (3 migration versions)

---

## Database Schema

### Entity-Relationship Overview

```text
app (1) ──> (N) namespace (1) ──> (N) permission
                               ──> (N) role
                               ──> (N) context
                               ──> (N) condition (1) ──> (N) condition_parameter
                               ──> (N) capability (N) ──> (N) permission       [via capability_permission]
                                                    (1) ──> (N) capability_condition (N) ──> (1) condition
                                                    (N) ──> (1) role
```

All entities except `app` are scoped to a namespace. Uniqueness is enforced at the `(namespace_id, name)` level for all namespaced entities.

---

### Table: `app`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, auto-increment | Internal ID |
| `name` | VARCHAR(256) | UNIQUE, NOT NULL | App identifier (e.g., `ucsschool`) |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |

**Relationships:** `namespaces` -> one-to-many `namespace`

---

### Table: `namespace`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `app_id` | INTEGER | FK(`app.id`), NOT NULL | Parent app |
| `name` | VARCHAR(256) | NOT NULL | Namespace identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |

**Unique constraint:** `(app_id, name)`
**Relationships:** `app` -> many-to-one `app` (joined eager)

---

### Table: `role`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `namespace_id` | INTEGER | FK(`namespace.id`), NOT NULL | Parent namespace |
| `name` | VARCHAR(256) | NOT NULL | Role identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |

**Unique constraint:** `(namespace_id, name)`
**Relationships:** `namespace` -> many-to-one `namespace` (joined eager)

---

### Table: `permission`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `namespace_id` | INTEGER | FK(`namespace.id`), NOT NULL | Parent namespace |
| `name` | VARCHAR(256) | NOT NULL | Permission identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |

**Unique constraint:** `(namespace_id, name)`
**Relationships:** `namespace` -> many-to-one `namespace` (joined eager)

---

### Table: `context`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `namespace_id` | INTEGER | FK(`namespace.id`), NOT NULL | Parent namespace |
| `name` | VARCHAR(256) | NOT NULL | Context identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |

**Unique constraint:** `(namespace_id, name)`
**Relationships:** `namespace` -> many-to-one `namespace` (joined eager)

---

### Table: `condition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `namespace_id` | INTEGER | FK(`namespace.id`), NOT NULL | Parent namespace |
| `name` | VARCHAR(256) | NOT NULL | Condition identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |
| `documentation` | TEXT | nullable | Usage documentation |
| `code` | LARGEBINARY | NOT NULL | Rego source code (stored as bytes) |

**Unique constraint:** `(namespace_id, name)`
**Relationships:**

- `namespace` -> many-to-one `namespace` (joined eager)
- `parameters` -> one-to-many `condition_parameter` (joined eager, cascade all/delete-orphan, ordered by `position`)

---

### Table: `condition_parameter`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `condition_id` | INTEGER | FK(`condition.id`), NOT NULL | Parent condition |
| `name` | VARCHAR(256) | NOT NULL | Parameter name |
| `value_type` | ENUM(`ConditionParameterType`) | NOT NULL | Type: ANY, STRING, FLOAT, INT, BOOLEAN, ROLE, CONTEXT |
| `position` | INTEGER | NOT NULL | Positional ordering within the condition |

---

### Table: `capability`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `namespace_id` | INTEGER | FK(`namespace.id`), NOT NULL | Parent namespace |
| `name` | VARCHAR(256) | NOT NULL | Capability identifier |
| `display_name` | VARCHAR(256) | nullable | Human-readable name |
| `role_id` | INTEGER | FK(`role.id`), NOT NULL | Associated role |
| `relation` | ENUM(`CapabilityConditionRelation`) | NOT NULL | AND or OR relation for conditions |

**Unique constraint:** `(namespace_id, name)`
**Relationships:**
- `namespace` -> many-to-one `namespace` (joined eager)
- `role` -> many-to-one `role` (joined eager)
- `permissions` -> many-to-many `permission` (via `capability_permission`, joined eager, passive_deletes)
- `conditions` -> one-to-many `capability_condition` (joined eager, cascade all/delete)

---

### Table: `capability_permission` (Association Table)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `capability_id` | INTEGER | FK(`capability.id`, ondelete=CASCADE), composite PK | Capability reference |
| `permission_id` | INTEGER | FK(`permission.id`, ondelete=CASCADE), composite PK | Permission reference |

---

### Table: `capability_condition`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK | Internal ID |
| `capability_id` | INTEGER | FK(`capability.id`, ondelete=CASCADE) | Parent capability |
| `condition_id` | INTEGER | FK(`condition.id`, ondelete=CASCADE) | Referenced condition |
| `kwargs` | JSON | NOT NULL | Parametrized condition arguments (includes `value_type` from condition parameter definition) |

**Relationships:**
- `capability` -> many-to-one `capability` (joined, back_populates)
- `condition` -> many-to-one `condition` (joined eager)

---

## Domain Model Layer (Dataclasses)

All domain models are Python `@dataclass` classes in `models/`. Key types:

| Model | Mutable | Fields |
|-------|---------|--------|
| `App` | Yes | `name`, `display_name` |
| `Namespace` | Frozen | `app_name`, `name`, `display_name` |
| `Role` | Yes | `app_name`, `namespace_name`, `name`, `display_name` |
| `Permission` | Frozen | `app_name`, `namespace_name`, `name`, `display_name` |
| `Context` | Yes | `app_name`, `namespace_name`, `name`, `display_name` |
| `Condition` | Yes | `app_name`, `namespace_name`, `name`, `code` (bytes), `display_name`, `documentation`, `parameters[]` |
| `ConditionParameter` | Yes | `name`, `value_type` (ConditionParameterType enum) |
| `Capability` | Yes | `app_name`, `namespace_name`, `name`, `display_name`, `role` (Role), `permissions[]`, `relation` (AND/OR), `conditions[]` (ParametrizedCondition) |
| `ParametrizedCondition` | Yes | `app_name`, `namespace_name`, `name`, `parameters[]` (CapabilityConditionParameter) |
| `CapabilityConditionParameter` | Yes | `name`, `value`, `value_type` |

### ConditionParameterType Enum

| Value | Description |
|-------|-------------|
| `ANY` | Any type |
| `STRING` | String value |
| `FLOAT` | Float value |
| `INT` | Integer value |
| `BOOLEAN` | Boolean value |
| `ROLE` | Role identifier (app:ns:name) |
| `CONTEXT` | Context identifier (app:ns:name) |

---

## Migration History

### Migration 1.0.0 -- Initial Schema (2023-09-22)

Creates all tables: `app`, `namespace`, `role`, `permission`, `context`, `condition`, `condition_parameter`, `capability`, `capability_permission`, `capability_condition`.

Seeds 12 builtin conditions in `guardian:builtin` namespace (loaded from `.rego` and `.json` files in `alembic/1.0.0_builtin_conditions/`).

### Migration 2.0.0 -- Positional Condition Parameters (2024-01-10)

Adds `position` column to `condition_parameter` table. Backfills existing parameters with sequential positions.

### Migration 3.0.4 -- New Builtin Conditions (2025-12-04)

Adds new builtin conditions to the existing `guardian:builtin` namespace (if they don't already exist). Updates existing conditions if their code or parameters have changed.

---

## Design Notes

1. **Three model layers**: Domain dataclasses, Pydantic router models, and SQLAlchemy ORM models are kept strictly separate. Adapters translate between them.
2. **All relationships use `lazy="joined"`**: Eager loading by default avoids N+1 queries.
3. **Capability update is delete + create**: The `SQLCapabilityPersistenceAdapter.update()` deletes the old capability and creates a new one (full replacement semantics matching PUT).
4. **FK enforcement for SQLite**: A pragma event listener ensures `PRAGMA foreign_keys=ON` for SQLite connections.
5. **IntegrityError mapping**: SQLite and PostgreSQL unique constraint violations are mapped to `ObjectExistsError`; FK violations are mapped to `ParentNotFoundError`.
6. **Cascade deletes**: Capability -> capability_permission and capability_condition cascade on delete.

---

_Generated using BMAD Method `document-project` workflow, Step 4_
