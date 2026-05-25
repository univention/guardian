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

---

## Simplification approaches

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
