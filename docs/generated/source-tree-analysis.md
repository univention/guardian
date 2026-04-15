# Source Tree Analysis -- Guardian

**Date:** 2026-03-29
**Repository Type:** Monorepo (5 parts + infrastructure)

---

## Root Directory

```text
guardian/
├── .env.example                    # Environment variable template for all services
├── .gitlab-ci.yml                  # CI/CD pipeline entry point
├── .pre-commit-config.yaml         # Pre-commit hooks (Black, Ruff, Bandit, mypy)
├── .ruff.toml                      # Ruff linter configuration
├── .mypy.ini                       # mypy type checker configuration
├── .bandit                         # Bandit security scanner config
├── .black                          # Black formatter config
├── AGENTS.md                       # AI agent instructions for this project
├── README.md                       # Project README
├── README.dev.md                   # Developer setup instructions
├── dev-compose.yaml                # Docker Compose for local dev (8 services)
├── dev-compose-postgres.yaml       # PostgreSQL override for dev-compose
├── renovate.json5                  # Renovate dependency update config
├── sonar-project.properties        # SonarQube analysis config
├── ABAC-system.drawio              # Architecture diagram (draw.io)
├── ABAC-system.png                 # Architecture diagram (rendered)
│
├── management-api/                 # [PART] Management API (Python/FastAPI)
├── authorization-api/              # [PART] Authorization API (Python/FastAPI)
├── guardian-lib/                   # [PART] Shared Python library
├── authorization-client/           # [PART] Python client SDK
├── management-ui/                  # [PART] Vue 3 frontend
│
├── opa/                            # [INFRA] OPA container config
├── keycloak/                       # [INFRA] Keycloak IdP config + provisioning
├── docs/                           # Generated + manual documentation
├── _bmad/                          # BMAD method configuration
├── _bmad-output/                   # BMAD generated artifacts (project-context.md)
├── .opencode/                      # OpenCode AI configuration + skills
├── .gitlab-ci/                     # CI pipeline includes and helpers
├── .reuse/                         # REUSE license compliance
│
├── appcenter-authz/                # UCS App Center packaging (authorization-api)
├── appcenter-management/           # UCS App Center packaging (management-api)
├── appcenter-management-ui/        # UCS App Center packaging (management-ui)
├── appcenter-common/               # Shared App Center packaging resources
└── dev-run/                        # Development helper scripts
```

---

## Part 1: Management API (`management-api/`)

```text
management-api/
├── pyproject.toml                          # Dependencies, entry points, metadata (v3.0.6)
├── Dockerfile                              # Multi-stage build (builder, dev, production)
├── alembic.ini                             # Alembic migration config
├── README.md                               # Part README
├── update_client_secret.sh                 # Keycloak client secret updater
│
├── guardian_management_api/                # Application source
│   ├── main.py                             # ★ ENTRY POINT: FastAPI app, lifespan, middleware
│   ├── business_logic.py                   # ★ Core orchestration (1746 lines, all CRUD functions)
│   ├── adapter_registry.py                 # Adapter selection from env vars + entry points
│   ├── constants.py                        # API prefix, CORS config
│   ├── correlation_id.py                   # Per-request correlation ID (ContextVar)
│   ├── errors.py                           # Custom exceptions (5 classes)
│   ├── logging.py                          # Loguru configuration (partial)
│   │
│   ├── models/                             # Domain model layer (dataclasses)
│   │   ├── base.py                         # Shared base classes, TypeVars, pagination
│   │   ├── app.py                          # App domain + query models
│   │   ├── namespace.py                    # Namespace domain + query models
│   │   ├── role.py                         # Role domain + query models
│   │   ├── permission.py                   # Permission domain + query models
│   │   ├── condition.py                    # Condition domain + ConditionParameterType enum
│   │   ├── capability.py                   # Capability domain (most complex, with relations)
│   │   ├── context.py                      # Context domain + query models
│   │   ├── authz.py                        # OperationType, ResourceType, Actor, Resource
│   │   ├── sql_persistence.py              # ★ SQLAlchemy ORM schema (10 tables, 201 lines)
│   │   └── routers/                        # Router model layer (Pydantic)
│   │       ├── base.py                     # Shared mixins, name regex, pagination
│   │       ├── app.py                      # App request/response models
│   │       ├── namespace.py                # Namespace request/response models
│   │       ├── role.py                     # Role request/response models
│   │       ├── permission.py               # Permission request/response models
│   │       ├── condition.py                # Condition request/response (with code as base64)
│   │       ├── capability.py               # Capability request/response (most complex)
│   │       ├── context.py                  # Context request/response models
│   │       └── custom_endpoint.py          # Custom endpoint models (stub)
│   │
│   ├── ports/                              # Port interfaces (ABCs)
│   │   ├── base.py                         # BasePersistencePort (CRUD generic)
│   │   ├── app.py                          # AppAPIPort + AppPersistencePort
│   │   ├── namespace.py                    # NamespaceAPIPort + NamespacePersistencePort
│   │   ├── role.py                         # RoleAPIPort + RolePersistencePort
│   │   ├── permission.py                   # PermissionAPIPort + PermissionPersistencePort
│   │   ├── condition.py                    # ConditionAPIPort + ConditionPersistencePort
│   │   ├── capability.py                   # CapabilityAPIPort + CapabilityPersistencePort (+ delete)
│   │   ├── context.py                      # ContextAPIPort + ContextPersistencePort
│   │   ├── authz.py                        # ResourceAuthorizationPort
│   │   └── bundle_server.py                # BundleServerPort (OPA bundle generation)
│   │
│   ├── routers/                            # HTTP route handlers (thin wrappers)
│   │   ├── app.py                          # /apps/* (5 endpoints)
│   │   ├── namespace.py                    # /namespaces/* (5 endpoints)
│   │   ├── role.py                         # /roles/* (6 endpoints)
│   │   ├── permission.py                   # /permissions/* (6 endpoints)
│   │   ├── condition.py                    # /conditions/* (6 endpoints)
│   │   ├── context.py                      # /contexts/* (6 endpoints)
│   │   ├── capability.py                   # /capabilities/* (7 endpoints, incl. PUT + DELETE)
│   │   └── custom_endpoint.py              # /custom_endpoints/* (stub, 6 endpoints)
│   │
│   └── adapters/                           # Concrete implementations
│       ├── sql_persistence.py              # ★ Shared SQL infrastructure (SQLAlchemyMixin)
│       ├── app.py                          # SQLAppPersistenceAdapter
│       ├── namespace.py                    # SQLNamespacePersistenceAdapter
│       ├── role.py                         # SQLRolePersistenceAdapter
│       ├── permission.py                   # SQLPermissionPersistenceAdapter
│       ├── condition.py                    # SQLConditionPersistenceAdapter
│       ├── context.py                      # SQLContextPersistenceAdapter
│       ├── capability.py                   # SQLCapabilityPersistenceAdapter (552 lines)
│       ├── fastapi_utils.py                # TransformExceptionMixin for all API adapters
│       ├── authz.py                        # Always/Never/GuardianAuthorizationAdapter
│       └── bundle_server.py                # OPA bundle builder (asyncio queues)
│
├── alembic/                                # Database migrations
│   ├── env.py                              # Alembic environment config
│   ├── versions/
│   │   ├── 1.0.0_initial_schema.py         # Initial tables + 12 builtin conditions
│   │   ├── 2.0.0_positional_condition_params.py  # Add position to condition_parameter
│   │   └── 3.0.4_new_builtin_conditions.py       # Add new builtin conditions
│   ├── 1.0.0_builtin_conditions/           # 12 builtin condition definitions
│   │   ├── target_is_self.{rego,json}      # Per-condition: Rego code + JSON metadata
│   │   ├── target_has_role.{rego,json}
│   │   ├── target_has_same_context.{rego,json}
│   │   ├── no_targets.{rego,json}
│   │   ├── ... (12 conditions total, each with _test.rego)
│   │   └── utils.rego                      # Shared Rego utilities for tests
│   └── 3.0.4_builtin_conditions/           # New conditions added in migration 3.0.4
│       └── actor_field_equals_value.{rego,json}
│
├── rego_policy_bundle_template/            # ★ OPA Rego policy source
│   ├── .manifest                           # Bundle roots: univention, guardian/conditions
│   ├── univention/
│   │   ├── base.rego                       # ★ Core policy: get_permissions, check_permissions
│   │   ├── utils.rego                      # evaluate_conditions, extract_role_and_context
│   │   ├── base_test.rego                  # Policy unit tests
│   │   ├── utils_test.rego                 # Utility unit tests
│   │   └── test_mapping/data.json          # Test role-capability mapping data
│   └── guardian/conditions/
│       ├── stock.rego                      # Stock condition: only_if_param_result_true
│       └── stock_test.rego                 # Stock condition tests
│
└── tests/                                  # (not listed; mirrors source structure)
```

---

## Part 2: Authorization API (`authorization-api/`)

```text
authorization-api/
├── pyproject.toml                          # Dependencies, entry points (v3.0.6)
├── Dockerfile                              # Multi-stage build
├── README.md
│
├── guardian_authorization_api/             # Application source
│   ├── main.py                             # ★ ENTRY POINT: FastAPI app, lifespan, CORS, correlation ID
│   ├── business_logic.py                   # 4 orchestration functions (125 lines)
│   ├── adapter_registry.py                 # Adapter selection (4 ports)
│   ├── ports.py                            # ★ All port interfaces (6 ports in one file)
│   ├── routes.py                           # ★ All routes (5 endpoints in one file)
│   ├── constants.py                        # API prefix, CORS origins
│   ├── correlation_id.py                   # Per-request correlation ID
│   ├── errors.py                           # 3 custom exceptions
│   ├── logging.py                          # Loguru configuration
│   ├── udm_client.py                       # ★ Vendored UDM REST client (801 lines)
│   │
│   ├── models/
│   │   ├── routes.py                       # Pydantic request/response models
│   │   ├── policies.py                     # Domain dataclasses (frozen)
│   │   ├── persistence.py                  # UDM persistence models + ObjectType enum
│   │   └── opa.py                          # OPA wire-format models (camelCase)
│   │
│   └── adapters/
│       ├── api.py                          # FastAPI API port adapters (428 lines)
│       ├── persistence.py                  # UDMPersistenceAdapter (192 lines)
│       └── policies.py                     # OPAAdapter (263 lines)
│
└── tests/                                  # (mirrors source; unit + integration tests)
```

---

## Part 3: Guardian Lib (`guardian-lib/`)

```text
guardian-lib/
├── pyproject.toml                          # Dependencies (v1.8.1, port-loader 1.2.0)
│
├── guardian_lib/                            # Shared library source
│   ├── ports.py                            # ★ BasePort, SettingsPort, AuthenticationPort
│   ├── adapter_registry.py                 # ADAPTER_REGISTRY singleton, port_dep(), initialize_adapters()
│   ├── logging.py                          # configure_logger() with InterceptHandler
│   ├── adapters/
│   │   ├── authentication.py              # AlwaysAuthorized, NeverAuthorized, OAuth2 adapters
│   │   └── settings.py                    # EnvSettingsAdapter
│   └── models/
│       └── authentication.py              # FastAPIOAuth2AdapterSettings
│
├── guardian_pytest/                        # Shared test fixtures package
│   └── authentication.py                  # RSA keys, mock JWKS, 7 token fixtures
│
└── tests/                                  # Unit tests for all lib components
```

---

## Part 4: Authorization Client (`authorization-client/`)

```text
authorization-client/
├── pyproject.toml                          # Dependencies (v0.1.0, requests, pyyaml, python-ldap)
│
└── guardian_authorization_client/
    ├── __init__.py                         # Package exports (all public classes)
    ├── authorization.py                    # ★ GuardianAuthorizationClient (HTTP) + LocalGuardianAuthorizationClient (file-based)
    ├── management.py                       # ★ GuardianManagementClient (HTTP) + GuardianManagementClientLocal (filesystem)
    └── config.py                           # AuthorizationConfig (YAML parser with capability bundles)
```

---

## Part 5: Management UI (`management-ui/`)

```text
management-ui/
├── package.json                            # Dependencies (Vue 3, Pinia, Vite, keycloak-js)
├── vite.config.ts                          # Vite configuration
├── tsconfig*.json                          # TypeScript configs
├── playwright.config.ts                    # E2E test config
├── docker/Dockerfile                       # Nginx-based production container
│
└── src/
    ├── main.ts                             # ★ ENTRY POINT: Vue app creation, plugin install
    ├── App.vue                             # ★ Root component: init sequence, error boundary
    │
    ├── ports/                              # TypeScript port interfaces
    │   ├── authentication.ts               # AuthenticationPort interface
    │   ├── data.ts                         # DataPort interface (20 methods)
    │   └── settings.ts                     # SettingsPort interface
    │
    ├── adapters/                           # Concrete adapter implementations
    │   ├── authentication.ts               # InMemory + Keycloak auth adapters
    │   ├── data.ts                         # ★ GenericDataAdapter + InMemory + ApiDataAdapter (1805 lines)
    │   ├── settings.ts                     # Env + URL settings adapters
    │   └── errors.ts                       # InvalidAdapterError
    │
    ├── stores/                             # Pinia state management
    │   ├── adapter.ts                      # Adapter factory store (wires adapters from config)
    │   ├── error.ts                        # Error queue with dedup
    │   └── settings.ts                     # Settings loader (env vars or remote JSON)
    │
    ├── views/                              # Vue view components
    │   ├── ListView.vue                    # ★ Generic list view (644 lines, all entity types)
    │   ├── EditView.vue                    # ★ Generic edit/add form (992 lines, multi-page)
    │   └── PageNotFound.vue                # 404 page
    │
    ├── router/
    │   └── index.ts                        # Vue Router config (14 production + 5 test routes)
    │
    ├── helpers/
    │   ├── dataAccess.ts                   # ★ Bridge: views <-> data adapter (651 lines)
    │   ├── validators.ts                   # Name validation regex
    │   ├── cookies.ts                      # Cookie parser
    │   ├── models/                         # TypeScript interfaces (9 files)
    │   │   ├── interface.ts                # Core UI types (ObjectType, Field, Page, etc.)
    │   │   ├── apps.ts                     # App request/response/display types
    │   │   ├── namespaces.ts               # Namespace types
    │   │   ├── roles.ts                    # Role types
    │   │   ├── contexts.ts                 # Context types
    │   │   ├── permissions.ts              # Permission types
    │   │   ├── conditions.ts               # Condition types
    │   │   ├── capabilities.ts             # ★ Capability types (most complex, 158 lines)
    │   │   └── pagination.ts               # Pagination types
    │   ├── configs/                        # View configuration objects (9 files)
    │   │   ├── listViewConfig.ts           # List view column/filter definitions
    │   │   ├── add{Role,Namespace,Context,Capability}ViewConfig.ts  # Add form configs
    │   │   ├── {role,namespace,context,capability}DetailResponseModel.ts  # Edit form configs
    │   │   └── index.ts                    # Re-exports
    │   └── mocks/api/                      # Mock data generators (8 files)
    │       ├── apps.ts                     # 100 mock apps
    │       ├── namespaces.ts               # 300 mock namespaces
    │       ├── roles.ts                    # 1,500 mock roles
    │       └── ...                         # contexts, permissions, conditions, capabilities
    │
    ├── i18n/                               # Internationalization
    │   ├── index.ts                        # i18next config (cookie-based language detection)
    │   ├── locales/{en,de}.json            # 181 translation keys each
    │   └── univentionVebOverwrites/        # VEB component library overrides
    │
    ├── tests/views/                        # Manual test views (5 components)
    │   ├── DataAdapter.vue                 # Comprehensive CRUD test (1800+ lines)
    │   └── ...
    │
    └── assets/
        └── style.styl                      # Global styles (empty)
```

---

## Infrastructure

```text
opa/
├── Dockerfile                              # OPA v1.11.0 container (multi-stage, non-root)
├── opa_config.yaml                         # Bundle polling config (2 bundles from management-api)
└── README.md                               # Running/testing instructions

keycloak/
├── Dockerfile                              # Keycloak container
└── provisioning/
    ├── Dockerfile                           # Provisioning one-shot container
    ├── configure.py                         # Realm/client provisioning script
    ├── guardian_client_management_api_config.json  # Management API client config
    └── guardian_client_ui_config.json        # Management UI client config

.gitlab-ci/
├── gitlab-ci.yml                           # Main CI config (431 lines, 7 stages)
└── pre_commit_hook_parser.py               # Selective hook execution utility

docs/
├── guardian-manual/                        # Sphinx manual (RST, 13 pages)
├── architecture-documentation/             # Architecture docs (RST)
└── devel/
    ├── concept_proposal.md                 # ★ Core domain model document (1,584 lines)
    └── ...                                 # Developer reference (setup, testing, releases)
```

---

## Integration Points (Cross-Part References)

```text
management-ui ──HTTP──> management-api     # CRUD operations on all entities
                                            # via ApiDataAdapter -> /guardian/management/*

management-api ──HTTP──> OPA               # Policy evaluation (via bundle polling)
                                            # OPA polls /bundles/Guardian{Data,Policy}Bundle.tar.gz

authorization-api ──HTTP──> OPA            # Permission checks
                                            # via OPAAdapter -> /v1/data/univention/base/*

authorization-api ──HTTP──> UDM REST API   # Actor/target lookup
                                            # via UDMPersistenceAdapter -> vendored udm_client.py

management-api ──uses──> guardian-lib      # Shared ports, auth adapters, settings, logging
authorization-api ──uses──> guardian-lib   # Same shared library

management-api ──OAuth2──> Keycloak        # Authentication (JWT validation)
authorization-api ──OAuth2──> Keycloak     # Authentication (JWT validation)
management-ui ──OIDC/PKCE──> Keycloak      # SSO login (keycloak-js)

authorization-client ──HTTP──> authorization-api  # Remote permission checks
authorization-client ──HTTP──> management-api     # Remote CRUD operations
authorization-client ──file──> local JSON         # Local file-based evaluation (alternative)
```

---

## Key Files Summary

| File | Lines | Significance |
|------|-------|-------------|
| `management-api/.../business_logic.py` | 1,746 | All CRUD orchestration + authz checks |
| `management-ui/src/views/EditView.vue` | 992 | Generic multi-page edit/add form |
| `management-ui/src/adapters/data.ts` | 1,805 | 3 data adapter implementations |
| `authorization-api/.../udm_client.py` | 801 | Vendored UDM REST client |
| `management-ui/src/views/ListView.vue` | 644 | Generic list view for all entities |
| `management-ui/src/helpers/dataAccess.ts` | 651 | View-to-adapter bridge layer |
| `management-api/.../adapters/capability.py` | 552 | Most complex SQL adapter |
| `authorization-api/.../adapters/api.py` | 428 | API port adapters with model translation |
| `.gitlab-ci/gitlab-ci.yml` | 431 | Full CI/CD pipeline definition |
| `docs/devel/concept_proposal.md` | 1,584 | Core domain concept document |

---

_Generated using BMAD Method `document-project` workflow, Step 5_
