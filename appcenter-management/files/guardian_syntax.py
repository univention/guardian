# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import re

from univention.admin.syntax import simple


class GuardianRole(simple):
    regex = re.compile(
        r"^([a-z0-9-_]+:[a-z0-9-_]+:[a-z0-9-_]+)(&[a-z0-9-_]+:[a-z0-9-_]+:[a-z0-9-_]+)?$"
    )
    # TODO prod: Add translation: univention/components/authorization-engine/guardian#28
    error_message = (
        "Guardian role strings must be lowercase ASCII alphanumeric with hyphens and underscores, "
        "in the format 'app:namespace:role' or 'app:namespace:role&app:namespace:context'!"
    )
