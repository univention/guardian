# Current State — Guardian

This document is a baseline snapshot of Guardian's container images, packages, and services
as they exist at the start of the package-reduction initiative. The goal of that initiative
is to shrink SBOM and VEX size, which directly reduces CVE triage volume.

Last updated: 2026-05-21

---

## Production container images

| Image | Base | Language runtime | Container process |
|---|---|---|---|
| `management-api` | UCS `base-python` | Python 3.11 | `management-api` |
| `authorization-api` | UCS `base-python` | Python 3.11 | `authorization-api` |
| `opa` | Alpine | Go (OPA 1.11.0) | `opa` |
| `management-ui` | Alpine + nginx | Node 24 (build only) | `management-ui` |

**Total: 4 production images, 4 container processes**

## Dev / CI-only images (not in scope)

| Image | Purpose |
|---|---|
| `keycloak` | OIDC provider for local dev environment |
| `keycloak-provisioning` | One-shot Keycloak realm setup for local dev |
| `testrunner` | CI test execution |

---

## Python dependencies per image

Dependencies are managed via a `uv` workspace. Versions are pinned in `uv.lock`.

### management-api

Core packages (direct dependencies):

| Package | Purpose |
|---|---|
| FastAPI | HTTP framework |
| Gunicorn + Uvicorn | WSGI/ASGI server |
| SQLAlchemy + Alembic | ORM + migrations |
| asyncpg + aiosqlite | PostgreSQL and SQLite drivers |
| Pydantic | Data validation |
| Authlib + PyJWT | OAuth2 / JWT handling |
| Loguru | Logging |
| httpx | Async HTTP client |
| guardian-lib | Shared ports/adapters (internal) |

OPA CLI binary is also bundled in this image (used for policy bundle management).

### authorization-api

| Package | Purpose |
|---|---|
| FastAPI | HTTP framework |
| Gunicorn + Uvicorn | WSGI/ASGI server |
| opa-client | OPA REST client |
| Pydantic | Data validation |
| Requests + uritemplate | HTTP client |
| Loguru | Logging |
| Cryptography | Token verification |
| guardian-lib | Shared ports/adapters (internal) |

---

## Frontend dependencies (management-ui)

Runtime (shipped in the built image):

| Package | Purpose |
|---|---|
| Vue 3 + Vue Router + Pinia | Framework, routing, state |
| Keycloak-JS 26.0.5 | OIDC client |
| @univention/univention-veb | Univention component library |
| i18next + i18next-vue | Internationalisation |
| Stylus | CSS preprocessor |

The image ships only the compiled static output (HTML/JS/CSS). The Node runtime and all
dev/build dependencies (Vite, TypeScript, ESLint, Playwright, Vitest, etc.) are **not**
present in the production image.

---

## Supporting services (not part of the Guardian release images)

| Service | Shipped by | Notes |
|---|---|---|
| PostgreSQL | Nubus / UCS infrastructure | Guardian does not own this image |
| Traefik | Nubus / UCS infrastructure | Reverse proxy, not owned by Guardian |

---

## Observations relevant to reduction work

1. **Two Python API images share almost all dependencies** — `management-api` and `authorization-api`
   are separate images with overlapping dependency trees. Consolidation or slimming shared
   transitive deps would affect both.

2. **OPA binary in management-api** — The OPA CLI is bundled into `management-api` for policy
   bundle management. This pulls in a Go binary and inflates the image and its SBOM.

3. **UCS `base-python` base image** — The Python images inherit from Univention's base image.
   The packages present in that base are a significant source of CVEs outside Guardian's
   direct control. Switching to a distroless base eliminates this entirely.

---

## What to measure

To track progress, compare these metrics before and after any reduction change:

- SBOM package count per image (output of `syft` or equivalent)
- Total CVE count across all images (output of `grype` or equivalent)
- Triaged-as-false-positive CVE count (reduction in triage load)
- Image layer count and compressed size (secondary indicator)
