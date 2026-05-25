# Measurements

## Baseline (before any changes)

| Image | Components | SBOM KB | VEX entries | VEX KB |
|---|---|---|---|---|
| `management-api` | 259 | 352 | | |
| `authorization-api` | 156 | 264 | | |
| `opa` | 190 | 308 | | |
| `management-ui` | | | | |
| **Total** (excl. `management-ui`) | 605 | 924 | | |

Note: `management-api` already bundles the OPA binary in its production Dockerfile, so the
standalone `opa` image is a duplicate of that bundling on top of `ucs-base-flex`. Approach 1
is therefore "stop publishing the redundant image" — `guardian-server` after approach 1
equals `management-api` today.

---

## After each approach

### After 1 — OPA unified into management-api image

| Image | Components | SBOM KB | VEX entries | VEX KB | Component delta |
|---|---|---|---|---|---|
| `guardian-server` | 259 | 352 | | | 0 vs `management-api` |
| `authorization-api` | 156 | 264 | | | 0 |
| `management-ui` | | | | | |
| **Total** (excl. `management-ui`) | 415 | 616 | | | −190 vs baseline |

### After 2 — Distroless Python base

| Image | Components | SBOM KB | VEX entries | VEX KB | Component delta |
|---|---|---|---|---|---|
| `guardian-server` | 179 | 192 | | | −80 vs After 1 |
| `authorization-api` | 156 | 264 | | | 0 |
| `management-ui` | | | | | |
| **Total** (excl. `management-ui`) | 335 | 456 | | | −80 vs After 1 |

### After 3 — authorization-api unified into management-api image

| Image | Components | SBOM KB | VEX entries | VEX KB | Component delta |
|---|---|---|---|---|---|
| `guardian-server` | 190 | 204 | | | +11 vs After 2 |
| `management-ui` | | | | | |
| **Total** (excl. `management-ui`) | 190 | 204 | | | −145 vs After 2 |

Adding authorization-api to the distroless `guardian-server` cost only 11 components / 12 KB,
because ~145 of authorization-api's 156 standalone components were already shared with
management-api (FastAPI, pydantic, uvicorn, the Python runtime, etc.).

### After 4 — management-ui absorbed into guardian-server

| Image | Components | SBOM KB | VEX entries | VEX KB | Component delta |
|---|---|---|---|---|---|
| `guardian-server` | | | | | |
| **Total** | | | | | |

---

## Reference baselines

Anchor images used to decompose the totals above.

| Image | Components | SBOM KB |
|---|---|---|
| `ucs-base-flex:5.2.5` | 91 | 212 |
| `guardian-opa` (after 1, OPA image still standalone) | 190 | 308 |

`ucs-base-flex` ≈ UCS Debian base with no Python. Subtracting it from the OPA image gives
the OPA static binary's Go-module contribution: **~99 components**, which is a floor for any
image that bundles the OPA binary.

---

## SBOM — Trivy (local, per image)

Generate a CycloneDX SBOM for each production image using Trivy and count components.
Component count is more stable and comparable than file size.

```bash
# Generate SBOM for one image
trivy image --format cyclonedx --output <image>-sbom.json <image>:<tag>

# Count packages
jq '.components | length' <image>-sbom.json

# File size in KB
du -k <image>-sbom.json
```

## VEX — vul-man (requires Dependency-Track)

VEX reflects the triage state in Dependency-Track and can only be measured after the image
has been imported and findings have been triaged. The two-step flow:

```bash
# Step 1: import the image into Dependency-Track (generates and uploads SBOM)
docker compose run --rm vul-man \
  --dep-track-api-uri "$DEP_TRACK_API_URI" \
  --dep-track-api-key "$DEP_TRACK_API_KEY" \
  import-helm guardian \
  --helm-chart-version <version> \
  --helm-repository-url oci://artifacts.software-univention.de/nubus-dev/charts

# Step 2: export VEX + SBOM from Dependency-Track
docker compose run --rm vul-man \
  --dep-track-api-uri "$DEP_TRACK_API_URI" \
  --dep-track-api-key "$DEP_TRACK_API_KEY" \
  export-vex-sbom guardian \
  --helm-chart-version <version> \
  --oci-registry-username <user> \
  --oci-registry-token <token> \
  --cosign-key /path/to/key

# Count VEX entries (vulnerability assessments)
jq '.vulnerabilities | length' <image>-vex.json

# File size in KB
du -k <image>-vex.json
```

For local branch measurements, build and push the image first, then run `import-helm`
against the locally-built tag before exporting.

---

