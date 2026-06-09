# Architecture -- Guardian Cerbos PoC

**Date:** 2026-06-09
**Version:** 0.0.1
**Type:** Standalone UCS Debian package

---

## Executive Summary

Standalone UCS package (`univention-cerbos-server`) that runs
[Cerbos](https://docs.cerbos.dev/) as a policy engine on a UCS primary.
The goal is to evaluate whether Cerbos could replace OPA as Guardian's
policy backend, **without** touching the existing Guardian services. The
package ships with a small set of YAML policies translated from
Guardian's current OPA-based capabilities, plus an opt-in oauth2-proxy
that gates the Cerbos endpoint on a Keycloak-issued bearer.

This is a Proof of Concept. It does not change Guardian's
`authorization-api` / `management-api` / `management-ui` and is not
intended for production.

---

## Decisions

| Decision | Rationale |
|---|---|
| **Standalone** on the UCS primary | No changes to existing Guardian services; safe to add and remove without affecting current authorization paths |
| **Policies as YAML** under `/usr/share/univention-cerbos-server/policies` | Shipped in the deb. Single dir (no shipped/admin split) — Cerbos's disk driver has no shadow semantics, so a dual-mount design was abandoned |
| **Product-shipped only** | Defaults are baked into the package; `apt upgrade` replaces them. A multi-package "register policies across debs" mechanism is the subject of [guardian#286 follow-up issues](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues) |
| **Authentication is opt-in** (`cerbos/authentication`, default `false`) | Default install needs only `apt install`; no Keycloak dependency. Opt-in via UCR flips the auth path on |
| **oauth2-proxy fronts Cerbos** when auth is on | Cerbos has no built-in bearer verification; oauth2-proxy in API mode (`api_routes = ["^/"]`) returns 401 on missing/invalid token instead of redirecting |
| **Service auto-starts** at install | No `--no-enable --no-start` override on `dh_installsystemd`; default flow needs no manual `systemctl` |
| **First scenario translated**: Guardian's `<app>-admin` capability | CRUD on management-api resources where `app_name` matches. One Cerbos resource policy + one derived role; policy tests lock in ALLOW/DENY |

---

## Component Layout

```text
/usr/share/univention-cerbos-server/
├── docker-compose.yaml      ─── UCR-templated; conditionally includes oidc-proxy
├── config/config.yaml       ─── Cerbos config; auxData.jwt block is UCR-conditional
├── proxy/oauth2-proxy.cfg   ─── Keycloak provider config, bearer-only mode
└── policies/
    ├── *.yaml               ─── Product-shipped policies (loaded by Cerbos)
    ├── examples/            ─── UDM/helpdesk/ouadmin example policies
    └── tests/               ─── Policy test files (not loaded by Cerbos)

/usr/sbin/univention-cerbos-server-test   ─── compile + run policy tests against the installed tree
/usr/lib/univention-install/90univention-cerbos-server.inst
/usr/lib/univention-uninstall/20univention-cerbos-server.uinst
```

The systemd unit `univention-cerbos-server.service` runs the docker-compose
stack as a long-lived process; `Restart=on-failure` recovers from
container exits.

---

## Authentication Flow

When `cerbos/authentication=true`:

```text
client (with Keycloak bearer)
    │
    ▼
oauth2-proxy :8593         ─── verifies signature vs Keycloak JWKS,
    │                          checks aud == client_id, 401s on failure
    ▼
cerbos-server :3592      ─── re-verifies bearer into auxData.jwt
                               for use in policy conditions
```

The proxy and Cerbos share an internal docker network; only the proxy
publishes a host port. Cerbos's `:3592` is published to `127.0.0.1` so
operators can curl it from the host for testing (in either auth mode).

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `apt install` fails on `docker-compose` | Not preinstalled on UCS 5 | `sudo apt install docker-compose` first |
| Service active but no `cerbos-oidc-proxy` container | `cerbos/authentication=false` (default) | Expected. To enable, see the README |
| Join script `die`d with "Keycloak is not reachable" | `cerbos/authentication=true` but the Keycloak app isn't installed | `sudo univention-app install keycloak`, then re-run the join script |
| `cerbos-oidc-proxy` restart-loops with `x509: certificate signed by unknown authority` | Container doesn't trust the UCS root CA | Already handled by mounting `/etc/univention/ssl/ucsCA/CAcert.pem` and setting `SSL_CERT_FILE`. If you've replaced the UCS CA, restart the service |
| `401` with valid token, proxy log says `email in id_token () isn't verified` | Token has no email claim (typical for service-account tokens) | Already handled by `oidc_email_claim = "preferred_username"` in the proxy config |
| Cerbos refuses to start with `keyset 'keycloak': remote URL is empty` | `cerbos/authentication=true` set but the join script hasn't run since | Run `sudo univention-run-join-scripts --force --run-scripts 90univention-cerbos-server.inst` |
| Added a policy file under `/usr/share/univention-cerbos-server/policies/` but `EFFECT_DENY` says it's not loaded | Filename ends in `_test.yaml`; Cerbos treats it as a test file | Rename to something without the `_test` suffix |

### UCR variables this package owns

| Variable | Default | Set by |
|---|---|---|
| `cerbos/authentication` | `false` | operator (opt-in to OIDC) |
| `cerbos/keycloak/issuer-url` | — | join script (when auth=true) |
| `cerbos/keycloak/jwks-url` | — | join script (when auth=true) |
| `cerbos/keycloak/client-id` | `cerbos-server` | join script (when auth=true) |

The oauth2-proxy cookie secret is generated in the `postinst` and
stored at `/etc/univention/cerbos-server.secret` (root-only);
docker-compose passes it to the proxy via `env_file`.

All other knobs (image pin, log level, mount paths) are hardcoded in
the UCR-templated `/usr/share/univention-cerbos-server/docker-compose.yaml`.
Edit the template under `/etc/univention/templates/files/…` and
`ucr commit` to override.

---

## Appendix -- Hiccups encountered during development

Non-obvious problems we hit and how they're handled now.

### 1. `.inst` / `.uinst` location

`dh-univention-join-install` looks for `*<package>.inst` files at the
**source tree root**, not under `debian/`. The starter branch had them
in `debian/`, where they were silently dropped from the deb. Fixed by
moving to the package source root.

### 2. oauth2-proxy `bearer_token_login_fallback` doesn't exist in v7.8.2

The plan called for that option to make the proxy 401 on missing
bearer. It's not in v7.8.2 (`--help` confirms). Replaced with
`api_routes = ["^/"]` — same intent, return 401 instead of redirecting.

### 3. Cookie secret format

oauth2-proxy requires `cookie_secret` to decode to exactly 16, 24, or
32 raw bytes. `head -c 32 /dev/urandom | base64` adds `=` padding that
decodes to 33 bytes and gets rejected. Switched to
`python3 -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'`.

### 4. Cerbos has no shadow-override semantics

Two policies with the same `(resource, version)` raise
`duplicate policy definitions` — Cerbos drops the duplicate rather
than letting one shadow the other. This killed an early idea of
splitting policies into shipped `defaults/` and admin-writable
`overrides/`. Layout simplified to a single `policies/` directory.

### 5. Join script assumed Keycloak presence

`univention-keycloak` is on every primary as a binary but fails if no
Keycloak realm is reachable. The join script now skips Keycloak
provisioning entirely when `cerbos/authentication=false` (default).
When auth is set to true, it `die`s with a clear error if Keycloak
isn't reachable.

### 6. UCS root CA not trusted by containers

oauth2-proxy and Cerbos run in containers, which don't trust the UCS
self-signed root CA by default. JWKS fetches and OIDC discovery
against `https://ucs-sso-ng.<domain>/…` fail with `x509: certificate
signed by unknown authority`. Fixed by mounting
`/etc/univention/ssl/ucsCA/CAcert.pem` into both containers and
pointing `SSL_CERT_FILE` at it.

### 7. Service-account tokens have no verified email

Tokens from the `client_credentials` grant don't include an `email`
claim, but oauth2-proxy's default config requires a verified email.
Fixed by setting `oidc_email_claim = "preferred_username"` in the
proxy config — the service-account user has a stable
`preferred_username` (e.g. `service-account-cerbos-server`).

### 8. Cerbos refuses to start with an empty `auxData.jwt` URL

Cerbos validates `auxData.jwt.keySets[].remote.url` at startup and
errors out if it's empty. Initially the template emitted the block
unconditionally; with `cerbos/authentication=false` the join script
doesn't populate the URL, so Cerbos crashed. Fixed by wrapping the
`auxData` block in a UCR Python conditional that only emits it when
`cerbos/authentication=true`.
