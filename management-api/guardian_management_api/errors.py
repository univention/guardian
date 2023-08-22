# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


class ObjectNotFoundError(ValueError):
    """If the requested object could not be found."""

    ...


class PersistenceError(RuntimeError):
    """For any errors other than object not found."""

    ...
