---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
workflowComplete: true
completedAt: '2026-03-30'
classification:
  projectType: api_backend_saas_b2b_hybrid
  domain: enterprise_identity_access_management
  complexity: high
  projectContext: brownfield
inputDocuments:
  - '_bmad-output/project-context.md'
  - 'docs/index.md'
  - 'docs/project-overview.md'
  - 'docs/technology-stack.md'
  - 'docs/source-tree-analysis.md'
  - 'docs/integration-architecture.md'
  - 'docs/development-guide.md'
  - 'docs/architecture-management-api.md'
  - 'docs/architecture-authorization-api.md'
  - 'docs/architecture-management-ui.md'
  - 'docs/architecture-guardian-lib.md'
  - 'docs/architecture-authorization-client.md'
  - 'docs/data-models-management-api.md'
  - 'docs/data-models-authorization-api.md'
  - 'docs/api-contracts-management-api.md'
  - 'docs/api-contracts-authorization-api.md'
  - 'docs/api-contracts-management-ui.md'
  - 'docs/ui-components-management-ui.md'
  - 'docs/state-management-management-ui.md'
  - 'docs/devel/concept_proposal.md'
  - 'docs/devel/Integrate_Guardian.md'
  - 'docs/devel/management_ports/README.md'
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 0
  projectDocs: 21
  projectContext: 1
workflowType: 'prd'
---

# Product Requirements Document - Guardian

**Author:** Nubus Core team
**Date:** 2026-03-30

## Executive Summary

Guardian is Univention's Attribute-Based Access Control (ABAC) authorization engine, serving as the central policy decision point (PDP) for all Univention software products. Applications externalize their authorization logic to Guardian, backed by Open Policy Agent (OPA), where administrators manage fine-grained access policies through a no-code UI and REST API -- without writing Rego, CEL, or any policy language.

Guardian was architecturally complete but never deployed to production because consuming applications were not ready. Multiple applications -- UDM, Portal, UCS@school, Provisioning, Self-Service, SCIM server, and third-party integrations -- are now ready to integrate. Guardian lacks features required for production operation: DELETE operations for all entity types, comprehensive structured logging, referential integrity enforcement, configurable database connectivity, secure OPA bundle distribution, support tooling, and the ability to assign capabilities to multiple roles. This PRD defines the work to close these gaps, organized into incremental application-specific milestones.

The strategic outcome is enabling **delegated administration** -- fine-grained, per-application permission management -- across the Univention product portfolio. Customer demand for this capability is a competitive market differentiator. When complete, customers manage access to all applications from a single authorization backbone, reducing both operational costs (unified role management) and internal development costs (applications reuse Guardian instead of building per-application authorization engines).

### What Makes This Special

- **Unified cross-application access management.** A single role object controls access across UDM, Portal, UCS@school, and other applications. Customers configure authorization in one place.
- **No-code policy management.** Administrators define ABAC policies through a management UI and API without touching any policy language. Primary differentiator over Cerbos, OPAL, or raw OPA.
- **UDM data lookup.** The Authorization API resolves actor and target attributes directly from UDM on behalf of applications, eliminating the need for applications to query UDM themselves.
- **Engine-agnostic API abstraction.** Guardian's API contract is independent of the underlying policy engine. OPA/Rego can be replaced with Cerbos without changing the API or application integrations.
- **Application-incremental adoption.** Each consuming application can begin integration as its specific prerequisites are met, rather than requiring all work to complete first.

## Project Classification

| Dimension | Value |
|---|---|
| **Project Type** | API backend / B2B platform hybrid |
| **Domain** | Enterprise identity & access management |
| **Complexity** | High -- regulated environments (education sector), distributed system (OPA + PostgreSQL + LDAP), multi-application integration surface, dual deployment targets (Kubernetes + UCS App Center) |
| **Project Context** | Brownfield -- massive feature expansion of existing v3.0.6 system across all 4 components (Management API, Authorization API, guardian-lib, Management UI) |

## Success Criteria

### User Success

- **Customer operators** can configure fine-grained, delegated access policies for multiple applications from a single Guardian Management UI, without writing code or policy language.
- **Customer operators** can understand what Guardian is doing through structured logging output and audit trails, enabling them to verify their security policies are applied correctly.
- **Application administrators** can correct configuration mistakes by deleting any previously created object (app, namespace, role, context, permission, condition, capability) through both API and UI.
- **Application administrators** can assign a single capability to multiple roles, eliminating the need to duplicate capability definitions across roles.
- **Support and PS engineers** can diagnose customer issues using structured log output from all three components (Management API, Authorization API, OPA), with configurable log levels on both App Center and Helm deployments.
- **Support and PS engineers** can dump and restore Guardian configuration using a CLI tool, on both UCS and Kubernetes environments.

### Business Success

- **UCS@school** can integrate Guardian for delegated administration by **August 2026**.
- **Portal** can integrate Guardian for cross-namespace permission management **immediately following** UCS@school (Q3 2026).
- **UDM** can integrate Guardian for fine-grained object-level permissions by **end of 2026**.
- Each application integration unlocks delegated administration as a **customer-facing differentiator** for that product line.
- Development teams stop building per-application authorization engines, reducing ongoing development and maintenance cost.

### Technical Success

- Authorization check latency < 20ms (p95), excluding UDM REST API lookup time (see NFR1).
- Structured logging across all components conforming to Univention logging ADRs.
- DELETE operations for all entity types with referential integrity enforcement.
- Secure OPA bundle endpoint (no unauthenticated access to policy bundles).
- Configurable SQL database URI (defaulting to UCS PostgreSQL, supporting custom databases).
- Full CI automation with 100% unit test coverage maintained and integration tests for all endpoints.
- Dual deployment targets (Kubernetes Helm chart + UCS App Center) both fully functional and configurable.

### Measurable Outcomes

| Metric | Target | Timeframe |
|---|---|---|
| Authorization check latency (excl. UDM lookup) | < 20ms p95 | Before first app integration |
| UCS@school Guardian integration | Shipped | August 2026 |
| Portal Guardian integration | Shipped | Q3 2026 |
| UDM Guardian integration | Shipped | End of 2026 |
| Entity types with DELETE operations | All (apps, namespaces, roles, contexts, permissions, conditions) | Before first app integration |
| Stakeholder readiness: Development | Full CI, good debuggability, app integration complete | Per-application milestone |
| Stakeholder readiness: Support/PS | Documentation, logging, CLI tooling operational | Per-application milestone |
| Stakeholder readiness: Customer Ops | Logging, auditing, deployment docs, UI usable | Per-application milestone |

## User Journeys

### Journey 1: Markus -- The School District Sysadmin (Primary User, Success Path)

**Situation:** Markus administers a UCS@school environment for a school district with 12 schools. Each school has a principal who should manage their own staff accounts, but only within their school. Until now, Markus handled every permission change himself because UCS@school only offered coarse-grained "admin or nothing" roles.

**Opening Scene:** Markus receives yet another ticket: "Please give the new IT coordinator at Goethe-Gymnasium access to manage user accounts for that school only." He's done this manually dozens of times -- editing LDAP attributes, hoping he doesn't accidentally grant district-wide access.

**Rising Action:** With Guardian integrated into UCS@school, Markus opens the Guardian Management UI. He creates a "School IT Coordinator" role scoped to the Goethe-Gymnasium context. He assigns capabilities for user account management -- create, modify, disable -- constrained by a `target_in_school` condition.

**Climax:** The coordinator logs in and can manage users at Goethe-Gymnasium. She cannot see or modify users at any other school. Markus verifies this through the permission report in the UI.

**Resolution:** When three more schools request the same setup, Markus reuses the same capability across all school contexts. What used to take a ticket per school per coordinator now takes minutes.

**Capabilities revealed:** Role creation, context scoping, capability assignment to roles, capability reuse across multiple roles, permission report (UI), Management UI CRUD.

### Journey 2: Claudia -- The Support Engineer (Troubleshooting Path)

**Situation:** Claudia works in Univention Support. A customer calls: "One of our teachers says they can't access the exam scheduling module anymore. It worked last week."

**Opening Scene:** Claudia connects to the customer's system. She has no idea what roles or capabilities are configured -- this is a complex UCS@school setup with hundreds of roles across 20 schools.

**Rising Action:** Claudia uses the CLI tool to query: "What permissions does user `teacher42@schule-nord` have?" The tool returns a structured report showing all roles assigned to the teacher, what capabilities each role grants, and the contexts they apply to. She notices the teacher's role was recently modified -- a condition was changed that now excludes teachers who aren't in the `exam_coordinators` group.

**Climax:** Claudia can see the exact permission chain: role -> capability -> condition -> permission. She identifies that the condition modification inadvertently restricted exam scheduling access to coordinators only.

**Resolution:** Claudia advises the customer admin to either add the teacher to the `exam_coordinators` group or create a separate capability for basic exam viewing. She exports the structured log showing the authorization denial. The issue is resolved in one call.

**Capabilities revealed:** CLI permission query per user, structured log output, authorization decision audit trail, condition chain visibility, text export for support workflows.

### Journey 3: Stefan -- The CISO (Compliance Reporting Path)

**Situation:** Stefan is the CISO at a large municipal government that uses Nubus with multiple applications (Portal, UDM, UCS@school). An internal audit requires him to document which roles have which permissions across all applications.

**Opening Scene:** Stefan needs to produce a compliance report showing all roles, their capabilities, the permissions those capabilities grant, and under which conditions they apply. He needs this for all applications in one view.

**Rising Action:** Stefan opens the Guardian Management UI and navigates to the reporting section. He generates a permissions matrix report showing every role, grouped by application namespace, with its associated capabilities, permissions, and conditions.

**Climax:** The report shows that a "District Administrator" role has cross-namespace permissions spanning both UCS@school and the Portal. Stefan can see exactly what this role can do in each application context and verify it matches the organization's security policy.

**Resolution:** Stefan exports the report for the auditors. When the audit team asks "Who can modify student records at Schiller-Schule?", he can filter the report to answer precisely.

**Capabilities revealed:** Permission matrix report (UI export), cross-namespace visibility, role-to-capability-to-permission chain display, filtering by application/namespace/context.

### Journey 4: Jaime -- The Application Developer (Integration Path)

**Situation:** Jaime is a developer on the Portal team. The Portal needs to check whether a user can see a specific tile (e.g., "User Management") based on their Guardian permissions. Until now, the Portal had its own hardcoded permission checks.

**Opening Scene:** Jaime reads the Guardian integration documentation. He needs to: (1) register the Portal's permissions and default roles at deployment time, and (2) call the Authorization API at runtime to check permissions.

**Rising Action:** Jaime writes deployment code that calls the Management API to register the Portal's namespace, its permissions (`view_tile`, `edit_settings`, `manage_users`), and default roles with capabilities. He uses the authorization client library to add permission checks in the Portal's backend.

**Climax:** The Authorization API responds in under 20ms. The Portal renders only the tiles the user is authorized to see. Jaime doesn't need to understand OPA, Rego, or Guardian internals -- he registers permissions and checks them through a clean API.

**Resolution:** When a customer later creates a custom role that grants `view_tile` only for specific Portal tiles, it just works -- Jaime's code doesn't need to change. The authorization logic is entirely externalized.

**Capabilities revealed:** Management API for programmatic registration, Authorization API check/get permissions, authorization client library, < 20ms response time, deployment-time setup code pattern.

### Journey 5: Nadia -- The SaaS DevOps Engineer (Deployment Path)

**Situation:** Nadia works for a managed service provider offering a hosted Nubus bundle with Guardian, Portal, UDM, and UCS@school to multiple school districts. Each district is a tenant. She needs to deploy a consistent baseline configuration across all tenants.

**Opening Scene:** Nadia is scripting the automated deployment of a new tenant. She needs to register all applications, their default namespaces, roles, permissions, and capabilities through the Management API as part of the provisioning pipeline.

**Rising Action:** Nadia writes Helm post-install hooks that call the Management API to register the full application bundle's authorization configuration. She uses the CLI dump tool to capture a "golden configuration" from a reference tenant, and the restore tool to apply it to new tenants.

**Climax:** A new school district is provisioned. All three applications are registered in Guardian with their default roles and capabilities. The district's admin can immediately start customizing roles for their schools.

**Resolution:** When Guardian ships an update, Nadia tests it against the reference tenant, dumps the updated config, and rolls it out. The CLI tool handles the operational lifecycle a SaaS provider needs.

**Capabilities revealed:** Management API bulk registration, CLI dump/restore tool, Kubernetes Helm integration, automated provisioning workflows, configuration lifecycle management.

### Journey 6: Markus Again -- The Admin Who Made a Mistake (Error Recovery Path)

**Situation:** Markus (from Journey 1) accidentally created a role with the wrong capabilities and assigned it to 15 users. Teachers at three schools now have admin-level access they shouldn't have.

**Opening Scene:** Markus realizes the mistake when a teacher reports they can see other schools' user lists. He needs to fix this immediately.

**Rising Action:** Markus opens the Management UI and navigates to the role. He uses the permission report to see exactly what permissions the role provides.

**Climax:** He decides the safest approach is to delete the incorrect capability entirely and create a new, correctly scoped one. The DELETE operation succeeds because no other roles reference it.

**Resolution:** The 15 users' permissions are immediately corrected. Markus checks the structured logs to confirm the authorization decisions changed. He exports the permission report for the role to verify correctness.

**Capabilities revealed:** DELETE operations (API + UI), referential integrity checks, permission report for verification, structured logging for confirmation, capability modification.

### Journey Requirements Summary

| Capability Area | Revealed By Journeys |
|---|---|
| Management UI CRUD (create, read, update, delete) | 1, 6 |
| DELETE operations with referential integrity | 6 |
| Capability reuse across multiple roles | 1, 5 |
| Permission report -- UI export (CISO/audit) | 1, 3 |
| Per-user permission query -- CLI (Support) | 2 |
| Per-user permission query -- UI (Admin) | 1, 6 |
| Structured logging / audit trail | 2, 6 |
| CLI dump/restore tool | 5 |
| Management API programmatic registration | 4, 5 |
| Authorization API < 20ms checks | 4 |
| Authorization client library | 4 |
| Cross-namespace permission visibility | 3 |
| Configurable log levels (App Center + Helm) | 2 |
| Documentation with real-world examples | 4, 5 |

## Domain-Specific Requirements

### Compliance & Regulatory

- **GDPR/DSGVO scope:** Guardian is classified as infrastructure, not a data processor. During policy evaluation, actor and target objects may contain PII (full names, addresses, birthdays) resolved from UDM.
- **PII logging constraint:** Components must log entity IDs (usernames, role names, object identifiers) at INFO level but restrict PII to TRACE level only. Applies to Management API, Authorization API, and OPA. See NFR9 for the testable requirement.
- **OPA decision log PII risk:** OPA's decision logging can include entire input documents containing PII. A **spike is required** to determine how OPA decision logs can be configured to redact PII at non-TRACE levels -- native configuration, custom plugin, or log shipper filtering. This spike must complete before the logging epic.
- **PII leak detection in CI:** Negative tests must capture log output at INFO level and assert that defined PII attributes do not appear. The forbidden attribute list must be configurable per test suite. See NFR27.
- **Audit trail:** Authorization decisions must be logged with sufficient detail to reconstruct who was authorized for what and when, without exposing PII at standard log levels.

### Technical Constraints

- **API versioning:** Both APIs must include version prefixes in URL paths (e.g., `/v1/`). Breaking changes require a new version. Non-breaking additions permitted within a version. Critical for staggered consumer adoption -- UCS@school's August integration must not break when changes are made for UDM later. See NFR10.
- **Backward compatibility policy:** API v1 endpoints must remain stable and supported for the duration of 2026. Deprecation requires at least one release cycle of overlap with the replacement version.
- **Stateless services:** All components must be stateless for horizontal scaling. No in-process session state, no local file dependencies beyond OPA's cached policy bundle. See NFR13.
- **High availability architecture:** Each Authorization API instance runs alongside a dedicated OPA sidecar. OPA regularly downloads policy bundles and operates from its local cache. If the Management API or bundle server is temporarily unavailable, authorization continues using cached policies. Operators are responsible for load balancing; Guardian must ensure this is technically possible and documented.
- **Deployment topology:** Dual targets (Kubernetes Helm chart + UCS App Center) with component-level scaling. Documentation must describe HA deployment for each target.
- **Data isolation:** SaaS deployments use separate databases per tenant. Within a single deployment, namespace-based logical separation is sufficient.
- **Policy propagation SLA:** Changes through the Management API take up to **one minute** to propagate to OPA instances (async bundle rebuild + OPA poll interval). This is documented behavior. See NFR4.

### Integration Requirements

- **UDM dependency:** The Authorization API's "with-lookup" endpoints resolve actor/target attributes from UDM's REST API. UDM availability and response time directly impact lookup-based authorization latency. "Direct" endpoints are unaffected.
- **OIDC authentication:** Management API and Management UI authenticate via OIDC (Keycloak). Configuration must be correctly applied during both App Center install/upgrade and Helm deployment.
- **Application registration contract:** Applications register namespaces, permissions, roles, and default capabilities at deployment time via the Management API. Registration must be idempotent for re-deployment and upgrade scenarios.
- **Bundle server security:** The OPA bundle endpoint must require authentication. Policy bundles encode the complete authorization configuration. See NFR7.

### Risk Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| PII exposure in logs at non-TRACE levels | GDPR violation, data breach | PII-only-at-TRACE across all components; CI tests with forbidden attribute lists; OPA decision log spike |
| OPA decision logs include full input documents | PII leak through policy engine | Spike to determine OPA log redaction capabilities; complete before logging epic |
| API breaking changes affect integrated apps | Integration breaks after update | Versioned API URLs; backward compatibility policy; non-breaking additions only within a version |
| OPA bundle server downtime | Stale policies; new changes not applied | OPA local cache; monitoring for bundle sync failures; documented recovery procedure |
| Authorization latency exceeding budget | Application slowdown | Performance benchmarking before each milestone; < 20ms target enforced in CI |
| Incorrect policy deployment (admin error) | Unauthorized access or lost access | Permission report (UI + CLI); structured logging; DELETE for cleanup |
| Database migration on upgrade | Data loss or downtime | Alembic migrations tested in CI; dump/restore CLI as backup |
| Referential integrity gaps on DELETE | Dangling references, runtime errors | Exhaustive integration test matrix; automated test generation for cross-references |

## API Backend & B2B Platform Requirements

### API Specification

- **Data format:** JSON for all API request/response bodies. Future CISO reporting may require CSV/PDF export (out of scope; format TBD).
- **Authentication:** OIDC (Keycloak) for Management API and Management UI. Service-to-service authentication for Authorization API via OIDC client credentials or bearer tokens.
- **Rate limiting:** None. Guardian is on the critical path of every application action.
- **Error handling:** Existing HTTP status code + JSON error body schema. New DELETE referential integrity violations use HTTP 409 Conflict with a body describing blocking references.
- **API documentation:** OpenAPI schema auto-generated from FastAPI. All new endpoints must be included.

### Observability

- **Health probes:** All Guardian components must expose `/health` (liveness) and `/ready` (readiness) endpoints for Kubernetes probes and App Center health monitoring. See FR25.
- **Prometheus metrics (Growth):** The Authorization API must expose a `/metrics` endpoint: request count, latency histogram (p50/p95/p99), error rate, and OPA bundle age.

### Per-User Permission Query

- **API location:** Lives in the **Management API**, which has the full picture of roles, capabilities, and conditions.
- **Response structure:** Accepts a user identifier, returns the full permission chain: roles -> capabilities -> permissions -> conditions. Not a flat permission list.
- **Client access:** Consumed via a small Python library or directly from the Management UI in JavaScript (TBD).

### Client Library

- **Authorization-client (Python):** Must be updated for all new Authorization API features. No new language bindings required. Per-user permission query is not part of this library (Management API feature).
- **Idempotent registration:** Client library and API must support idempotent create/update operations for deployment-time registration.

### Deployment & Operations

- **Bundling:** Guardian is included in all Nubus tiers. No feature gating.
- **Multi-tenancy:** Separate databases per SaaS tenant. Namespace-based logical separation within a single deployment.
- **Helm chart:** Configurable replicas, resource limits, database URI, OIDC settings, log levels, OPA bundle server configuration.
- **App Center:** Equivalent configuration options exposed as App Center settings.

### Documentation Deliverables

| # | Deliverable | Audience | Key Content |
|---|---|---|---|
| 1 | **OpenAPI Specification** | Application developers | Auto-generated from FastAPI; all endpoints |
| 2 | **Integration Guide** | Application developers | Register apps/permissions, call Authorization API, use authorization-client library; real-world examples |
| 3 | **Operations Guide** | Customer operators, SaaS DevOps | HA deployment for Kubernetes and App Center; scaling, database config, OIDC, bundle server security; propagation delay |
| 4 | **Support Handbook** | Support/PS engineers | CLI dump/restore, diagnostic workflows, per-user permission query, log interpretation, known behaviors |
| 5 | **Administrator Guide** | Customer operators | Management UI with real-world examples; role/capability/permission management; permission reports; DELETE and referential integrity |

### Implementation Considerations

- **Hexagonal architecture:** All new features must follow ports-and-adapters. New functionality implemented as adapters behind port interfaces.
- **Three model layers:** Domain dataclasses, Pydantic router models, and SQLAlchemy DB models remain separate.
- **Database migrations:** All schema changes via Alembic. Migrations tested in CI, backward-compatible within a release.
- **OPA policy generation:** Capability and role-capability-mapping changes trigger async bundle regeneration. Pipeline must handle multi-role capability assignments.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Platform MVP -- minimum feature set for UCS@school production integration with all three stakeholder readiness gates satisfied (Development, Support/PS, Customer Ops).

**Team:** 5 developers
**MVP Deadline:** August 2026 (UCS@school integration)

The MVP is a production release. The three-gate readiness model requires API features, logging, tooling, documentation, and developer experience. Features only needed for later applications (Portal, UDM) or Kubernetes-specific features are deferred.

### MVP Feature Set (Phase 1: UCS@school -- August 2026)

**Core User Journeys Supported:** Markus (sysadmin), Claudia (support), Jaime (developer), Markus error recovery

| Feature | Component | Rationale |
|---|---|---|
| DELETE operations for all entity types | Management API | Operators must clean up configuration (Epic #1000) |
| Referential integrity on DELETE | Management API | Prevent dangling references; clear error messages |
| Capabilities assignable to multiple roles | Management API | Reuse capability across school contexts (Epic #1000) |
| Structured logging (all components) | Management API, Authorization API, OPA | Support/PS must diagnose issues (Epic #1002) |
| Configurable log levels | Helm chart, App Center | Operators and support need adjustable verbosity |
| PII logging constraint enforcement | All components | GDPR compliance -- IDs at INFO, PII at TRACE only |
| PII leak detection tests in CI | Test suite | Compliance safety net; prevents regression |
| OPA decision log PII spike | Research | Must complete before logging implementation |
| Secure OPA bundle endpoint | Authorization API / OPA | Policy bundles contain full authorization config (Epic #961) |
| Configurable SQL database URI | Management API | UCS PostgreSQL default, custom DB support (Epic #961) |
| OIDC client configuration fix | Helm chart, App Center | Blocking bug -- invalid redirect URI (Epic #1004) |
| Management API bug fixes | Management API | Condition modification, Authorization API error handling (Epic #1001) |
| CLI dump/restore tool | New CLI tool | Support/PS must manage configuration (Epic #944) |
| Per-user permission query | Management API | Support must diagnose "why can't user X do Y?" |
| Authorization-client library update | authorization-client | Must support new API features for developer integration |
| API versioning (URL path prefix) | Management API, Authorization API | Protect UCS@school integration from future breaking changes |
| Documentation: Integration Guide | Docs | Developers must know how to integrate |
| Documentation: Support Handbook | Docs | Support/PS must know how to diagnose |
| Documentation: Administrator Guide | Docs | Customer ops must know how to use |
| Authorization check latency < 20ms | Authorization API | Performance requirement across all phases |

### Phase 2: Growth (Portal + early UDM -- Q3-Q4 2026)

**Additional Journeys Supported:** Stefan (CISO), Nadia (SaaS DevOps)

| Feature | Component | Rationale |
|---|---|---|
| Cross-namespace permission support | Management API, Authorization API | Portal and UDM require permissions spanning namespaces |
| Optional namespaces for roles/contexts | Management API | Portal and UDM requirement |
| DELETE operations in Management UI | Management UI | UI parity with API |
| Capabilities in multiple roles via UI | Management UI | UI parity with API |
| UI global theme compliance (light/dark) | Management UI | UCS theme standards (Epic #1004) |
| Health/readiness probes | Management API, Authorization API | Kubernetes deployment requirement |
| Prometheus metrics endpoint | Authorization API | UDM requirement -- request count, latency, error rate, bundle age |
| CISO permission matrix report (UI) | Management UI | Compliance reporting for auditors |
| Per-user permission query (UI) | Management UI | Admin self-service diagnostic |
| Documentation: Operations Guide | Docs | Kubernetes HA deployment, scaling, configuration |
| Broader character set for entity names | Management API | UDM requirement |
| New condition objects | Management API | UDM requirement |
| Management API performance optimization | Management API | UDM requirement |

### Phase 3: Expansion (Future)

| Feature | Rationale |
|---|---|
| Application-specific UIs | Tailored per-app experience beyond generic Management UI |
| Cerbos as alternative policy engine | Transparent engine swap behind existing API |
| Per-application performance benchmarking | Validate latency targets per consuming application |
| Recursive/cascading DELETE | Delete object and all dependents |
| Third-party application integration SDK | Documentation and tooling for external developers |
| CISO report export formats (CSV/PDF) | Format TBD; depends on customer feedback |

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OPA decision log PII redaction not feasible natively | Medium | High | Spike early (before logging epic); fallback to log shipper filtering |
| Authorization latency exceeds 20ms under load | Medium | High | Performance benchmarking in CI; optimize OPA policy structure if needed |
| Alembic migrations break existing data | Low | Critical | Migration tests in CI; dump/restore CLI as backup |
| Bundle regeneration introduces latency spikes | Low | Medium | Async rebuild; documented 1-minute propagation SLA |

**Schedule Risks:**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| August deadline too tight for 5 developers | Medium | High | MVP scope tightly defined; defer all Growth features |
| OPA PII spike reveals major rework | Medium | Medium | Schedule spike in first sprint; results inform logging estimation |
| UCS@school integration testing reveals new requirements | Medium | Medium | Start integration testing early; 2-week buffer before deadline |

**Resource Risks:**
- 5 developers adequate for MVP if Growth features are strictly deferred.
- First deferral candidates if a developer is lost: per-user permission query and CLI dump/restore (move to Growth).
- Minimum shippable MVP without those two features satisfies Development and Customer Ops gates but weakens Support/PS gate.

## Functional Requirements

### Entity Lifecycle Management

- **FR1:** Operators can create apps, namespaces, roles, contexts, permissions, conditions, and capabilities through the Management API.
- **FR2:** Operators can update apps, namespaces, roles, contexts, permissions, and conditions through the Management API using PATCH operations.
- **FR3:** Operators can replace capabilities through the Management API using PUT operations (full replacement).
- **FR4:** Operators can delete apps, namespaces, roles, contexts, permissions, conditions, and capabilities through the Management API.
- **FR5:** The system rejects delete operations that would create dangling references, returning a clear error identifying the blocking references.
- **FR6:** Operators can list and search entities by type, namespace, and application through the Management API.

### Capability & Role Assignment

- **FR7:** Operators can assign a single capability to multiple roles simultaneously.
- **FR8:** Operators can define capabilities with AND/OR permission relations and optional conditions.
- **FR9:** Operators can scope roles to specific contexts (e.g., a school) to restrict where permissions apply.
- **FR10:** Application deployment code can register default roles, capabilities, and permissions for an application through the Management API, idempotently.

### Authorization Decisions

- **FR11:** Applications can check whether an actor has all of a set of specific permissions for given targets (check permissions).
- **FR12:** Applications can retrieve the full set of permissions an actor has for given targets (get permissions).
- **FR13:** Applications can supply actor and target objects directly in the authorization request (direct variant).
- **FR14:** Applications can request Guardian to resolve actor and target attributes from UDM on their behalf (with-lookup variant).
- **FR15:** The authorization decision engine evaluates conditions attached to capabilities against actor, target, and request context attributes.

### Permission Reporting & Diagnostics

- **FR16:** Support engineers can query the system for all permissions a specific user has, receiving the full permission chain (roles -> capabilities -> permissions -> conditions) as structured text output via CLI.
- **FR17:** Administrators can query the system for all permissions a specific user has via the Management UI, receiving the full permission chain.
- **FR18:** CISOs can generate a permission matrix report showing all roles, their capabilities, permissions, and conditions, grouped by application namespace, exportable from the Management UI.
- **FR19:** Administrators can filter permission reports by application, namespace, context, and role.

### Logging & Observability

- **FR20:** All Guardian components produce structured log output conforming to Univention logging ADRs.
- **FR21:** Operators can configure log levels for each Guardian component independently, on both App Center and Helm deployments.
- **FR22:** The system logs entity IDs at INFO level and restricts PII to TRACE level only.
- **FR23:** The Authorization API logs authorization request details (actor ID, target IDs, requested permissions, decision) at INFO level.
- **FR24:** The Management API logs entity modification actions (create, update, delete) with actor and entity identifiers at INFO level.
- **FR25:** All Guardian components expose health (liveness) and readiness endpoints.
- **FR26:** The Authorization API exposes a Prometheus-compatible metrics endpoint with request count, latency distribution, error rate, and OPA bundle age.

### Configuration & Deployment

- **FR27:** Operators can configure the SQL database URI, defaulting to the UCS PostgreSQL instance.
- **FR28:** The OPA bundle endpoint requires authentication; unauthenticated access is rejected.
- **FR29:** The OIDC client configuration is correctly applied during both App Center install/upgrade and Helm deployment.
- **FR30:** All Guardian API endpoints include a version prefix in their URL path.
- **FR31:** The system supports horizontal scaling of all components through stateless service design.

### Support & Operations Tooling

- **FR32:** Support engineers can dump the complete Guardian configuration to a portable format using a CLI tool.
- **FR33:** Support engineers can restore a Guardian configuration from a dump file using the CLI tool, on both UCS and Kubernetes environments.
- **FR34:** The CLI tool operates against both App Center and Kubernetes deployments.

### Management UI

- **FR35:** Administrators can create, view, update, and delete all entity types through the Management UI.
- **FR36:** Administrators can assign capabilities to multiple roles through the Management UI.
- **FR37:** The Management UI respects the UCS global theme (light/dark mode).
- **FR38:** The Management UI provides the per-user permission query as an interactive feature.
- **FR39:** The Management UI provides the CISO permission matrix report with export functionality.

### Authorization Client Library

- **FR40:** Application developers can check permissions through the Python authorization-client library using the same operations as the Authorization API.
- **FR41:** Application developers can register application authorization configuration (apps, namespaces, permissions, roles, capabilities) through the Management API with idempotent operations.

### Documentation

- **FR42:** Application developers can follow an integration guide with real-world examples to register their application and implement authorization checks.
- **FR43:** Support/PS engineers can follow a support handbook to use CLI tooling, interpret structured logs, and execute diagnostic workflows.
- **FR44:** Customer operators can follow an administrator guide with real-world examples to manage roles, capabilities, and permissions through the Management UI.
- **FR45:** Customer operators and SaaS DevOps engineers can follow an operations guide to configure high-availability deployments on both Kubernetes and App Center.
- **FR46:** All new API endpoints are documented in the auto-generated OpenAPI specification.

## Non-Functional Requirements

### Performance

- **NFR1:** Authorization API check/get permissions responses complete in < 20ms (p95), excluding UDM REST API lookup time.
- **NFR2:** Management API CRUD operations complete in < 50ms (p95) for single-entity operations.
- **NFR3:** Management API bulk listing operations complete in < 10s (p95) for full result sets.
- **NFR4:** OPA policy bundle regeneration completes within 30 seconds of the database commit. Regeneration is asynchronous, does not block the API response. Combined with OPA's poll interval, this enables the one-minute propagation SLA.
- **NFR5:** Management UI renders entity lists and forms within 2 seconds of navigation.
- **NFR6:** PII leak detection CI tests add no more than 60 seconds to the test suite execution time.

### Security

- **NFR7:** The OPA bundle endpoint rejects all unauthenticated requests.
- **NFR8:** All Management API and Management UI access is authenticated via OIDC (Keycloak). No anonymous access.
- **NFR9:** PII (full names, addresses, birthdays) never appears in log output at INFO level or above. PII is restricted to TRACE level only. CI tests enforce this constraint.
- **NFR10:** API versioning prevents breaking changes from affecting existing integrations. Breaking changes require a new API version; non-breaking additions are permitted within a version.
- **NFR11:** Delete operations enforce referential integrity -- no dangling references in the database.
- **NFR12:** CLI dump/restore output does not expose credentials or secrets.

### Scalability

- **NFR13:** All Guardian components are stateless, supporting horizontal scaling via multiple instances behind a load balancer.
- **NFR14:** The system supports deployments with up to 20 registered applications, 100 roles, 500 capabilities, and 500 permission entries without degradation below performance targets.
- **NFR15:** Each Authorization API instance runs alongside a dedicated OPA sidecar. Scaling means adding API + OPA instance pairs.
- **NFR16:** Database connection pooling supports concurrent connection demands of multiple Management API instances.

### Reliability

- **NFR17:** If the Management API or bundle server is temporarily unavailable, OPA instances continue serving authorization decisions using their last-cached policy bundle.
- **NFR18:** OPA bundle sync failures are detectable through structured logs and (Growth phase) through the Prometheus bundle age metric.
- **NFR19:** Database schema migrations (Alembic) are backward-compatible within a release, allowing rollback without data loss.
- **NFR20:** Health and readiness probes accurately reflect component state -- a component reporting "ready" can serve requests.

### Integration

- **NFR21:** Authorization API maintains < 20ms response time (excluding UDM lookup) with up to 20 registered applications.
- **NFR22:** UDM REST API failures during "with-lookup" requests return a clear error, not a silent authorization denial.
- **NFR23:** OIDC token validation failures return HTTP 401 with a clear error message.
- **NFR24:** Management API correctly processes concurrent requests from multiple deployment scripts registering configurations simultaneously.

### Test Quality

- **NFR25:** All code maintains 100% unit test coverage. This is the current standard and must not regress.
- **NFR26:** All API endpoints have integration test coverage, including new DELETE, multi-role capability, and per-user permission query endpoints.
- **NFR27:** PII leak detection tests are included in CI, capturing log output at INFO level and asserting configurable forbidden PII attributes do not appear.
- **NFR28:** Referential integrity on DELETE has exhaustive integration test coverage across all entity type cross-references.
