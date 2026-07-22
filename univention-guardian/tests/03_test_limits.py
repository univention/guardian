#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Guardian request limits - 500 actions/resource, 500 resources/request
## tags: [guardian]
## exposure: safe
## packages:
##   - univention-guardian-server

# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Pin cerbos.yaml's requestLimits contract: 500 actions/resource, 500 resources/request."""

from conftest import check_resources


def test_l1_five_hundred_resources_in_one_request(cerbos):
    """500 distinct `document` resources in one call — mixed ALLOW/DENY, keyed by id."""
    resources = [{'id': f'doc-view-{i:03d}', 'kind': 'document', 'actions': ['view']} for i in range(1, 251)] + [
        {'id': f'doc-delete-{i:03d}', 'kind': 'document', 'actions': ['delete']} for i in range(1, 251)
    ]
    assert len(resources) == 500

    by_id = check_resources(cerbos, roles=['user'], resources=resources)

    assert len(by_id) == 500, by_id
    for i in range(1, 251):
        assert by_id[f'doc-view-{i:03d}']['view'] == 'EFFECT_ALLOW'
        assert by_id[f'doc-delete-{i:03d}']['delete'] == 'EFFECT_DENY'


def test_l2_five_hundred_actions_in_one_request(cerbos):
    """500 actions on a single `document` — 4 real ALLOW under admin + 496 synthetic DENY."""
    real_actions = ['view', 'create', 'update', 'delete']
    synthetic_actions = [f'probe_{i:04d}' for i in range(1, 497)]
    actions = real_actions + synthetic_actions
    assert len(actions) == 500

    result = check_resources(
        cerbos,
        roles=['admin'],
        resources=[{'id': 'r-1', 'kind': 'document', 'actions': actions}],
    )['r-1']

    assert len(result) == 500, result
    for a in real_actions:
        assert result[a] == 'EFFECT_ALLOW', f'{a!r} should be ALLOW under admin'
    for a in synthetic_actions:
        assert result[a] == 'EFFECT_DENY', f'synthetic {a!r} should be DENY'
