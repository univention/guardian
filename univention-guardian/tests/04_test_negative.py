#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Guardian negative tests - deny-by-default for uncovered inputs
## tags: [guardian]
## exposure: safe
## packages:
##   - univention-guardian-server

# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Negative / robustness: deny-by-default for inputs no policy covers."""

from conftest import check_resources

UNKNOWN_KIND = "pytest.does_not_exist"


def test_n1_unknown_kind_denies(cerbos):
    """Unknown kind returns EFFECT_DENY for all actions, even under `admin`."""
    actions = [
        "view",
        "read",
        "create",
        "update",
        "delete",
        "do_anything",
        "frobnicate",
    ]
    result = check_resources(
        cerbos,
        roles=["admin"],
        resources=[{"id": "r-1", "kind": UNKNOWN_KIND, "actions": actions}],
    )["r-1"]
    assert all(effect == "EFFECT_DENY" for effect in result.values()), result
