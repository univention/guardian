<!--
Copyright (C) 2023-2026 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](../issues/?search=Dependency%20Dashboard)
[![Renovate](https://img.shields.io/badge/renovate-pipeline-brightgreen.svg)](../pipelines/new?var[RUN_RENOVATE]=yes)

# Guardian

The Guardian is the UCS authorization engine. It is built on
[Cerbos](https://docs.cerbos.dev/) as the policy decision point (PDP).

The release deliverable is the **`univention-guardian-server`** Debian
package, which runs Cerbos as a systemd-managed container on a UCS server
and ships a set of YAML policies. It is packaged in `univention-guardian/`
and shipped through the regular UCS errata release process. It is also
published as the `univention-guardian` App Center **component App** (a
package-based app that installs the errata package), so other apps can
depend on it via `RequiredAppsInDomain = univention-guardian`.

> **Migration from OPA:** the Guardian previously used Open Policy Agent
> (OPA) together with the Authorization/Management APIs and UI. Those
> OPA-based components have been retired in favour of the Cerbos package.
> The last commit containing the full OPA source is tagged
> **`v3.0.9-opa-final`**.

## Documentation

- Package overview, installation and UCR variables:
  [`univention-guardian/README.md`](univention-guardian/README.md)
- Architecture and design rationale:
  [`docs/generated/architecture-cerbos-server.md`](docs/generated/architecture-cerbos-server.md)
- How to test (developer-facing):
  [`docs/RELEASING.md`](docs/RELEASING.md)
- Policy test suite and ucs-test integration:
  [`univention-guardian/tests/README.md`](univention-guardian/tests/README.md)
- App Center component App definition:
  [`appcenter-guardian/ini`](appcenter-guardian/ini)

## Quick start

Install a branch build on a UCS server (see
[`docs/RELEASING.md`](docs/RELEASING.md) for how branch builds are
published) and verify Cerbos is serving:

```bash
apt install univention-guardian-server
systemctl is-active univention-guardian-server.service   # -> active
docker ps                                                # cerbos container healthy
```
