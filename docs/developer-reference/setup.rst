.. Copyright (C) 2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

***************
Developer Setup
***************

The entire Guardian application can be run locally on your notebook.
All you need for that is `docker <https://docs.docker.com/engine/install/ubuntu/>`_.
The following command assumes that you followed the steps to use `docker as a non root user <https://docs.docker.com/engine/install/linux-postinstall/>`_.
If you prefer to run docker with *sudo*, adapt accordingly.

.. _start_guardian_code_block:

.. code-block:: bash
   :caption: Start Guardian stack on :guilabel:`HOST`

   cp .env.example .env  # Only needs to be done once.
   ./dev-run

Once the Guardian started, the components can be found under the following URLs:

.. note::

   Your browser needs to be able to resolve the hostname ``traefik`` to ``localhost`` for the Guardian to work.
   One way to achieve this, is to add the following line to the ``/etc/hosts`` file:

   .. code-block::

      127.0.0.1 traefik

* `Management UI <http://localhost/univention/guardian/management-ui>`_
* `Management API <http://localhost/guardian/management/docs>`_
* `Authorization API <http://localhost/guardian/authorization/docs>`_
* `Keycloak <http://traefik/guardian/keycloak>`_
* `Traefik Dashboard <http://traefik:8888/dashboard/>`_

The credentials are documented in :ref:`changing_authentication`.

App Troubleshooting
-------------------

If you receive 404s for any of the apps,
the `Traefik dashboard <http://traefik:8888/dashboard/#/http/routers>`_
provides a list of routers and other troubleshooting interfaces.

In the app container configuration in ``dev-compose.yaml``,
ensure that the ``PathPrefix`` listed in the compose file appears in the Traefik dashboard.
If not, this may indicate that the app container is not healthy.
Verify that the docker container is running and passes its health checks.
If the app container is not running,
verify that its dependencies started without error.

If the docker container and its dependencies are healthy,
verify that the ``PathPrefix`` listed in the ``dev-compose.yaml`` configuration matches the URL that nginx or uvicorn uses to serve the application.
In the case of Keycloak,
verify the ``KC_HTTP_RELATIVE_PATH`` in the Keycloak Dockerfile.

If you receive a "Bad Gateway" instead of a 404,
this may indicate a misconfigured proxy port.
Verify the following:

1. The nginx or uvicorn port matches the configured traefik loadbalancer port.
2. The Docker container exposes the effected port.

In the case of Keycloak,
the `Keycloak Container Guide <https://www.keycloak.org/server/containers#_starting_the_optimized_keycloak_container_image>`_
has more information on which ports the Docker container exposes.
By default we expect port 8080 for the http service.

Choice of database
==================

Per default the local Guardian runs with a sqlite database.
You also have the option to run the Guardian with a postgresql database.
For that you have to start the local setup with:

.. code-block:: bash
   :caption: Start Guardian stack with Postgresql on :guilabel:`HOST`

   ./dev-run --postgres

Configuration
=============

The configuration of the local Guardian stack can be changed by editing the ``.env`` file,
which you copied in :ref:`start_guardian_code_block`.

Which environment variables and values are possible is documented in :ref:`adapters`.
