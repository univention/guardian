from abc import ABC

from ..models.namespace import Namespace, NamespaceGetQuery, NamespacesGetQuery
from .base import BasePersistencePort


class NamespacePersistencePort(
    BasePersistencePort[Namespace, NamespaceGetQuery, NamespacesGetQuery], ABC
):
    ...
