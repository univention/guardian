# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Hot-reload: policy changes under the policies dir take effect within CERBOS_RELOAD_TIMEOUT."""

import time

from .conftest import RELOAD_TIMEOUT, SCRATCH_PREFIX, check_resources, wait_until

SCRATCH_KIND = "pytest.scratch"

SCRATCH_POLICY = """\
---
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: pytest.scratch
  version: default
  rules:
    - actions:
        - view
      effect: EFFECT_ALLOW
      roles:
        - tester
"""

MALFORMED_YAML = """\
this is: not: valid: yaml
  - {{{
:::
"""


def test_hr1_add_policy_makes_kind_decidable(cerbos, scratch_dir):
    """Drop a new resource policy and a previously-unknown kind becomes decidable."""
    baseline = check_resources(
        cerbos,
        roles=["tester"],
        resources=[{"id": "r-1", "kind": SCRATCH_KIND, "actions": ["view"]}],
    )
    assert (
        baseline["r-1"]["view"] == "EFFECT_DENY"
    ), "scratch kind unexpectedly already decidable — leftover from a previous run?"

    (scratch_dir / f"{SCRATCH_PREFIX}scratch.yaml").write_text(SCRATCH_POLICY)

    wait_until(
        lambda: check_resources(
            cerbos,
            roles=["tester"],
            resources=[{"id": "r-1", "kind": SCRATCH_KIND, "actions": ["view"]}],
        )["r-1"]["view"]
        == "EFFECT_ALLOW",
        message=(
            f"{SCRATCH_KIND}.view did not flip to ALLOW within {RELOAD_TIMEOUT}s "
            "of dropping the policy"
        ),
    )

    sanity = check_resources(
        cerbos,
        roles=["user"],
        resources=[{"id": "r-1", "kind": "document", "actions": ["view"]}],
    )
    assert (
        sanity["r-1"]["view"] == "EFFECT_ALLOW"
    ), "shipped document policy stopped serving during reload"


def test_hr2_malformed_yaml_does_not_take_cerbos_down(cerbos, scratch_dir):
    """Drop invalid YAML into the policies dir → Cerbos keeps serving everything else."""
    before = check_resources(
        cerbos,
        roles=["user"],
        resources=[{"id": "r-1", "kind": "document", "actions": ["view"]}],
    )
    assert before["r-1"]["view"] == "EFFECT_ALLOW"

    (scratch_dir / f"{SCRATCH_PREFIX}broken.yaml").write_text(MALFORMED_YAML)

    # No positive signal to poll — give the watcher time to attempt the load.
    time.sleep(min(RELOAD_TIMEOUT, 3.0))

    after = check_resources(
        cerbos,
        roles=["user"],
        resources=[{"id": "r-1", "kind": "document", "actions": ["view"]}],
    )
    assert after["r-1"]["view"] == "EFFECT_ALLOW", (
        "document.view stopped returning ALLOW after dropping malformed YAML — "
        "Cerbos may have crashed or unloaded valid policies"
    )

    # And the malformed file did not somehow register a policy.
    broken = check_resources(
        cerbos,
        roles=["user", "admin"],
        resources=[{"id": "r-1", "kind": "broken", "actions": ["view"]}],
    )
    assert broken["r-1"]["view"] == "EFFECT_DENY"
