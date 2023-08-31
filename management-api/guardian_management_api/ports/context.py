# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC

from ..models.context import Context, ContextGetQuery, ContextsGetQuery
from .base import BasePersistencePort


class ContextPersistencePort(
    BasePersistencePort[Context, ContextGetQuery, ContextsGetQuery], ABC
):
    ...
