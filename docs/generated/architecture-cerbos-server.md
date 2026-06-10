# Architecture -- Guardian Cerbos PoC

**Date:** 2026-06-09
**Version:** 0.0.1
**Type:** Standalone UCS Debian package

---

## Executive Summary

Standalone UCS package (`univention-guardian-server`) that runs
[Cerbos](https://docs.cerbos.dev/) as a policy engine on a UCS primary.
The goal is to evaluate whether Cerbos could replace OPA as Guardian's
policy backend, **without** touching the existing Guardian services. The
package ships with a small set of YAML policies translated from
Guardian's current OPA-based capabilities. Cerbos is reachable on
`127.0.0.1:3592` (localhost only).

This is a Proof of Concept. It does not change Guardian's
`authorization-api` / `management-api` / `management-ui` and is not
intended for production.

Tracking issue:
[guardian#286](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/286).

---

## Decisions

| Decision | Rationale |
|---|---|
| **Standalone** on the UCS primary | No changes to existing Guardian services; safe to add and remove without affecting current authorization paths |
| **Policies as YAML** under `/usr/share/univention-guardian-server/policies` | Shipped in the deb. Single dir (no shipped/admin split) — Cerbos's disk driver has no shadow semantics, so a dual-mount design was abandoned |
| **Product-shipped only** | Defaults are baked into the package; `apt upgrade` replaces them. A multi-package "register policies across debs" mechanism is the subject of [guardian#286 follow-up issues](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues) |
| **No transport authentication** | Cerbos binds to `127.0.0.1:3592` (localhost only). Authentication is not yet implemented; see [guardian#288](https://git.knut.univention.de/univention/dev/projects/authorization-engine/guardian/-/issues/288) |
| **Service auto-starts** at install | No `--no-enable --no-start` override on `dh_installsystemd`; default flow needs no manual `systemctl` |
| **First scenario translated**: Guardian's `<app>-admin` capability | CRUD on management-api resources where `app_name` matches. One Cerbos resource policy + one derived role; policy tests lock in ALLOW/DENY |

---

## Component Layout

```text
/usr/share/univention-guardian-server/
├── docker-compose.yaml      ─── UCR-templated
├── config/config.yaml       ─── UCR-templated Cerbos config
└── policies/
    ├── default/*.yaml               ─── Product-shipped policies (loaded by Cerbos)
    ├── examples/            ─── UDM/helpdesk/ouadmin example policies
    └── tests/               ─── Policy test files (not loaded by Cerbos)

/usr/sbin/univention-guardian-server-test   ─── compile + run policy tests against the installed tree
/usr/lib/univention-install/90univention-guardian-server.inst
/usr/lib/univention-uninstall/20univention-guardian-server.uinst
```

The systemd unit `univention-guardian-server.service` runs the docker-compose
stack as a long-lived process; `Restart=on-failure` recovers from
container exits.

---

## Install

The deb is built and published via CI. On a UCS primary, add the apt
source for this branch:

```sh
echo "deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian rowino-cerbos-poc main" \
  | sudo tee /etc/apt/sources.list.d/guardian-cerbos.list
sudo apt update
sudo apt install -y docker-compose univention-guardian-server
```

That's it. The systemd unit auto-starts Cerbos bound to
`127.0.0.1:3592`. Verify with the steps below.

## Verify it's working

```sh
sudo systemctl is-active univention-guardian-server.service    # active
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

Hot-reload: edit a YAML file under `/usr/share/univention-guardian-server/policies/`
and Cerbos picks it up within ~3 s (`journalctl -u univention-guardian-server.service`
shows the reload). Note these edits are lost on next package upgrade.

Do **not** name a policy file `*_test.yaml` — Cerbos treats those as
test files (not policies) and silently ignores them at runtime.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `apt install` fails on `docker-compose` | Not preinstalled on UCS 5 | `sudo apt install docker-compose` first |
| Added a policy file under `/usr/share/univention-guardian-server/policies/` but `EFFECT_DENY` says it's not loaded | Filename ends in `_test.yaml`; Cerbos treats it as a test file | Rename to something without the `_test` suffix |

### UCR variables this package owns

| Variable | Default | Notes |
|---|---|---|
| `guardian/cerbos/log-level` | `WARN` | One of `DEBUG`, `INFO`, `WARN`, `ERROR`. Change with `ucr set` then `systemctl restart univention-guardian-server.service`. |

All other knobs (image pin, mount paths) are hardcoded in the
UCR-templated `/usr/share/univention-guardian-server/docker-compose.yaml`.
Edit the template under `/etc/univention/templates/files/…` and
`ucr commit` to override.

---

## PoC limitations

These are intentional gaps — fine for the PoC, would need to be
addressed before any production use.

- **No transport authentication.** Cerbos is bound to localhost only;
  any caller on the primary can reach it.
- **No primary-role gate** in the deb. Just don't install it on a
  non-primary.
- **Shipped policies are still replaced on upgrade; custom ones can be
  added but not shadowed.** The deb owns only `policies/default/` and
  `policies/examples/`, so `apt upgrade` overwrites files there (and drops
  any a new version stops shipping). Admin- or third-party-supplied
  policies in *any other* subdir under
  `/usr/share/univention-guardian-server/policies/` (e.g. `local/` or a
  per-app dir from a separate package) are not owned by this deb and
  survive upgrades — Cerbos loads the whole tree recursively. The
  remaining limit is *override*, not placement: two policies with the same
  `(resource, version)` are a duplicate-definition error, not a shadow, so
  a custom dir can only add new policies, not replace the shipped ones.

---

## Appendix -- Hiccups encountered during development

Non-obvious problems we hit and how they're handled now.

### 1. `.inst` / `.uinst` location

`dh-univention-join-install` looks for `*<package>.inst` files at the
**source tree root**, not under `debian/`. The starter branch had them
in `debian/`, where they were silently dropped from the deb. Fixed by
moving to the package source root (`90univention-guardian-server.inst` /
`20univention-guardian-server.uinst`).

### 2. Cerbos has no shadow-override semantics

Two policies with the same `(resource, version)` raise
`duplicate policy definitions` — Cerbos drops the duplicate rather
than letting one shadow the other. This killed an early idea of
splitting policies into shipped `defaults/` and admin-writable
`overrides/`. Layout simplified to a single `policies/` directory.

---

## Verified on `claude-vm` (UCS 5.2-6)

- `dpkg-buildpackage -us -uc -b` produces the `.deb`.
- `apt install univention-guardian-server` (after `apt install docker-compose`)
  → service auto-starts, `guardian-cerbos` container healthy on
  `127.0.0.1:3592`.
- `curl http://127.0.0.1:3592/api/check/resources` returns
  `EFFECT_ALLOW` / `EFFECT_DENY` as expected for the `<app>-admin`
  scenario.
- `univention-guardian-test` → 38/38 policy tests pass.
- Hot-reload of an edited YAML file in
  `/usr/share/univention-guardian-server/policies/` works.
