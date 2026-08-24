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

## UCS package builds on the main branch

Pipeline jobs automatically build the UCS packages `univention-guardian` and
`ucs-test-guardian` via repo-ng after pushing to `main`.

**You need to bump the version in `univention-guardian/debian/changelog`**

These packages are available in the internal apt repository:

```bash
deb [trusted=yes] http://omar.knut.univention.de/build2/ ucs_5.2-0-errata5.2-6/all/
deb [trusted=yes] http://omar.knut.univention.de/build2/ ucs_5.2-0-errata5.2-6/$(ARCH)/
```

and in the external errata test component, used by the jenkins tests.

The UCS version for the build system can be configured in `.gitlab-ci.yml`.

### New UCS patchlevel version

Update `UCS_VERSION` in `.gitlab-ci.yml` to the new patchlevel version.
Bump the MINOR version of the debian package version in
`univention-guardian/debian/changelog` (no release need if that is the only changes).

### New UCS major/minor version

Once we have a new UCS major/minor version, for example `5.3-0`, we need to
create a new protected branch, for example `5.2`, for updates we might need
to ship for the old UCS version.

The `main` branch should always be for the newest UCS version.

Update `UCS_VERSION` in `.gitlab-ci.yml` to the new patchlevel version.
Bump the MAJOR version of the debian package version in
`univention-guardian/debian/changelog` (no release need if that is the only changes).

And create a new component App version in the provider portal (test App Center)
for the corresponding UCS version.

## Linting

Run the hooks defined in `.pre-commit-config.yaml` and apply Ruff autofixes
locally:

```sh
prek run -a && ruff check --fix
```

To run them in the same image the pipeline uses, without installing anything:

```sh
docker compose run pre-commit
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
process; the release mechanics are not Guardian-specific.

It is additionally published as the `univention-guardian` App Center component app.
For regular updates we do not need to make any changes on this component App.
For new minor or major UCS versions we need to create a corresponding App in the
provider portal (test App Center); see
[New UCS major/minor version](#new-ucs-majorminor-version).

**Cerbos image.** Both the package and the Helm chart pull Cerbos from
Univention's artifact registry. The `mirror-cerbos-image` CI job copies the
pinned upstream image there; it runs automatically on protected branches and as a
manual job on any branch or MR that changes the pin. The registry image is shared
and immutable, so once a version is mirrored it is available to every branch.

The pin is spelled out in four places, which have to agree:

| Where | What |
| --- | --- |
| `.gitlab-ci.yml` | `CERBOS_VERSION`, `CERBOS_IMAGE_DIGEST` |
| `univention-guardian/conffiles/usr/share/univention-guardian-server/docker-compose.yaml` | `image:` |
| `helm/guardian-cerbos/values.yaml` | `cerbos.image.tag` |
| `helm/guardian-cerbos/Chart.yaml` | `appVersion` |

When updating the version, change all of them keeping version and digest
identical, and keep the `rules:changes` list of `mirror-cerbos-image` covering
every file that holds the pin. Then trigger the manual `mirror-cerbos-image` job
on the branch pipeline before installing the branch `.deb` on a VM or the chart
in a cluster -- until the image is mirrored, neither can pull it.
