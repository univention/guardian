#!/usr/bin/python3
#
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

from cerbos.sdk.grpc.client import CerbosClient
from cerbos.sdk.model import Principal, Resource


def main():
    with CerbosClient('localhost:3593') as client:
        principal = Principal(id='admin_1', roles={'admin'})
        resource = Resource(id='system_config', kind='setting')
        if client.is_allowed(action='write', principal=principal, resource=resource):
            print('gRPC Check: ALLOWED')
        else:
            print('gRPC Check: DENIED')


if __name__ == '__main__':
    main()
