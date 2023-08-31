from abc import ABC

from ..models.condition import Condition, ConditionGetQuery, ConditionsGetQuery
from .base import BasePersistencePort


class ConditionPersistencePort(
    BasePersistencePort[Condition, ConditionGetQuery, ConditionsGetQuery], ABC
):
    ...
