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

univention-app shell guardian-management-api cp /app/management-api/rego_policy_bundle_template/univention/test_mapping/data.json /guardian_service_dir/bundle_server/build/GuardianDataBundle/guardian/mapping/data.json
univention-app shell guardian-management-api opa build -b /guardian_service_dir/bundle_server/build/GuardianDataBundle -o /guardian_service_dir/bundle_server/bundles/GuardianDataBundle.tar.gz
