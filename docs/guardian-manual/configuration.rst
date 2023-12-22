.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _configuration:

*************
Configuration
*************

This chapter is a reference to all :term:`app` settings of the Guardian divided by component. These settings
can be configured either via the ``univention-app`` command line interface or the Univention App center
dialog for app settings.

To change the log level for the :term:`Management API` for example, use the following command:

.. code-block:: bash

   univention-app configure guardian-management-api --set \
      "guardian-management-api/logging/level=ERROR"

If any of the settings are changed, the application is restarted automatically.

.. _guardian-management-api-configuration:

Guardian Management API
=======================

.. _guardian-management-api-general-configuration:

General
-------

.. figure:: /_static/images/management-api/settings_general.png
   :alt: The General settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-api/base_url

Defines the base URL of the API. If unset the URL is generated from hostname and domain name of the server
the API is installed on. You must not specify the protocol here as this is set in :envvar:`guardian-management-api/protocol`.

.. envvar:: guardian-management-api/protocol

Defines the protocol of the API. Can be either ``http`` or ``https``.
Default is ``https``.

.. _guardian-management-api-logging-configuration:

Logging
-------

.. figure:: /_static/images/management-api/settings_logging.png
   :alt: The logging settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-api/logging/structured

Can be either ``True`` or ``False``. If set to ``True``, the logging output of the Management API is structured
as json data.

.. envvar:: guardian-management-api/logging/level

Sets the log level of the application. It can be one of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.

.. envvar:: guardian-management-api/logging/format

This setting defines the format of the log output if :envvar:`guardian-management-api/logging/structured`
is set to ``False``. The documentation for configuring the log format can be found
`here <https://loguru.readthedocs.io/en/stable/api/logger.html>`_.

.. _guardian-management-api-cors-configuration:

CORS
----

.. figure:: /_static/images/management-api/settings_cors.png
   :alt: The CORS settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-api/cors/allowed-origins

Comma-separated list of hosts that are allowed to make cross-origin resource sharing (CORS) requests to the server.
At a minimum, this must include the host of the :term:`Management UI`, if installed on a different server.

.. _guardian-management-api-authentication-configuration:

Authentication
--------------

.. figure:: /_static/images/management-api/settings_authentication.png
   :alt: The authentication settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-api/oauth/keycloak-uri

Base URI of the Keycloak server for authentication. If unset the application tries to derive the Keycloak URI from
the UCR variable ``keycloak/server/sso/fqdn`` or fall back to the domain name of the host the application is installed on.

.. envvar:: guardian-management-api/oauth/keycloak-client-secret

Keycloak client secret.

.. _guardian-management-api-authorization-configuration:

Authorization
-------------

.. figure:: /_static/images/management-api/settings_authorization.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-api/authorization_api_url

URL to the Authorization API. If not set, the URL is generated from hostname and domain name of the server the application
is installed on.

.. _guardian-authorization-api-configuration:

Guardian Authorization API
==========================

.. figure:: /_static/images/authorization-api/settings_settings.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-authorization-api/bundle_server_url

URL to the Management API from which to fetch the policy data for decision making.
If not set, the URL is generated from hostname and domain name of the server the application is installed on.

.. _guardian-authorization-api-logging-configuration:

Logging
-------

.. figure:: /_static/images/authorization-api/settings_logging.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-authorization-api/logging/structured

Can be either ``True`` or ``False``. If set to ``True``, the logging output of the Authorization API is structured
as json data.

.. envvar:: guardian-authorization-api/logging/level

Sets the log level of the application. It can be one of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.

.. envvar:: guardian-authorization-api/logging/format

This setting defines the format of the log output if :envvar:`guardian-authorization-api/logging/structured`
is set to ``False``. The documentation for configuring the log format can be found
`here <https://loguru.readthedocs.io/en/stable/api/logger.html>`_.

.. _guardian-authorization-api-cors-configuration:

CORS
----

.. figure:: /_static/images/authorization-api/settings_cors.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-authorization-api/cors/allowed-origins

Comma-separated list of hosts that are allowed to make cross-origin resource sharing (CORS) requests to the server.
You may need to add third-party :term:`apps<app>` to this list, if they need to use the Guardian.

.. _guardian-authorization-api-udm-configuration:

UDM
---

.. figure:: /_static/images/authorization-api/settings_udm.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-authorization-api/udm_data/url

The URL of the UDM REST API for data queries.

.. envvar:: guardian-authorization-api/udm_data/username

Username for authentication against the UDM REST API.

.. envvar:: guardian-authorization-api/udm_data/password

Password for authentication against the UDM REST API.

.. _guardian-authorization-api-authentication-configuration:

Authentication
--------------

.. figure:: /_static/images/authorization-api/settings_authentication.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-authorization-api/oauth/keycloak-uri

Base URI of the Keycloak server for authentication. If unset the application tries to derive the Keycloak URI from
the UCR variable ``keycloak/server/sso/fqdn`` or fall back to the domain name of the host the application is installed on.

.. _guardian-management-ui-configuration:

Guardian Management UI
======================

.. figure:: /_static/images/management-ui/settings_settings.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-ui/management-api-url

URL for the Guardian Management API. If not set, the URL is generated from hostname and domain name.

.. _guardian-management-ui-authentication-configuration:

Authentication
--------------

.. figure:: /_static/images/management-ui/settings_authentication.png
   :alt: The authorization settings category of the Management API in the Univention App center
   :align: left

.. envvar:: guardian-management-ui/oauth/keycloak-uri

Base URI of the Keycloak server for authentication. If unset the application tries to derive the Keycloak URI from
the UCR variable ``keycloak/server/sso/fqdn`` or fall back to the domain name of the host the application is installed on.
