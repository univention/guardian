# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

udm users/user delete --dn=uid=guardian,cn=users,dc=school,dc=test || true

udm users/user create \
  --set username=guardian \
  --set lastname=app-admin \
  --set password=univention \
  --set guardianRole=guardian:builtin:app-admin \
  --position cn=users,$(ucr get ldap/base)
