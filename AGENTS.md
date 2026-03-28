# AGENTS.md -- Guardian

Guardian is an Attribute-Based Access Control (ABAC) authorization engine for
Univention Corporate Server (UCS). It is a monorepo with four main components:
`management-api`, `authorization-api`, `guardian-lib` (shared Python library),
and `management-ui` (Vue 3 frontend). OPA (Open Policy Agent) handles policy
evaluation.

For detailed implementation rules, code style, naming conventions, version
constraints, anti-patterns, and edge cases, see
`_bmad-output/project-context.md`.

## Purpose and Main Concepts

Guardian is an authorization service (not authentication) for UCS and SWP
applications. It acts as a **policy decision point (PDP)** -- applications remain
the **policy enforcement point (PEP)** and must enforce decisions themselves.
Guardian uses OPA with Rego policies as its evaluation backend.

Key domain concepts (see `docs/devel/concept_proposal.md` for full details):

**Terminology note:** The term **capability** is deprecated and will be replaced
by **privilege** in a future refactoring. The codebase, API endpoints, database
schema, and concept proposal document still use "capability" throughout. Until
the rename is applied, use "capability" in code to match the existing codebase.
In new documentation, prefer "privilege". The two terms are synonymous.

- **Actor**: An authenticated entity (user, server, machine account) that
  performs actions. Actors are assigned roles.
- **Permission**: An opaque string representing an operation an application
  wants to authorize (e.g., `read_first_name`, `export`). Guardian does not
  know what a permission means -- the application defines and enforces that.
- **Target**: The object a permission applies to (e.g., a student LDAP object,
  an API endpoint). Targets are optional in authorization requests.
- **Role**: A namespaced identifier (e.g., `ucsschool:users:teacher`) that maps
  actors to capabilities via role-capability-mappings. Roles are scoped by app
  and namespace.
- **Context**: An optional tag that restricts a role to a subset of targets
  sharing the same tag (e.g., a school). Primarily used by UCS@school.
- **Capability** (to be renamed **Privilege**): A combination of permissions and
  conditions that defines what a role is allowed to do. A capability links a
  role to a set of permissions, with an AND/OR relation and optional conditions
  that further constrain when those permissions apply.
- **Namespace**: A two-part scoping mechanism (`app_name` + `name`, displayed as
  `app-name:namespace-name`) that prevents collisions between different
  applications' roles, permissions, and contexts. Entities within a namespace
  use three-part identifiers: `app:namespace:entity`.
- **Role-Capability-Mapping**: Configuration that maps roles to capabilities.
  This is what generates OPA policies. The Rego data key is
  `roleCapabilityMapping`.
- **Condition**: A boolean Rego function used within capabilities to restrict
  permissions based on attributes of the actor, target, or request context
  (e.g., `target_is_self`, `target_has_role`). Conditions accept typed
  parameters and are evaluated with AND or OR relation within a capability.

The two main API surfaces are:

1. **Management API** -- CRUD for apps, namespaces, roles, permissions, contexts,
   conditions, and capabilities. All entities except capabilities use PATCH for
   updates; capabilities use PUT (full replacement) and are the only entity with
   a DELETE endpoint.
2. **Authorization API** -- two main operations:
   - **Get Permissions**: "What permissions does this actor have for these
     targets?" Returns the set of permissions.
   - **Check Permissions**: "Does this actor have all of these specific
     permissions?" Returns yes/no.
   Both operations have a direct variant (caller supplies full objects) and a
   "with-lookup" variant (Guardian resolves actor/targets from a data store).

## Architecture

**IMPORTANT:** All code changes must adhere to the **hexagonal / ports and
adapters architecture**. Business logic must depend only on abstract port
interfaces, never on concrete adapter implementations. New functionality should
be added by implementing new adapters behind existing ports or by defining new
ports where needed. Do not bypass the port layer by calling adapters directly
from business logic or routes.

The project uses hexagonal architecture in both backend and frontend:
- **Ports** define abstract interfaces (Python ABCs / TypeScript interfaces).
- **Adapters** provide concrete implementations.
- **Business logic** lives exclusively in `business_logic.py` -- routers are
  thin wrappers that only wire dependencies and delegate.
- Backend adapters are registered via Python entry points (`port-loader`
  library) in `pyproject.toml` and selected at runtime through
  `GUARDIAN__<SERVICE>__ADAPTER__<PORT_NAME>` environment variables.
- Frontend adapters are selected via Pinia adapter store with switch/case on
  configuration strings.

Flow: Router -> Business Logic -> Ports (abstract) -> Adapters (concrete).

The codebase enforces three separate model layers -- domain `@dataclass` classes,
Pydantic router models, and SQLAlchemy DB models (management-api only). Adapters
translate between these layers; they are never the same classes.

## Build & Test Commands

### Python (Poetry)

Each Python subproject (`management-api`, `authorization-api`, `guardian-lib`,
`authorization-client`) uses Poetry. Install deps from within a subproject dir:

```bash
poetry install                          # install deps for the subproject
```

### Running Tests

**Management API** (can run directly, no external services required for unit tests):

```bash
# All tests (inside Docker dev environment)
docker exec management-guardian-dev pytest -v /app/management-api/tests/

# Locally, from the management-api directory
poetry run pytest tests/                         # all tests
poetry run pytest tests/test_business_logic.py   # single file
poetry run pytest tests/routes/test_app.py::TestAppEndpoints::test_post_app_minimal  # single test
poetry run pytest -k "test_post_app"             # by name pattern
poetry run pytest -m "not e2e"                   # skip e2e tests
```

**Authorization API** (integration tests require OPA with test data loaded):

```bash
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/
# Same pytest options as above apply for local runs
```

**Management UI** (frontend):

```bash
cd management-ui
yarn install
yarn test:unit                           # Vitest unit tests (watch mode)
yarn test:unit --run                     # single run, no watch
CI=1 yarn test:e2e --project=chromium    # Playwright E2E (headless)
CI=1 yarn test:e2e                       # all browsers
```

### Linting & Formatting

**IMPORTANT:** After changing any file, ALWAYS run `pre-commit run --all-files`
to execute the pre-commit linters and verify that all checks pass. Fix any
issues reported before proceeding. Do NOT skip this step.

**IMPORTANT:** Black, Ruff, mypy, and Bandit are NOT dev dependencies -- they
exist only in pre-commit's isolated environments. Run them exclusively via
`pre-commit run --all-files`, never install or run them directly.
