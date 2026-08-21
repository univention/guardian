#!/usr/bin/python3
#
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

from cerbos.sdk.client import CerbosClient
from cerbos.sdk.model import Principal, Resource


def main():
    principal = Principal(
        id='user_123',
        roles={'employee', 'editor'},
        attr={'department': 'IT', 'location': 'Bremen'},
    )
    resource = Resource(
        id='doc_99',
        kind='document',
        attr={'owner_id': 'user_123', 'status': 'DRAFT'},
    )
    with CerbosClient(host='http://localhost:3592', raise_on_error=True) as client:
        print(f"Checking authorization for principal '{principal.id}' on resource '{resource.id}'...")
        decision = client.is_allowed(
            action='edit',
            principal=principal,
            resource=resource,
        )
        print(f'Decision is {decision}')


if __name__ == '__main__':
    main()
