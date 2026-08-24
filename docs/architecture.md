<!--
Copyright (C) 2026 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian architecture

The Guardian is delivered as a standalone UCS Debian package
(`univention-guardian-server`) that runs [Cerbos](https://docs.cerbos.dev/) as
the policy engine on a UCS server. Cerbos replaces the legacy OPA-based engine
and evaluates requests against a set of YAML policies. It is reachable on
`127.0.0.1:3593` (gRPC) and `127.0.0.1:3592` (HTTP), and from containers on the
shared `guardian` Docker network.

For install and configuration, see the [root README](../README.md); for
building, testing and releasing, see [`README.dev.md`](../README.dev.md).

## Design decisions

| Decision | Rationale |
|---|---|
| **Standalone package** on the UCS server | Self-contained: Cerbos runs as a docker-compose stack under systemd, with no runtime dependency on other services. It can be installed and removed cleanly. |
| **Policies as YAML** under `/usr/share/univention-guardian-server/policies` | Included in the deb, loaded from a single directory. Cerbos's disk driver has no shadow semantics, so a dual-mount split into included and admin-writable directories was not adopted. |
| **Policy distribution model** | The package includes its own policies in the deb (replaced by `apt upgrade`); apps and other packages distribute their policies across the domain by registering policy bundles in LDAP that the listener installs (see [Policy delivery](#policy-delivery)). |
| **Service auto-starts** at install | Default `dh_installsystemd` flow; no manual `systemctl` needed. |

## Component layout

```text
/usr/share/univention-guardian-server/
├── docker-compose.yaml      UCR-templated
├── config/cerbos.yaml       UCR-templated Cerbos config
└── policies/
    ├── default/             Included example policy (loaded by Cerbos)
    └── examples/            Illustrative policies (document, UDM helpdesk/ouadmin)

/usr/lib/univention-directory-listener/system/cerbos-policies.py   Policy-bundle listener
/usr/lib/univention-install/90univention-guardian-server.inst
/usr/lib/univention-uninstall/20univention-guardian-server.uinst
```

The package installs only `policies/default/` and `policies/examples/`. The
source tree also contains `policies/tests/`, run by CI with `cerbos compile`;
those test files are not part of the installed package.

Cerbos runs with `watchForChanges: false` and schema `enforcement: reject`. The
systemd unit `univention-guardian-server.service` runs the docker-compose stack
as a long-lived process; `Restart=on-failure` recovers from container exits.

## Included policies

The policies in `policies/default/` and `policies/examples/` originate from the
Cerbos proof of concept. They are illustrative only, not a finalized
authorization model, and will be replaced. `policies/tests/` (source tree only)
exercises them with Cerbos policy tests.

A product's own authorization policies are delivered by its app or package as
policy bundles (see [Policy delivery](#policy-delivery)), not by this package.

## Policy delivery

Policies reach a server two ways: the policies included in the deb, and
domain-distributed bundles registered in LDAP. A bundle is a `settings/data`
object; the included listener (`listener/src/cerbos-policies.py`) installs it into
a per-app subdirectory (`policies/<app>/`, owned `64110:64110`), validates it
with `cerbos compile`, and restarts Cerbos. Cerbos does not hot-reload; a
restart is required for any policy change to take effect. The authoring and
registration workflow is documented in
[`policy-bundles.md`](policy-bundles.md).

On Nubus for Kubernetes,
the `guardian-cerbos` chart mounts each policy source
as its own subdirectory below `/policies`
and compiles the whole tree in an init container before the server starts.
There is no listener and no LDAP bundle there;
a packaged integration carries the policy files instead.
The per-source subdirectory layout is the same on both platforms.
See [`kubernetes-policies.md`](kubernetes-policies.md).

## Design concepts (not yet implemented)

### Configuration setting for guardian endpoint

We need a configuration for services to retrieve the Cerbos endpoint
This will be required as soon as a service starts using guardian and
runs on both deployments, UCS and N4K (such as UDM or the Portal).

Because endpoints will likely differ between deployments, we should simplify
service integration by providing a standardized configuration.

### Transport authentication

Cerbos currently trusts every local caller.

### Role-to-context mapping

Guardian roles are currently global. To restrict a role to part of the LDAP
tree (for example, an `ouadmin` who may only manage a specific OU), Cerbos can
evaluate a *context* as a condition on a derived role.

The client or UDM would provide a role-to-context mapping in the principal data:

```yaml
attr:
  assignments:
    - role: ouadmin
      context: base.hamburg
    - role: ouadmin
      context: base.bremen
    - role: helpdesk
      context: base.berlin
```

A resource policy references a derived role:

```yaml
rules:
  - actions:
      - modify_user
    effect: EFFECT_ALLOW
    derivedRoles:
      - ouadmin_context
```

The derived role evaluates the context condition, allowing the action only when
the principal's assignment covers the resource's position in the tree:

```yaml
derivedRoles:
  name: udm_derived_roles
  definitions:
    - name: ouadmin_context
      parentRoles:
        - ouadmin
      condition:
        match:
          expr: >-
            request.principal.attr.assignments.exists(
              a,
              a.role == "ouadmin" && (
                hierarchy(a.context).descendentOf(hierarchy(request.resource.attr.position))
                || a.context == request.resource.attr.position
              )
            )
```

Open questions:

- Expose the role-to-context mapping as a UDM property to simplify client
  handling (for example a complex `guardianRoles` syntax of role plus context).
- Reuse Cerbos's built-in `hierarchy` functions by converting an LDAP position
  to a scope string (`ou=school1,ou=hamburg,dc=base` ->
  `dc=base.ou=hamburg.ou=school1`), or provide a CEL extension for LDAP-based
  hierarchy checks such as
  `ldap("ou=it,ou=bremen,dc=base").descendentOf(ldap("ou=bremen,dc=base"))`.

## Implementation notes

Constraints encountered during development and their current resolution.

### Cerbos has no shadow-override semantics

Two policies with the same `(resource, version)` raise
`duplicate policy definitions`; Cerbos discards the duplicate rather than
allowing one to shadow the other. This precludes splitting policies into included
`defaults/` and admin-writable `overrides/`; the layout is therefore a single
`policies/` tree. A custom directory can add new policies but cannot replace
the included ones.
