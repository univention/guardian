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

Cerbos exposes an HTTP API on `3592` and a gRPC API on `3593`, published on the
host loopback interface and reachable from containers on the shared `guardian`
Docker network.

> **Migration from OPA.** The Guardian previously used Open Policy Agent (OPA)
> together with a Management API, an Authorization API and a web UI. Those
> components have been retired in favour of the Cerbos package. The last commit
> containing the full OPA source is tagged **`v3.0.9-opa-final`**.
>
> No upgrade path from the OPA-based Guardian is supported. The Cerbos package is
> a fresh install; there is no automated migration of policies, roles or data
> from an existing OPA deployment.

## Documentation

- **This file** - install, operate and configure the package, manage its
  policies, and call it from your own service.
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

## Accessing the Cerbos endpoint

A native host process uses the published loopback port, `http://127.0.0.1:3592`.

A container cannot reach that interface, so it joins the shared `guardian`
network instead and addresses Cerbos by its DNS name:

```yaml
# your service's docker-compose.yaml
services:
  my-service:
    environment:
      CERBOS_URL: http://cerbos:3592
    networks:
      - guardian
networks:
  guardian:
    external: true
```

For a single-container App Center app, set this UCR variable from the app's
`preinst`, which runs before the container is started. `--network guardian` is
then added to the container's docker parameters:

```sh
ucr set appcenter/apps/<app-id>/docker/params='--network guardian'
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

Write policies in the Cerbos policy language. Upstream documents the format:
[resource policies](https://docs.cerbos.dev/cerbos/latest/policies/resource_policies),
[derived roles](https://docs.cerbos.dev/cerbos/latest/policies/derived_roles) and
[conditions](https://docs.cerbos.dev/cerbos/latest/policies/conditions).

Two constraints of the on-disk model:

- **No hot-reload.** Cerbos runs with `watchForChanges: false`, so editing a
  YAML file has no effect until Cerbos restarts. Manual on-disk edits are also
  lost on the next package upgrade.
- **Do not name a policy file `*_test.yaml`.** Cerbos treats those as test
  files, not policies, and silently ignores them at runtime.

Cerbos has no shadow-override semantics. Two policies for the same resource and
version raise a `duplicate policy definitions` error and one of them is
discarded. Your policies can add resources and actions, but they cannot replace
a policy that another bundle already defines.

### Manage policies on a UCS server

List what a server currently loads:

```sh
ls -R /usr/share/univention-guardian-server/policies/
```

Each subdirectory is one source. `default/` and `examples/` come from the
package. Every other subdirectory is named after the `app` value of a
registered bundle.

To try a policy on a single server, copy it into a per-app subdirectory and
restart Cerbos:

```sh
mkdir -p /usr/share/univention-guardian-server/policies/<app-name>/
cp my_policy.yaml /usr/share/univention-guardian-server/policies/<app-name>/
systemctl restart univention-guardian-server.service
```

Use this for local experiments only. The next package upgrade removes the file,
and the change reaches no other server in the domain. Register a policy bundle
once the policy is ready.

### Test a policy before you ship it

Compile the policy directory and run its test suites. This needs no UCS server:

```sh
docker run --rm -v "$PWD/my-policies:/policies" \
  ghcr.io/cerbos/cerbos:0.54.0 compile /policies
```

`cerbos compile` reports syntax and reference errors, and it runs every
`*_test.yaml` file it finds. A successful compile proves that the policy is
valid, not that it grants what you intend. Write Cerbos tests for the decisions
that matter. See
[validating and testing policies](https://docs.cerbos.dev/cerbos/latest/policies/compile).

The same compile step runs on the server. The listener rejects a bundle that
does not compile and keeps the previous policies in place.

### Diagnose a policy that does not work

Read the Cerbos log to see which policies loaded and why a policy was skipped:

```sh
journalctl -u univention-guardian-server.service
```

Read the listener log to see whether a bundle was installed or rejected:

```sh
grep cerbos-policies /var/log/univention/listener.log
```

Set `guardian/cerbos/log-level` to `DEBUG` for more detail, and
`guardian/cerbos/audit-logging/enabled` to `true` to log the requests and the
decisions. Reset both when you finish. Debug logs and audit logs contain
request payloads.

### Nubus for Kubernetes

Nubus for Kubernetes has no Cerbos deployment today. The Guardian package and
the policy bundle mechanism are available on UCS only.

## Integrating your service

Your service is the policy enforcement point (PEP). It collects the facts about
a request and asks Cerbos, the policy decision point (PDP), for a decision. Your
service then enforces that decision.

Cerbos binds to `localhost` only. Your service must run on the same UCS server
as the Guardian package. There is no remote access to the PDP.

### Choose a client

Use an official Cerbos SDK rather than raw HTTP. The SDKs handle connection
reuse, retries and the request format. Cerbos publishes SDKs for Go, Java,
JavaScript, .NET, PHP, Python, Ruby and Rust. See the
[Cerbos ecosystem](https://www.cerbos.dev/ecosystem).

Prefer the gRPC API on port 3593. It is the faster interface and the one
upstream recommends for new code. Use the HTTP API on port 3592 when your
language has no SDK, or for shell-based checks.

The Python SDK (`pip install cerbos`) connects like this:

```python
from cerbos.sdk.grpc.client import CerbosClient
from cerbos.engine.v1 import engine_pb2
from google.protobuf.struct_pb2 import Value

principal = engine_pb2.Principal(
    id="alice",
    roles={"guardian:myapp-admin"},
)
resource = engine_pb2.Resource(
    id="x",
    kind="guardian.management_api",
    attr={"app_name": Value(string_value="myapp")},
)

with CerbosClient("127.0.0.1:3593", tls_verify=False) as client:
    if not client.is_allowed("read_resource", principal, resource):
        raise PermissionError("read_resource denied")
```

Cerbos runs without TLS here, because it is reachable on the loopback interface
only. `tls_verify=False` selects a plaintext channel.

### Send everything the policy needs

Cerbos never reads LDAP, a database or any other source. It decides on the
content of the request alone. Your service must supply every attribute that
your policies evaluate.

Cerbos also trusts what you send. It does not authenticate the end user and it
does not verify the roles in the request. Your service must authenticate the
user and resolve the roles before it asks for a decision.

A decision request carries:

- `principal`: the actor. An `id`, a list of `roles`, and free-form `attr`.
- `resources`: the objects to check. Each has a `kind` that selects the
  resource policy, an `id`, free-form `attr`, and the `actions` to check.

Read the request and response format in the
[Cerbos API reference](https://docs.cerbos.dev/cerbos/latest/api/).

### Handle the response

The response returns one result per resource, in request order. Each result maps
every requested action to `EFFECT_ALLOW` or `EFFECT_DENY`.

Treat any value other than `EFFECT_ALLOW` as a deny. Do not infer an allow from
a missing action or an empty result.

Set `includeMeta` while you develop a policy. The response then names the
matched policy, the matched scope and the effective derived roles. Turn it off
in production.

The Guardian runs Cerbos with `schema.enforcement: reject`. If a policy declares
a schema and your request does not match it, Cerbos returns `validationErrors`
with the offending path and message, and denies the action. Log these errors.
They indicate a bug in the caller, not a policy decision.

### Batch your checks

One request can carry many resources and many actions. Ask once for a whole
page of objects instead of once per object.

The Guardian raises the Cerbos request limits to 500 resources per request and
500 actions per resource. The upstream defaults are 50 and 50.

To filter a large collection, do not check every row. Call
`PlanResources` instead. Cerbos returns a query plan that says
`KIND_ALWAYS_ALLOWED`, `KIND_ALWAYS_DENIED`, or a condition that you translate
into a query filter. See
[filtering resources](https://docs.cerbos.dev/cerbos/latest/recipes/filtering-resources).

### Expect restarts, and fail closed

Cerbos restarts when an administrator sets one of the UCR variables, and when
the listener applies a new policy bundle. Requests fail during a restart.

Retry a failed call, then deny if it still fails. Never allow an action because
the PDP is unreachable. The SDKs retry transient gRPC failures by default.

### Ship your own policies

Your service needs its own resource policies. Do not rely on the policies that
come with the package. Those are illustrative and will be replaced.

Package your policies as a policy bundle and register them from your join
script. The listener then installs them on every server in the domain that runs
Cerbos. See [`docs/policy-bundles.md`](docs/policy-bundles.md).

## Current limitations

- **No transport authentication.** Cerbos is bound to localhost only, but any
  caller on the server can reach it
  ([guardian#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/288)).
- **No server-role check** in the deb. Install it only on Primary or Backup
  Directory Nodes (the App Center component enforces this; installing the `.deb`
  directly does not).

See [`docs/architecture.md`](docs/architecture.md) for the reasoning behind
these and the planned work.
