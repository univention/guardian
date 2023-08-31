from abc import ABC

from ..models.context import Context, ContextGetQuery, ContextsGetQuery
from .base import BasePersistencePort


class ContextPersistencePort(
    BasePersistencePort[Context, ContextGetQuery, ContextsGetQuery], ABC
):
    ...
