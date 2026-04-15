<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

<!-- This is a compressed, agent-oriented version of concept_proposal.md.
     It keeps the domain model, rolestring grammar, context semantics,
     invariants, built-in conditions, and RCM shape. It omits user
     stories, requirement identifiers (C1..SUPP3), deliberation, and
     historical rationale. For those, read concept_proposal.md directly. -->

# Guardian Domain Model -- Agent Reference

## What Guardian Is

Guardian is an **ABAC authorization engine** for UCS. It is a **Policy
Decision Point (PDP) only** -- it does not enforce decisions or mutate data
on behalf of applications. The calling application remains the Policy
Enforcement Point (PEP). Actor/target role storage lives in UDM (the
Policy Information Point, PIP), not in Guardian.

Policies are expressed as OPA/Rego, built from **Role-Capability-Mappings**
(RCMs, JSON) plus Rego **conditions** -- either built-in to Guardian or
registered by apps during join scripts.

## Core Concepts

**Actor** -- an authenticated entity (user, machine account, server) that
acts within an application. Actors carry **roles**. Group roles apply
transitively to members (via a group's `member_roles` field).

**Target** -- the object a permission applies to. Usually an LDAP object,
but can be any JSON-serialisable object. Optional in authz requests --
when omitted, only **general permissions** apply.

**Application (app)** -- a component that registers and owns one or more
**namespaces**. In UCS, typically an App Center app ID.

**Namespace** -- ownership scope for roles, contexts, permissions,
conditions, and RCMs. Prevents cross-app collisions.

**Permission** -- a string tag representing an operation the application
wants to perform (e.g. `read_first_name`, `export`, `write_password`).
Guardian is **opaque to what permissions mean** -- it only answers "does
this actor have this permission for this target?". Applications
interpret and enforce.

**General permission** -- a permission granted when the target is the
empty object `{}`. A capability whose conditions make claims about
target content cannot be a general permission.

**Role** -- a named set of capabilities a principal can carry. Always
scoped to an app+namespace, and optionally to a context. Stored on
LDAP objects as rolestrings in a `roles` field (or `member_roles` for
groups). **Apps don't parse rolestrings themselves** -- UDM returns
role fields on its object responses in the format Guardian expects,
so apps pass UDM objects straight through to Guardian's authz
endpoints.

**Context** -- an arbitrary string tag that narrows a role to targets
sharing the same tag (primary use case: UCS@school per-school scoping).
Contexts are themselves namespaced. Optional feature -- most apps don't
use contexts.

**Condition** -- a Rego function returning a boolean, deciding whether a
capability applies given actor/target/context. May take parameters from
the RCM and extra data from the authz request.

**Capability** -- the tuple `(permissions, conditions, relation)`, where
`relation` is `AND` or `OR` across conditions. A role holds a list of
capabilities per namespace.

**Role-Capability-Mapping (RCM)** -- JSON mapping each rolestring to
its list of capabilities. Compiled into OPA policy bundles.

**Policy** -- the compiled OPA/Rego output of an RCM plus the condition
library. Policy propagation to OPA is bounded at **1 minute**.

## String Format Rules

| Element | Allowed chars | Case | Notes |
|---------|--------------|------|-------|
| App name | `[a-z0-9_-]` | lower | No spaces |
| Namespace | `[a-z0-9_-]` | lower | No spaces |
| Role name | `[a-z0-9_-]` | lower | |
| Context | `[a-z0-9_-]` | lower | |
| Permission | `[a-z0-9_-]` | lower | |
| Condition name | `[a-z0-9_]` | lower | Underscores only, **no hyphens** |
| Parameter keys | `[A-Za-z0-9_]` | any | May be camelCase (come from JSON) |

All lookups and comparisons are **case-insensitive**; the backend
lowercases before storing.

## Rolestring Grammar

```text
role-without-context = app-name ":" namespace ":" role-name
role-with-context    = role-without-context "&" app-name ":" namespace ":" context
```

Examples:

- `ucsschool:users:teacher`
- `ucsschool:users:teacher&ucsschool:default:school1`
- `guardian:guardian:role-superuser`

Separator between role and context is `&`. In RCMs and when stored on
LDAP objects, always use the full namespaced form.

## Context Matching Semantics

When deciding whether an actor's context matches a target's:

| Actor context | Target context | Match? |
|--------------|---------------|--------|
| none | none | YES |
| none | set | NO |
| set | none | NO |
| `"*"` (either side) | anything | YES |
| same value | same value | YES |

Contexts may come from rolestrings on actor/target, or from a
`contexts` key in the authz request.

## Invariants

1. **Allow-only, no DENY.** Any matching rule returns true; there are no
   subtractive rules. To simulate DENY, use `actor_does_not_have_role` /
   `target_does_not_have_role` conditions.
2. **Undefined is false.** Any undefined reference in Rego evaluation
   resolves to `false`, never `undefined`.
3. **Conditions return booleans only.** Output is cast via
   `cast_boolean`; anything non-boolean becomes undefined -> false.
4. **Closed failure.** If required inputs are missing (actor has no
   roles, target missing `id`, permission doesn't exist, etc.), return
   `false`.
5. **Cross-namespace read is allowed; modify is not.** An app can *read*
   any namespace and *do authz checks* against any namespace, but can
   only *modify* namespaces it owns.
6. **Rolestrings in RCMs are always fully namespaced** --
   `app:namespace:role`, never a bare role name.
7. **Custom condition names are namespaced.** Format:
   `{appname}_{namespace}_{conditionname}` (underscores only),
   e.g. `ucsschool_users_target_has_same_school`. This is to prevent
   cross-app collisions when custom Rego is bundled.
8. **Delete is mostly out of scope (first release).** Only RCMs support
   DELETE. Namespaces, roles, contexts, permissions, conditions have
   CRU only. Updates on roles/contexts/permissions typically only
   affect the display name.

## Condition Contract

Every condition receives a `condition_data` object with these fields:

| Key | Meaning |
|-----|---------|
| `actor` | The actor object |
| `role` | The rolestring of the actor being evaluated (from the RCM) |
| `target_old` | Target before modification (nullable) |
| `target_new` | Target after modification (nullable) |
| `parameters` | Extra data from the RCM entry for this condition |
| `extra_request_data` | Extra data from the authz request |

When registering a custom condition, declare:

- The parameter names read from `parameters`
- The extra-data keys read from `extra_request_data`
- A docstring and display name

The server rejects custom conditions whose Rego does not compile.

## Built-in Conditions

Registered globally under the `guardian:guardian` namespace. Parameters
come from `parameters` (RCM) unless marked as `extra_request_data`.

| Name | Purpose | Parameters |
|------|---------|-----------|
| `target_is_self` | Named fields of actor == target | `fields: [str]` |
| `target_is_empty` | Target is `{}` (models general permissions) | - |
| `target_has_role` | Target carries given role (any context) | `role: str` |
| `target_does_not_have_role` | Inverse of above | `role: str` |
| `actor_does_not_have_role` | Actor does NOT carry given role | `role: str` |
| `target_has_context` | Target has any of given contexts | `contexts` via `extra_request_data` |
| `actor_has_context` | Actor has any of given contexts (for `role` from condition_data) | `contexts` via `extra_request_data` |
| `target_field_equals_value` | `target[field] == value` | `field`, `value` |
| `target_field_not_equals_value` | `target[field] != value` | `field`, `value` |
| `target_has_same_context` | Actor and target share a context (no-context on either side = true) | - |
| `target_field_equals_actor_field` | `target[target_field] == actor[actor_field]` | `target_field`, `actor_field` |
| `target_has_role_in_same_context` | Target has given role in actor's context | `role: str` |
| `target_does_not_have_role_in_same_context` | Inverse | `role: str` |
| `actor_does_not_have_role_in_same_context` | Actor does NOT have extra role in target's context | `role: str` |

Helpers available to all conditions (built-in and custom):

- `get_object_roles(obj)` -> list of rolestrings for that object
- `get_available_permissions(actor, target)` -> list of permissions the
  actor has on the target

## Special Namespaces and Roles

All live under app name `guardian`:

- **`guardian:guardian:role-superuser`** -- granted to Domain Admins at
  install. Full administrative access across all namespaces. There is
  an internal recovery CLI on the primary server that can re-grant
  this role without authentication if it's ever lost.
- **`guardian:guardian:role-admin`** -- delegated admin; CRU roles,
  contexts, and CRUD RCMs across any namespace, but NOT permissions,
  namespaces, custom conditions, or custom endpoints.
- **`guardian:<app>:app-admin`** -- created when an app registers. CRU
  for roles/contexts/permissions, CRUD for RCMs, CU for custom
  conditions and custom endpoints *within the app's namespaces only*.
  Typically attached to the app's machine account.
- **`guardian:guardian:custom`** -- the default "custom" namespace for
  admin-created roles/contexts not belonging to any app. No pre-created
  role-admin.

## RCM Shape

```json
{
  "roleCapabilityMapping": {
    "<full-rolestring>": [
      {
        "appName": "<app>",
        "namespace": "<namespace>",
        "conditions": [
          { "name": "<condition_name>", "parameters": { "...": "..." } }
        ],
        "relation": "AND",
        "permissions": ["perm_a", "perm_b"]
      }
    ]
  }
}
```

Each entry reads: "When `<rolestring>` is evaluated against
`<app>/<namespace>`, if all/any (per `relation`) of the conditions hold,
grant these permissions." A role can have multiple entries across
namespaces.

## Authz Endpoints (semantic summary)

Two primary questions:

1. **Check permissions**: "Does actor A have permissions P1..Pn for
   target T?" -> boolean per target.
2. **List permissions**: "What permissions does actor A have for
   target T in namespace/context X?" -> list.

Both take:

- Full actor object (must include `id` and `roles`; other fields are
  consulted by conditions that reference them)
- Optional list of targets (each with `id`, `roles`, +other fields)
- Optional `target_new` list (same length as targets; enables
  before/after condition evaluation)
- Optional `contexts` array
- Optional namespace filter (for question 2)

There are **two endpoint variants with different auth profiles**:

- **Standard endpoints** take the full actor and target objects in the
  request body. Guardian does no LDAP/UDM lookup; it evaluates
  policies purely on the data supplied. These endpoints **can be
  unauthenticated** (and often are, when Guardian runs as a per-service
  sidecar -- see Deployment Topology below).
- **Lookup endpoints** take actor/targets as references only (DN,
  `uid`, `entryUUID`) and Guardian resolves them via UDM. These
  **must be authenticated**. Without authentication an attacker could
  probe for valid usernames and discover privileged accounts by
  observing authz responses, so this variant is always behind authn.
  Lookup endpoints also return only the reference fields supplied in
  the request (not the full resolved object), to avoid leaking data
  the caller didn't already possess.

## Policy Lifecycle

1. App install -> join script calls the Management API:
   - Register app (receives `app-admin` role)
   - Register namespaces, permissions, contexts
   - Register custom conditions and/or custom Rego endpoints (optional)
   - Create default roles and RCM entries
2. Domain admin assigns roles to users/groups -- stored in UDM, not
   Guardian.
3. RCM changes compile into OPA policy bundles; effective within
   **1 minute**.
4. Apps call authz endpoints at runtime; OPA evaluates policies.

## Deployment Topology

The intended runtime model is **one OPA instance per service, deployed
as a sidecar**. Each OPA knows only the policies relevant to its
service, and scales with the service's pods rather than being a shared
resource. Caching of authz results is recommended for hot paths. The
sidecar model is also the reason the standard (non-lookup) authz
endpoints can safely run unauthenticated -- in that topology they are
reachable only from the co-located service.

## Terminology Rename (in progress)

The code still uses **`capability`** where newer documents use
**`privilege`**. Treat them as synonyms. When writing code, follow the
code's current naming. When writing docs, follow the newer term.

## Not in Scope (First Release)

Do not assume these exist:

- DELETE endpoints for anything except RCMs
- Bulk operations
- DENY rules
- Capability bundles
- READ endpoints for custom Rego code
- Export / import / merge tools
- Management UIs for custom conditions (join scripts only)
- JWT verification inside Guardian
- Guardian maintaining the list of roles per user (UDM does this)

## Where to Go for More Detail

- Requirements, user stories, rationale, historical context, UCS/SWP
  integration notes: [`concept_proposal.md`](concept_proposal.md)
  (this file is a compressed view of that document)
- Current behaviour and implementation of these concepts: **the code**
  (router -> business_logic -> ports -> adapters)
- Architecture invariants, conventions, layering rules:
  [`../../_bmad-output/project-context.md`](../../_bmad-output/project-context.md)
- Phase 1 architectural decisions:
  [`../../_bmad-output/planning-artifacts/architecture.md`](../../_bmad-output/planning-artifacts/architecture.md)
