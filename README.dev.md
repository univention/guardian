<!--
Copyright (C) 2023-2026 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](../issues/?search=Dependency%20Dashboard)
[![Renovate](https://img.shields.io/badge/renovate-pipeline-brightgreen.svg)](../pipelines/new?var[RUN_RENOVATE]=yes)

# Developing Guardian

This file covers building, testing and releasing the
`univention-guardian-server` package. It relies on Univention's internal build
and release infrastructure. For what the package is and how to operate it, see
the [root README](README.md); for design decisions see
[`docs/architecture.md`](docs/architecture.md).

## Branch builds

Every branch or MR build publishes the `.deb` to a per-branch Aptly repo
(`debian-aptly`). Install it on a UCS server to test your branch. Replace
`<branch>` with your branch.

```sh
echo "deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian <branch> main" \
  > /etc/apt/sources.list.d/guardian-branch.list
apt update
apt install -y univention-guardian-server

systemctl is-active univention-guardian-server.service   # -> active
docker ps                                                # guardian-cerbos healthy
```

## Linting

Run the hooks defined in `.pre-commit-config.yaml` and apply Ruff autofixes
locally:

```sh
prek run -a && ruff check --fix
```

## Compiling and testing policies

Run a local `cerbos compile` from the repo root to check correctness of policies.
If you push changes to the files in `/policies` to your branch with an open MR,
this also runs in the test stage in the job `compile-policies`.

```sh
docker run --rm -v "$PWD/univention-guardian/policies:/policies" \
  ghcr.io/cerbos/cerbos:0.54.0 compile /policies
```

## Testing on UCS

Run the integration tests on a UCS VM that has the package installed:

```sh
univention-install ucs-test ucs-test-guardian
ucs-test -E dangerous -s guardian
```

## Releasing

The `.deb` is released like any other UCS package through the regular errata
process; the release mechanics are not Guardian-specific. It is additionally
published as the `univention-guardian` App Center component app.

Every branch or MR build publishes the `.deb` to a per-branch Aptly repo
(`debian-aptly`), which is what [Branch builds](#branch-builds) installs from.

**Cerbos image.** The package pulls Cerbos from Univention's artifact registry.
The `mirror-cerbos-image` CI job copies the pinned upstream image there; it runs
automatically on protected branches and as a manual job on any branch or MR that
changes the pin. The registry image is shared and immutable, so once a version
is mirrored it is available to every branch. When updating the version, trigger
the manual `mirror-cerbos-image` job on the branch pipeline first, then install
the branch `.deb` on a VM. Update the pin in both
`univention-guardian/conffiles/usr/share/univention-guardian-server/docker-compose.yaml`
and the `mirror-cerbos-image` job in `.gitlab-ci.yml`, keeping the digest
identical.
