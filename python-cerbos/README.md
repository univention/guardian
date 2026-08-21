# python-cerbos Debian package

This repository contains the Debian package to use [cerbos](https://cerbos.dev) in UCS 5.2.

The cerbos SDK is licensed under the Apache-2.0 license.

From the `cerbos` README:

SDK for working with Cerbos:
an open core, language-agnostic, scalable authorization solution.

## Update version

- Update `$VERSION` in `Makefile`
- Provide `cerbos-${VERSION}.tar.gz.sha256` (e.g. via `make hash`)
- Update changelog (`dch -i`)
- Update `DEBIAN_RELEASE` and `DEBIAN_SCOPE` in `.gitlab-ci.yml` and/or repository settings.
- Commit and push changes
- Either build manually (e.g. by triggering the pipeline via GitLab UI),
  or push a git tag, then the CI pipeline will build the package.

## Manual build

```bash
@omar repo_admin.py -G "https://git.knut.univention.de/univention/dev/libraries/python-cerbos.git" -p python-cerbos -b "main" -P . -s errata5.2-6 -r 5.2
@ladda build-package-ng -r 5.2 -s errata5.2-6 -p python-cerbos
```
