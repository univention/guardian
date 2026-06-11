#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH


if [ -f /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret ]; then
    echo "Copying m2m secret file..."
    mkdir -p /guardian_service_dir/conf
    cp /var/lib/univention-appcenter/apps/guardian-management-api/conf/m2m.secret /guardian_service_dir/conf/m2m.secret
    chmod 600 /guardian_service_dir/conf/m2m.secret
    chown guardian: /guardian_service_dir/conf/m2m.secret
fi
