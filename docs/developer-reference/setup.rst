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

The credentials are documented in :ref:`changing_authentication`.

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
