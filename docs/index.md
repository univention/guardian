# Guardian — Project Documentation Index

[[_TOC_]]

---

- **Generated:** 2026-05-12
- **Scan Level:** Exhaustive (all source files read)

## Project Overview

- **Type:** Monorepo with 5 parts
- **Primary Language:** Python 3.11, TypeScript
- **Architecture:** Hexagonal (Ports & Adapters)
- **Domain:** ABAC Authorization Engine for UCS

### Parts

| Part | Type | Tech Stack | Root |
|------|------|-----------|------|
| Management API | Backend | Python/FastAPI/SQLAlchemy | `management-api/` |
| Authorization API | Backend | Python/FastAPI/OPA | `authorization-api/` |
| Guardian Lib | Library | Python/port-loader | `guardian-lib/` |
| Authorization Client | Library | Python/requests/python-ldap | `authorization-client/` |
| Management UI | Web | Vue 3/TypeScript/Vite/Pinia | `management-ui/` |

---

## Generated Documentation

The documents in this section are AI-generated.
See [How to regenerate the generated docs](./generated/README.md)
for the workflow used to produce and refresh them.

### Overview & Cross-Cutting

- [Project Overview](./generated/project-overview.md) — Purpose, structure, tech stack summary
- [Technology Stack](./generated/technology-stack.md) — Full dependency analysis per part
- [Source Tree Analysis](./generated/source-tree-analysis.md) — Annotated directory structure with integration markers
- [Integration Architecture](./generated/integration-architecture.md) — How parts communicate: REST, OPA, UDM, OAuth2, shared bundles
- [Development Guide](./generated/development-guide.md) — Setup, testing, linting, CI/CD, deployment procedures

### Architecture (Per Part)

- [Architecture — Management API](./generated/architecture-management-api.md)
- [Architecture — Authorization API](./generated/architecture-authorization-api.md)
- [Architecture — Guardian Lib](./generated/architecture-guardian-lib.md)
- [Architecture — Authorization Client](./generated/architecture-authorization-client.md)
- [Architecture — Management UI](./generated/architecture-management-ui.md)

### API Contracts

- [API Contracts — Management API](./generated/api-contracts-management-api.md) — 50 REST endpoints
- [API Contracts — Authorization API](./generated/api-contracts-authorization-api.md) — 5 REST endpoints
- [API Contracts — Management UI](./generated/api-contracts-management-ui.md) — Client-side DataPort interface

### Data & State

- [Data Models — Management API](./generated/data-models-management-api.md) — 10 SQL tables, ER diagram, migrations
- [Data Models — Authorization API](./generated/data-models-authorization-api.md) — 4 model layers, UDM integration
- [State Management — Management UI](./generated/state-management-management-ui.md) — 3 Pinia stores (adapter, error, settings)
- [UI Components — Management UI](./generated/ui-components-management-ui.md) — Views, routes, field types, i18n

---

## Strategic Documentation

### Architecture & Domain

- [Guardian ABAC System](./Guardian-ABAC-system.md) — How Guardian implements ABAC: authorization path, management path, deployment overview
- [Guardian 3.0 Cheat Sheet](./guardian_cheat_sheet.pdf) — Quick-reference: roles, capabilities, permissions, actors/targets, request flow (2-page PDF)

---

## Reference Documentation

### Sphinx Manuals

- [Guardian Manual](./guardian-manual/) — Installation, configuration, API reference, conditions, troubleshooting (13 RST pages)
- [Architecture Documentation](./architecture-documentation/) — Sphinx-generated architecture reference

### Developer Resources

- [Concept Proposal (AI-Optimized)](./devel/concept_proposal_ai-optimized.md) — Core domain model optimized for AI agents
- [Concept Proposal (Full)](./devel/concept_proposal.md) — Complete technical specification (1,584 lines)
- [Integration Guide](./devel/Integrate_Guardian.md) — How to integrate Guardian into UCS environments
- [Developer Setup Guide](./devel/) — Local development, testing, releases, adapter patterns

### Project Context (AI Guidance)

- [Project Context](./project-context.md) — 127 AI-optimized rules for code generation (Pydantic v2, hexagonal architecture, testing patterns, naming conventions, etc.)

### READMEs

- [Root README](../README.md) — Project introduction and overview
- [Developer README](../README.dev.md) — Development quick-start guide
- [Management API README](../management-api/README.md)
- [Authorization API README](../authorization-api/README.md)
- [Management UI README](../management-ui/README.md)
- [Guardian Lib README](../guardian-lib/README.md)
- [OPA README](../opa/README.md)

---

## Getting Started

### For New Developers

1. Read this index and the [Project Overview](./generated/project-overview.md)
2. Follow the [Development Guide](./generated/development-guide.md) to set up your environment
3. Read the [Project Context](./project-context.md) for AI-enforced coding rules
4. Run `pre-commit run --all-files` after every change

### For Feature Development

1. Read the relevant architecture doc(s) for your feature's scope
2. Check API contracts for existing endpoints
3. Review data models for schema understanding
4. For full-stack features, read [Integration Architecture](./generated/integration-architecture.md)
5. Reference the [Guardian ABAC System](./Guardian-ABAC-system.md) for authorization concepts
