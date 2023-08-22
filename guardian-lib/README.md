<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian lib

This package contains code shared by the authorization-api and management-api.

It is not intended for use outside of this repository!

## Rule for adding code to this package

Code should only be added to this package, if it is known without a doubt that the code will be needed
for **both** APIs. If code is only used in one, it should not be added here prematurely. This will ensure fewer version changes
of this package and prevent unnecessary content in this shared code library.

## Versioning

The guardian-lib is used by management-api and authorization-api. The versioning of guardian-lib is not connected
to either versions of the consuming projects. SemVer should be followed to allow for a problem free development of this
shared library.

## Building the package

While you develop on a branch, the package is build in the pipeline, but not automatically published to the registry.
This job can be triggered manually if needed. If on a feature branch, a temporary version will be generated based on
the commit hash. This should only be necessary if you have to do testing with the docker images for the APIs.
The development setup installs the local guardian-lib into the containers.

If on the main branch, the package is published automatically with the version specified in the pyproject.toml.

After that, the package can be used in the pyproject.toml for management-api and authorization-api. When using a dev version,
do not forget to change to a proper version of guardian-lib before merging your branch.

Due to a lack of a better solution the following process is currently recommended:

- Keep changes to guardian-lib in separate commits from other changes.
- If QA of the feature branch is complete, cherry-pick the commits for guardian-lib into main for a proper package build.
- Use this version for management-api and authorization-api on the feature branch if needed.
- Merge the rest of the MR.
