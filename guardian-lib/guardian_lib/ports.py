# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Generic, TypeVar

from port_loader.ports import BasePort

RequestObject = TypeVar("RequestObject")


class AuthenticationPort(BasePort, Generic[RequestObject]):
    async def get_actor_identifier(self, request: RequestObject):
        """Returns the identifier of the actor that is currently authenticated."""
        raise NotImplementedError  # pragma: no cover
