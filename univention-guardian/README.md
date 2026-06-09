# univention-guardian — Cerbos PoC

A standalone UCS package that runs [Cerbos](https://docs.cerbos.dev/) as
a policy engine on a UCS primary. Cerbos is reachable on
`127.0.0.1:3592` by default; an optional oauth2-proxy in front of it
gates traffic on a Keycloak-issued bearer token.

The goal is to evaluate whether Cerbos can replace OPA in Guardian. This
package does not change Guardian itself — it runs in parallel so we can
compare. Tracking issue:
[guardian#286](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/286).

## Decisions

- **Scope**: standalone on the UCS primary. No changes to Guardian's
  existing `authorization-api` / `management-api` / `management-ui`.
- **Policies live as YAML files on the primary** under
  `/usr/share/univention-guardian/policies` (product-shipped, in the
  deb). `apt upgrade` replaces them, so local edits are lost on
  upgrade.
- **Only product ships rules.** Defaults are baked into the package;
  upgrades replace them.
- **Authentication is opt-in.** Default is unauthenticated, Cerbos
  bound to `127.0.0.1:3592` (localhost only). Setting
  `ucr set guardian/authentication=true` and re-running the join
  script switches on the oauth2-proxy and exposes `:8593` to the
  network, gated on a Keycloak bearer.
- **Service auto-starts at install.** No manual enable needed for the
  default (unauth) path.
- **First scenario translated**: Guardian's `<app>-admin` capability
  (CRUD on management-api resources where `app_name` matches). One
  Cerbos resource policy + one derived role; test file locks in the
  ALLOW/DENY behavior.

## Install

The deb is built and published via CI. On a UCS primary, add the apt
source for this branch:

```sh
echo "deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian rowino-cerbos-poc main" \
  | sudo tee /etc/apt/sources.list.d/guardian-cerbos.list
sudo apt update
sudo apt install -y docker-compose univention-guardian
```

That's it. The systemd unit auto-starts Cerbos bound to
`127.0.0.1:3592`. Verify with the steps below.

To switch on authentication later, see "Enable Keycloak authentication"
further down.

## Verify it's working

```sh
sudo systemctl is-active univention-guardian.service    # active
sudo docker ps                                           # guardian-cerbos healthy

# Same-app: alice (guardian:myapp-admin) on a myapp resource → ALLOW
curl -s -X POST -H "Content-Type: application/json" -d '{
  "requestId": "r1",
  "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
  "resources": [{
    "resource": {"id": "x", "kind": "guardian.management_api",
                 "attr": {"app_name": "myapp"}},
    "actions": ["read_resource"]
  }]
}' http://127.0.0.1:3592/api/check/resources

# Cross-app: same alice on an otherapp resource → DENY
curl -s -X POST -H "Content-Type: application/json" -d '{
  "requestId": "r2",
  "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
  "resources": [{
    "resource": {"id": "y", "kind": "guardian.management_api",
                 "attr": {"app_name": "otherapp"}},
    "actions": ["read_resource"]
  }]
}' http://127.0.0.1:3592/api/check/resources
```

To compile and self-test the policies in the installed tree:

```sh
sudo univention-guardian-test
```

This runs Cerbos's compiler against the shipped policies plus the test
files; expect "38 tests executed [38 OK]".

Hot-reload: edit a YAML file under `/usr/share/univention-guardian/policies/`
and Cerbos picks it up within ~3 s (`journalctl -u univention-guardian.service`
shows the reload). Note these edits are lost on next package upgrade.

Do **not** name a policy file `*_test.yaml` — Cerbos treats those as
test files (not policies) and silently ignores them at runtime.

## Enable Keycloak authentication

By default Cerbos is unauthenticated on localhost only. To gate access
on a Keycloak bearer token, the UCS primary needs the Keycloak app:

```sh
sudo univention-app install keycloak
```

Then opt in and re-run the join script:

```sh
sudo ucr set guardian/authentication=true
sudo univention-run-join-scripts --force --run-scripts univention-guardian.inst
```

This provisions an OIDC client `guardian-cerbos` in the `ucs` realm,
writes the JWKS URL / issuer URL / cookie secret into UCR, re-renders
the proxy and Cerbos configs, and restarts the service. The proxy now
listens on `0.0.0.0:8593` and Cerbos itself stays on
`127.0.0.1:3592`.

### One-time client setup for service-to-service calls

The join script creates the client with `serviceAccountsEnabled: false`
(interactive flows only). To call Cerbos from another service via the
`client_credentials` grant, enable service accounts and grab the
client secret:

```sh
sudo univention-keycloak --bindpwdfile /etc/keycloak.secret \
  oidc/rp update guardian-cerbos '{"serviceAccountsEnabled": true}'

# Print the client secret (treat as a credential):
sudo univention-keycloak --bindpwdfile /etc/keycloak.secret \
  oidc/rp get --client-id guardian-cerbos --all --json \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)[0]["secret"])'
```

### Request a token and call Cerbos

```sh
ISSUER="$(ucr get guardian/cerbos/keycloak/issuer-url)"
CLIENT_ID="$(ucr get guardian/cerbos/keycloak/client-id)"
CLIENT_SECRET=…  # from the command above

TOKEN=$(curl -s --cacert /etc/univention/ssl/ucsCA/CAcert.pem \
  -X POST "$ISSUER/protocol/openid-connect/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')

curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{
    "requestId": "r1",
    "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
    "resources": [{
      "resource": {"id": "x", "kind": "guardian.management_api",
                   "attr": {"app_name": "myapp"}},
      "actions": ["read_resource"]
    }]
  }' http://localhost:8593/api/check/resources
```

Expected: `EFFECT_ALLOW` for `app_name="myapp"`, `EFFECT_DENY` for
`app_name="otherapp"`, **HTTP 401** for any request without (or with
an invalid) bearer.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `apt install` fails on `docker-compose` | Not preinstalled on UCS 5 | `sudo apt install docker-compose` first |
| Service active but no `guardian-oidc-proxy` container | `guardian/authentication=false` (default) | Expected. To enable, see "Enable Keycloak authentication" |
| Join script `die`d with "Keycloak is not reachable" | `guardian/authentication=true` but the Keycloak app isn't installed | `sudo univention-app install keycloak`, then re-run the join script |
| `guardian-oidc-proxy` keeps restarting with `x509: certificate signed by unknown authority` | Container doesn't trust the UCS root CA | Already handled by mounting `/etc/univention/ssl/ucsCA/CAcert.pem` and setting `SSL_CERT_FILE`. If you've replaced the UCS CA, restart the service |
| `401` with valid token, proxy log says `email in id_token () isn't verified` | Token has no email claim (typical for service-account tokens) | Already handled by `oidc_email_claim = "preferred_username"` in the proxy config |
| Cerbos refuses to start with `keyset 'keycloak': remote URL is empty` | `guardian/authentication=true` set but the join script hasn't run since | Run `sudo univention-run-join-scripts --force --run-scripts univention-guardian.inst` |
| Added a policy file under `/usr/share/univention-guardian/policies/` but `EFFECT_DENY` says it's not loaded | Filename ends in `_test.yaml`; Cerbos treats it as a test file | Rename to something without the `_test` suffix |

UCR variables this package owns:

| Variable | Default | Set by |
|---|---|---|
| `guardian/authentication` | `false` | operator (opt-in to OIDC) |
| `guardian/cerbos/keycloak/issuer-url` | — | join script (when auth=true) |
| `guardian/cerbos/keycloak/jwks-url` | — | join script (when auth=true) |
| `guardian/cerbos/keycloak/client-id` | `guardian-cerbos` | join script (when auth=true) |
| `guardian/cerbos/proxy/cookie-secret` | — | join script (when auth=true) |

All other knobs (image pin, log level, mount paths) are hardcoded in
the UCR-templated `/usr/share/univention-guardian/docker-compose.yaml`.
Edit the template under `/etc/univention/templates/files/...` and
`ucr commit` to override.

## PoC limitations

These are intentional gaps — fine for the PoC, would need to be
addressed before any production use.

- **No TLS on the proxy.** Port `:8593` is plain HTTP.
- **No firewall rule.** The PoC assumes you reach the proxy from a
  workstation on the same network.
- **No primary-role gate** in the deb. Just don't install it on a
  non-primary.
- **No audience whitelisting** beyond the join-provisioned client ID.
  If test tokens carry an unexpected `aud`, oauth2-proxy will reject
  them — add issuers via `oidc_extra_audiences` in the proxy config.
- **`serviceAccountsEnabled` is off by default** on the OIDC client.
  An operator has to enable it to use `client_credentials`. See
  "Enable Keycloak authentication" above.
- **No override directory for shipped policies.** Edits under
  `/usr/share/univention-guardian/policies/` are overwritten by
  `apt upgrade`. To add policies that survive upgrades, ship them in
  a separate package or extend Cerbos's storage driver.

---

## Appendix — hiccups encountered during development

For reviewers / future-us, the non-obvious problems we hit and how
they're handled now:

### 1. `.inst` / `.uinst` location

`dh-univention-join-install` looks for `*<package>.inst` files at the
**source tree root**, not under `debian/`. The starter branch had them
in `debian/`, where they were silently dropped from the deb. Fixed by
moving to `univention-guardian/univention-guardian.inst` /
`.uinst` at the package root.

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
provisioning entirely when `guardian/authentication=false` (default).
When auth is set to true, it `die`s with a clear error if Keycloak
isn't reachable.

### 6. UCS root CA not trusted by containers

oauth2-proxy and Cerbos run in containers, which don't trust the UCS
self-signed root CA by default. JWKS fetches and OIDC discovery against
`https://ucs-sso-ng.<domain>/...` fail with `x509: certificate signed
by unknown authority`. Fixed by mounting `/etc/univention/ssl/ucsCA/CAcert.pem`
into both containers and pointing `SSL_CERT_FILE` at it.

### 7. Service-account tokens have no verified email

Tokens from the `client_credentials` grant don't include an `email`
claim, but oauth2-proxy's default config requires a verified email.
Fixed by setting `oidc_email_claim = "preferred_username"` in the
proxy config — the service-account user has a stable
`preferred_username` (e.g. `service-account-guardian-cerbos`).

### 8. Cerbos refuses to start with an empty `auxData.jwt` URL

Cerbos validates `auxData.jwt.keySets[].remote.url` at startup and
errors out if it's empty. Initially the template emitted the block
unconditionally; with `guardian/authentication=false` the join script
doesn't populate the URL, so Cerbos crashed. Fixed by wrapping the
`auxData` block in a UCR Python conditional that only emits it when
`guardian/authentication=true`.

## Verified on `claude-vm` (UCS 5.2-6)

Default (unauthenticated) flow:

- `dpkg-buildpackage -us -uc -b` produces the `.deb`.
- `apt install univention-guardian` (after `apt install docker-compose`)
  → service auto-starts, `guardian-cerbos` container healthy on
  `127.0.0.1:3592`.
- `curl http://127.0.0.1:3592/api/check/resources` returns
  `EFFECT_ALLOW` / `EFFECT_DENY` as expected for the `<app>-admin`
  scenario.
- `univention-guardian-test` → 38/38 policy tests pass.
- Hot-reload of an edited YAML file in
  `/usr/share/univention-guardian/policies/` works.

Authentication flow:

- `univention-app install keycloak` + `ucr set guardian/authentication=true`
  + force-rerun of the join script → OIDC client provisioned, both
  containers up (Cerbos on `127.0.0.1:3592`, oauth2-proxy on
  `0.0.0.0:8593`).
- After enabling `serviceAccountsEnabled` on the client, the
  `client_credentials` grant yields a bearer that oauth2-proxy
  accepts. `curl https://localhost:8593/api/check/resources` with the
  bearer → ALLOW/DENY as expected; without it → 401.
