<!--
Copyright (C) 2023-2026 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian

The Guardian is the Nubus authorization engine. It runs
[Cerbos](https://docs.cerbos.dev/) as the policy decision point (PDP) and
evaluates access requests against a set of YAML policies.

The release deliverable is the **`univention-guardian-server`** Debian package.
It runs Cerbos as a systemd-managed container on a UCS server and includes
example policies; products deliver their own policies as policy bundles
registered in LDAP (see [Policies](#policies)). The package is released through the regular UCS errata
process and is also published as the `univention-guardian` App Center component,
so other apps can depend on it via `RequiredAppsInDomain = univention-guardian`.

Cerbos exposes two listeners, both bound to `localhost` only:

- `127.0.0.1:3593` — gRPC API
- `127.0.0.1:3592` — HTTP API

> **Migration from OPA.** The Guardian previously used Open Policy Agent (OPA)
> together with a Management API, an Authorization API and a web UI. Those
> components have been retired in favour of the Cerbos package. The last commit
> containing the full OPA source is tagged **`v3.0.9-opa-final`**.
>
> No upgrade path from the OPA-based Guardian is supported. The Cerbos package is
> a fresh install; there is no automated migration of policies, roles or data
> from an existing OPA deployment.

## Documentation

- **This file** — install, operate and configure the package.
- [`docs/architecture.md`](docs/architecture.md) — design decisions, component
  layout and design concepts not yet implemented.
- [`docs/policy-bundles.md`](docs/policy-bundles.md) — how to author and register
  your own policies from another app or package.
- [`README.dev.md`](README.dev.md) — building, testing and releasing the package
  (internal developer workflows).

## Installation

Install the `univention-guardian` App Center component through the UCS App
Center, or from the command line:

```sh
univention-app install univention-guardian
```

The package is intended for Primary and Backup Directory Nodes; the App Center
component restricts the app to these roles. The systemd unit
`univention-guardian-server.service` runs the docker-compose stack as a
long-lived process and auto-starts at install; `Restart=on-failure` recovers
from container exits.

### Verify Cerbos is serving decisions

The following requests to Cerbos's HTTP API confirm that it loads
policies and returns decisions — one expected allow and one expected deny:

```sh
# Same-app: alice (guardian:myapp-admin) on a myapp resource -> EFFECT_ALLOW
curl -s http://127.0.0.1:3592/api/check/resources \
  -H 'Content-Type: application/json' \
  -d '{
  "requestId": "r1",
  "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
  "resources": [{
    "resource": {"id": "x", "kind": "guardian.management_api",
                 "attr": {"app_name": "myapp"}},
    "actions": ["read_resource"]
  }]
}'

# Cross-app: same alice on an otherapp resource -> EFFECT_DENY
curl -s http://127.0.0.1:3592/api/check/resources \
  -H 'Content-Type: application/json' \
  -d '{
  "requestId": "r2",
  "principal": {"id": "alice", "roles": ["guardian:myapp-admin"]},
  "resources": [{
    "resource": {"id": "y", "kind": "guardian.management_api",
                 "attr": {"app_name": "otherapp"}},
    "actions": ["read_resource"]
  }]
}'
```

## Configuration

The package owns two UCR variables. Setting these will restart Cerbos.

| Variable | Default | Notes |
|---|---|---|
| `guardian/cerbos/log-level` | `WARN` | One of `DEBUG`, `INFO`, `WARN`, `ERROR`. |
| `guardian/cerbos/audit-logging/enabled` | `false` | Writes Cerbos access and decision logs to stdout. |

All other settings (image pin, mount paths, listener addresses) are fixed in the
UCR-templated `/usr/share/univention-guardian-server/docker-compose.yaml` and
`config/cerbos.yaml`.

## Policies

Cerbos loads every policy under
`/usr/share/univention-guardian-server/policies/` recursively. Policies reach a
server two ways:

- **Included with the package.** `policies/default/` and `policies/examples/`
  contain illustrative policies. These are example content, not a finalized
  policy set.
- **Domain-distributed bundles.** Any app or package can register its own
  policies as a `settings/data` object in LDAP. The included listener
  (`cerbos-policies.py`) installs each bundle into a per-app subdirectory
  (`policies/<app>/`) on every server running Cerbos, validates it with
  `cerbos compile`, and restarts Cerbos to apply it. See
  [`docs/policy-bundles.md`](docs/policy-bundles.md).

For a local test on a single server, copy policy files into a per-app
subdirectory and restart Cerbos:

```sh
cp my_policy.yaml /usr/share/univention-guardian-server/policies/<app-name>/
systemctl restart univention-guardian-server.service
```

Two constraints of the on-disk model:

- **No hot-reload.** Cerbos runs with `watchForChanges: false`, so editing a
  YAML file has no effect until Cerbos restarts. Manual on-disk edits are also
  lost on the next package upgrade.
- **Do not name a policy file `*_test.yaml`.** Cerbos treats those as test
  files, not policies, and silently ignores them at runtime.

## Current limitations

- **No transport authentication.** Cerbos is bound to localhost only, but any
  caller on the server can reach it
  ([guardian#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/288)).
- **No server-role check** in the deb. Install it only on Primary or Backup
  Directory Nodes (the App Center component enforces this; installing the `.deb`
  directly does not).

See [`docs/architecture.md`](docs/architecture.md) for the reasoning behind
these and the planned work.
