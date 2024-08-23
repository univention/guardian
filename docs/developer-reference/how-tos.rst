.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _how-tos:

*******
How-tos
*******

This chapter contains little how-tos and troubleshooting steps for different developer activities.

Live-edit the Guardian Manual
=============================

The following command starts up a live server for the Guardian manual:

.. code-block:: bash
   :caption: Start the Guardian manual live server on :guilabel:`HOST`

   docker run -ti --rm -v "$PWD:/project" -w /project -u $UID --network=host --pull always \
   docker-registry.knut.univention.de/sphinx:latest \
   make -C docs/guardian-manual/ livehtml

Problems with CORS
==================

If you run into problems with CORS, it might be possible to fix them, by adding the following to your ``.env`` file:

.. code-block::

   export GUARDIAN__AUTHZ__CORS__ALLOWED_ORIGINS=*
   export GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS=*

If you don't want to allow all (*), change it to a comma-separated list of
hosts that you would like to use, without spaces.

Adding licensing information
=============================

License information is added to source files via `REUSE <https://reuse.software/>`_. License information can be added
like this:

.. code-block:: bash
   :caption: Add licensing information to sources

   # Activate your preferred python env, e.g.
   # . ~/venvs/management-api/bin/activate
   pip install reuse
   reuse annotate \
   --copyright="Univention GmbH" \
   --license="AGPL-3.0-only" \
   --copyright-style="string-c" \
   --template=univention \
   --year "2023" \
   --recursive \
   --merge-copyrights \
   --skip-unrecognised \
   --skip-existing \
   .

.. _changing_authentication:

Changing authentication
=======================

You can choose between multiple authentication providers.
Set them in ``GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT`` and ``GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT``.

* `fast_api_always_authorized`
* `fast_api_never_authorized`
* `fast_api_oauth`

If you choose ``fast_api_oauth`` the local keycloak started in the compose file will be used.
The username is ``dev:univention``. The admin credentials for keycloak are ``admin:admin``.

You can use your own keycloak by changing ``OAUTH_ADAPTER__WELL_KNOWN_URL``.
You might need to change ``SSL_CERT_FILE`` and provide a cert file.
