# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


class ObjectNotFoundError(ValueError):
    """If the requested object could not be found."""

    ...


class PersistenceError(RuntimeError):
    """For any errors other than object not found."""

    ...


class ObjectExistsError(RuntimeError):
    """If the object to be created already exists in the persistence"""


class ParentNotFoundError(RuntimeError):
    """If the parent of the object to be created could not be found."""


class BundleGenerationIOError(RuntimeError):
    """If there are any io problems during the bundle creation"""


class BundleBuildError(Exception):
    """If the subprocess to build the OPA bundle fails"""
