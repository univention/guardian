# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from pathlib import Path

import pytest


base_dir = (Path(__file__).parent / '../../').resolve()


@pytest.fixture
def chart_default_path():
    chart_path = base_dir / 'helm/guardian-cerbos'
    return chart_path
