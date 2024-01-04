.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _conf:

*************
Configuration
*************

This section is a reference for all :term:`app` settings of the Guardian organized by component.
:term:`Guardian administrators <guardian administrator>` can configure the settings using
either the :command:`univention-app` command
or the app settings dialog in the
:external+uv-ucs-manual:ref:`App Center UMC module <software-appcenter>`.

The App Center automatically restarts the application after changing any setting.

For example, to change the log level for the :term:`Management API`,
use the following command:

.. code-block:: bash
   :caption: Example: Change log level for *Management API*

   $ univention-app \
      configure guardian-management-api \
      --set "guardian-management-api/logging/level=ERROR"

You find configuration settings for the following Guardian components at:

* :ref:`conf-management-api`
* :ref:`conf-authorization-api`
* :ref:`conf-management-ui`


.. _conf-management-api:

Management API
==============

This section describes the configuration settings for the :term:`Management API`.

.. _conf-management-api-general:

General
-------

:numref:`conf-management-api-general-fig` shows the *General* settings category
of the *Management API* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-api-general-fig:

.. figure:: /images/management-api/settings_general.png
   :alt: The General settings category of the Management API in the App Center

   The *General* settings category of the Management API in the App Center

.. envvar:: guardian-management-api/base_url

   Defines the base URL of the API.
   If the value is unset,
   the *Management API* generates the URL from hostname and domain name of the UCS system, where you installed it.
   You mustn't specify the protocol.
   :envvar:`guardian-management-api/protocol` sets the protocol separately.

.. envvar:: guardian-management-api/protocol

   Defines the protocol of the *Management API*.
   It can have the value ``http`` or ``https``.
   The default value is ``https``.

.. _conf-management-api-logging:

Logging
-------

:numref:`conf-management-api-logging-fig` shows the *Logging* settings category
of the *Management API* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-api-logging-fig:

.. figure:: /images/management-api/settings_logging.png
   :alt: The Logging settings category of the Management API in the Univention App Center

   The *Logging* settings category of the Management API in the Univention App Center

.. envvar:: guardian-management-api/logging/structured

   Defines if the logging output of the *Management API* uses structured JSON data.
   The value can either be ``True`` or ``False``.
   The default value is ``False``.
   Set the value to ``True`` for structured JSON data.

.. envvar:: guardian-management-api/logging/level

   Defines the logging level of the *Management API* application.
   The value can be ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.
   The default value is ``INFO``.

.. envvar:: guardian-management-api/logging/format

   This setting defines the format of the logging output,
   if :envvar:`guardian-management-api/logging/structured` has the value ``False``.
   For the logging output format,
   see the section :external+loguru:ref:`time` in the
   :external+loguru:doc:`loguru documentation <index>`.

.. _conf-management-api-cors:

Cross-origin resource sharing (CORS)
------------------------------------

:numref:`conf-management-api-cors-fig` shows the *CORS* settings category
of the *Management API* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-api-cors-fig:

.. figure:: /images/management-api/settings_cors.png
   :alt: The CORS settings category of the Management API in the Univention App Center

   The *CORS* settings category of the Management API in the Univention App Center

.. envvar:: guardian-management-api/cors/allowed-origins

   Defines a comma-separated list of hosts
   that the *Management API* allows to make cross-origin resource sharing (CORS) requests to the server.
   At a minimum, the setting must include the UCS system
   where you installed the :term:`Management UI`, if installed on a different system.

.. _conf-management-api-authentication:

Authentication
--------------

:numref:`conf-management-api-authentication-fig` shows the *Authentication* settings category
of the *Management API* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-api-authentication-fig:

.. figure:: /images/management-api/settings_authentication.png
   :alt: The Authentication settings category of the Management API in the Univention App Center

   The *Authentication* settings category of the Management API in the Univention App Center

.. envvar:: guardian-management-api/oauth/keycloak-uri

   Defines the base URI of the Keycloak server for authentication.
   If unset, the application tries to derive the Keycloak URI from the UCR variable
   :external+uv-keycloak-app:envvar:`keycloak/server/sso/fqdn`
   or falls back to the domain name of the UCS system where you installed the application.

.. envvar:: guardian-management-api/oauth/keycloak-client-secret

   Defines the Keycloak client secret that the *Management API* needs for accessing Keycloak.

.. _conf-management-api-authorization:

Authorization
-------------

:numref:`conf-management-api-authorization-fig` shows the *Authorization* settings category
of the *Management API* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-api-authorization-fig:

.. figure:: /images/management-api/settings_authorization.png
   :alt: The Authorization settings category of the Management API in the Univention App Center

   The *Authorization* settings category of the Management API in the Univention App Center

.. envvar:: guardian-management-api/authorization_api_url

   Defines the URL to the *Authorization API*.
   If not set, the *Management API* generates the URL from hostname and domain name of the UCS system
   where you installed the application.

.. _conf-authorization-api:

Authorization API
=================

This section describes the configuration settings for the :term:`Authorization API`.

:numref:`conf-authorization-api-fig` shows the settings category
of the *Authorization API* in the App Center.
The available configuration settings and their description follow.

.. _conf-authorization-api-fig:

.. figure:: /images/authorization-api/settings_settings.png
   :alt: The Authorization settings category of the Authorization API in the Univention App Center

   The *Authorization* settings category of the Authorization API in the Univention App Center

.. envvar:: guardian-authorization-api/bundle_server_url

   Defines the URL to the *Management API*
   from which the *Authorization API* fetches the policy data for decision making.
   If not set, the *Authorization API* generates the URL from hostname and domain name of the UCS system
   where you installed the application.

.. _conf-authorization-api-logging:

Logging
-------

:numref:`conf-authorization-api-logging-fig` shows the *Logging* settings category
of the *Authorization API* in the App Center.
The available configuration settings and their description follow.

.. _conf-authorization-api-logging-fig:

.. figure:: /images/authorization-api/settings_logging.png
   :alt: The *Logging* settings category of the Authorization API in the Univention App Center

   The *Logging* settings category of the Authorization API in the Univention App Center

.. envvar:: guardian-authorization-api/logging/structured

   Defines if the logging output of the *Authorization API* uses structured JSON data.
   The value can either be ``True`` or ``False``.
   The default value is ``False``.
   Set the value to ``True`` for structured JSON data.

.. envvar:: guardian-authorization-api/logging/level

   Defines the logging level of the *Authorization API* application.
   The value can be ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.
   The default value is ``INFO``.

.. envvar:: guardian-authorization-api/logging/format

   This setting defines the format of the logging output,
   if :envvar:`guardian-authorization-api/logging/structured` has the value ``False``.
   For the logging output format,
   see the section :external+loguru:ref:`time` in the
   :external+loguru:doc:`loguru documentation <index>`.

.. _conf-authorization-api-cors:

Cross-origin resource sharing (CORS)
------------------------------------

:numref:`conf-authorization-api-cors-fig` shows the *CORS* settings category
of the *Authorization API* in the App Center.
The available configuration settings and their description follow.

.. _conf-authorization-api-cors-fig:

.. figure:: /images/authorization-api/settings_cors.png
   :alt: The CORS settings category of the Authorization API in the Univention App Center

   The *CORS* settings category of the Authorization API in the Univention App Center

.. envvar:: guardian-authorization-api/cors/allowed-origins

   Defines a comma-separated list of hosts
   that the *Authorization API* allows to make cross-origin resource sharing (CORS) requests to the server.
   Add third-party :term:`apps <app>` to this list,
   if they need to use the Guardian.

.. _conf-authorization-api-udm:

UDM
---

:numref:`conf-authorization-api-udm-fig` shows the *UDM* settings category
of the *Authorization API* in the App Center.
The available configuration settings and their description follow.

.. _conf-authorization-api-udm-fig:

.. figure:: /images/authorization-api/settings_udm.png
   :alt: The UDM settings category of the Authorization API in the Univention App Center

   The *UDM* settings category of the Authorization API in the Univention App Center

.. envvar:: guardian-authorization-api/udm_data/url

   Defines the URL of the
   :external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`
   for data queries.

.. envvar:: guardian-authorization-api/udm_data/username

   Defines the username for authentication against the
   :external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`.

.. envvar:: guardian-authorization-api/udm_data/password

   Defines the password for authentication against the
   :external+uv-dev-ref:ref:`UDM REST API <udm-rest-api>`.

.. _conf-authorization-api-authentication:

Authentication
--------------

:numref:`conf-authorization-api-authentication-fig` shows the *Authentication* settings category
of the *Authorization API* in the App Center.
The available configuration settings and their description follow.

.. _conf-authorization-api-authentication-fig:

.. figure:: /images/authorization-api/settings_authentication.png
   :alt: The Authentication settings category of the Management API in the Univention App Center

   The *Authentication* settings category of the Management API in the Univention App Center

.. envvar:: guardian-authorization-api/oauth/keycloak-uri

   Defines the base URI of the Keycloak server for authentication.
   If unset, the application tries to derive the Keycloak URI from the UCR variable
   :external+uv-keycloak-app:envvar:`keycloak/server/sso/fqdn`
   or falls back to the domain name of the UCS system where you installed the application.

.. _conf-management-ui:

Management UI
=============

This section describes the configuration settings for the :term:`Management UI`.

:numref:`conf-management-ui-fig` shows the settings category
of the *Management UI* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-ui-fig:

.. figure:: /images/management-ui/settings_settings.png
   :alt: The settings of the Management UI in the Univention App Center

   The settings of the Management UI in the Univention App Center

.. envvar:: guardian-management-ui/management-api-url

   Defines the URL to the *Management API*
   If not set, the *Management UI* generates the URL from hostname and domain name of the UCS system
   where you installed the application.

.. _conf-management-ui-authentication:

Authentication
--------------

:numref:`conf-management-ui-authentication-fig` shows the *Authentication* settings category
of the *Management UI* in the App Center.
The available configuration settings and their description follow.

.. _conf-management-ui-authentication-fig:

.. figure:: /images/management-ui/settings_authentication.png
   :alt: The Authentication settings category of the Management UI in the Univention App Center

   The *Authentication* settings category of the Management UI in the Univention App Center

.. envvar:: guardian-management-ui/oauth/keycloak-uri

   Defines the base URI of the Keycloak server for authentication.
   If unset, the application tries to derive the Keycloak URI from the UCR variable
   :external+uv-keycloak-app:envvar:`keycloak/server/sso/fqdn`
   or falls back to the domain name of the UCS system where you installed the application.
