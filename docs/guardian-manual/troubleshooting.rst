.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only


.. _trouble:

***************
Troubleshooting
***************

This section provides a guide to troubleshooting the Univention Guardian.
It assumes that you have a basic understanding of the Guardian and its components,
as well as familiarity with command-line tools and Docker.

.. _trouble-common:

Common issues
=============

Before attempting any other solutions, go through the following steps:

#. Restart all Guardian services.

#. Verify connectivity between the Guardian components.

Some examples for how to do this:

* Connectivity from :term:`Management API` to :term:`Authorization API`:

  .. code-block:: bash
     :caption: Check the connectivity between the *Management API* and the *Authorization API*

     $ univention-app shell guardian-authorization-api
     $ apt update; apt install -y curl
     $ curl $GUARDIAN__MANAGEMENT__ADAPTER__AUTHORIZATION_API_URL/openapi.json -I
     # verify 200 OK

* Connectivity from Open Policy Agent (OPA) to *Management API*:

  .. code-block:: bash
     :caption: Check the connectivity between the *OPA* and the *Management API*

     $ univention-app shell -s opa guardian-authorization-api
     $ apt update; apt install -y curl

     # Validate connection to management API
     $ curl -I $OPA_GUARDIAN_MANAGEMENT_URL/openapi.json
     # verify 200 OK

     # Validate if the bundle can be retrieved
     $ curl -I $OPA_GUARDIAN_MANAGEMENT_URL/$OPA_POLICY_BUNDLE
     # verify 200 OK

* Connectivity from *Management UI* to *Management API*:

  Use the developer tools in your browser and have a look for errors on the network tab.

If any of these steps fail, there could be several reasons:

#. The Guardian component that you're trying to reach
   might not be running or might not have started properly.
   Verify the :ref:`logging output <trouble-logging>` of the component
   and restart the component if necessary.

#. The Guardian component that you're trying to reach is running,
   but can't be reached by the component you're on.
   This could be due to incorrect configuration or connectivity issues.
   Use the :command:`env` command to verify the environment variables inside the container,
   and the :command:`ping` command to verify the connectivity between the containers.

#. The Guardian component that you're trying to reach is running and reachable,
   but doesn't respond to the request.
   This could be the case if the *Management API* is running,
   but it didn't generate the OPA bundle.
   Verify the component's :ref:`logging output <trouble-logging>`
   and restart the component if necessary.

.. _trouble-logging:

Logging
=======

The components of the Guardian generate logging output,
but they don't write log files.
To view the logging output,
use the following commands for the respective Guardian component:

*Authorization API*
   .. code-block:: console

      $ univention-app logs guardian-authorization-api

*Management API*
   .. code-block:: console

      $ univention-app logs guardian-management-api

*Management UI*
   .. code-block:: console

      $ univention-app logs guardian-management-ui

.. _trouble-first-time:

First time installation and configuration
=========================================

Make sure that you complete all steps of the :ref:`configuration <conf>` process.
Services don't work properly if the configuration isn't complete.

.. _trouble-management-ui:

Management UI
=============

If the *Management UI* loads but with an error,
verify the network and console tabs of your browser's developer tools.
There you can see if the UI was able to connect to the *Management API*
and if the *Management API* responded with an error.
If the *Management API* responded with an error,
verify the :ref:`logging output <trouble-logging>` of the Management API.

.. _trouble-management-api:

Management API
==============

If you see the following error message in the *Management API* logging output::

   ERROR | Unsuccessful response from the Authorization API: {'Detail': 'Not Authorized'}

then the *Management API* couldn't authorize itself to the *Authorization API*.
For more information, verify the *Authorization API* :ref:`logging output <trouble-logging>`.
Failed authorization can occur if the client secret for the *Management API* isn't configured or is incorrect.

.. _trouble-debug-opa:

Debugging OPA decisions
=======================

The Open Policy Agent (OPA) decisions can't be easily debugged at the moment.
However, there are some ways to make sure everything is working as expected:

#. OPA fetches the bundle from the Management API.
   The bundle contains the policies and the data
   that OPA needs to make decisions.
   The *Management API* generates the API from its database.

#. If OPA can't fetch the bundle,
   it shows it in its logging output.
   Whenever there's an update in the *Management API*,
   it regenerates the bundle,
   OPA fetches it again and logs it.

#. To inspect the contents of the bundle, use the following commands:

   .. code-block:: bash
      :caption: Inspect OPA bundle contents

      $ univention-app shell guardian-management-api
      $ apt update; apt install -y jq
      $ jq '.' \
        /guardian_service_dir/bundle_server/build/GuardianDataBundle/guardian/mapping/data.json

   There you can see what permissions get assigned to which roles under which conditions.

.. _trouble-authentication:

Authentication issues
=====================

If you can't sign in to the *Management UI*
or to any of the Swagger UIs for the Management API
or the Authorization API,
make sure that the Keycloak server is reachable.
You can use the following command to verify the :ref:`logging output <trouble-logging>` of the Keycloak container:

.. code-block:: bash
   :caption: Verify Keycloak logging output

   $ univention-app logs keycloak

The most common problems are incorrect redirect URLs and clock problems.

For the redirect URL,
make sure that the URL is correct.
You can verify the Keycloak server configuration at the following URL:
:samp:`https://{$FQDN_KEYCLOAK_SERVER}/admin/master/console/#/ucs/clients`.
Make sure that the redirect URL matches the *Management UI* URL for the ``guardian-ui`` client,
including the schema, such as ``https://``.

For clock problems,
a small difference between the clock of the Keycloak server
and the clock of the *Management API*
or the *Authorization API* can cause authentication problems.
If this is the case, you see it in the :ref:`logging output <trouble-logging>` of the *Management API* or the *Authorization API*.
Look for::

   WARNING | Invalid Token: "The token is not yet valid (iat)"
