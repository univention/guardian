# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Smoke tests against shipped example policies."""

from .conftest import check_actions


def test_d1_document_view_allowed_for_user(cerbos):
    """Pure role gate: roles=['user'] can view a document (examples/base.yaml)."""
    result = check_actions(
        cerbos,
        roles=["user"],
        kind="document",
        actions=["view"],
    )
    assert result["view"] == "EFFECT_ALLOW"


def test_u1_helpdesk_resets_password_in_matching_context(cerbos):
    """Derived role + CEL condition: principal's assignments must include the resource's position."""
    result = check_actions(
        cerbos,
        roles=["helpdesk"],
        principal_id="ian",
        principal_attr={
            "assignments": [
                {"role": "helpdesk", "context": "hamburg"},
                {"role": "helpdesk", "context": "bremen"},
            ],
        },
        kind="user",
        attr={"position": "hamburg"},
        actions=["reset_password"],
    )
    assert result["reset_password"] == "EFFECT_ALLOW"
