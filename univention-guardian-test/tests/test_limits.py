# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Pin config.yaml's requestLimits contract: 100 actions/resource, 50 resources/request."""

from .conftest import check_resources


def test_l1_fifty_resources_in_one_request(cerbos):
    """50 distinct `document` resources in one call — mixed ALLOW/DENY, keyed by id."""
    resources = [
        {"id": f"doc-view-{i:03d}", "kind": "document", "actions": ["view"]}
        for i in range(1, 26)
    ] + [
        {"id": f"doc-delete-{i:03d}", "kind": "document", "actions": ["delete"]}
        for i in range(1, 26)
    ]
    assert len(resources) == 50

    by_id = check_resources(cerbos, roles=["user"], resources=resources)

    assert len(by_id) == 50, by_id
    for i in range(1, 26):
        assert by_id[f"doc-view-{i:03d}"]["view"] == "EFFECT_ALLOW"
        assert by_id[f"doc-delete-{i:03d}"]["delete"] == "EFFECT_DENY"


def test_l2_one_hundred_actions_in_one_request(cerbos):
    """100 actions on a single `document` — 4 real ALLOW under admin + 96 synthetic DENY."""
    real_actions = ["view", "create", "update", "delete"]
    synthetic_actions = [f"probe_{i:04d}" for i in range(1, 97)]
    actions = real_actions + synthetic_actions
    assert len(actions) == 100

    result = check_resources(
        cerbos,
        roles=["admin"],
        resources=[{"id": "r-1", "kind": "document", "actions": actions}],
    )["r-1"]

    assert len(result) == 100, result
    for a in real_actions:
        assert result[a] == "EFFECT_ALLOW", f"{a!r} should be ALLOW under admin"
    for a in synthetic_actions:
        assert result[a] == "EFFECT_DENY", f"synthetic {a!r} should be DENY"
