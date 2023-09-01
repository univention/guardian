# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC

from ..models.namespace import Namespace, NamespaceGetQuery, NamespacesGetQuery
from .base import BasePersistencePort


class NamespacePersistencePort(
    BasePersistencePort[Namespace, NamespaceGetQuery, NamespacesGetQuery], ABC
):
    ...
