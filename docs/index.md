# Guardian -- Project Documentation Index

[[_TOC_]]

---

- **Generated:** 2026-03-29
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
| Authorization Client | Library | Python/requests | `authorization-client/` |
| Management UI | Web | Vue 3/TypeScript/Vite/Pinia | `management-ui/` |

---

## Generated Documentation

### Overview & Cross-Cutting

- [Project Overview](./project-overview.md) -- Purpose, structure, tech stack summary
- [Technology Stack](./technology-stack.md) -- Full dependency analysis per part
- [Source Tree Analysis](./source-tree-analysis.md) -- Annotated directory structure
- [Integration Architecture](./integration-architecture.md) -- How parts communicate, data flows
- [Development Guide](./development-guide.md) -- Setup, testing, linting, CI/CD, deployment

### Architecture (Per Part)

- [Architecture -- Management API](./architecture-management-api.md)
- [Architecture -- Authorization API](./architecture-authorization-api.md)
- [Architecture -- Guardian Lib](./architecture-guardian-lib.md)
- [Architecture -- Authorization Client](./architecture-authorization-client.md)
- [Architecture -- Management UI](./architecture-management-ui.md)

### API Contracts

- [API Contracts -- Management API](./api-contracts-management-api.md) -- 50 REST endpoints
- [API Contracts -- Authorization API](./api-contracts-authorization-api.md) -- 5 REST endpoints
- [API Contracts -- Management UI](./api-contracts-management-ui.md) -- Client-side DataPort interface

### Data & State

- [Data Models -- Management API](./data-models-management-api.md) -- 10 SQL tables, ER diagram, migrations
- [Data Models -- Authorization API](./data-models-authorization-api.md) -- 4 model layers, UDM integration
- [State Management -- Management UI](./state-management-management-ui.md) -- 3 Pinia stores
- [UI Components -- Management UI](./ui-components-management-ui.md) -- Views, routes, field types, i18n

---

## Existing Documentation

### Sphinx Manuals

- [Guardian Manual](../docs/guardian-manual/) -- Installation, configuration, API reference, conditions, troubleshooting (13 RST pages)
- [Architecture Documentation](../docs/architecture-documentation/) -- Sphinx architecture docs

### Developer Reference

- [Concept Proposal](../docs/devel/concept_proposal.md) -- Core domain model document (1,584 lines)
- [Developer Setup](../docs/devel/) -- Setup, testing, releases, adapter how-tos

### Project Context (BMAD)

- [Project Context](./../_bmad-output/project-context.md) -- 127 AI-optimized rules for code generation

### READMEs

- [Root README](../README.md) -- Project introduction
- [Developer README](../README.dev.md) -- Development quick-start
- [Management API README](../management-api/README.md)
- [Authorization API README](../authorization-api/README.md)
- [Management UI README](../management-ui/README.md)
- [Guardian Lib README](../guardian-lib/README.md)
- [OPA README](../opa/README.md)

---

## Getting Started

### For New Developers

1. Read this index and the [Project Overview](./project-overview.md)
2. Follow the [Development Guide](./development-guide.md) to set up your environment
3. Read the architecture doc for the part you'll work on
4. Run `pre-commit run --all-files` after every change

### For Feature Development

1. Read the relevant architecture doc(s) for your feature's scope
2. Check API contracts for existing endpoints
3. Review data models for schema understanding
4. For full-stack features, read [Integration Architecture](./integration-architecture.md)

### For AI-Assisted Development (Brownfield PRD)

Point the PRD workflow to this file: `docs/index.md`

---

_Generated using BMAD Method `document-project` workflow, Step 10_
