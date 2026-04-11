# Architecture -- Authorization Client

**Date:** 2026-03-29
**Version:** 0.1.0
**Type:** Python Client SDK / Library

---

## Executive Summary

The Authorization Client is a Python SDK for integrating external applications with Guardian. It provides both remote HTTP clients (communicating with the Guardian APIs) and a local file-based evaluation client (for offline/embedded use). It also includes a YAML-based configuration system that abstracts Guardian's API into higher-level concepts like permission sets and capability bundles.

---

## Architecture Pattern

**Imperative Client** with two evaluation strategies (remote and local).

---

## Authorization Clients

### `GuardianAuthorizationClient` (Remote)

- Authenticates with Keycloak via password grant (`oidc_client_id="guardian-scripts"`)
- `get_permissions(actor, targets, contexts, namespaces)` -> POSTs to `/permissions`
- `check_permissions(...)` -> POSTs to `/permissions/check`
- `get_and_check_permissions(...)` -> calls both, merges results
- Token caching (LRU, maxsize=1), auto-refresh on 401
- 5 retries with 2s delay on HTTP errors

### `LocalGuardianAuthorizationClient` (File-Based)

- Reads capabilities, permissions, roles from JSON files on disk
- Evaluates permissions locally in Python (no network calls)
- LRU-cached policy loading (maxsize=1 for capabilities, maxsize=20 for filtered queries)
- Implements 4 hardcoded conditions: `target_position_from_context`, `target_position_in`, `target_object_type_equals`, `target_is_self`
- LDAP scope checks: subtree, base, one-level (via `DN` wrapper class)

---

## Management Clients

### `GuardianManagementClient` (Remote)

- Full CRUD: create/modify app, namespace, role, permission, condition, context, capability
- **Idempotent creates**: All `create_*` methods detect "already exists" and fall through to `modify_*`
- Capability uses PUT (full replacement), all others use PATCH
- `prune()` is a no-op ("Guardian supports no removal")

### `GuardianManagementClientLocal` (Filesystem)

- Extends remote client, overrides `request()` to write JSON files to local path
- `prune()` actually deletes directories via `shutil.rmtree()`

---

## Configuration System (`config.py`)

`AuthorizationConfig` parses a YAML format with abstractions not native to Guardian:
- **Named conditions**: Reusable condition definitions
- **Permission sets**: Grouping of permissions under a name
- **Capability bundles**: Reusable sets of capabilities
- **Role-capability-mapping**: Maps roles to capabilities/bundles/permissions

`create(client)` materializes the configuration via a `GuardianManagementClient`.

---

## Dependencies

Core: `requests` ^2.28, `pyyaml` ^6.0, `python-ldap` ^3.4

---

_Generated using BMAD Method `document-project` workflow, Step 8_
