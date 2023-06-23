# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

"""
API Endpoints Reference:

* app
  * POST /apps/register
  * POST /apps
  * GET /apps
  * GET /apps/{app_name}
  * PATCH /apps/{app_name}

* namespace
  * POST /namespaces
  * GET /namespaces
  * GET /namespaces/{app_name}
  * GET /namespaces/{app_name}/{namespace_name}
  * PATCH /namespaces/{app_name}/{namespace_name}

* role
  * POST /roles
  * GET /roles
  * GET /roles/{app_name}
  * GET /roles/{app_name}/{namespace_name}
  * GET /roles/{app_name}/{namespace_name}/{role_name}
  * PATCH /roles/{app_name}/{namespace_name}/{role_name}

* context
  * POST /contexts
  * GET /contexts
  * GET /contexts/{app_name}
  * GET /contexts/{app_name}/{namespace_name}
  * GET /contexts/{app_name}/{namespace_name}/{context_name}
  * PATCH /contexts/{app_name}/{namespace_name}/{context_name}

* permission
  * POST /permissions
  * GET /permissions
  * GET /permissions/{app_name}
  * GET /permissions/{app_name}/{namespace_name}
  * GET /permissions/{app_name}/{namespace_name}/{permissions_name}
  * PATCH /merissions/{app_name}/{namespace_name}/{permissions_name}

* condition
  * POST /conditions
  * GET /conditions
  * GET /conditions/{app_name}/{namespace_name}/{condition_name}
  * PATCH /conditions/{app_name}/{namespace_name}/{condition_name}

* custom endpoint
  * POST /custom-endpoints
  * PATCH /custom-endpoints/{app_name}/{namespace_name}/{endpoint_name}

* role-capability-mapping
  * PUT /role-capability-mapping
  * GET /role-capability-mapping
  * PUT /role-capability-mapping/{app_name}/{namespace_name}
  * GET /role-capability-mapping/{app_name}/{namespace_name}
  * DELETE /role-capability-mapping/{app_name}/{namespace_name}
"""
