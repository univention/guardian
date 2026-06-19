# ucs-test-guardian

Pytest suite for the `univention-guardian-server` package. Talks to the
Cerbos instance run by the installed package (systemd-watched
container on `127.0.0.1:3592`)
Tests never start, stop, or reconfigure Cerbos.

## What's covered

| Test | What it pins |
|---|---|
| `test_smoke.py::test_d1_document_view_allowed_for_user` | Pure role-gate ALLOW path (examples/base.yaml) |
| `test_smoke.py::test_u1_helpdesk_resets_password_in_matching_context` | Full chain — parent role + derived role + CEL condition over principal/resource attrs (examples/udm_*.yaml) |
| `test_limits.py::test_l1_fifty_resources_in_one_request` | Documented contract: 500 resources/request, decisions keyed by resource id |
| `test_limits.py::test_l2_one_hundred_actions_in_one_request` | Documented contract: 500 actions/resource, real ALLOW + synthetic DENY |
| `test_hot_reload.py::test_hr1_add_policy_makes_kind_decidable` | Drop a `pytest_scratch_*.yaml` policy; new kind decidable within `CERBOS_RELOAD_TIMEOUT` |
| `test_hot_reload.py::test_hr2_malformed_yaml_does_not_take_cerbos_down` | Drop invalid YAML; shipped policies keep serving |
| `test_negative.py::test_n1_unknown_kind_denies` | Deny-by-default for an unknown kind, even under `admin` |

## Prerequisites

- **Root** — the hot-reload tests write `pytest_scratch_*.yaml` directly
  into `/usr/share/univention-guardian-server/policies/`. Non-root runs
  auto-skip those.

## Install and run

```sh
univention-install ucs-test ucs-test-guardian
ucs-test -E dangerous -s guardian
```

## Configuration

Defaults match the package's install layout. Override with environment
variables:

| Variable | Default | Purpose |
|---|---|---|
| `CERBOS_HOST` | `127.0.0.1:3592` | Cerbos HTTP endpoint |
| `CERBOS_POLICIES_DIR` | `/usr/share/univention-guardian-server/policies` | Where hot-reload tests drop files |
| `CERBOS_RELOAD_TIMEOUT` | `5` | Seconds to wait for a reload to take effect |

## Notes

- Scratch files use the `pytest_scratch_` prefix and land directly in
  `POLICIES_DIR`, not a subdirectory. Cerbos only watches directories that
  exist at startup; directories created at runtime are silently ignored because
  `processEvent` drops directory-creation events as non-indexable before
  `triggerUpdate` can add a watcher for them.
- The fixture removes all `pytest_scratch_*.yaml` files in teardown (even on
  test failure). If a previous run crashed hard, clean up by hand:
  `sudo rm -f /usr/share/univention-guardian-server/policies/pytest_scratch_*.yaml`.
