# AGENTS.md -- Guardian

> **Read [`_bmad-output/project-context.md`](_bmad-output/project-context.md)
> before implementing any code.** It contains all critical rules and conventions
> (127 rules covering imports, typing, testing, architecture, anti-patterns).
>
> **When implementing Phase 1 features**, also read
> [`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md)
> for architectural decisions, implementation patterns, new file layout, and
> anti-patterns.

Guardian is an **Attribute-Based Access Control (ABAC) authorization engine** for
Univention Corporate Server (UCS) -- a monorepo with 4 Python packages
(`management-api`, `authorization-api`, `guardian-lib`, `authorization-client`)
and 1 Vue 3 frontend (`management-ui`). Python 3.11+ / Poetry (backend),
TypeScript / Yarn 1.22.x (frontend). AGPL-3.0-only, REUSE-compliant (SPDX
header required on every source file).

**Architecture invariant:** Hexagonal / ports and adapters throughout. All
business logic in `business_logic.py` -- never in routers or adapters.
Flow: **Router -> Business Logic -> Ports (abstract) -> Adapters (concrete).**
Three separate model layers (domain `@dataclass`, Pydantic router models,
SQLAlchemy DB models) -- never shared across layers.

**Terminology:** "capability" in code = "privilege" in new docs (rename pending).

## Quick-Reference Commands

```bash
poetry install                                      # Install Python deps (from subproject dir)
cd management-ui && yarn install                    # Install frontend deps
pre-commit run --all-files                          # All linters (MANDATORY after any change)
```

```bash
# Management API tests (from management-api/)
poetry run pytest tests/                            # All tests
poetry run pytest tests/test_business_logic.py      # Single file
poetry run pytest -k "test_post_app"                # By name pattern

# Inside Docker dev containers
docker exec management-guardian-dev pytest -v /app/management-api/tests/
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/

# Management UI
yarn test:unit --run                                # Vitest (single run)
CI=1 yarn test:e2e --project=chromium               # Playwright E2E (headless)
```

For Docker Compose setup, individual linter commands, CI/CD details, and full
dev environment docs see [`docs/development-guide.md`](docs/development-guide.md).

## Context Loading

Before answering any question or starting any task, consult the "Where to Find
What" table below to identify relevant documentation. Use the Read or Glob tool
to load those files before proceeding. Only load files relevant to the task at
hand -- do not preemptively load everything.

Examples:

- Questions about REST endpoints or API design → load `docs/api-contracts-*.md`
- Questions about data models or schema → load `docs/data-models-*.md`
- Questions about project/component structure → load `docs/project-overview.md`
  and/or `docs/source-tree-analysis.md`
- Questions about architecture or hexagonal boundaries → load the matching
  `docs/architecture-*.md` and `_bmad-output/project-context.md`
- Questions about the domain model (roles, capabilities, namespaces, ...) →
  load `docs/devel/concept_proposal.md`
- Implementation work → always load `_bmad-output/project-context.md` plus any
  architecture or API-contract docs matching the component being changed
- Dev setup, testing, linting, CI/CD → load `docs/development-guide.md`

## Where to Find What

| Topic | Location |
|-------|----------|
| Project overview, tech stack, component diagrams | [`docs/project-overview.md`](docs/project-overview.md) |
| Directory tree, per-file descriptions | [`docs/source-tree-analysis.md`](docs/source-tree-analysis.md) |
| Per-component architecture deep dives | [`docs/architecture-*.md`](docs/) |
| API contracts (50+ REST endpoints) | [`docs/api-contracts-*.md`](docs/) |
| Data models & SQL schema | [`docs/data-models-*.md`](docs/) |
| Integration architecture & data flows | [`docs/integration-architecture.md`](docs/integration-architecture.md) |
| Domain model (actors, roles, capabilities, ...) | [`docs/devel/concept_proposal.md`](docs/devel/concept_proposal.md) |
| Dev setup, testing, linting, CI/CD, env vars | [`docs/development-guide.md`](docs/development-guide.md) |
| Technology stack & version pins | [`project-context.md` > Technology Stack](_bmad-output/project-context.md) |
| Import, typing, exception, logging conventions | [`project-context.md` > Language-Specific Rules](_bmad-output/project-context.md) |
| Hexagonal architecture & boundary rules | [`project-context.md` > Framework-Specific Rules](_bmad-output/project-context.md) |
| Testing patterns, fixtures, mocking | [`project-context.md` > Testing Rules](_bmad-output/project-context.md) |
| Formatting, naming, linting, SPDX headers | [`project-context.md` > Code Quality & Style Rules](_bmad-output/project-context.md) |
| CI/CD, release process, dependency management | [`project-context.md` > Development Workflow Rules](_bmad-output/project-context.md) |
| Anti-patterns, edge cases, gotchas | [`project-context.md` > Critical Don't-Miss Rules](_bmad-output/project-context.md) |
| Phase 1 architectural decisions & patterns | [`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md) |
| Phase 1 product requirements | [`_bmad-output/planning-artifacts/prd.md`](_bmad-output/planning-artifacts/prd.md) |
| Phase 1 UX design specification | [`_bmad-output/planning-artifacts/ux-design-specification.md`](_bmad-output/planning-artifacts/ux-design-specification.md) |
| Full documentation index | [`docs/index.md`](docs/index.md) |
