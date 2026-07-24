<!--
Copyright (C) 2026 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Testing the Guardian

The release deliverable is the `univention-guardian-server` Debian package
(source package `univention-guardian`). It is shipped like any other UCS
package through the regular errata process there is nothing
Guardian-specific about the release mechanics. It is additionally published
as the `univention-guardian` App Center component App.

## On a UCS VM

Every branch/MR build publishes the `.deb` to a per-branch Aptly repo
(`debian-aptly`). On a UCS server, add the branch source and install:

```sh
echo "deb [trusted=yes] http://omar.knut.univention.de/build2/git/guardian <branch-slug> main" \
  > /etc/apt/sources.list.d/guardian-branch.list
apt update && apt install -y docker-compose univention-guardian-server
systemctl is-active univention-guardian-server.service
```

Run the integration tests (details in
[`univention-guardian/tests/README.md`](../univention-guardian/tests/README.md)):

```sh
univention-install ucs-test ucs-test-guardian
ucs-test -E dangerous -s guardian
```

## Offline policy tests

No VM required, compile and self-test the shipped policies directly:

```sh
cerbos compile univention-guardian/policies
```

## Cerbos image

The package pulls Cerbos from Univention's artifact registry; the
`mirror-cerbos-image` CI job copies the pinned upstream image there. It runs
automatically on protected branches and as a manual job on a branch/MR that changes the pin.
The registry image is shared and immutable, so once a version is mirrored, it is available to
every branch. Only when bumping a version do you need to click the manual `mirror-cerbos-image`
job on the branch pipeline first then the branch `.deb` installs the same image on a VM.
For an unchanged version, it is already in the registry.

When bumping Cerbos, update the pin in both the shipped
`univention-guardian/conffiles/usr/share/univention-guardian-server/docker-compose.yaml`
and the `mirror-cerbos-image` job in `.gitlab-ci.yml`, keeping the digest
identical.
