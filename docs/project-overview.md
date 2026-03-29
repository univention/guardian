# Project Overview -- Guardian

**Date:** 2026-03-29

---

## Purpose

Guardian is an **Attribute-Based Access Control (ABAC) authorization engine** for Univention Corporate Server (UCS) and SWP applications. It acts as a **policy decision point (PDP)** -- applications remain the **policy enforcement point (PEP)** and must enforce decisions themselves.

Guardian uses **OPA (Open Policy Agent) with Rego policies** as its evaluation backend.

---

## Repository Structure

| Type | Monorepo |
|------|----------|
| Parts | 5 (2 backend APIs, 2 Python libraries, 1 Vue 3 frontend) |
| Infrastructure | OPA, Keycloak, Traefik (Docker Compose) |
| License | AGPL-3.0-only |

| Part | Type | Technology | Description |
|------|------|-----------|-------------|
| `management-api` | Backend | Python 3.11 / FastAPI / SQLAlchemy | CRUD for all ABAC entities + OPA bundle server |
| `authorization-api` | Backend | Python 3.11 / FastAPI / OPA client | Permission evaluation (get/check permissions) |
| `guardian-lib` | Library | Python 3.11 / port-loader | Shared ports, auth adapters, settings, logging |
| `authorization-client` | Library | Python 3.11 / requests | SDK for external app integration (remote + local) |
| `management-ui` | Web | Vue 3 / TypeScript / Vite / Pinia | Admin UI for managing ABAC configuration |

---

## Architecture

All parts follow **hexagonal (ports & adapters) architecture**:

- **Ports** define abstract interfaces (Python ABCs / TypeScript interfaces)
- **Adapters** provide concrete implementations
- **Business logic** depends only on ports, never on adapters directly
- Backend adapters are loaded from Python entry points at runtime
- Frontend adapters are selected via Pinia store switch/case on config strings

---

## Key Domain Concepts

| Concept | Description |
|---------|-------------|
| **Actor** | Authenticated entity (user, server) that performs actions |
| **Permission** | Opaque string representing an operation (e.g., `read_first_name`) |
| **Target** | Object a permission applies to (e.g., a student LDAP object) |
| **Role** | Namespaced identifier mapping actors to capabilities |
| **Context** | Tag restricting a role to a subset of targets (e.g., a school) |
| **Capability** (Privilege) | Combination of permissions + conditions defining what a role can do |
| **Condition** | Boolean Rego function constraining when permissions apply |
| **Namespace** | Two-part scoping (`app:namespace`) preventing collisions |

---

## Tech Stack Summary

| Category | Technology |
|----------|-----------|
| Backend Language | Python 3.11 |
| Backend Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Policy Engine | OPA 1.11.0 with Rego |
| Frontend | Vue 3, TypeScript, Vite, Pinia |
| IdP | Keycloak (OIDC/OAuth2) |
| CI/CD | GitLab CI, Kaniko, pre-commit |
| Distribution | UCS App Center (3 separate apps) |

---

## Documentation Map

| Document | Description |
|----------|-------------|
| [Technology Stack](./technology-stack.md) | Full dependency analysis per part |
| [Source Tree Analysis](./source-tree-analysis.md) | Annotated directory structure |
| [Integration Architecture](./integration-architecture.md) | How parts communicate |
| [Development Guide](./development-guide.md) | Setup, testing, CI/CD |
| [Architecture - Management API](./architecture-management-api.md) | Management API design |
| [Architecture - Authorization API](./architecture-authorization-api.md) | Authorization API design |
| [Architecture - Guardian Lib](./architecture-guardian-lib.md) | Shared library design |
| [Architecture - Authorization Client](./architecture-authorization-client.md) | SDK design |
| [Architecture - Management UI](./architecture-management-ui.md) | Frontend design |
| [API Contracts - Management API](./api-contracts-management-api.md) | 50 REST endpoints |
| [API Contracts - Authorization API](./api-contracts-authorization-api.md) | 5 REST endpoints |
| [API Contracts - Management UI](./api-contracts-management-ui.md) | Client-side DataPort |
| [Data Models - Management API](./data-models-management-api.md) | 10 SQL tables |
| [Data Models - Authorization API](./data-models-authorization-api.md) | 4 model layers |
| [State Management - Management UI](./state-management-management-ui.md) | 3 Pinia stores |
| [UI Components - Management UI](./ui-components-management-ui.md) | Views, routes, i18n |

---

_Generated using BMAD Method `document-project` workflow, Step 9_
