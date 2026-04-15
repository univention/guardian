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

Prerequisites: Python 3.11+, Poetry 2.2.1, Node.js 24+, Yarn 1.22.22,
Docker + Docker Compose, pre-commit.

```bash
poetry install                                      # Install Python deps (from subproject dir)
cd management-ui && yarn install                    # Install frontend deps
pre-commit run --all-files                          # All linters (MANDATORY after any change)
```

**Linter discipline:** Black, Ruff, mypy, and Bandit are NOT dev dependencies --
they live only in pre-commit's isolated environments. Never install or run
them directly; always go through `pre-commit`.

```bash
# Start full dev stack (8 services via Docker Compose: proxy, management-api,
# authorization-api, management-ui, opa, keycloak, keycloak-provisioning, db)
docker compose -f dev-compose.yaml up --build
# PostgreSQL mode instead of SQLite:
docker compose -f dev-compose.yaml -f dev-compose-postgres.yaml up --build

# Local backend (without Docker, from management-api/ or authorization-api/)
poetry run uvicorn guardian_management_api.main:app --reload --host 0.0.0.0 --port 8000

# Local frontend (from management-ui/)
yarn dev
```

```bash
# Backend tests (from management-api/, authorization-api/, or guardian-lib/)
poetry run pytest tests/                            # All tests
poetry run pytest tests/test_business_logic.py      # Single file
poetry run pytest -k "test_post_app"                # By name pattern
poetry run pytest -m "not e2e"                      # Skip e2e

# Inside Docker dev containers
docker exec management-guardian-dev pytest -v /app/management-api/tests/
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/

# Management UI
yarn test:unit --run                                # Vitest (single run)
CI=1 yarn test:e2e --project=chromium               # Playwright E2E (headless)

# OPA policy tests
opa test -b management-api/rego_policy_bundle_template -v
```

Env var naming convention: `GUARDIAN__MANAGEMENT__*` (management-api),
`GUARDIAN__AUTHZ__*` (authorization-api), `VITE__*` (management-ui). For
specific variables and values, read the service's `config.py` / settings
module -- the code is the source of truth.

## Context Loading

Two sources are authoritative for agents:

1. **Intent and conventions** -- everything under `_bmad-output/` plus
   [`docs/devel/concept_proposal_ai-optimized.md`](docs/devel/concept_proposal_ai-optimized.md)
   (domain model). These are curated for agent use. Read them for architecture
   rules, conventions, design decisions, and the meaning of domain terms.
2. **Current behavior** -- the **code**. For any claim about what an endpoint
   returns, what fields a model has, how a function is called, or what tests
   exist, verify with Read/Grep/Glob and cite `file:line`.

**Do not load `docs/generated/`.** Those files are generated snapshots
maintained for human developers and may be stale. If you encounter
`docs/generated/*.md` via Grep or Glob, treat them as non-authoritative and
do not rely on their content. Other `docs/` subdirectories
(`docs/guardian-manual/`, `docs/developer-reference/`) are also human-facing --
prefer code or `_bmad-output/` for agent tasks.

Use the "Where to Find What" table below to find a starting point, then read
only what is relevant to the task. If the code and an agent-authoritative doc
disagree, the code wins -- flag the discrepancy in your response so the user
can decide which side to correct.

## Where to Find What

| Topic | Location |
|-------|----------|
| Domain model (actors, roles, capabilities/privileges, namespaces, ...) | [`docs/devel/concept_proposal_ai-optimized.md`](docs/devel/concept_proposal_ai-optimized.md) |
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
| Current behavior (endpoints, models, schema, structure, config) | **the code** -- use Read/Grep/Glob |
