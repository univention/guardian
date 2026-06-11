# univention-guardian-test

Pytest suite for the `univention-guardian-server` package. Talks to the
Cerbos instance run by the installed package (systemd-watched
container on `127.0.0.1:3593`) using the official Cerbos Python SDK (gRPC).
Tests never start, stop, or reconfigure Cerbos.

## What's covered

| Test | What it pins |
|---|---|
| `test_smoke.py::test_d1_document_view_allowed_for_user` | Pure role-gate ALLOW path (examples/base.yaml) |
| `test_smoke.py::test_u1_helpdesk_resets_password_in_matching_context` | Full chain — parent role + derived role + CEL condition over principal/resource attrs (examples/udm_*.yaml) |
| `test_limits.py::test_l1_fifty_resources_in_one_request` | Documented contract: 50 resources/request, decisions keyed by resource id |
| `test_limits.py::test_l2_one_hundred_actions_in_one_request` | Documented contract: 100 actions/resource, real ALLOW + synthetic DENY |
| `test_hot_reload.py::test_hr1_add_policy_makes_kind_decidable` | Drop a `pytest_scratch_*.yaml` policy; new kind decidable within `CERBOS_RELOAD_TIMEOUT` |
| `test_hot_reload.py::test_hr2_malformed_yaml_does_not_take_cerbos_down` | Drop invalid YAML; shipped policies keep serving |
| `test_negative.py::test_n1_unknown_kind_denies` | Deny-by-default for an unknown kind, even under `admin` |

## Prerequisites

- A UCS VM with `univention-guardian-server` installed and the service
  active (`systemctl is-active univention-guardian-server.service`).
- Cerbos config bumps `requestLimits` to 100 actions × 50 resources
  per request — already in the shipped `config.yaml`.
- Python 3.11+.
- **Root** — the hot-reload tests write `pytest_scratch_*.yaml` directly
  into `/usr/share/univention-guardian-server/policies/`. Non-root runs
  auto-skip those.

## Install and run (no venv)

```sh
sudo pip install cerbos pytest --break-system-packages
sudo pytest tests/ -v
```

(`sudo` on pytest so the hot-reload tests aren't skipped.)

## Configuration

Defaults match the package's install layout. Override with environment
variables:

| Variable | Default | Purpose |
|---|---|---|
| `CERBOS_HOST` | `127.0.0.1:3593` | Cerbos gRPC endpoint |
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
