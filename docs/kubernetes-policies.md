<!--
SPDX-FileCopyrightText: 2026 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
-->

# Deploying policies in Nubus for Kubernetes

This guide lists the ways a Cerbos policy set reaches the Cerbos container
deployed by the `guardian` chart, and when to use which.

Each policy source is mounted as **its own subdirectory** below `/policies`,
and Cerbos loads that tree recursively at startup.
The layout mirrors the per-app policy directories
that the UCS listener module creates,
so a policy set looks the same on both platforms.

**The chart ships no policies of its own.**
Cerbos denies by default,
so a fresh install authorizes nothing
until one of the mechanisms below puts policies in front of it.

The examples below are the chart's own values.

## At a glance

| Way | Use it for | Mounted at | Rolls the pod |
|---|---|---|---|
| [A packaged integration](#1-a-packaged-integration) | a product's own policy set | `/policies/extensions` | yes, on the image tag |
| [The chart values](#2-policies-in-the-chart-values) | a handful of rules, or a trial | `/policies/chart` | yes, on the ConfigMap checksum |
| [Another component's ConfigMap](#3-a-configmap-from-another-component) | an escape hatch | `/policies/<component>` | no, restart it yourself |

## 1. A packaged integration

This is the primary way to ship a policy set.
A [packaged integration](https://docs.software-univention.de/nubus-customization/1.x/en/packaged-integrations/overview.html)
is a container image that ships extension files into a Nubus deployment.
Cerbos policies can be included in a packaged integration
as a new plugin type
just like the existing plugin types.

Building a packaged integration container is documented in the
[Nubus customization manual](https://docs.software-univention.de/nubus-customization/1.x/en/packaged-integrations/bundle.html).

This chart adds a new extension type: **`guardian-policies`**.
Put the Cerbos policy files in the matching directory of your image,
and the loader copies them to `/target/guardian-policies`
like it does for every other type:

```text
plugins/
└── guardian-policies/
    ├── derived_roles_myapp.yaml
    └── resource_myapp.yaml
```

Operators load the image through `global.extensions`, as described in
[Load packaged integrations](https://docs.software-univention.de/nubus-customization/1.x/en/packaged-integrations/load.html).
That list reaches every Nubus component that supports extensions,
Cerbos among them:

```yaml
global:
  extensions:
    - name: "my-integration"
      image:
        registry: "artifacts.example.com"
        repository: "path/to/my-integration"
        tag: "1.1.10"
```

Cerbos reads what the loaders wrote, at `/policies/extensions`.
Three consequences:

- **The loaders run before `validate-policies`**,
  so a third-party policy set that does not compile
  stalls the rollout with a named file and line
  instead of crash-looping the server.
- **Updating an integration rolls the pod on its own**,
  because its image tag is part of the pod spec.
- **All integrations share one directory**,
  so two of them cannot ship a file of the same name.
  As with every nubus extenison type.

## 2. Policies in the chart values

`cerbos.policies` is the slot for policies
that belong to this deployment rather than to a product.
Each key becomes one file in `/policies/chart`:

```yaml
cerbos:
  policies:
    resource_portal_tile.yaml: |
      apiVersion: api.cerbos.dev/v1
      resourcePolicy:
        resource: portal.tile
        version: "default"
        rules:
          - actions: ["read"]
            effect: EFFECT_ALLOW
            roles: ["*"]
```

Use this for a handful of rules,
or to try a policy out on a running deployment.
Past that, a packaged integration keeps the policies in files
that `cerbos compile` can test in CI,
rather than as strings inside a values file.
The ConfigMap is subject to the usual ~1 MiB limit.

## 3. A ConfigMap from another component

An escape hatch, not a supported interface:
A chart that renders its own policy ConfigMap
can mount it as a subdirectory of `/policies`
through the `extraVolumes` and `extraVolumeMounts` interface.
`values.yaml` documents both.
Do not use the subdirectory names `chart` or `extensions`.

## Validation before start

The `validate-policies` init container runs
`cerbos compile --skip-tests /policies` over the mounted tree
before the server starts, using the same image as the server.
An invalid policy set stalls the rollout with the offending file named,
instead of crash-looping Cerbos,
and the previously running pod keeps serving.

Set `cerbos.policyValidation.enabled` to `false` to skip the check.
