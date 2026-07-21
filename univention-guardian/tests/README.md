# ucs-test-guardian

Pytest suite for the `univention-guardian-server` package. Talks to the
Cerbos instance run by the installed package (systemd-watched
container on `127.0.0.1:3592`).

`02_test_bundle_e2e.py` drives the full end-to-end delivery flow: it registers
a bundle in LDAP and verifies the listener extracts it to disk, validates it
with `cerbos compile`, restarts Cerbos, and Cerbos then serves it (invalid
bundles are rolled back and never served). This is behavior only observable on
a running UCS system. Policy correctness itself (that the shipped policies
compile and their native `policies/tests/` suites pass) is checked in the CI
pipeline with `cerbos compile`, not here.

For how policies get from LDAP onto disk (the delivery model), see
[`../listener/README.md`](../listener/README.md).

## What's covered

| Test | What it pins |
|---|---|
| `02_test_bundle_e2e.py::test_e2e_valid_bundle_is_applied` | Full chain — register a bundle, listener writes it to disk (owned 64110:64110), Cerbos restarts and serves it |
| `02_test_bundle_e2e.py::test_e2e_invalid_bundle_is_rejected` | A bundle that fails `cerbos compile` is rolled back, logged, and never served |

## Prerequisites

- **The Primary Directory Node** — restricted to the `domaincontroller_master`
  role via the `## roles:` header (only the Primary can register LDAP
  extensions); ucs-test skips it on other roles.
- **`univention-guardian-server` installed** — declared in the `## packages:`
  header, so ucs-test only runs it where the package (hence Cerbos and the
  policies dir) is present.

The test runs as root (ucs-test runs its tests as root), registers a bundle via
`ucs_registerLDAPExtension` with `cn=admin` / `/etc/ldap.secret`, restarts
Cerbos, and cleans up the LDAP object and app directory afterwards.

## Install and run

```sh
univention-install ucs-test ucs-test-guardian
ucs-test -E dangerous -s guardian
```
