# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC

from ..models.condition import Condition, ConditionGetQuery, ConditionsGetQuery
from .base import BasePersistencePort


class ConditionPersistencePort(
    BasePersistencePort[Condition, ConditionGetQuery, ConditionsGetQuery], ABC
):
    ...
