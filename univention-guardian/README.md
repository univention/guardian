# univention-guardian-server - Cerbos PoC

Standalone UCS package that runs [Cerbos](https://docs.cerbos.dev/) as
a local policy (PDP) engine on a UCS Server. In it's current configuration,
Cerbos exposes two listeners, both bound to `localhost` only:

- `127.0.0.1:3593` — gRPC API
- `127.0.0.1:3592` — HTTP API

> This is a Proof of Concept. The audience for this README is fellow
> developers, not operators.
> Design rationale and troubleshooting live in
> [`docs/generated/architecture-cerbos-server.md`](../docs/generated/architecture-cerbos-server.md).

## Current limitations

- No authentication
- Not exposed outside the Server, only reachable on `localhost`
- No policy distribution across the UCS domain.
This will be handled in
[#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/work_items/288).

## Installation

The debian package can be installed on all UCS server roles.

```bash
echo 'deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian cerbos main' | tee /etc/apt/sources.list.d/guardian.list
apt update
apt install univention-guardian-server
```

## Integrate your own policies

The package ships its builtin policies under `policies/default/` and
examples under `policies/examples/`. To add your own, copy your Cerbos
policy files into a *separate*, per-app subdirectory:

```bash
/usr/share/univention-guardian-server/policies/<app-name>/<policy-name>.yaml
```

This manual step is only necessary until we've implemented [policy distribution across the UCS domain](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/work_items/291)

## UCR variables this package owns

| Variable | Default | Notes |
|---|---|---|
| `guardian/cerbos/log-level` | `WARN` | One of `DEBUG`, `INFO`, `WARN`, `ERROR`. Change with `ucr set` then `systemctl restart univention-guardian-server.service`. |

## Outlook

### How to implement context

#### Condition and role<->context mapping

Context as a parameter/restriction for roles can be implemented in cerbos as a condition

- Client or UDM needs to provide a role context mapping as part of the
  `principal` data

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

- `resourcePolicy` defines rules and derived role

  ```yaml
  rules:
    - actions:
        - modify_user
      effect: EFFECT_ALLOW
      derivedRoles:
        - ouadmin_context
  ```

- `derivedRoles` evaluates "context" condition

  ```yaml
  derivedRoles:
    name: udm_derived_roles
      - name: ouadmin_context
        parentRoles:
          - ouadmin
        condition:
          match:
            expr: request.principal.attr.assignments.exists(
                    a,
                    a.role == "ouadmin" && (
                      hierarchy(a.context).descendentOf(hierarchy(request.resource.attr.position)) || a.context == request.resource.attr.position
                    )
                  )
  ```

##### Open questions

- Provide the role<->context mapping as UDM property to simplify client handling? e.g.

  ```python
  class newGuardianRole(complex):
      delimiter = ', '
      subsyntaxes = [(_('Role'), string), (_('Context'), TwoThirdsString)]
      subsyntax_names = ('role', 'context')
      all_required = False
  ...
  def register_role_mapping(mapping):
      mapping.register('guardianRoles', 'univentionGuardianRoles', mapRole, unmapRole)

  def mapRole(old: Sequence[str], encoding: Sequence[str] = ()) -> list[bytes]:
      new = []
      for i in old:
          new.append('&'.join(i).encode(*encoding))
      return new

  def unmapRole(old: Sequence[bytes], encoding: Sequence[str] = ()) -> list[list[str]]:
      new = []
      for i in old:
          if b'&' in i:
              new.append(i.decode(*encoding).split('&'))
          else:
              new.append([i.decode(*encoding), ' ', ' '])
      return new
  ```

- Provide `roles` UDM property attribute?
- We could make use of the built-in hierarchy functions if we would convert LDAP position and context to a cerbos scope string: ou=school1.ou=hamburg.dc=base -> dc=base.ou=hamburg.ou=school1
- Or provide a cerbos/CEL extension for "LDAP" based hierarchy functions

  ```text
  ldap("ou=it,ou=bremen,dc=base")
    .descendentOf(
        ldap("ou=bremen,dc=base")
  )
  ```

#### Cerbos extension for role<->context mapping

To Be Discussed
