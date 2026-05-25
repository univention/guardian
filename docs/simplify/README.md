# Guardian — Container Simplification

## The problem

A full Nubus release scans ~40 container images. The resulting SBOM and VEX size creates a
CVE triage workload that strains infrastructure and consumes significant engineering time.
Reducing the number of containers and the packages inside them is the most effective way to
shrink that surface at the root.

Guardian currently ships **4 production images, 4 container processes**. The goal is
**1 image** (`guardian-server`) running as **3 container processes** — the management-ui
process is the only one that gets merged (into the Python server via approach 4).
`opa`, `management-api`, and `authorization-api` keep their separate processes.

See [current-state.md](current-state.md) for the baseline.

Approaches 1–3 implemented and measured: backend images go from 3 → 1, components from
605 → 190 (−69%). See the [impact summary](#impact-summary) below.

---

## Implemented simplifications

### 1. Unify OPA into the management-api image

Build OPA into the `management-api` image so the `opa` container process can run from the
same image. The `opa` process stays separate; only the dedicated `opa` image is eliminated.

### 2. Switch to a distroless Python base image

Replace the Debian-based UCS `base-python` image with a distroless Python image. Distroless
images contain only the language runtime and the application — no shell, no package manager,
no OS userspace. This eliminates the largest single source of CVEs in the Python images.

### 3. Unify authorization-api into the management-api image

Both are Python/FastAPI services with heavily overlapping dependencies. Build them into a
single image with separate entrypoints. The `authorization-api` process stays separate;
one image is eliminated and the duplicated dependency footprint halved.

## Future simplifications

### 4. Absorb management-ui → merge image and process into `guardian-server`

Switch from Gunicorn/Uvicorn to [Granian](https://github.com/emmett-framework/granian)
(a Rust-based ASGI server). Add the Vue frontend build as a separate Docker stage and serve
the compiled static files directly from Granian — no nginx, no separate UI image or process.

This is the only approach that also eliminates a container process, merging `management-ui`
into the Python server. The result is a single `guardian-server` image, 3 processes.

### 5. Unify authorization-api and management-api into one FastAPI process

Mount both APIs into a single FastAPI application with separate router prefixes. This
eliminates the second Python server process entirely — one Granian worker serves both APIs.
Requires that the two apps have no conflicting middleware, startup logic, or configuration,
which needs to be verified first.

---

## Impact summary

| Approach | Images | Components | Notes |
|---|---|---|---|
| Baseline | 3 | 605 | mgmt-api + opa + authz |
| After 1 | 2 (−1) | 415 (−190) | opa image gone |
| After 2 | 2 | 335 (−80) | distroless mgmt-api |
| After 3 | 1 (−1) | 190 (−145) | authz folded in |

Counts exclude `management-ui` (not yet measured). See [measurements.md](measurements.md)
for per-image breakdowns and SBOM file sizes.
